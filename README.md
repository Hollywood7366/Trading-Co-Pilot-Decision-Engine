# Trading Co-Pilot Decision Engine

Runtime system for the Al Brooks trading copilot: retrieval, decision engine, state machine, and live NT8 integration.

## Architecture

```
src/
├── signals/      # Tag vocabulary + pattern rules (from Trading-Copilot data pipeline)
├── retrieval/    # LanceDB-native vector + SQLite structured retrieval
├── engine/       # Decision engine (scenario generation, probability reasoning)
├── state/        # Anticipatory trading state machine
├── vision/       # Slide inference (consumes trained YOLOv8 model)
└── live/         # NT8 JSONL bar stream + live loop
```

## Data Assets

Copied from the Trading-Copilot data pipeline repo (not tracked in git):

| Asset | Path | Contents |
|---|---|---|
| SQLite DB | `data/scratch.db` | 75K+ records: book chunks, slide summaries, transcripts, market updates, tags |
| LanceDB vectors | `data/lance_db/` | 75,128 embedded vectors (unified collection) |
| Tag catalogs | `data/tags/` | Canonical tag vocabulary, aliases, signal mappings |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # add your API keys
```
