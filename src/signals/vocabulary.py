"""
@file vocabulary.py
@history
2026-01-26: Refactored - Layer 3: Atomic Signals (continuous measurements only)
           Binary classifications moved to tag_signals.py (Layer 1)
           Pattern detection moved to pattern_rules.py (Layer 2)

Layer 3: Atomic Signals (Multi-Bar Context Measurements)
- Continuous numerical values (ratios, counts, distances)
- Used to assess quality/strength of tag signals and patterns
- Feed into regime inference and decision engine
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class DetectionSpec:
    lookback_bars: int
    inputs: List[str]
    formula: str
    threshold: Optional[float]
    comparison: Optional[str]
    notes: Optional[str] = None


@dataclass(frozen=True)
class AtomicSignal:
    """Definition of a continuous atomic signal measurement."""
    signal_id: str
    tier: int  # 0 = pure OHLC, 1 = needs context, 2 = needs patterns
    description: str
    detection: DetectionSpec
    value_range: str  # e.g., "0-1", "-1 to 1", "0+", "any"
    category: str
    requires_context: List[str] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)


def _spec(
    lookback_bars: int,
    inputs: List[str],
    formula: str,
    threshold: Optional[float] = None,
    comparison: Optional[str] = None,
    notes: Optional[str] = None,
) -> DetectionSpec:
    return DetectionSpec(
        lookback_bars=lookback_bars,
        inputs=inputs,
        formula=formula,
        threshold=threshold,
        comparison=comparison,
        notes=notes,
    )


_SRC_TRADING_RANGES = "Trading_Ranges_enriched.json"
_SRC_REVERSALS = "Reversals_concept_chunks.json"
_SRC_TRENDS = "Trends_concept_chunks.json"
_SRC_RPC = "Reading_Price_Charts_concept_chunks.json"


# =============================================================================
# CATEGORY 1: BAR ANATOMY (Single bar measurements)
# =============================================================================

BAR_ANATOMY_SIGNALS = [
    AtomicSignal(
        signal_id="close_position",
        tier=0,
        description="Close location within bar range (0=low, 1=high)",
        detection=_spec(
            lookback_bars=1,
            inputs=["high", "low", "close"],
            formula="(close - low) / max(high - low, 1e-9)",
        ),
        value_range="0-1",
        category="bar_anatomy",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="body_ratio",
        tier=0,
        description="Body size as fraction of total range",
        detection=_spec(
            lookback_bars=1,
            inputs=["open", "high", "low", "close"],
            formula="abs(close - open) / max(high - low, 1e-9)",
            notes="<0.25 = doji, >0.6 = strong trend bar",
        ),
        value_range="0-1",
        category="bar_anatomy",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="upper_tail_ratio",
        tier=0,
        description="Upper tail size as fraction of total range",
        detection=_spec(
            lookback_bars=1,
            inputs=["open", "high", "low", "close"],
            formula="(high - max(open, close)) / max(high - low, 1e-9)",
        ),
        value_range="0-1",
        category="bar_anatomy",
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="lower_tail_ratio",
        tier=0,
        description="Lower tail size as fraction of total range",
        detection=_spec(
            lookback_bars=1,
            inputs=["open", "high", "low", "close"],
            formula="(min(open, close) - low) / max(high - low, 1e-9)",
        ),
        value_range="0-1",
        category="bar_anatomy",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="tail_asymmetry",
        tier=0,
        description="Upper tail minus lower tail, normalized (-1=all lower tail, +1=all upper tail)",
        detection=_spec(
            lookback_bars=1,
            inputs=["open", "high", "low", "close"],
            formula="((high - max(open, close)) - (min(open, close) - low)) / max(high - low, 1e-9)",
        ),
        value_range="-1 to 1",
        category="bar_anatomy",
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="bar_range_atr",
        tier=0,
        description="Bar range relative to ATR",
        detection=_spec(
            lookback_bars=1,
            inputs=["high", "low", "atr20"],
            formula="(high - low) / atr20",
        ),
        value_range="0+",
        category="bar_anatomy",
        sources=[_SRC_TRADING_RANGES],
    ),
]

# =============================================================================
# CATEGORY 2: MOMENTUM / FOLLOW-THROUGH (Multi-bar direction)
# =============================================================================

MOMENTUM_SIGNALS = [
    AtomicSignal(
        signal_id="follow_through_bull",
        tier=0,
        description="Bull follow-through ratio over last N bars",
        detection=_spec(
            lookback_bars=4,
            inputs=["close"],
            formula="sum(1 for i in range(1,4) if close[-i] > close[-i-1]) / 3",
        ),
        value_range="0-1",
        category="momentum",
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="follow_through_bear",
        tier=0,
        description="Bear follow-through ratio over last N bars",
        detection=_spec(
            lookback_bars=4,
            inputs=["close"],
            formula="sum(1 for i in range(1,4) if close[-i] < close[-i-1]) / 3",
        ),
        value_range="0-1",
        category="momentum",
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="consecutive_bull_count",
        tier=0,
        description="Count of consecutive bull bars",
        detection=_spec(
            lookback_bars=10,
            inputs=["open", "close"],
            formula="count_consecutive(close > open)",
        ),
        value_range="0+",
        category="momentum",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="consecutive_bear_count",
        tier=0,
        description="Count of consecutive bear bars",
        detection=_spec(
            lookback_bars=10,
            inputs=["open", "close"],
            formula="count_consecutive(close < open)",
        ),
        value_range="0+",
        category="momentum",
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="body_dominance",
        tier=0,
        description="Average body ratio over recent bars (conviction measure)",
        detection=_spec(
            lookback_bars=5,
            inputs=["open", "high", "low", "close"],
            formula="avg(abs(close - open) / max(high - low, 1e-9))",
        ),
        value_range="0-1",
        category="momentum",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="body_relative_size",
        tier=0,
        description="Current body size relative to recent average",
        detection=_spec(
            lookback_bars=6,
            inputs=["open", "close"],
            formula="abs(close[-1] - open[-1]) / avg(abs(close[-6:-1] - open[-6:-1]))",
            notes=">1.5 = surprise bar candidate",
        ),
        value_range="0+",
        category="momentum",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="pressure_score",
        tier=0,
        description="Net bull/bear pressure over recent bars",
        detection=_spec(
            lookback_bars=5,
            inputs=["open", "high", "low", "close"],
            formula="avg((close - open) / max(high - low, 1e-9) for last 5 bars)",
            notes="Positive = bull pressure, negative = bear pressure",
        ),
        value_range="-1 to 1",
        category="momentum",
        sources=[_SRC_TRADING_RANGES],
    ),
]

# =============================================================================
# CATEGORY 3: OVERLAP / TWO-SIDED (Congestion measurement)
# =============================================================================

OVERLAP_SIGNALS = [
    AtomicSignal(
        signal_id="overlap_ratio",
        tier=0,
        description="Overlap ratio between last two bars",
        detection=_spec(
            lookback_bars=2,
            inputs=["high", "low"],
            formula="max(0, min(high[-1], high[-2]) - max(low[-1], low[-2])) / min(high[-1]-low[-1], high[-2]-low[-2])",
        ),
        value_range="0-1",
        category="overlap",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="avg_overlap_ratio",
        tier=0,
        description="Average overlap ratio over recent bars",
        detection=_spec(
            lookback_bars=5,
            inputs=["high", "low"],
            formula="avg(overlap_ratio[-5:])",
            notes=">0.6 = two-sided/congestion, <0.3 = trending",
        ),
        value_range="0-1",
        category="overlap",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="two_sided_score",
        tier=0,
        description="Two-sided trading score (high = range, low = trend)",
        detection=_spec(
            lookback_bars=5,
            inputs=["high", "low"],
            formula="avg(overlap_ratio[-5:])",
        ),
        value_range="0-1",
        category="overlap",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="one_sided_score",
        tier=0,
        description="One-sided/trending score (inverse of two_sided)",
        detection=_spec(
            lookback_bars=5,
            inputs=["high", "low"],
            formula="1 - avg(overlap_ratio[-5:])",
        ),
        value_range="0-1",
        category="overlap",
        sources=[_SRC_TRADING_RANGES],
    ),
]

# =============================================================================
# CATEGORY 4: RANGE / COMPRESSION
# =============================================================================

RANGE_SIGNALS = [
    AtomicSignal(
        signal_id="range_compression",
        tier=0,
        description="Current range vs recent average (compression if <1)",
        detection=_spec(
            lookback_bars=6,
            inputs=["high", "low"],
            formula="(high[-1] - low[-1]) / avg(high[-6:-1] - low[-6:-1])",
            notes="<0.6 = compressing, >1.5 = expanding",
        ),
        value_range="0+",
        category="range",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="range_position",
        tier=1,
        description="Position within a detected trading range",
        detection=_spec(
            lookback_bars=1,
            inputs=["close", "range_high", "range_low"],
            formula="(close - range_low) / max(range_high - range_low, 1e-9)",
        ),
        value_range="0-1",
        category="range",
        requires_context=["range_detection"],
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="bars_in_range",
        tier=1,
        description="Bar count within detected range",
        detection=_spec(
            lookback_bars=50,
            inputs=["close", "range_high", "range_low"],
            formula="count(bars where low > range_low and high < range_high)",
        ),
        value_range="0+",
        category="range",
        requires_context=["range_detection"],
        sources=[_SRC_TRADING_RANGES],
    ),
]

# =============================================================================
# CATEGORY 5: GAP MEASUREMENTS
# =============================================================================

GAP_SIGNALS = [
    AtomicSignal(
        signal_id="gap_size_atr",
        tier=0,
        description="Gap size relative to ATR",
        detection=_spec(
            lookback_bars=2,
            inputs=["open", "close", "atr20"],
            formula="abs(open[-1] - close[-2]) / atr20[-1]",
        ),
        value_range="0+",
        category="gap",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="body_gap_size",
        tier=0,
        description="Gap between bodies (open vs prior close)",
        detection=_spec(
            lookback_bars=2,
            inputs=["open", "close"],
            formula="open[-1] - close[-2]",
            notes="Positive = gap up, negative = gap down",
        ),
        value_range="any",
        category="gap",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="gap_fill_percent",
        tier=0,
        description="Percentage of gap filled by current bar",
        detection=_spec(
            lookback_bars=2,
            inputs=["open", "high", "low", "close"],
            formula="gap_filled_amount / gap_size",
            notes="1.0 = fully filled, 0 = unfilled",
        ),
        value_range="0-1+",
        category="gap",
        sources=[_SRC_TRADING_RANGES],
    ),
]

# =============================================================================
# CATEGORY 6: EMA / TREND POSITION
# =============================================================================

EMA_SIGNALS = [
    AtomicSignal(
        signal_id="ema_distance",
        tier=0,
        description="Distance from EMA in ATR units",
        detection=_spec(
            lookback_bars=1,
            inputs=["close", "ema20", "atr20"],
            formula="(close - ema20) / atr20",
            notes="Positive = above EMA, negative = below",
        ),
        value_range="any",
        category="ema_trend",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="ema_distance_abs",
        tier=0,
        description="Absolute distance from EMA in ATR units",
        detection=_spec(
            lookback_bars=1,
            inputs=["close", "ema20", "atr20"],
            formula="abs(close - ema20) / atr20",
            notes=">2 = extended, <0.5 = near EMA",
        ),
        value_range="0+",
        category="ema_trend",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="ema_slope",
        tier=0,
        description="EMA slope in ATR units over 5 bars",
        detection=_spec(
            lookback_bars=6,
            inputs=["ema20", "atr20"],
            formula="(ema20[-1] - ema20[-6]) / atr20[-1]",
        ),
        value_range="any",
        category="ema_trend",
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="bars_since_ema_touch",
        tier=0,
        description="Bars since price touched EMA",
        detection=_spec(
            lookback_bars=50,
            inputs=["high", "low", "ema20"],
            formula="count_bars_since(low <= ema20 <= high)",
        ),
        value_range="0+",
        category="ema_trend",
        sources=[_SRC_TRADING_RANGES],
    ),
]

# =============================================================================
# CATEGORY 7: STRUCTURE / SWING MEASUREMENTS
# =============================================================================

STRUCTURE_SIGNALS = [
    AtomicSignal(
        signal_id="rel_high_vs_prior",
        tier=0,
        description="Current high vs max high of prior 4 bars (ratio)",
        detection=_spec(
            lookback_bars=5,
            inputs=["high"],
            formula="high[-1] / max(high[-5:-1])",
            notes=">1 = HH, <1 = LH",
        ),
        value_range="0+",
        category="structure",
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="rel_low_vs_prior",
        tier=0,
        description="Current low vs min low of prior 4 bars (ratio)",
        detection=_spec(
            lookback_bars=5,
            inputs=["low"],
            formula="low[-1] / min(low[-5:-1])",
            notes="<1 = LL, >1 = HL",
        ),
        value_range="0+",
        category="structure",
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="swing_high_count",
        tier=1,
        description="Count of swing highs in recent bars",
        detection=_spec(
            lookback_bars=50,
            inputs=["swing_points"],
            formula="count(swing_highs)",
        ),
        value_range="0+",
        category="structure",
        requires_context=["swing_detection"],
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="swing_low_count",
        tier=1,
        description="Count of swing lows in recent bars",
        detection=_spec(
            lookback_bars=50,
            inputs=["swing_points"],
            formula="count(swing_lows)",
        ),
        value_range="0+",
        category="structure",
        requires_context=["swing_detection"],
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="push_count",
        tier=1,
        description="Count of pushes in same direction (for wedge detection)",
        detection=_spec(
            lookback_bars=50,
            inputs=["swing_points"],
            formula="count_consecutive_pushes(direction)",
            notes="3+ pushes = potential wedge",
        ),
        value_range="0+",
        category="structure",
        requires_context=["swing_detection"],
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="leg_count",
        tier=1,
        description="Count of legs in current move",
        detection=_spec(
            lookback_bars=50,
            inputs=["swing_points"],
            formula="count_legs()",
        ),
        value_range="0+",
        category="structure",
        requires_context=["swing_detection"],
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="pullback_depth",
        tier=1,
        description="Retracement depth of pullback (0-1+)",
        detection=_spec(
            lookback_bars=50,
            inputs=["swing_points"],
            formula="pullback_size / prior_leg_size",
            notes="0.5 = 50% retracement",
        ),
        value_range="0+",
        category="structure",
        requires_context=["swing_detection"],
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="pullback_bar_count",
        tier=1,
        description="Bar count in current pullback",
        detection=_spec(
            lookback_bars=50,
            inputs=["swing_points"],
            formula="count_bars_in_pullback()",
        ),
        value_range="0+",
        category="structure",
        requires_context=["swing_detection"],
        sources=[_SRC_REVERSALS],
    ),
]

# =============================================================================
# CATEGORY 8: BREAKOUT / FAILURE RATES
# =============================================================================

BREAKOUT_SIGNALS = [
    AtomicSignal(
        signal_id="breakout_failure_rate",
        tier=1,
        description="Rate of failed breakouts in recent history",
        detection=_spec(
            lookback_bars=20,
            inputs=["breakout_outcomes"],
            formula="failed_breakouts / max(total_breakouts, 1)",
            notes=">0.7 = favor fades, <0.3 = favor breakouts",
        ),
        value_range="0-1",
        category="breakout",
        requires_context=["breakout_detection"],
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="breakout_strength",
        tier=1,
        description="Strength of current breakout (bars exceeded)",
        detection=_spec(
            lookback_bars=20,
            inputs=["high", "low"],
            formula="count(prior bars whose range is exceeded)",
        ),
        value_range="0+",
        category="breakout",
        requires_context=["breakout_detection"],
        sources=[_SRC_TRADING_RANGES],
    ),
]

# =============================================================================
# CATEGORY 9: MEASURED MOVE / TARGET DISTANCES
# =============================================================================

MEASURED_MOVE_SIGNALS = [
    AtomicSignal(
        signal_id="mm_distance_atr",
        tier=1,
        description="Distance to measured move target in ATR units",
        detection=_spec(
            lookback_bars=1,
            inputs=["close", "mm_target", "atr20"],
            formula="abs(close - mm_target) / atr20",
        ),
        value_range="0+",
        category="measured_move",
        requires_context=["measured_move_detection"],
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="mm_percent_complete",
        tier=1,
        description="Percentage completion of measured move",
        detection=_spec(
            lookback_bars=1,
            inputs=["move_size", "mm_target_size"],
            formula="move_size / max(mm_target_size, 1e-9)",
        ),
        value_range="0+",
        category="measured_move",
        requires_context=["measured_move_detection"],
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="distance_to_support",
        tier=1,
        description="Distance to support level in ATR units",
        detection=_spec(
            lookback_bars=1,
            inputs=["close", "support", "atr20"],
            formula="(close - support) / atr20",
        ),
        value_range="any",
        category="measured_move",
        requires_context=["level_detection"],
        sources=[_SRC_TRADING_RANGES],
    ),
    AtomicSignal(
        signal_id="distance_to_resistance",
        tier=1,
        description="Distance to resistance level in ATR units",
        detection=_spec(
            lookback_bars=1,
            inputs=["close", "resistance", "atr20"],
            formula="(resistance - close) / atr20",
        ),
        value_range="any",
        category="measured_move",
        requires_context=["level_detection"],
        sources=[_SRC_TRADING_RANGES],
    ),
]

# =============================================================================
# CATEGORY 10: CLIMAX / SPIKE MEASUREMENTS
# =============================================================================

CLIMAX_SIGNALS = [
    AtomicSignal(
        signal_id="spike_strength",
        tier=0,
        description="Body dominance in recent spike (0-1)",
        detection=_spec(
            lookback_bars=5,
            inputs=["open", "high", "low", "close"],
            formula="sum(abs(close - open)) / sum(high - low)",
        ),
        value_range="0-1",
        category="climax",
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="acceleration",
        tier=0,
        description="Rate of change acceleration (positive = parabolic)",
        detection=_spec(
            lookback_bars=6,
            inputs=["close"],
            formula="(close[-1] - close[-3]) - (close[-3] - close[-6])",
            notes="Positive = accelerating, negative = decelerating",
        ),
        value_range="any",
        category="climax",
        sources=[_SRC_REVERSALS],
    ),
    AtomicSignal(
        signal_id="climax_bar_range",
        tier=0,
        description="Current bar range vs ATR (for climax detection)",
        detection=_spec(
            lookback_bars=1,
            inputs=["high", "low", "atr20"],
            formula="(high - low) / atr20",
            notes=">2 = potential climax",
        ),
        value_range="0+",
        category="climax",
        sources=[_SRC_REVERSALS],
    ),
]

# =============================================================================
# AGGREGATE: ALL ATOMIC SIGNALS
# =============================================================================

ALL_ATOMIC_SIGNALS = (
    BAR_ANATOMY_SIGNALS +
    MOMENTUM_SIGNALS +
    OVERLAP_SIGNALS +
    RANGE_SIGNALS +
    GAP_SIGNALS +
    EMA_SIGNALS +
    STRUCTURE_SIGNALS +
    BREAKOUT_SIGNALS +
    MEASURED_MOVE_SIGNALS +
    CLIMAX_SIGNALS
)

ATOMIC_SIGNAL_LOOKUP: Dict[str, AtomicSignal] = {
    sig.signal_id: sig for sig in ALL_ATOMIC_SIGNALS
}


def get_atomic_signal(signal_id: str) -> AtomicSignal | None:
    """Get an atomic signal definition by ID."""
    return ATOMIC_SIGNAL_LOOKUP.get(signal_id)


def list_signals_by_category(category: str) -> list[AtomicSignal]:
    """List all signals in a category."""
    return [s for s in ALL_ATOMIC_SIGNALS if s.category == category]


def list_tier0_signals() -> list[AtomicSignal]:
    """List all tier-0 signals (pure OHLC, no context needed)."""
    return [s for s in ALL_ATOMIC_SIGNALS if s.tier == 0]


def list_signals_requiring_context() -> list[AtomicSignal]:
    """List signals that need additional context (tier 1+)."""
    return [s for s in ALL_ATOMIC_SIGNALS if s.tier > 0]
