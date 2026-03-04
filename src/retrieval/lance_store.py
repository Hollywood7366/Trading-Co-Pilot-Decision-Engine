"""
@file lance_store.py
@history
2026-01-18: Created as ChromaDB replacement - LanceDB is more stable on Windows and Python 3.14+

LanceDB client wrapper providing a ChromaDB-compatible API.

WHY LanceDB:
- Works on Python 3.11-3.14+ (no pydantic v1 dependency)
- No native backend crashes on Windows
- Embedded (no server needed), single-file storage
- Faster queries (columnar/Arrow format)
- Simple API, easy migration from Chroma
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import pyarrow as pa

logger = logging.getLogger(__name__)

# Lazy import to avoid issues at module load time
lancedb = None  # type: ignore[assignment]
LANCEDB_AVAILABLE = False


def _ensure_lancedb_imported():
    """Lazy import of lancedb."""
    global lancedb, LANCEDB_AVAILABLE
    
    if lancedb is not None:
        return
    
    try:
        import lancedb as _lancedb
        lancedb = _lancedb
        LANCEDB_AVAILABLE = True
    except ImportError:
        LANCEDB_AVAILABLE = False


@dataclass
class LanceStoreConfig:
    """Configuration for LanceDB store.
    
    WHY: Centralized config makes it easy to enforce production protections
    and consistent settings across all LanceDB operations.
    """
    persist_path: Path
    allow_production_write: bool = False
    
    def __post_init__(self):
        if not isinstance(self.persist_path, Path):
            self.persist_path = Path(self.persist_path)


class LanceCollection:
    """ChromaDB-compatible collection wrapper for LanceDB table.
    
    This provides the same API as ChromaDB collections so existing code
    can migrate with minimal changes.
    """
    
    def __init__(self, table: Any, name: str, db: Any, pending_create: bool = False):
        self._table = table
        self._name = name
        self._db = db
        self._pending_create = pending_create
        self.metadata: dict[str, Any] = {}
    
    def _ensure_table(self):
        """Ensure table exists (may have been deferred for schema inference)."""
        if self._table is None and self._pending_create:
            # Table will be created on first add
            pass
        return self._table is not None
    
    @property
    def name(self) -> str:
        return self._name
    
    def count(self) -> int:
        """Return number of records in the collection."""
        if self._table is None:
            return 0
        return self._table.count_rows()
    
    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        """Add documents to the collection (ChromaDB-compatible API)."""
        if not ids:
            return
        
        import json
        records = []
        for i, doc_id in enumerate(ids):
            # Store metadata as a single JSON column for flexibility
            # This matches ChromaDB's actual storage model
            meta = metadatas[i] if metadatas and i < len(metadatas) else {}
            record = {
                "id": doc_id,
                "vector": embeddings[i],
                "document": documents[i],
                "metadata": json.dumps(meta or {}),
            }
            records.append(record)
        
        # Create table on first add (allows schema inference)
        if self._table is None and self._pending_create:
            self._table = self._db.create_table(self._name, records)
            self._pending_create = False
        else:
            self._table.add(records)
    
    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        """Upsert documents (insert or update). ChromaDB-compatible API."""
        if not ids:
            return
        
        # If table doesn't exist yet, just add
        if self._table is None:
            self.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
            return
        
        # LanceDB's merge_insert is more complex; for simplicity, delete then add
        try:
            self._table.delete(f"id IN ({', '.join(repr(i) for i in ids)})")
        except Exception:
            pass  # IDs may not exist yet
        
        self.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    
    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int = 10,
        include: Optional[list[str]] = None,
        where: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Query by vector similarity. Returns ChromaDB-compatible response format."""
        include = include or ["documents", "metadatas", "distances"]
        
        if not query_embeddings or not query_embeddings[0]:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        if self._table is None:
            return {"ids": [[]], "documents": [[]], "metadatas": [[]], "distances": [[]]}
        
        # LanceDB query
        query_vec = query_embeddings[0]
        search = self._table.search(query_vec).limit(n_results)
        
        # Apply filter if provided
        if where:
            # Convert ChromaDB where clause to LanceDB filter
            filter_expr = _where_to_lance_filter(where)
            if filter_expr:
                search = search.where(filter_expr)
        
        results = search.to_list()
        
        import json
        
        # Convert to ChromaDB format
        ids = []
        documents = []
        metadatas = []
        distances = []
        
        for row in results:
            ids.append(row.get("id", ""))
            documents.append(row.get("document", ""))
            distances.append(row.get("_distance", 0.0))
            
            # Parse metadata from JSON column
            meta_str = row.get("metadata", "{}")
            try:
                meta = json.loads(meta_str) if isinstance(meta_str, str) else (meta_str or {})
            except json.JSONDecodeError:
                meta = {}
            metadatas.append(meta)
        
        return {
            "ids": [ids],
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances],
        }
    
    def get(
        self,
        ids: Optional[list[str]] = None,
        limit: Optional[int] = None,
        include: Optional[list[str]] = None,
        where: Optional[dict[str, Any]] = None,
        offset: Optional[int] = None,
    ) -> dict[str, Any]:
        """Get documents by ID or all documents. ChromaDB-compatible API."""
        include = include or ["documents", "metadatas"]
        
        if self._table is None:
            return {"ids": [], "documents": [], "embeddings": [], "metadatas": []}
        
        # Build query
        if ids:
            filter_expr = f"id IN ({', '.join(repr(i) for i in ids)})"
            df = self._table.search().where(filter_expr).limit(len(ids)).to_pandas()
        elif where:
            filter_expr = _where_to_lance_filter(where)
            search = self._table.search()
            if filter_expr:
                search = search.where(filter_expr)
            if limit:
                search = search.limit(limit)
            df = search.to_pandas()
        elif limit:
            df = self._table.to_pandas()[:limit]
        else:
            df = self._table.to_pandas()
        
        # Convert to ChromaDB format
        result_ids = df["id"].tolist() if "id" in df.columns else []
        result_docs = df["document"].tolist() if "document" in df.columns and "documents" in include else []
        result_embeds = df["vector"].tolist() if "vector" in df.columns and "embeddings" in include else []
        
        # Reconstruct metadatas from JSON column
        import json
        result_metas = []
        if "metadatas" in include and "metadata" in df.columns:
            for _, row in df.iterrows():
                meta_str = row.get("metadata", "{}")
                try:
                    meta = json.loads(meta_str) if isinstance(meta_str, str) else (meta_str or {})
                except json.JSONDecodeError:
                    meta = {}
                result_metas.append(meta)
        
        return {
            "ids": result_ids,
            "documents": result_docs,
            "embeddings": result_embeds,
            "metadatas": result_metas,
        }
    
    def delete(
        self,
        ids: Optional[list[str]] = None,
        where: Optional[dict[str, Any]] = None,
    ) -> None:
        """Delete documents by ID or filter."""
        if ids:
            filter_expr = f"id IN ({', '.join(repr(i) for i in ids)})"
            self._table.delete(filter_expr)
        elif where:
            filter_expr = _where_to_lance_filter(where)
            if filter_expr:
                self._table.delete(filter_expr)


def _where_to_lance_filter(where: dict[str, Any]) -> Optional[str]:
    """Convert ChromaDB where clause to LanceDB SQL filter.
    
    ChromaDB uses: {"field": "value"} or {"field": {"$eq": "value"}}
    
    Since we store metadata as JSON, we use LIKE for string matching.
    This is less precise than ChromaDB's exact matching but works for most cases.
    """
    if not where:
        return None
    
    conditions = []
    for key, value in where.items():
        if key.startswith("$"):
            # Logical operator ($and, $or)
            continue  # TODO: implement if needed
        
        # For JSON storage, use LIKE to search within the metadata JSON string
        # This matches {"key": "value"} patterns
        if isinstance(value, dict):
            # Operator format: {"$eq": "value"}
            for op, val in value.items():
                if op == "$eq":
                    # Match "key": "value" or "key": value in JSON
                    if isinstance(val, str):
                        conditions.append(f"metadata LIKE '%\"{key}\": \"{val}\"%'")
                    else:
                        conditions.append(f"metadata LIKE '%\"{key}\": {val}%'")
                elif op == "$in":
                    # OR together all values
                    or_parts = []
                    for v in val:
                        if isinstance(v, str):
                            or_parts.append(f"metadata LIKE '%\"{key}\": \"{v}\"%'")
                        else:
                            or_parts.append(f"metadata LIKE '%\"{key}\": {v}%'")
                    if or_parts:
                        conditions.append(f"({' OR '.join(or_parts)})")
        else:
            # Simple format: {"field": "value"}
            if isinstance(value, str):
                conditions.append(f"metadata LIKE '%\"{key}\": \"{value}\"%'")
            else:
                conditions.append(f"metadata LIKE '%\"{key}\": {value}%'")
    
    return " AND ".join(conditions) if conditions else None


class LanceClient:
    """ChromaDB-compatible client wrapper for LanceDB.
    
    This provides the same API as ChromaDB PersistentClient so existing code
    can migrate with minimal changes.
    """
    
    def __init__(self, db: Any, path: Path):
        self._db = db
        self._path = path
        self._collections: dict[str, LanceCollection] = {}
    
    def list_collections(self) -> list[Any]:
        """List all collections (tables)."""
        return [type("Col", (), {"name": n})() for n in self._db.table_names()]
    
    def get_collection(self, name: str) -> LanceCollection:
        """Get an existing collection."""
        if name in self._collections:
            return self._collections[name]
        
        if name not in self._db.table_names():
            raise ValueError(f"Collection '{name}' not found")
        
        table = self._db.open_table(name)
        collection = LanceCollection(table, name, self._db)
        self._collections[name] = collection
        return collection
    
    def create_collection(
        self,
        name: str,
        metadata: Optional[dict[str, Any]] = None,
        get_or_create: bool = False,
    ) -> LanceCollection:
        """Create a new collection."""
        if name in self._db.table_names():
            if get_or_create:
                return self.get_collection(name)
            raise ValueError(f"Collection '{name}' already exists")
        
        # Don't create table yet - LanceDB creates it on first add with inferred schema
        # This allows dynamic metadata columns
        collection = LanceCollection(None, name, self._db, pending_create=True)
        collection.metadata = metadata or {}
        self._collections[name] = collection
        return collection
    
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> LanceCollection:
        """Get or create a collection."""
        return self.create_collection(name, metadata=metadata, get_or_create=True)
    
    def delete_collection(self, name: str) -> None:
        """Delete a collection."""
        if name in self._db.table_names():
            self._db.drop_table(name)
        if name in self._collections:
            del self._collections[name]


def get_lance_client(
    cfg: LanceStoreConfig,
    *,
    operation: str = "unknown_operation",
) -> LanceClient:
    """Get a LanceDB client with production protection.
    
    This is the LanceDB equivalent of get_persistent_client() for Chroma.
    
    Args:
        cfg: LanceStore configuration
        operation: Description of the operation (for logging/debugging)
    
    Returns:
        LanceClient instance with ChromaDB-compatible API
    """
    _ensure_lancedb_imported()
    
    if not LANCEDB_AVAILABLE:
        raise RuntimeError(
            "lancedb is not installed. Install with: pip install lancedb"
        )
    
    # Production protection check
    try:
        from src.config import PROD_CHROMA_PATH
        is_production = cfg.persist_path.resolve() == PROD_CHROMA_PATH.resolve()
        
        if is_production and not cfg.allow_production_write:
            raise RuntimeError(
                f"Production LanceDB access requires explicit permission. "
                f"Set allow_production_write=True if intentional. Operation: {operation}"
            )
    except ImportError:
        pass  # Config not available, skip production check
    
    # Ensure directory exists
    cfg.persist_path.mkdir(parents=True, exist_ok=True)
    
    # Open LanceDB
    db = lancedb.connect(str(cfg.persist_path))
    
    logger.debug(
        "Created LanceDB client: path=%s, operation=%s",
        cfg.persist_path,
        operation,
    )
    
    return LanceClient(db, cfg.persist_path)


def get_or_create_collection(
    client: LanceClient,
    *,
    name: str,
    metadata: Optional[dict[str, Any]] = None,
) -> LanceCollection:
    """Get or create a LanceDB collection.
    
    WHY: Idempotent collection access - safe to call multiple times.
    This matches the Chroma API.
    """
    return client.get_or_create_collection(name=name, metadata=metadata)


# Migration helper
def migrate_from_chroma(
    chroma_path: Path,
    lance_path: Path,
    *,
    collection_names: Optional[list[str]] = None,
    batch_size: int = 1000,
) -> dict[str, int]:
    """Migrate data from ChromaDB to LanceDB.
    
    Args:
        chroma_path: Path to ChromaDB persist directory
        lance_path: Path for new LanceDB storage
        collection_names: Specific collections to migrate (None = all)
        batch_size: Number of records per batch
    
    Returns:
        Dict of collection_name -> record_count migrated
    """
    _ensure_lancedb_imported()
    
    # Import Chroma (requires Python 3.11)
    try:
        import chromadb
        from chromadb.config import Settings
    except ImportError:
        raise RuntimeError("chromadb required for migration. Run with Python 3.11")
    
    # Open Chroma
    chroma_client = chromadb.PersistentClient(
        path=str(chroma_path),
        settings=Settings(anonymized_telemetry=False),
    )
    
    # Open Lance
    lance_path.mkdir(parents=True, exist_ok=True)
    lance_db = lancedb.connect(str(lance_path))
    
    results = {}
    collections = collection_names or [c.name for c in chroma_client.list_collections()]
    
    for coll_name in collections:
        logger.info(f"Migrating collection: {coll_name}")
        
        chroma_coll = chroma_client.get_collection(coll_name)
        count = chroma_coll.count()
        
        if count == 0:
            logger.info(f"  Skipping empty collection: {coll_name}")
            results[coll_name] = 0
            continue
        
        # Get all data from Chroma
        data = chroma_coll.get(include=["documents", "embeddings", "metadatas"])
        
        # Prepare records for Lance
        records = []
        for i, doc_id in enumerate(data["ids"]):
            record = {
                "id": doc_id,
                "vector": data["embeddings"][i] if data.get("embeddings") else [0.0] * 384,
                "document": data["documents"][i] if data.get("documents") else "",
            }
            
            # Flatten metadata
            if data.get("metadatas") and i < len(data["metadatas"]):
                import json
                for k, v in (data["metadatas"][i] or {}).items():
                    if isinstance(v, (dict, list)):
                        record[f"meta_{k}"] = json.dumps(v)
                    else:
                        record[f"meta_{k}"] = v
            
            records.append(record)
        
        # Create Lance table and insert
        if coll_name in lance_db.table_names():
            lance_db.drop_table(coll_name)
        
        if records:
            lance_db.create_table(coll_name, records)
            results[coll_name] = len(records)
            logger.info(f"  Migrated {len(records)} records")
        else:
            results[coll_name] = 0
    
    return results
