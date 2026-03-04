"""
Signal Detection Module - Three-Layer Architecture

Layer 1: Tag Signals (tag_signals.py)
    - Single bar classifications (doji, trend_bar, inside_bar, etc.)
    - Binary/categorical labels
    - OHLC rules for detection

Layer 2: Pattern Rules (pattern_rules.py)
    - Multi-bar patterns (wedge, triangle, ii, ioi, etc.)
    - Range from objective (ii) to subjective (wedge)
    - Detection logic using tag signals as building blocks

Layer 3: Atomic Signals (vocabulary.py)
    - Continuous measurements (ratios, counts, distances)
    - Quality assessment for patterns
    - Feed into regime inference

Usage:
    from src.signals import (
        # Layer 1
        TAG_SIGNAL_LOOKUP, get_tag_signal, ALL_TAG_SIGNALS,
        # Layer 2
        PATTERN_RULE_LOOKUP, get_pattern_rule, ALL_PATTERN_RULES,
        # Layer 3
        ATOMIC_SIGNAL_LOOKUP, get_atomic_signal, ALL_ATOMIC_SIGNALS,
    )
"""

from .tag_signals import (
    TagSignalRule,
    ALL_TAG_SIGNALS,
    TAG_SIGNAL_LOOKUP,
    get_tag_signal,
    list_tag_signals_by_confidence,
    # Category lists
    BAR_TYPE_TAGS,
    TREND_BAR_TAGS,
    REVERSAL_BAR_TAGS,
    SIGNAL_BAR_TAGS,
    INSIDE_OUTSIDE_TAGS,
    SHAVED_BAR_TAGS,
    GAP_BAR_TAGS,
    SURPRISE_BAR_TAGS,
    BREAKOUT_BAR_TAGS,
    CLOSE_POSITION_TAGS,
    EMA_POSITION_TAGS,
    RELATIVE_HL_TAGS,
)

from .pattern_rules import (
    PatternRule,
    ALL_PATTERN_RULES,
    PATTERN_RULE_LOOKUP,
    get_pattern_rule,
    list_patterns_by_subjectivity,
    list_patterns_requiring_swings,
    list_objective_patterns,
    # Category lists
    OBJECTIVE_PATTERNS,
    MEDIUM_PATTERNS,
    HIGH_SUBJECTIVITY_PATTERNS,
    FLAG_PATTERNS,
    ENTRY_PATTERNS,
)

from .vocabulary import (
    AtomicSignal,
    DetectionSpec,
    ALL_ATOMIC_SIGNALS,
    ATOMIC_SIGNAL_LOOKUP,
    get_atomic_signal,
    list_signals_by_category,
    list_tier0_signals,
    list_signals_requiring_context,
    # Category lists
    BAR_ANATOMY_SIGNALS,
    MOMENTUM_SIGNALS,
    OVERLAP_SIGNALS,
    RANGE_SIGNALS,
    GAP_SIGNALS,
    EMA_SIGNALS,
    STRUCTURE_SIGNALS,
    BREAKOUT_SIGNALS,
    MEASURED_MOVE_SIGNALS,
    CLIMAX_SIGNALS,
)

__all__ = [
    # Layer 1: Tag Signals
    "TagSignalRule",
    "ALL_TAG_SIGNALS",
    "TAG_SIGNAL_LOOKUP",
    "get_tag_signal",
    "list_tag_signals_by_confidence",
    # Layer 2: Pattern Rules
    "PatternRule",
    "ALL_PATTERN_RULES",
    "PATTERN_RULE_LOOKUP",
    "get_pattern_rule",
    "list_patterns_by_subjectivity",
    "list_patterns_requiring_swings",
    "list_objective_patterns",
    # Layer 3: Atomic Signals
    "AtomicSignal",
    "DetectionSpec",
    "ALL_ATOMIC_SIGNALS",
    "ATOMIC_SIGNAL_LOOKUP",
    "get_atomic_signal",
    "list_signals_by_category",
    "list_tier0_signals",
    "list_signals_requiring_context",
]
