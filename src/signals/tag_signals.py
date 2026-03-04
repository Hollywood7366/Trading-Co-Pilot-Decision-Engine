"""
@file tag_signals.py
@history
2026-01-26: Created - Layer 1: Single Bar Classification signals with OHLC rules

Layer 1: Tag Signals (Single Bar Classification)
- Binary/categorical labels for individual bars
- Computed from OHLC of current bar (and sometimes prior bar for inside/outside)
- These are the "what type of bar is this?" questions
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TagSignalRule:
    """Definition of a single-bar tag signal with OHLC detection rule."""
    tag_id: str
    description: str
    ohlc_rule: str  # Human-readable formula
    formula: str    # Python-executable formula
    confidence: str  # "high" (objective), "medium" (threshold-dependent), "low" (subjective)
    requires_prior_bar: bool = False
    threshold: Optional[float] = None
    notes: Optional[str] = None


# =============================================================================
# BAR TYPE CLASSIFICATIONS
# =============================================================================

BAR_TYPE_TAGS = [
    TagSignalRule(
        tag_id="bar_type_bull",
        description="Bullish bar (close > open)",
        ohlc_rule="C > O",
        formula="close > open",
        confidence="high",
    ),
    TagSignalRule(
        tag_id="bar_type_bear",
        description="Bearish bar (close < open)",
        ohlc_rule="C < O",
        formula="close < open",
        confidence="high",
    ),
    TagSignalRule(
        tag_id="bar_type_doji",
        description="Doji bar (small body relative to range)",
        ohlc_rule="body / range < 0.25",
        formula="abs(close - open) / max(high - low, 1e-9) < 0.25",
        confidence="high",
        threshold=0.25,
    ),
]

# =============================================================================
# TREND BAR CLASSIFICATIONS
# =============================================================================

TREND_BAR_TAGS = [
    TagSignalRule(
        tag_id="bull_trend_bar",
        description="Strong bull trend bar with close near high",
        ohlc_rule="C > O AND body/range > 0.5 AND close in upper third",
        formula="close > open and (abs(close - open) / max(high - low, 1e-9)) > 0.5 and (close - low) / max(high - low, 1e-9) > 0.66",
        confidence="high",
        threshold=0.5,
    ),
    TagSignalRule(
        tag_id="bear_trend_bar",
        description="Strong bear trend bar with close near low",
        ohlc_rule="C < O AND body/range > 0.5 AND close in lower third",
        formula="close < open and (abs(close - open) / max(high - low, 1e-9)) > 0.5 and (close - low) / max(high - low, 1e-9) < 0.33",
        confidence="high",
        threshold=0.5,
    ),
    TagSignalRule(
        tag_id="big_trend_bar",
        description="Large directional bar (body > 1.5x recent average)",
        ohlc_rule="body > 1.5 * avg_body(5)",
        formula="abs(close - open) > 1.5 * avg_body_5",
        confidence="medium",
        threshold=1.5,
        notes="Requires recent bar context for average",
    ),
]

# =============================================================================
# REVERSAL BAR CLASSIFICATIONS
# =============================================================================

REVERSAL_BAR_TAGS = [
    TagSignalRule(
        tag_id="bull_reversal_bar",
        description="Bull reversal bar with prominent lower tail rejecting lows",
        ohlc_rule="lower_tail > 2 * body AND C > midpoint",
        formula="(min(open, close) - low) > 2 * abs(close - open) and (close - low) / max(high - low, 1e-9) > 0.5",
        confidence="medium",
        notes="Strong rejection of lower prices",
    ),
    TagSignalRule(
        tag_id="bear_reversal_bar",
        description="Bear reversal bar with prominent upper tail rejecting highs",
        ohlc_rule="upper_tail > 2 * body AND C < midpoint",
        formula="(high - max(open, close)) > 2 * abs(close - open) and (close - low) / max(high - low, 1e-9) < 0.5",
        confidence="medium",
        notes="Strong rejection of higher prices",
    ),
    TagSignalRule(
        tag_id="reversal_bar",
        description="General reversal bar (either direction)",
        ohlc_rule="bull_reversal_bar OR bear_reversal_bar",
        formula="is_bull_reversal_bar or is_bear_reversal_bar",
        confidence="medium",
    ),
]

# =============================================================================
# SIGNAL BAR CLASSIFICATIONS
# =============================================================================

SIGNAL_BAR_TAGS = [
    TagSignalRule(
        tag_id="bull_signal_bar",
        description="Buy signal bar - good body, bullish close, after bearish context",
        ohlc_rule="C > O AND body/range > 0.4 AND close in upper half AND after bear move",
        formula="close > open and body_ratio > 0.4 and close_position > 0.5 and prior_context_bearish",
        confidence="low",
        notes="Context-dependent - requires prior bar analysis",
    ),
    TagSignalRule(
        tag_id="bear_signal_bar",
        description="Sell signal bar - good body, bearish close, after bullish context",
        ohlc_rule="C < O AND body/range > 0.4 AND close in lower half AND after bull move",
        formula="close < open and body_ratio > 0.4 and close_position < 0.5 and prior_context_bullish",
        confidence="low",
        notes="Context-dependent - requires prior bar analysis",
    ),
    TagSignalRule(
        tag_id="poor_signal_bar",
        description="Signal bar with weak characteristics (small body, bad close position)",
        ohlc_rule="body/range < 0.3 OR close against direction",
        formula="body_ratio < 0.3 or close_against_signal_direction",
        confidence="medium",
    ),
]

# =============================================================================
# INSIDE/OUTSIDE BAR CLASSIFICATIONS
# =============================================================================

INSIDE_OUTSIDE_TAGS = [
    TagSignalRule(
        tag_id="inside_bar",
        description="Bar range entirely within prior bar range",
        ohlc_rule="H < prior_H AND L > prior_L",
        formula="high < prior_high and low > prior_low",
        confidence="high",
        requires_prior_bar=True,
    ),
    TagSignalRule(
        tag_id="outside_bar",
        description="Bar range encompasses prior bar range",
        ohlc_rule="H > prior_H AND L < prior_L",
        formula="high > prior_high and low < prior_low",
        confidence="high",
        requires_prior_bar=True,
    ),
    TagSignalRule(
        tag_id="outside_up",
        description="Outside bar closing up (bullish engulfing)",
        ohlc_rule="outside_bar AND C > O",
        formula="is_outside_bar and close > open",
        confidence="high",
        requires_prior_bar=True,
    ),
    TagSignalRule(
        tag_id="outside_down",
        description="Outside bar closing down (bearish engulfing)",
        ohlc_rule="outside_bar AND C < O",
        formula="is_outside_bar and close < open",
        confidence="high",
        requires_prior_bar=True,
    ),
]

# =============================================================================
# SHAVED BAR CLASSIFICATIONS
# =============================================================================

SHAVED_BAR_TAGS = [
    TagSignalRule(
        tag_id="shaved_top",
        description="No upper tail (close or open at high)",
        ohlc_rule="upper_tail / range < 0.05",
        formula="(high - max(open, close)) / max(high - low, 1e-9) < 0.05",
        confidence="high",
        threshold=0.05,
    ),
    TagSignalRule(
        tag_id="shaved_bottom",
        description="No lower tail (close or open at low)",
        ohlc_rule="lower_tail / range < 0.05",
        formula="(min(open, close) - low) / max(high - low, 1e-9) < 0.05",
        confidence="high",
        threshold=0.05,
    ),
]

# =============================================================================
# GAP BAR CLASSIFICATIONS
# =============================================================================

GAP_BAR_TAGS = [
    TagSignalRule(
        tag_id="gap_bar_up",
        description="Gap up bar (current low > prior high)",
        ohlc_rule="L > prior_H",
        formula="low > prior_high",
        confidence="high",
        requires_prior_bar=True,
    ),
    TagSignalRule(
        tag_id="gap_bar_down",
        description="Gap down bar (current high < prior low)",
        ohlc_rule="H < prior_L",
        formula="high < prior_low",
        confidence="high",
        requires_prior_bar=True,
    ),
    TagSignalRule(
        tag_id="gap_bar",
        description="Any gap bar (no overlap with prior bar)",
        ohlc_rule="L > prior_H OR H < prior_L",
        formula="low > prior_high or high < prior_low",
        confidence="high",
        requires_prior_bar=True,
    ),
]

# =============================================================================
# SURPRISE BAR CLASSIFICATIONS
# =============================================================================

SURPRISE_BAR_TAGS = [
    TagSignalRule(
        tag_id="surprise_bar",
        description="Surprisingly large bar relative to recent bars",
        ohlc_rule="range > 2 * avg_range(5)",
        formula="(high - low) > 2 * avg_range_5",
        confidence="medium",
        threshold=2.0,
        notes="Requires recent bar context",
    ),
    TagSignalRule(
        tag_id="bull_surprise_bar",
        description="Large bullish surprise bar",
        ohlc_rule="surprise_bar AND C > O AND body/range > 0.6",
        formula="is_surprise_bar and close > open and body_ratio > 0.6",
        confidence="medium",
    ),
    TagSignalRule(
        tag_id="bear_surprise_bar",
        description="Large bearish surprise bar",
        ohlc_rule="surprise_bar AND C < O AND body/range > 0.6",
        formula="is_surprise_bar and close < open and body_ratio > 0.6",
        confidence="medium",
    ),
]

# =============================================================================
# BREAKOUT BAR CLASSIFICATIONS
# =============================================================================

BREAKOUT_BAR_TAGS = [
    TagSignalRule(
        tag_id="breakout_bar_up",
        description="Bar that breaks above prior N bars' high",
        ohlc_rule="H > max(H[-N:])",
        formula="high > max_high_prior_n",
        confidence="high",
        notes="N typically 5-20 bars",
    ),
    TagSignalRule(
        tag_id="breakout_bar_down",
        description="Bar that breaks below prior N bars' low",
        ohlc_rule="L < min(L[-N:])",
        formula="low < min_low_prior_n",
        confidence="high",
        notes="N typically 5-20 bars",
    ),
]

# =============================================================================
# CLOSE POSITION CLASSIFICATIONS
# =============================================================================

CLOSE_POSITION_TAGS = [
    TagSignalRule(
        tag_id="close_top_third",
        description="Close in upper third of bar range",
        ohlc_rule="(C - L) / range > 0.66",
        formula="(close - low) / max(high - low, 1e-9) > 0.66",
        confidence="high",
        threshold=0.66,
    ),
    TagSignalRule(
        tag_id="close_bottom_third",
        description="Close in lower third of bar range",
        ohlc_rule="(C - L) / range < 0.33",
        formula="(close - low) / max(high - low, 1e-9) < 0.33",
        confidence="high",
        threshold=0.33,
    ),
    TagSignalRule(
        tag_id="close_middle_third",
        description="Close in middle third of bar range",
        ohlc_rule="0.33 <= (C - L) / range <= 0.66",
        formula="0.33 <= (close - low) / max(high - low, 1e-9) <= 0.66",
        confidence="high",
    ),
]

# =============================================================================
# EMA POSITION CLASSIFICATIONS
# =============================================================================

EMA_POSITION_TAGS = [
    TagSignalRule(
        tag_id="bar_above_ema",
        description="Entire bar above EMA (low > EMA)",
        ohlc_rule="L > EMA",
        formula="low > ema",
        confidence="high",
        notes="Requires EMA calculation",
    ),
    TagSignalRule(
        tag_id="bar_below_ema",
        description="Entire bar below EMA (high < EMA)",
        ohlc_rule="H < EMA",
        formula="high < ema",
        confidence="high",
        notes="Requires EMA calculation",
    ),
    TagSignalRule(
        tag_id="bar_touching_ema",
        description="Bar touches/crosses EMA",
        ohlc_rule="L <= EMA <= H",
        formula="low <= ema <= high",
        confidence="high",
        notes="Requires EMA calculation",
    ),
]

# =============================================================================
# RELATIVE HIGH/LOW CLASSIFICATIONS
# =============================================================================

RELATIVE_HL_TAGS = [
    TagSignalRule(
        tag_id="higher_high",
        description="Bar makes higher high than prior N bars",
        ohlc_rule="H > max(H[-N:])",
        formula="high > max_high_prior_n",
        confidence="high",
        notes="N typically 4 bars for swing detection",
    ),
    TagSignalRule(
        tag_id="lower_low",
        description="Bar makes lower low than prior N bars",
        ohlc_rule="L < min(L[-N:])",
        formula="low < min_low_prior_n",
        confidence="high",
    ),
    TagSignalRule(
        tag_id="higher_low",
        description="Bar makes higher low than prior N bars' lowest low",
        ohlc_rule="L > min(L[-N:])",
        formula="low > min_low_prior_n",
        confidence="high",
    ),
    TagSignalRule(
        tag_id="lower_high",
        description="Bar makes lower high than prior N bars' highest high",
        ohlc_rule="H < max(H[-N:])",
        formula="high < max_high_prior_n",
        confidence="high",
    ),
]

# =============================================================================
# AGGREGATE: ALL TAG SIGNALS
# =============================================================================

ALL_TAG_SIGNALS = (
    BAR_TYPE_TAGS +
    TREND_BAR_TAGS +
    REVERSAL_BAR_TAGS +
    SIGNAL_BAR_TAGS +
    INSIDE_OUTSIDE_TAGS +
    SHAVED_BAR_TAGS +
    GAP_BAR_TAGS +
    SURPRISE_BAR_TAGS +
    BREAKOUT_BAR_TAGS +
    CLOSE_POSITION_TAGS +
    EMA_POSITION_TAGS +
    RELATIVE_HL_TAGS
)

TAG_SIGNAL_LOOKUP = {tag.tag_id: tag for tag in ALL_TAG_SIGNALS}


def get_tag_signal(tag_id: str) -> TagSignalRule | None:
    """Get a tag signal definition by ID."""
    return TAG_SIGNAL_LOOKUP.get(tag_id)


def list_tag_signals_by_confidence(confidence: str) -> list[TagSignalRule]:
    """List all tag signals with given confidence level."""
    return [t for t in ALL_TAG_SIGNALS if t.confidence == confidence]
