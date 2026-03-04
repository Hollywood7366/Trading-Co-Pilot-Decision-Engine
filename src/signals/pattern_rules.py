"""
@file pattern_rules.py
@history
2026-01-26: Created - Layer 2: Multi-Bar Pattern detection rules
2026-01-27: Added 120 missing patterns from tags_catalog.v193

Layer 2: Multi-Bar Patterns
- Patterns requiring analysis of multiple bars
- Range from objective (ii, ioi) to subjective (wedge, triangle)
- These require the tag signals from Layer 1 as building blocks
- Total: 168 patterns (aligned with tags_catalog.v193)
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class PatternRule:
    """Definition of a multi-bar pattern with detection rules."""
    pattern_id: str
    description: str
    bar_count: str  # "2", "3", "3+", "variable", etc.
    ohlc_rule: str  # Human-readable rule
    detection_logic: str  # Structured detection approach
    subjectivity: str  # "low" (objective), "medium", "high" (needs interpretation)
    required_tag_signals: List[str] = field(default_factory=list)
    requires_swing_detection: bool = False
    notes: Optional[str] = None


# =============================================================================
# OBJECTIVE PATTERNS (Low Subjectivity)
# =============================================================================

OBJECTIVE_PATTERNS = [
    PatternRule(
        pattern_id="ii",
        description="Two consecutive inside bars (ii pattern)",
        bar_count="2",
        ohlc_rule="bar[-1]=inside AND bar[-2]=inside",
        detection_logic="is_inside_bar[-1] and is_inside_bar[-2]",
        subjectivity="low",
        required_tag_signals=["inside_bar"],
    ),
    PatternRule(
        pattern_id="iii",
        description="Three consecutive inside bars",
        bar_count="3",
        ohlc_rule="bar[-1]=inside AND bar[-2]=inside AND bar[-3]=inside",
        detection_logic="all(is_inside_bar[-1:-4])",
        subjectivity="low",
        required_tag_signals=["inside_bar"],
    ),
    PatternRule(
        pattern_id="ioi",
        description="Inside-Outside-Inside pattern",
        bar_count="3",
        ohlc_rule="bar[-3]=inside, bar[-2]=outside, bar[-1]=inside",
        detection_logic="is_inside_bar[-3] and is_outside_bar[-2] and is_inside_bar[-1]",
        subjectivity="low",
        required_tag_signals=["inside_bar", "outside_bar"],
    ),
    PatternRule(
        pattern_id="oo",
        description="Two consecutive outside bars",
        bar_count="2",
        ohlc_rule="bar[-1]=outside AND bar[-2]=outside",
        detection_logic="is_outside_bar[-1] and is_outside_bar[-2]",
        subjectivity="low",
        required_tag_signals=["outside_bar"],
    ),
    PatternRule(
        pattern_id="two_bar_reversal_bull",
        description="Two-bar bull reversal (bear bar followed by bull bar that closes above)",
        bar_count="2",
        ohlc_rule="bar[-2]=bear_trend, bar[-1]=bull, H[-1]>H[-2], L[-1]<L[-2], C[-1]>O[-2]",
        detection_logic="is_bear_bar[-2] and is_bull_bar[-1] and high[-1] > high[-2] and low[-1] < low[-2] and close[-1] > open[-2]",
        subjectivity="low",
        required_tag_signals=["bar_type_bull", "bar_type_bear"],
    ),
    PatternRule(
        pattern_id="two_bar_reversal_bear",
        description="Two-bar bear reversal (bull bar followed by bear bar that closes below)",
        bar_count="2",
        ohlc_rule="bar[-2]=bull_trend, bar[-1]=bear, H[-1]>H[-2], L[-1]<L[-2], C[-1]<O[-2]",
        detection_logic="is_bull_bar[-2] and is_bear_bar[-1] and high[-1] > high[-2] and low[-1] < low[-2] and close[-1] < open[-2]",
        subjectivity="low",
        required_tag_signals=["bar_type_bull", "bar_type_bear"],
    ),
    PatternRule(
        pattern_id="three_bar_reversal_bull",
        description="Three-bar bull reversal pattern",
        bar_count="3",
        ohlc_rule="3 bars with lower low on bar 2, then higher close on bar 3",
        detection_logic="low[-2] < low[-3] and close[-1] > close[-2] and close[-1] > open[-3]",
        subjectivity="low",
    ),
    PatternRule(
        pattern_id="three_bar_reversal_bear",
        description="Three-bar bear reversal pattern",
        bar_count="3",
        ohlc_rule="3 bars with higher high on bar 2, then lower close on bar 3",
        detection_logic="high[-2] > high[-3] and close[-1] < close[-2] and close[-1] < open[-3]",
        subjectivity="low",
    ),
]

# =============================================================================
# MEDIUM SUBJECTIVITY PATTERNS
# =============================================================================

MEDIUM_PATTERNS = [
    PatternRule(
        pattern_id="failed_breakout",
        description="Breakout that immediately reverses (trap)",
        bar_count="2-3",
        ohlc_rule="breakout_bar followed by reversal back into range",
        detection_logic="is_breakout_bar[-2] and (close[-1] back_in_range or reversal_bar[-1])",
        subjectivity="medium",
        required_tag_signals=["breakout_bar_up", "breakout_bar_down", "reversal_bar"],
        notes="The 'immediately' part requires judgment on bar count",
    ),
    PatternRule(
        pattern_id="double_top",
        description="Two swing highs at approximately same level",
        bar_count="variable",
        ohlc_rule="swing_high[-1] ≈ swing_high[-2] (within threshold)",
        detection_logic="abs(swing_high[-1] - swing_high[-2]) / atr < threshold",
        subjectivity="medium",
        requires_swing_detection=True,
        notes="Threshold typically 0.5-1.0 ATR",
    ),
    PatternRule(
        pattern_id="double_bottom",
        description="Two swing lows at approximately same level",
        bar_count="variable",
        ohlc_rule="swing_low[-1] ≈ swing_low[-2] (within threshold)",
        detection_logic="abs(swing_low[-1] - swing_low[-2]) / atr < threshold",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="higher_low_double_bottom",
        description="Double bottom with second low higher than first",
        bar_count="variable",
        ohlc_rule="swing_low[-1] > swing_low[-2]",
        detection_logic="swing_low[-1] > swing_low[-2] and is_in_bull_context",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="lower_high_double_top",
        description="Double top with second high lower than first",
        bar_count="variable",
        ohlc_rule="swing_high[-1] < swing_high[-2]",
        detection_logic="swing_high[-1] < swing_high[-2] and is_in_bear_context",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="micro_double_bottom",
        description="Small double bottom within 10 bars",
        bar_count="3-10",
        ohlc_rule="two lows within 10 bars at similar level",
        detection_logic="count_bars_between_lows < 10 and abs(low1 - low2) / atr < 0.5",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="micro_double_top",
        description="Small double top within 10 bars",
        bar_count="3-10",
        ohlc_rule="two highs within 10 bars at similar level",
        detection_logic="count_bars_between_highs < 10 and abs(high1 - high2) / atr < 0.5",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# HIGH SUBJECTIVITY PATTERNS (Require Swing Detection)
# =============================================================================

HIGH_SUBJECTIVITY_PATTERNS = [
    PatternRule(
        pattern_id="wedge_bull",
        description="Falling wedge / wedge bottom (3 pushes down with converging trendlines)",
        bar_count="variable (typically 10-30)",
        ohlc_rule="3 lower lows with converging trendlines (lower lows getting shallower, lower highs getting lower)",
        detection_logic="""
            swing_lows = get_swing_lows(n=3)
            swing_highs = get_swing_highs(n=3)
            # Check 3 pushes down
            pushes_down = all(swing_lows[i] < swing_lows[i-1] for i in range(1, 3))
            # Check convergence (lower trendline slope > upper trendline slope)
            lower_slope = calc_slope(swing_lows)
            upper_slope = calc_slope(swing_highs)
            converging = lower_slope > upper_slope  # Both negative, lower less steep
            return pushes_down and converging
        """,
        subjectivity="high",
        requires_swing_detection=True,
        notes="Al Brooks: 3 pushes minimum, converging swings",
    ),
    PatternRule(
        pattern_id="wedge_bear",
        description="Rising wedge / wedge top (3 pushes up with converging trendlines)",
        bar_count="variable (typically 10-30)",
        ohlc_rule="3 higher highs with converging trendlines (higher highs getting shallower, higher lows getting higher)",
        detection_logic="""
            swing_highs = get_swing_highs(n=3)
            swing_lows = get_swing_lows(n=3)
            # Check 3 pushes up
            pushes_up = all(swing_highs[i] > swing_highs[i-1] for i in range(1, 3))
            # Check convergence (upper trendline slope < lower trendline slope)
            upper_slope = calc_slope(swing_highs)
            lower_slope = calc_slope(swing_lows)
            converging = upper_slope < lower_slope  # Both positive, upper less steep
            return pushes_up and converging
        """,
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="triangle",
        description="Converging triangle (highs getting lower, lows getting higher)",
        bar_count="variable",
        ohlc_rule="LH sequence AND HL sequence (converging swings)",
        detection_logic="""
            highs = get_swing_highs(n=3)
            lows = get_swing_lows(n=3)
            lower_highs = all(highs[i] < highs[i-1] for i in range(1, 3))
            higher_lows = all(lows[i] > lows[i-1] for i in range(1, 3))
            return lower_highs and higher_lows
        """,
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="expanding_triangle",
        description="Expanding triangle (highs getting higher, lows getting lower)",
        bar_count="variable",
        ohlc_rule="HH sequence AND LL sequence (diverging swings)",
        detection_logic="""
            highs = get_swing_highs(n=3)
            lows = get_swing_lows(n=3)
            higher_highs = all(highs[i] > highs[i-1] for i in range(1, 3))
            lower_lows = all(lows[i] < lows[i-1] for i in range(1, 3))
            return higher_highs and lower_lows
        """,
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="channel_bull",
        description="Bull channel (parallel trendlines, higher highs and higher lows)",
        bar_count="variable (typically 20+)",
        ohlc_rule="HH + HL sequences with roughly parallel trendlines",
        detection_logic="""
            highs = get_swing_highs(n=4)
            lows = get_swing_lows(n=4)
            hh_sequence = all(highs[i] > highs[i-1] for i in range(1, 4))
            hl_sequence = all(lows[i] > lows[i-1] for i in range(1, 4))
            upper_slope = calc_slope(highs)
            lower_slope = calc_slope(lows)
            parallel = abs(upper_slope - lower_slope) / max(abs(upper_slope), 1e-9) < 0.3
            return hh_sequence and hl_sequence and parallel
        """,
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="channel_bear",
        description="Bear channel (parallel trendlines, lower highs and lower lows)",
        bar_count="variable (typically 20+)",
        ohlc_rule="LH + LL sequences with roughly parallel trendlines",
        detection_logic="""
            highs = get_swing_highs(n=4)
            lows = get_swing_lows(n=4)
            lh_sequence = all(highs[i] < highs[i-1] for i in range(1, 4))
            ll_sequence = all(lows[i] < lows[i-1] for i in range(1, 4))
            upper_slope = calc_slope(highs)
            lower_slope = calc_slope(lows)
            parallel = abs(upper_slope - lower_slope) / max(abs(upper_slope), 1e-9) < 0.3
            return lh_sequence and ll_sequence and parallel
        """,
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="spike_and_channel_bull",
        description="Initial bull spike followed by bull channel phase",
        bar_count="variable",
        ohlc_rule="3+ consecutive bull trend bars (spike) then channel formation",
        detection_logic="""
            # Phase 1: Spike (3+ strong trend bars)
            spike_start = find_spike_start()
            spike_bars = consecutive_trend_bars_from(spike_start)
            has_spike = spike_bars >= 3 and body_dominance(spike_bars) > 0.6
            # Phase 2: Channel after spike
            has_channel = detect_channel_bull(after=spike_start + spike_bars)
            return has_spike and has_channel
        """,
        subjectivity="high",
        requires_swing_detection=True,
        required_tag_signals=["bull_trend_bar"],
    ),
    PatternRule(
        pattern_id="spike_and_channel_bear",
        description="Initial bear spike followed by bear channel phase",
        bar_count="variable",
        ohlc_rule="3+ consecutive bear trend bars (spike) then channel formation",
        detection_logic="same as bull but inverted",
        subjectivity="high",
        requires_swing_detection=True,
        required_tag_signals=["bear_trend_bar"],
    ),
]

# =============================================================================
# FLAG PATTERNS
# =============================================================================

FLAG_PATTERNS = [
    PatternRule(
        pattern_id="bull_flag",
        description="Pullback in bull trend forming flag shape",
        bar_count="5-20",
        ohlc_rule="After bull move, 5-20 bar sideways/down consolidation",
        detection_logic="""
            prior_trend = detect_bull_trend()
            pullback = detect_pullback(direction='down', max_bars=20)
            flag_tight = pullback.range < 0.5 * prior_trend.range
            return prior_trend and pullback and flag_tight
        """,
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bear_flag",
        description="Pullback in bear trend forming flag shape",
        bar_count="5-20",
        ohlc_rule="After bear move, 5-20 bar sideways/up consolidation",
        detection_logic="same as bull flag but inverted",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="wedge_bull_flag",
        description="Bull flag shaped as falling wedge",
        bar_count="10-30",
        ohlc_rule="bull_flag AND wedge_shape (converging)",
        detection_logic="is_bull_flag and is_wedge_shape",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="wedge_bear_flag",
        description="Bear flag shaped as rising wedge",
        bar_count="10-30",
        ohlc_rule="bear_flag AND wedge_shape (converging)",
        detection_logic="is_bear_flag and is_wedge_shape",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="double_bottom_bull_flag",
        description="Bull flag with double bottom shape",
        bar_count="variable",
        ohlc_rule="bull_flag AND double_bottom within flag",
        detection_logic="is_bull_flag and has_double_bottom_within",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="double_top_bear_flag",
        description="Bear flag with double top shape",
        bar_count="variable",
        ohlc_rule="bear_flag AND double_top within flag",
        detection_logic="is_bear_flag and has_double_top_within",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# ENTRY PATTERNS (High 1/2/3, Low 1/2/3)
# =============================================================================

ENTRY_PATTERNS = [
    PatternRule(
        pattern_id="high_1",
        description="First pullback in bull trend (High 1 entry)",
        bar_count="variable",
        ohlc_rule="First bar with high above prior bar's high after bull leg starts",
        detection_logic="first_higher_high_in_pullback",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="high_2",
        description="Second pullback in bull trend (High 2 entry)",
        bar_count="variable",
        ohlc_rule="Second bar with high above prior bar's high in pullback",
        detection_logic="second_higher_high_in_pullback",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="high_3",
        description="Third pullback entry (rarely taken)",
        bar_count="variable",
        ohlc_rule="Third High 1 in same pullback",
        detection_logic="third_higher_high_in_pullback",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="low_1",
        description="First pullback in bear trend (Low 1 entry)",
        bar_count="variable",
        ohlc_rule="First bar with low below prior bar's low after bear leg starts",
        detection_logic="first_lower_low_in_pullback",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="low_2",
        description="Second pullback in bear trend (Low 2 entry)",
        bar_count="variable",
        ohlc_rule="Second bar with low below prior bar's low in pullback",
        detection_logic="second_lower_low_in_pullback",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="low_3",
        description="Third pullback entry (rarely taken)",
        bar_count="variable",
        ohlc_rule="Third Low 1 in same pullback",
        detection_logic="third_lower_low_in_pullback",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# BREAKOUT PATTERNS
# =============================================================================

BREAKOUT_PATTERNS = [
    PatternRule(
        pattern_id="breakout",
        description="Price breaks above resistance or below support",
        bar_count="1-2",
        ohlc_rule="H > recent_high_N OR L < recent_low_N with strong close",
        detection_logic="(high > max(highs[-N:]) or low < min(lows[-N:])) and body_ratio > 0.5",
        subjectivity="medium",
        required_tag_signals=["breakout_bar_up", "breakout_bar_down"],
    ),
    PatternRule(
        pattern_id="bull_breakout",
        description="Bull breakout (breakout up)",
        bar_count="1-2",
        ohlc_rule="H > recent_high_N with strong bull close",
        detection_logic="high > max(highs[-N:]) and is_bull_bar and body_ratio > 0.5",
        subjectivity="medium",
        required_tag_signals=["breakout_bar_up", "bar_type_bull"],
    ),
    PatternRule(
        pattern_id="bear_breakout",
        description="Bear breakout (breakout down / breakdown)",
        bar_count="1-2",
        ohlc_rule="L < recent_low_N with strong bear close",
        detection_logic="low < min(lows[-N:]) and is_bear_bar and body_ratio > 0.5",
        subjectivity="medium",
        required_tag_signals=["breakout_bar_down", "bar_type_bear"],
    ),
    PatternRule(
        pattern_id="breakout_mode",
        description="Trading range state where price is coiling for breakout",
        bar_count="10+",
        ohlc_rule="Range compression with decreasing volatility",
        detection_logic="range_compression < 0.7 and bars_in_range > 10",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="breakout_pullback",
        description="First pullback after successful breakout",
        bar_count="3-10",
        ohlc_rule="Breakout followed by 2-5 bar pullback that holds above/below breakout level",
        detection_logic="had_breakout_within(10) and is_pullback and holds_breakout_level",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="breakout_test",
        description="Test of a breakout point",
        bar_count="variable",
        ohlc_rule="Price returns to breakout level and holds",
        detection_logic="abs(close - breakout_level) / atr < 0.5 and reversal_bar",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# CHANNEL VARIANT PATTERNS
# =============================================================================

CHANNEL_VARIANT_PATTERNS = [
    PatternRule(
        pattern_id="channel",
        description="Channel concept (sloping range with parallel trendlines)",
        bar_count="variable (15+)",
        ohlc_rule="Parallel trendlines on highs and lows",
        detection_logic="detect_parallel_trendlines(tolerance=0.3)",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bear_channel",
        description="Bear channel (down-sloping channel) context",
        bar_count="variable (15+)",
        ohlc_rule="LH + LL sequences with roughly parallel trendlines sloping down",
        detection_logic="channel_bear detection (alias for channel_bear)",
        subjectivity="high",
        requires_swing_detection=True,
        notes="Alias for channel_bear",
    ),
    PatternRule(
        pattern_id="bull_channel",
        description="Bull channel (up-sloping channel) context",
        bar_count="variable (15+)",
        ohlc_rule="HH + HL sequences with roughly parallel trendlines sloping up",
        detection_logic="channel_bull detection (alias for channel_bull)",
        subjectivity="high",
        requires_swing_detection=True,
        notes="Alias for channel_bull",
    ),
    PatternRule(
        pattern_id="tight_bull_channel",
        description="Tight bull channel (strong trend with minimal pullbacks)",
        bar_count="variable (10+)",
        ohlc_rule="Bull channel with small pullbacks (< 0.3 ATR)",
        detection_logic="is_channel_bull and avg_pullback_depth < 0.3",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="tight_bear_channel",
        description="Tight bear channel (strong trend with minimal pullbacks)",
        bar_count="variable (10+)",
        ohlc_rule="Bear channel with small pullbacks (< 0.3 ATR)",
        detection_logic="is_channel_bear and avg_pullback_depth < 0.3",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="broad_bull_channel",
        description="Wide/broad bull channel",
        bar_count="variable (20+)",
        ohlc_rule="Bull channel with wide swings (> 1 ATR pullbacks)",
        detection_logic="is_channel_bull and avg_pullback_depth > 1.0",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="broad_bear_channel",
        description="Wide/broad bear channel",
        bar_count="variable (20+)",
        ohlc_rule="Bear channel with wide swings (> 1 ATR pullbacks)",
        detection_logic="is_channel_bear and avg_pullback_depth > 1.0",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bull_micro_channel",
        description="Micro channel in bull direction (very tight, few bars)",
        bar_count="5-15",
        ohlc_rule="Sequence of bull bars with minimal overlap and no pullback",
        detection_logic="consecutive_bull_bars >= 5 and overlap_ratio < 0.3 and no_pullback",
        subjectivity="medium",
        required_tag_signals=["bull_trend_bar"],
    ),
    PatternRule(
        pattern_id="bear_micro_channel",
        description="Micro channel in bear direction (very tight, few bars)",
        bar_count="5-15",
        ohlc_rule="Sequence of bear bars with minimal overlap and no pullback",
        detection_logic="consecutive_bear_bars >= 5 and overlap_ratio < 0.3 and no_pullback",
        subjectivity="medium",
        required_tag_signals=["bear_trend_bar"],
    ),
    PatternRule(
        pattern_id="micro_channel",
        description="Tight sequence of small trend bars with little/no pullback",
        bar_count="5-15",
        ohlc_rule="Consecutive trend bars with no pullback",
        detection_logic="consecutive_trend_bars >= 5 and overlap_ratio < 0.3",
        subjectivity="medium",
    ),
    PatternRule(
        pattern_id="channel_as_flag",
        description="A tight channel that functions as a flag within a larger trend",
        bar_count="10-25",
        ohlc_rule="Channel forming as pullback/consolidation in trend",
        detection_logic="is_channel and prior_trend_exists and channel_range < 0.5 * prior_move",
        subjectivity="high",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# TREND PATTERNS
# =============================================================================

TREND_PATTERNS = [
    PatternRule(
        pattern_id="trend",
        description="Trend concept (directional price movement)",
        bar_count="variable",
        ohlc_rule="HH+HL (bull) or LH+LL (bear) sequence",
        detection_logic="detect_trend_via_swing_sequence",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bull_trend_from_the_open",
        description="Bull trend starting from market open",
        bar_count="variable",
        ohlc_rule="Bar 1-3 establish bull direction, then HH+HL continues",
        detection_logic="bar_number < 6 and is_bull_trend and close > open_price",
        subjectivity="medium",
        requires_swing_detection=True,
        notes="Requires session timing context",
    ),
    PatternRule(
        pattern_id="bear_trend_from_the_open",
        description="Bear trend starting from market open",
        bar_count="variable",
        ohlc_rule="Bar 1-3 establish bear direction, then LH+LL continues",
        detection_logic="bar_number < 6 and is_bear_trend and close < open_price",
        subjectivity="medium",
        requires_swing_detection=True,
        notes="Requires session timing context",
    ),
    PatternRule(
        pattern_id="trend_from_the_open",
        description="Intraday session that trends strongly from the open",
        bar_count="variable",
        ohlc_rule="Strong directional move from first bars",
        detection_logic="bar_number < 6 and (is_bull_trend or is_bear_trend)",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="small_pullback_bull_trend",
        description="Bull trend with small pullbacks (SPBT)",
        bar_count="variable",
        ohlc_rule="Bull trend with pullbacks < 0.5 ATR",
        detection_logic="is_bull_trend and avg_pullback_depth < 0.5",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="small_pullback_bear_trend",
        description="Bear trend with small pullbacks",
        bar_count="variable",
        ohlc_rule="Bear trend with pullbacks < 0.5 ATR",
        detection_logic="is_bear_trend and avg_pullback_depth < 0.5",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="stair_step_trend",
        description="Trend that advances in steps: impulse legs followed by consolidations",
        bar_count="variable",
        ohlc_rule="Alternating impulse legs and brief consolidations",
        detection_logic="detect_stair_step_pattern",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trend_resumption",
        description="Trend resuming after consolidation",
        bar_count="variable",
        ohlc_rule="Breakout from consolidation in prior trend direction",
        detection_logic="had_consolidation and breakout_in_trend_direction",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trend_weakening_sequence",
        description="Sequence showing loss of trend strength",
        bar_count="variable",
        ohlc_rule="Smaller trend bars, more overlap, deeper pullbacks",
        detection_logic="trend_bar_size_decreasing and overlap_increasing and pullback_depth_increasing",
        subjectivity="high",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# PULLBACK PATTERNS
# =============================================================================

PULLBACK_PATTERNS = [
    PatternRule(
        pattern_id="pullback",
        description="Pullback concept (countertrend move within larger trend)",
        bar_count="variable",
        ohlc_rule="Move against trend that holds above/below prior swing",
        detection_logic="is_countertrend_move and holds_structure",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="pullback_entry",
        description="Entry on pullback within existing trend",
        bar_count="variable",
        ohlc_rule="Reversal bar at end of pullback in trend direction",
        detection_logic="is_pullback and has_reversal_bar and trend_context",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="deep_pullback",
        description="Pullback that retraces large portion of prior move (50%+)",
        bar_count="variable",
        ohlc_rule="Pullback retraces > 50% of prior leg",
        detection_logic="pullback_depth > 0.5 * prior_leg_range",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="shallow_pullback",
        description="Shallow pullback that retraces small portion of prior move",
        bar_count="variable",
        ohlc_rule="Pullback retraces < 30% of prior leg",
        detection_logic="pullback_depth < 0.3 * prior_leg_range",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="endless_pullback",
        description="Pullback that keeps extending beyond expectations",
        bar_count="variable",
        ohlc_rule="Pullback exceeds typical duration/depth for context",
        detection_logic="pullback_bars > 10 or pullback_depth > 0.7",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="two_legged_pullback",
        description="Pullback that unfolds in two legs against the trend",
        bar_count="variable",
        ohlc_rule="Two pushes against trend before resumption",
        detection_logic="count_pullback_legs == 2",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="two_legs",
        description="Two legs / two-push concept (generic two-legged structure)",
        bar_count="variable",
        ohlc_rule="Two distinct legs in same direction",
        detection_logic="leg_count == 2",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="three_push_pullback",
        description="Pullback that unfolds in three pushes (wedge-like correction)",
        bar_count="variable",
        ohlc_rule="Three pushes against trend before resumption",
        detection_logic="count_pullback_legs == 3",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# REVERSAL PATTERNS
# =============================================================================

REVERSAL_PATTERNS = [
    PatternRule(
        pattern_id="reversal",
        description="Reversal concept (direction change / reversal attempt)",
        bar_count="variable",
        ohlc_rule="Change in trend direction at swing point",
        detection_logic="trend_change_detected",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bull_reversal",
        description="Bullish reversal concept (reversal up)",
        bar_count="variable",
        ohlc_rule="Bear-to-bull trend change with reversal bar",
        detection_logic="was_bear_trend and bull_reversal_bar and higher_low",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bear_reversal",
        description="Bearish reversal concept (reversal down)",
        bar_count="variable",
        ohlc_rule="Bull-to-bear trend change with reversal bar",
        detection_logic="was_bull_trend and bear_reversal_bar and lower_high",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="reversal_up",
        description="Upward reversal / bull reversal",
        bar_count="variable",
        ohlc_rule="Price reverses from low to move higher",
        detection_logic="bull_reversal detection (alias)",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="reversal_down",
        description="Downward reversal / bear reversal",
        bar_count="variable",
        ohlc_rule="Price reverses from high to move lower",
        detection_logic="bear_reversal detection (alias)",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="major_trend_reversal",
        description="Significant reversal of prior trend (MTR)",
        bar_count="variable",
        ohlc_rule="Trend reversal with strong reversal bar and follow-through",
        detection_logic="is_reversal and reversal_strength > threshold and follow_through",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="minor_reversal",
        description="Minor reversal (not major trend change)",
        bar_count="variable",
        ohlc_rule="Small reversal within larger trend",
        detection_logic="is_reversal and reversal_strength < threshold",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="opening_reversal",
        description="Reversal occurring near session open after initial drive",
        bar_count="3-10",
        ohlc_rule="Early directional move that reverses within first 30-60 min",
        detection_logic="bar_number < 12 and had_initial_move and now_reversing",
        subjectivity="medium",
        requires_swing_detection=True,
        notes="Requires session timing",
    ),
    PatternRule(
        pattern_id="higher_high_major_trend_reversal",
        description="Major trend reversal at higher high",
        bar_count="variable",
        ohlc_rule="HH followed by failed breakout and trend change",
        detection_logic="made_higher_high and then_reversed_down",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="lower_low_major_trend_reversal",
        description="Major trend reversal at lower low",
        bar_count="variable",
        ohlc_rule="LL followed by failed breakdown and trend change",
        detection_logic="made_lower_low and then_reversed_up",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="higher_low_major_trend_reversal",
        description="Major trend reversal at higher low",
        bar_count="variable",
        ohlc_rule="HL after downtrend, then trend change up",
        detection_logic="was_bear_trend and made_higher_low and now_bull",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="lower_high_major_trend_reversal",
        description="Major trend reversal at lower high",
        bar_count="variable",
        ohlc_rule="LH after uptrend, then trend change down",
        detection_logic="was_bull_trend and made_lower_high and now_bear",
        subjectivity="high",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# WEDGE VARIANT PATTERNS
# =============================================================================

WEDGE_VARIANT_PATTERNS = [
    PatternRule(
        pattern_id="wedge",
        description="Wedge concept (3 pushes / converging swings)",
        bar_count="variable",
        ohlc_rule="3 pushes in same direction with converging trendlines",
        detection_logic="push_count >= 3 and trendlines_converging",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="wedge_bottom",
        description="Three-push wedge pattern at bottom (falling wedge)",
        bar_count="variable (10-30)",
        ohlc_rule="3 lower lows with converging trendlines",
        detection_logic="wedge_bull detection (alias)",
        subjectivity="high",
        requires_swing_detection=True,
        notes="Alias for wedge_bull",
    ),
    PatternRule(
        pattern_id="wedge_top",
        description="Three-push wedge pattern at top (rising wedge)",
        bar_count="variable (10-30)",
        ohlc_rule="3 higher highs with converging trendlines",
        detection_logic="wedge_bear detection (alias)",
        subjectivity="high",
        requires_swing_detection=True,
        notes="Alias for wedge_bear",
    ),
    PatternRule(
        pattern_id="micro_wedge",
        description="Small wedge pattern (3 pushes) on lower timeframe",
        bar_count="5-15",
        ohlc_rule="Mini wedge with 3 pushes in tight range",
        detection_logic="is_wedge and total_bars < 15",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="minor_wedge",
        description="Small/minor wedge pattern",
        bar_count="5-20",
        ohlc_rule="Wedge in minor timeframe or context",
        detection_logic="is_wedge and wedge_range < atr * 2",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="nested_wedge",
        description="Wedge within a wedge pattern",
        bar_count="variable",
        ohlc_rule="Smaller wedge forming inside larger wedge structure",
        detection_logic="is_wedge and parent_is_wedge",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="truncated_wedge",
        description="Wedge with fewer than 3 legs (truncated)",
        bar_count="variable",
        ohlc_rule="Wedge-like structure with only 2 pushes",
        detection_logic="converging_structure and push_count == 2",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="parabolic_wedge",
        description="Accelerating wedge with climactic move",
        bar_count="variable",
        ohlc_rule="Wedge with accelerating slope and climactic final push",
        detection_logic="is_wedge and slope_accelerating and final_push_climactic",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="parabolic_wedge_top",
        description="Parabolic wedge top pattern",
        bar_count="variable",
        ohlc_rule="Rising parabolic wedge at top",
        detection_logic="is_parabolic_wedge and direction == 'up'",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="parabolic_wedge_bottom",
        description="Parabolic wedge bottom pattern",
        bar_count="variable",
        ohlc_rule="Falling parabolic wedge at bottom",
        detection_logic="is_parabolic_wedge and direction == 'down'",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="wedge_rally",
        description="Rally forming a wedge shape",
        bar_count="variable",
        ohlc_rule="Upward move with wedge characteristics",
        detection_logic="is_rally and has_wedge_shape",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# LEG AND STRUCTURE PATTERNS
# =============================================================================

LEG_STRUCTURE_PATTERNS = [
    PatternRule(
        pattern_id="bull_leg",
        description="Bull leg of a move",
        bar_count="variable",
        ohlc_rule="Swing low to swing high directional move",
        detection_logic="start_at_swing_low and end_at_swing_high",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bear_leg",
        description="Bear leg of a move",
        bar_count="variable",
        ohlc_rule="Swing high to swing low directional move",
        detection_logic="start_at_swing_high and end_at_swing_low",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="second_leg_up",
        description="Second leg of rally",
        bar_count="variable",
        ohlc_rule="Second bull leg after pullback from first leg",
        detection_logic="is_bull_leg and leg_number == 2",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="second_leg_down",
        description="Second leg down (follow-on leg lower)",
        bar_count="variable",
        ohlc_rule="Second bear leg after pullback from first leg",
        detection_logic="is_bear_leg and leg_number == 2",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="swing_higher_high",
        description="Swing higher high in structure",
        bar_count="variable",
        ohlc_rule="Current swing high > prior swing high",
        detection_logic="swing_high > prior_swing_high",
        subjectivity="low",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="swing_lower_low",
        description="Swing lower low in structure",
        bar_count="variable",
        ohlc_rule="Current swing low < prior swing low",
        detection_logic="swing_low < prior_swing_low",
        subjectivity="low",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="swing_higher_low",
        description="Swing higher low (HL) structural concept",
        bar_count="variable",
        ohlc_rule="Current swing low > prior swing low",
        detection_logic="swing_low > prior_swing_low",
        subjectivity="low",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="swing_lower_high",
        description="Swing lower high (LH) structural concept",
        bar_count="variable",
        ohlc_rule="Current swing high < prior swing high",
        detection_logic="swing_high < prior_swing_high",
        subjectivity="low",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="higher_high_double_top",
        description="Double top with higher high variant",
        bar_count="variable",
        ohlc_rule="Double top where second high is slightly higher",
        detection_logic="is_double_top and second_high > first_high",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="lower_low_double_bottom",
        description="Double bottom with lower low variant",
        bar_count="variable",
        ohlc_rule="Double bottom where second low is slightly lower",
        detection_logic="is_double_bottom and second_low < first_low",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# SPIKE PATTERNS
# =============================================================================

SPIKE_PATTERNS = [
    PatternRule(
        pattern_id="spike",
        description="Spike move (sudden strong breakout)",
        bar_count="1-5",
        ohlc_rule="3+ consecutive strong trend bars",
        detection_logic="consecutive_trend_bars >= 3 and body_dominance > 0.6",
        subjectivity="medium",
        required_tag_signals=["bull_trend_bar", "bear_trend_bar"],
    ),
    PatternRule(
        pattern_id="spike_bull",
        description="Bull spike (strong upward move)",
        bar_count="1-5",
        ohlc_rule="3+ consecutive strong bull trend bars",
        detection_logic="consecutive_bull_bars >= 3 and body_dominance > 0.6",
        subjectivity="medium",
        required_tag_signals=["bull_trend_bar"],
    ),
    PatternRule(
        pattern_id="spike_bear",
        description="Bear spike (strong downward move)",
        bar_count="1-5",
        ohlc_rule="3+ consecutive strong bear trend bars",
        detection_logic="consecutive_bear_bars >= 3 and body_dominance > 0.6",
        subjectivity="medium",
        required_tag_signals=["bear_trend_bar"],
    ),
    PatternRule(
        pattern_id="spike_and_channel",
        description="Trend structure with initial spike followed by orderly channel",
        bar_count="variable",
        ohlc_rule="Initial spike phase then channel phase",
        detection_logic="had_spike and now_in_channel",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="major_bull_surprise",
        description="Major surprise bar in bull direction",
        bar_count="1",
        ohlc_rule="Very large bull trend bar relative to recent bars",
        detection_logic="is_bull_bar and range > 2 * avg_range and body_ratio > 0.7",
        subjectivity="medium",
        required_tag_signals=["bull_surprise_bar"],
    ),
    PatternRule(
        pattern_id="major_bear_surprise",
        description="Major surprise bar in bear direction",
        bar_count="1",
        ohlc_rule="Very large bear trend bar relative to recent bars",
        detection_logic="is_bear_bar and range > 2 * avg_range and body_ratio > 0.7",
        subjectivity="medium",
        required_tag_signals=["bear_surprise_bar"],
    ),
]

# =============================================================================
# TRAP PATTERNS
# =============================================================================

TRAP_PATTERNS = [
    PatternRule(
        pattern_id="trapped_bulls",
        description="Trapped bulls (bulls who bought and are trapped)",
        bar_count="2-5",
        ohlc_rule="Bull entry followed by immediate reversal down",
        detection_logic="had_bull_signal_bar and then_failed_breakout_down",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trapped_bears",
        description="Trapped bears (shorts who sold and are trapped)",
        bar_count="2-5",
        ohlc_rule="Bear entry followed by immediate reversal up",
        detection_logic="had_bear_signal_bar and then_failed_breakout_up",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trap_trading",
        description="Trading setups that exploit trapped traders",
        bar_count="variable",
        ohlc_rule="Entry after failed breakout traps counter-trend traders",
        detection_logic="failed_breakout and reversal_bar_in_trap_direction",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="second_leg_trap",
        description="Trap on second leg",
        bar_count="variable",
        ohlc_rule="Second leg fails and traps traders",
        detection_logic="is_second_leg and then_trapped",
        subjectivity="high",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# GAP PATTERNS
# =============================================================================

GAP_PATTERNS = [
    PatternRule(
        pattern_id="gap_up",
        description="Upward gap opening",
        bar_count="1",
        ohlc_rule="Open > prior close (gap up)",
        detection_logic="open > prior_close",
        subjectivity="low",
    ),
    PatternRule(
        pattern_id="gap_down",
        description="Downward gap opening",
        bar_count="1",
        ohlc_rule="Open < prior close (gap down)",
        detection_logic="open < prior_close",
        subjectivity="low",
    ),
    PatternRule(
        pattern_id="gap_reversal",
        description="Reversal where gap fails and price reverses",
        bar_count="1-5",
        ohlc_rule="Gap up/down followed by reversal to close the gap",
        detection_logic="had_gap and now_reversing_toward_gap_close",
        subjectivity="medium",
    ),
]

# =============================================================================
# HEAD AND SHOULDERS PATTERNS
# =============================================================================

HEAD_SHOULDERS_PATTERNS = [
    PatternRule(
        pattern_id="head_and_shoulders_top",
        description="Head and shoulders top reversal",
        bar_count="variable",
        ohlc_rule="Left shoulder, higher head, right shoulder at similar level to left",
        detection_logic="detect_hs_top_pattern",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="head_and_shoulders_bottom",
        description="Head and shoulders bottom reversal (inverse H&S)",
        bar_count="variable",
        ohlc_rule="Left shoulder, lower head, right shoulder at similar level to left",
        detection_logic="detect_hs_bottom_pattern",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="head_and_shoulders_as_flag",
        description="H&S-shaped pullback that functions as continuation flag",
        bar_count="variable",
        ohlc_rule="H&S shape within larger trend as pullback",
        detection_logic="is_hs_pattern and functions_as_flag",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="neckline",
        description="Head and shoulders neckline",
        bar_count="variable",
        ohlc_rule="Support/resistance line connecting shoulders",
        detection_logic="identify_neckline_in_hs",
        subjectivity="high",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# MEASURED MOVE PATTERNS
# =============================================================================

MEASURED_MOVE_PATTERNS = [
    PatternRule(
        pattern_id="measured_move",
        description="Price projection based on prior swing or range height",
        bar_count="variable",
        ohlc_rule="Second leg equals first leg distance",
        detection_logic="leg2_range approximately equals leg1_range",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="measured_move_bull",
        description="Bull measured move (AB=CD up)",
        bar_count="variable",
        ohlc_rule="Bull leg followed by pullback, then equal second leg up",
        detection_logic="is_bull_leg and mm_target_up",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="measured_move_bear",
        description="Bear measured move (AB=CD down)",
        bar_count="variable",
        ohlc_rule="Bear leg followed by pullback, then equal second leg down",
        detection_logic="is_bear_leg and mm_target_down",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# TEST PATTERNS
# =============================================================================

TEST_PATTERNS = [
    PatternRule(
        pattern_id="test_of_high",
        description="Test of prior high",
        bar_count="variable",
        ohlc_rule="Price approaches prior high level",
        detection_logic="abs(high - prior_swing_high) / atr < 0.5",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="test_of_low",
        description="Test of prior low",
        bar_count="variable",
        ohlc_rule="Price approaches prior low level",
        detection_logic="abs(low - prior_swing_low) / atr < 0.5",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="test_of_ema",
        description="Test of moving average",
        bar_count="1-3",
        ohlc_rule="Price touches or approaches EMA",
        detection_logic="abs(close - ema) / atr < 0.3",
        subjectivity="low",
    ),
    PatternRule(
        pattern_id="test_of_open",
        description="Test of day's open price",
        bar_count="variable",
        ohlc_rule="Price returns to session open level",
        detection_logic="abs(close - session_open) / atr < 0.3",
        subjectivity="low",
        notes="Requires session context",
    ),
]

# =============================================================================
# RANGE PATTERNS
# =============================================================================

RANGE_PATTERNS = [
    PatternRule(
        pattern_id="trading_range",
        description="Sideways price action with defined support/resistance",
        bar_count="variable (10+)",
        ohlc_rule="Price oscillates between support and resistance",
        detection_logic="detect_horizontal_range",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trending_range",
        description="Trading range with directional drift",
        bar_count="variable",
        ohlc_rule="Range with slight HH/HL or LH/LL drift",
        detection_logic="is_range and has_drift",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trending_trading_range_bull",
        description="Bull-biased trading range that trends upward overall",
        bar_count="variable",
        ohlc_rule="Range with higher highs and higher lows drift",
        detection_logic="is_range and drift_direction == 'up'",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trending_trading_range_bear",
        description="Bear-biased trading range that trends downward overall",
        bar_count="variable",
        ohlc_rule="Range with lower highs and lower lows drift",
        detection_logic="is_range and drift_direction == 'down'",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trending_trading_range_day",
        description="Day with trending trading range character",
        bar_count="session",
        ohlc_rule="Session characterized by trending range behavior",
        detection_logic="session_type == 'trending_range'",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="triangle_pattern",
        description="Triangle consolidation pattern (symmetrical/ascending/descending)",
        bar_count="variable",
        ohlc_rule="Converging trendlines on highs and lows",
        detection_logic="detect_triangle_pattern",
        subjectivity="high",
        requires_swing_detection=True,
        notes="Alias for triangle with variants",
    ),
    PatternRule(
        pattern_id="triangle_breakout_mode",
        description="Triangle compression poised for breakout",
        bar_count="variable",
        ohlc_rule="Triangle with very tight compression ready to break",
        detection_logic="is_triangle and compression_very_high",
        subjectivity="high",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# LEDGE PATTERNS
# =============================================================================

LEDGE_PATTERNS = [
    PatternRule(
        pattern_id="ledge_pattern",
        description="Tight sideways pause/step that can act as continuation or reversal",
        bar_count="3-10",
        ohlc_rule="Tight horizontal consolidation with repeated level tests",
        detection_logic="detect_ledge_pattern",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bull_ledge",
        description="Bullish ledge: tight consolidation with repeated lows as support",
        bar_count="3-10",
        ohlc_rule="Repeated lows at similar level in bull context",
        detection_logic="is_ledge and direction == 'bull' and repeated_lows",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bear_ledge",
        description="Bearish ledge: tight consolidation with repeated highs as resistance",
        bar_count="3-10",
        ohlc_rule="Repeated highs at similar level in bear context",
        detection_logic="is_ledge and direction == 'bear' and repeated_highs",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# CLIMAX AND EXHAUSTION PATTERNS
# =============================================================================

CLIMAX_EXHAUSTION_PATTERNS = [
    PatternRule(
        pattern_id="climax",
        description="Climax concept (climactic move / exhaustion)",
        bar_count="1-5",
        ohlc_rule="Extreme bars with exhaustion characteristics",
        detection_logic="bar_range > 2 * atr and body_ratio > 0.7 and tail_rejection",
        subjectivity="medium",
    ),
    PatternRule(
        pattern_id="climactic_selloff",
        description="Climactic selling exhaustion",
        bar_count="1-5",
        ohlc_rule="Large bear bars with exhaustion tails at bottom",
        detection_logic="is_climax and direction == 'down' and lower_tail_prominent",
        subjectivity="medium",
    ),
    PatternRule(
        pattern_id="exhaustion",
        description="Exhaustion phase - trend losing momentum",
        bar_count="variable",
        ohlc_rule="Trend bars shrinking, overlap increasing, tails prominent",
        detection_logic="body_size_decreasing and overlap_increasing and tails_increasing",
        subjectivity="high",
    ),
]

# =============================================================================
# ALWAYS-IN PATTERNS
# =============================================================================

ALWAYS_IN_PATTERNS = [
    PatternRule(
        pattern_id="always_in",
        description="Always In concept (direction-neutral)",
        bar_count="variable",
        ohlc_rule="Strong trend with clear directional bias",
        detection_logic="trend_strength > threshold",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="always_in_long",
        description="Market condition where longs are favored continuously",
        bar_count="variable",
        ohlc_rule="Strong bull trend with HH+HL and bull closes",
        detection_logic="is_bull_trend and trend_strength > threshold and body_dominance > 0.5",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="always_in_short",
        description="Market condition where shorts are favored continuously",
        bar_count="variable",
        ohlc_rule="Strong bear trend with LH+LL and bear closes",
        detection_logic="is_bear_trend and trend_strength > threshold and body_dominance > 0.5",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# SECOND ENTRY PATTERNS
# =============================================================================

SECOND_ENTRY_PATTERNS = [
    PatternRule(
        pattern_id="second_entry_long",
        description="Second attempt long entry after first pullback",
        bar_count="variable",
        ohlc_rule="Second High 1 signal in pullback",
        detection_logic="is_high_2 context (alias)",
        subjectivity="medium",
        requires_swing_detection=True,
        notes="Related to high_2",
    ),
    PatternRule(
        pattern_id="second_entry_short",
        description="Second attempt short entry after first pullback",
        bar_count="variable",
        ohlc_rule="Second Low 1 signal in pullback",
        detection_logic="is_low_2 context (alias)",
        subjectivity="medium",
        requires_swing_detection=True,
        notes="Related to low_2",
    ),
    PatternRule(
        pattern_id="high_4",
        description="Fourth pullback in uptrend (High 4)",
        bar_count="variable",
        ohlc_rule="Fourth Higher High signal in pullback",
        detection_logic="pullback_count == 4 in bull trend",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="low_4",
        description="Fourth pullback in downtrend (Low 4)",
        bar_count="variable",
        ohlc_rule="Fourth Lower Low signal in pullback",
        detection_logic="pullback_count == 4 in bear trend",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# TRENDLINE PATTERNS
# =============================================================================

TRENDLINE_PATTERNS = [
    PatternRule(
        pattern_id="trend_line",
        description="Trend line / trendline concept",
        bar_count="variable",
        ohlc_rule="Line connecting swing points",
        detection_logic="detect_trendline",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="micro_trend_line",
        description="Short-term trendline over few bars",
        bar_count="3-10",
        ohlc_rule="Minor trendline over small number of bars",
        detection_logic="detect_micro_trendline",
        subjectivity="medium",
    ),
    PatternRule(
        pattern_id="trendline_break_retest",
        description="Trendline break followed by pullback/retest",
        bar_count="variable",
        ohlc_rule="Break trendline then return to test as support/resistance",
        detection_logic="broke_trendline and now_retesting",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trend_channel_line_overshoot",
        description="Price overshooting trend channel line",
        bar_count="1-3",
        ohlc_rule="Price extends beyond channel line",
        detection_logic="price > channel_line + threshold",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="trend_channel_line_undershoot",
        description="Price briefly breaks past channel line before reversing",
        bar_count="1-3",
        ohlc_rule="Price undershoots channel then reverses back",
        detection_logic="price_exceeded_channel and now_reversing",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="dueling_trendlines",
        description="Price compresses between opposing trendlines",
        bar_count="variable",
        ohlc_rule="Bull trendline below, bear trendline above, converging",
        detection_logic="has_bull_tl_below and has_bear_tl_above and converging",
        subjectivity="high",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# FLAG VARIANT PATTERNS
# =============================================================================

FLAG_VARIANT_PATTERNS = [
    PatternRule(
        pattern_id="bull_flag_around_moving_average_trap",
        description="Bull flag around MA that traps shorts before resuming up",
        bar_count="variable",
        ohlc_rule="Bull flag pullback to EMA that traps bears",
        detection_logic="is_bull_flag and at_ema and trapped_bears",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="bear_flag_around_moving_average_trap",
        description="Bear flag around MA that traps bears before reversing up",
        bar_count="variable",
        ohlc_rule="Bear flag rally to EMA that traps bears",
        detection_logic="is_bear_flag and at_ema and trapped_bulls",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="final_flag",
        description="Last flag/pullback late in trend before exhaustion",
        bar_count="variable",
        ohlc_rule="Flag pattern showing exhaustion characteristics",
        detection_logic="is_flag and late_in_trend and exhaustion_signs",
        subjectivity="high",
        requires_swing_detection=True,
    ),
]

# =============================================================================
# MISCELLANEOUS PATTERNS
# =============================================================================

MISC_PATTERNS = [
    PatternRule(
        pattern_id="abc_correction",
        description="Three-leg corrective move (A-B-C) against prior trend",
        bar_count="variable",
        ohlc_rule="Three legs: down-up-down or up-down-up",
        detection_logic="leg_count == 3 and alternating_direction",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="barb_wire",
        description="Tight overlapping bars with dojis, difficult to trade",
        bar_count="5+",
        ohlc_rule="High overlap ratio, many dojis, tight range",
        detection_logic="overlap_ratio > 0.7 and doji_count > 2 and range_compression < 0.5",
        subjectivity="medium",
        required_tag_signals=["bar_type_doji"],
    ),
    PatternRule(
        pattern_id="continuation",
        description="Trend continuation signal",
        bar_count="variable",
        ohlc_rule="Pattern resolves in trend direction",
        detection_logic="breakout_in_trend_direction",
        subjectivity="medium",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="follow_through",
        description="Confirmation price action after signal bar/breakout",
        bar_count="1-3",
        ohlc_rule="Bar(s) confirming prior signal direction",
        detection_logic="bar_in_signal_direction and body_ratio > 0.4",
        subjectivity="low",
    ),
    PatternRule(
        pattern_id="inside_outside_inside",
        description="Inside-Outside-Inside (IOI) pattern",
        bar_count="3",
        ohlc_rule="Inside bar, then outside bar, then inside bar",
        detection_logic="ioi detection (alias)",
        subjectivity="low",
        required_tag_signals=["inside_bar", "outside_bar"],
        notes="Alias for ioi",
    ),
    PatternRule(
        pattern_id="island_reversal",
        description="Reversal with gap away then gap back leaving isolated bars",
        bar_count="variable",
        ohlc_rule="Gap away, then gap back creating island of bars",
        detection_logic="gap_one_direction then gap_opposite_direction",
        subjectivity="high",
    ),
    PatternRule(
        pattern_id="outside_up_day",
        description="Outside day closing up",
        bar_count="1",
        ohlc_rule="Outside bar on daily timeframe closing bullish",
        detection_logic="is_outside_bar and is_bull_bar",
        subjectivity="low",
        required_tag_signals=["outside_bar", "bar_type_bull"],
    ),
    PatternRule(
        pattern_id="outside_down_day",
        description="Outside day closing down",
        bar_count="1",
        ohlc_rule="Outside bar on daily timeframe closing bearish",
        detection_logic="is_outside_bar and is_bear_bar",
        subjectivity="low",
        required_tag_signals=["outside_bar", "bar_type_bear"],
    ),
    PatternRule(
        pattern_id="doji_day",
        description="Day with doji characteristics",
        bar_count="session",
        ohlc_rule="Session open and close at similar levels",
        detection_logic="abs(session_close - session_open) / session_range < 0.1",
        subjectivity="low",
    ),
    PatternRule(
        pattern_id="crowded_trade_reversal",
        description="Reversal driven by overcrowded positioning",
        bar_count="variable",
        ohlc_rule="Extended move followed by sharp reversal (trapped late entries)",
        detection_logic="extended_move and sharp_reversal",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="stop_run",
        description="Move designed to trigger clustered stops",
        bar_count="1-3",
        ohlc_rule="Price exceeds swing high/low then reverses sharply",
        detection_logic="exceeded_swing_point and immediate_reversal",
        subjectivity="high",
        requires_swing_detection=True,
    ),
    PatternRule(
        pattern_id="twenty_gap_bars",
        description="Trend where bars don't touch MA for 20+ bars",
        bar_count="20+",
        ohlc_rule="No bar touches EMA for 20+ consecutive bars",
        detection_logic="bars_since_ema_touch >= 20",
        subjectivity="low",
    ),
    PatternRule(
        pattern_id="two_bar_reversal",
        description="Reversal pattern formed by two consecutive bars",
        bar_count="2",
        ohlc_rule="Two bars signaling direction change",
        detection_logic="two_bar_reversal_bull or two_bar_reversal_bear",
        subjectivity="low",
        notes="Generic version of two_bar_reversal_bull/bear",
    ),
]

# =============================================================================
# AGGREGATE: ALL PATTERN RULES
# =============================================================================

ALL_PATTERN_RULES = (
    OBJECTIVE_PATTERNS +
    MEDIUM_PATTERNS +
    HIGH_SUBJECTIVITY_PATTERNS +
    FLAG_PATTERNS +
    ENTRY_PATTERNS +
    BREAKOUT_PATTERNS +
    CHANNEL_VARIANT_PATTERNS +
    TREND_PATTERNS +
    PULLBACK_PATTERNS +
    REVERSAL_PATTERNS +
    WEDGE_VARIANT_PATTERNS +
    LEG_STRUCTURE_PATTERNS +
    SPIKE_PATTERNS +
    TRAP_PATTERNS +
    GAP_PATTERNS +
    HEAD_SHOULDERS_PATTERNS +
    MEASURED_MOVE_PATTERNS +
    TEST_PATTERNS +
    RANGE_PATTERNS +
    LEDGE_PATTERNS +
    CLIMAX_EXHAUSTION_PATTERNS +
    ALWAYS_IN_PATTERNS +
    SECOND_ENTRY_PATTERNS +
    TRENDLINE_PATTERNS +
    FLAG_VARIANT_PATTERNS +
    MISC_PATTERNS
)

PATTERN_RULE_LOOKUP = {p.pattern_id: p for p in ALL_PATTERN_RULES}


def get_pattern_rule(pattern_id: str) -> PatternRule | None:
    """Get a pattern rule definition by ID."""
    return PATTERN_RULE_LOOKUP.get(pattern_id)


def list_patterns_by_subjectivity(subjectivity: str) -> list[PatternRule]:
    """List all patterns with given subjectivity level."""
    return [p for p in ALL_PATTERN_RULES if p.subjectivity == subjectivity]


def list_patterns_requiring_swings() -> list[PatternRule]:
    """List all patterns that require swing detection."""
    return [p for p in ALL_PATTERN_RULES if p.requires_swing_detection]


def list_objective_patterns() -> list[PatternRule]:
    """List patterns that can be detected objectively from OHLC alone."""
    return [p for p in ALL_PATTERN_RULES if p.subjectivity == "low" and not p.requires_swing_detection]
