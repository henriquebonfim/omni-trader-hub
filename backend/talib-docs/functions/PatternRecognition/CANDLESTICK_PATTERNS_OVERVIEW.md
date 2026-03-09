# Candlestick Pattern Recognition - Technical Overview

## Introduction

TA-Lib implements a sophisticated candlestick pattern recognition system based on traditional Japanese candlestick analysis. This document explains the technical implementation details that apply to all candlestick pattern functions (CDL* functions).

## Adaptive Threshold System

### Overview

Unlike simple fixed-ratio pattern recognition, TA-Lib uses an **adaptive threshold system** that adjusts pattern criteria based on recent market conditions. This makes pattern recognition more robust across different securities and market environments.

### How It Works

When documentation describes pattern criteria like:
- "Long body"
- "Short body"
- "Small body"
- "Doji (open ≈ close)"
- "Long shadow"
- "Gap up/down"

The actual implementation compares current candle characteristics against **recent historical averages**, not fixed percentages.

### Adaptive Calculation

For each candle characteristic (e.g., body length), TA-Lib:

1. **Calculates a rolling average** of that characteristic over recent candles
2. **Compares the current value** against this adaptive threshold
3. **Adjusts for market volatility** automatically

#### Example: Doji Pattern

**Conceptual Description:**
```
A Doji occurs when |Close - Open| is very small relative to the range
```

**Actual Implementation:**
```c
if( TA_REALBODY(i) <= TA_CANDLEAVERAGE(BodyDoji, BodyDojiPeriodTotal, i) )
    // This is a Doji
```

Where:
- `TA_REALBODY(i)` = |Close - Open| for candle i
- `TA_CANDLEAVERAGE(BodyDoji, ...)` = Adaptive threshold based on recent candles
- The threshold automatically adjusts to market conditions

### Threshold Types

TA-Lib defines several candle characteristic types:

| Type | Description | Used For |
|------|-------------|----------|
| `BodyDoji` | Very small body | Doji patterns |
| `BodyShort` | Short body | Star patterns, small candles |
| `BodyLong` | Long body | Strong directional candles |
| `ShadowShort` | Short shadow | Limited wicks |
| `ShadowLong` | Long shadow | Extended wicks |
| `ShadowVeryShort` | Very short shadow | Marubozu-like |
| `ShadowVeryLong` | Very long shadow | Hammer, Shooting Star |
| `Near` | Close proximity | Gap analysis |
| `Far` | Significant separation | Gap analysis |
| `Equal` | Approximately equal | Level comparisons |

## Configurable Settings

### TA_SetCandleSettings Function

Users can customize pattern recognition thresholds using:

```c
TA_RetCode TA_SetCandleSettings(
    TA_CandleSettingType settingType,    // Which characteristic to adjust
    TA_RangeType rangeType,              // How to calculate the range
    int avgPeriod,                       // Lookback period for average
    double factor                        // Multiplier for threshold
);
```

### Parameters

**settingType**: Which candle characteristic to adjust (BodyLong, ShadowShort, etc.)

**rangeType**: How to measure the characteristic:
- `RealBody` - Uses |Close - Open|
- `HighLow` - Uses High - Low
- `Shadows` - Uses shadow lengths

**avgPeriod**: Number of candles for rolling average (0 = use default)

**factor**: Threshold multiplier (default values vary by setting)

### Default Settings

TA-Lib uses carefully calibrated defaults based on extensive testing:

```c
// Example defaults (simplified)
BodyDoji:      avgPeriod=10, factor=0.1   // Body ≤ 10% of recent avg range
BodyShort:     avgPeriod=10, factor=0.3   // Body ≤ 30% of recent avg body
BodyLong:      avgPeriod=10, factor=1.0   // Body ≥ 100% of recent avg body
ShadowLong:    avgPeriod=10, factor=1.0   // Shadow ≥ 100% of recent avg
```

### Restoring Defaults

```c
TA_RetCode TA_RestoreCandleDefaultSettings(TA_CandleSettingType settingType);
```

Set `settingType` to `TA_AllCandleSettings` to restore all defaults.

## Pattern Recognition Output

### Output Values

Candlestick pattern functions return integer values:

| Value | Meaning |
|-------|---------|
| `100` | Bullish pattern detected (strong) |
| `1-99` | Bullish pattern detected (weaker confidence) |
| `0` | No pattern detected |
| `-1 to -99` | Bearish pattern detected (weaker confidence) |
| `-100` | Bearish pattern detected (strong) |

### Strength Scoring

Some patterns adjust output strength based on:
- **Exact vs approximate matches** (e.g., 100 vs 80 for perfect/near-perfect engulfing)
- **Quality of pattern formation** (e.g., cleaner patterns score higher)
- **Completeness of criteria** (all conditions vs most conditions met)

## Implementation Details

### Macro System

TA-Lib uses C macros for efficient pattern detection:

```c
// Check candle color
TA_CANDLECOLOR(i)          // Returns 1 (white/bullish) or -1 (black/bearish)

// Measure candle characteristics
TA_REALBODY(i)             // |Close - Open|
TA_UPPERSHADOW(i)          // High - max(Open, Close)
TA_LOWERSHADOW(i)          // min(Open, Close) - Low
TA_HIGHHIGHLOW(i)          // High - Low

// Compare against adaptive averages
TA_CANDLEAVERAGE(type, total, i)  // Adaptive threshold

// Detect gaps
TA_REALBODYGAPUP(i, j)     // Real body gaps up
TA_REALBODYGAPDOWN(i, j)   // Real body gaps down
```

### Rolling Average Calculation

For each pattern recognition call, TA-Lib:

1. **Initializes period totals** for each threshold type used
2. **Accumulates historical values** over the avgPeriod
3. **Updates rolling totals** as it processes each new candle
4. **Calculates adaptive threshold** = (periodTotal / avgPeriod) × factor

This efficient approach allows real-time pattern detection without recalculating from scratch.

## Pattern Documentation Interpretation

### Reading Pattern Criteria

When a pattern's documentation states criteria like:

**"First candle: Long white body"**

This means:
```c
TA_CANDLECOLOR(i-2) == 1 &&  // White (bullish)
TA_REALBODY(i-2) > TA_CANDLEAVERAGE(BodyLong, BodyLongPeriodTotal, i-2)  // Long
```

**"Second candle: Small body"**

This means:
```c
TA_REALBODY(i-1) <= TA_CANDLEAVERAGE(BodyShort, BodyShortPeriodTotal, i-1)
```

**"Gap up between candles"**

This means:
```c
TA_REALBODYGAPUP(i, i-1)  // Current body gaps above previous body
```

### Fixed vs Adaptive Criteria

Some pattern criteria ARE fixed (not adaptive):

✅ **Adaptive** (adjusts to market):
- Body size classifications (long/short/doji)
- Shadow length classifications
- What constitutes a "gap"

🔒 **Fixed** (always the same):
- Candle color (bullish/bearish)
- Candle sequence and order
- Relative position requirements (e.g., "closes within previous body")
- Penetration percentages (when explicitly specified as parameters)

## Best Practices

### For Pattern Recognition Users

1. **Use default settings initially** - They work well for most markets
2. **Adjust settings for specific securities** if needed (e.g., crypto vs stocks)
3. **Test threshold changes** on historical data before live trading
4. **Combine with other analysis** - Candlestick patterns are signals, not certainties
5. **Consider market context** - Patterns are more reliable at support/resistance levels

### For Different Markets

**Stocks**: Default settings work well

**Forex**: May need slightly tighter thresholds (lower factors)

**Crypto**: May need looser thresholds due to higher volatility

**Low Volatility**: Consider reducing avgPeriod for faster adaptation

**High Volatility**: Consider increasing avgPeriod for more stability

## Technical References

### Key Functions

- `TA_SetCandleSettings()` - Customize thresholds
- `TA_RestoreCandleDefaultSettings()` - Reset to defaults
- All `TA_CDL*()` functions - Pattern recognition functions

### Source Code

Pattern recognition implementation: `ta-lib/src/ta_func/ta_CDL*.c`

Candlestick utilities: `ta-lib/src/ta_func/ta_utility.h`

Settings management: `ta-lib/src/ta_common/ta_global.c`

## Summary

TA-Lib's candlestick pattern recognition system provides:

✅ **Adaptive thresholds** that adjust to market conditions
✅ **Configurable settings** for customization
✅ **Robust detection** across different securities
✅ **Efficient calculation** via rolling averages
✅ **Traditional patterns** with modern implementation

This adaptive approach makes TA-Lib's pattern recognition more reliable than simple fixed-ratio systems, while still honoring the traditional Japanese candlestick analysis principles.

## See Also

- Individual pattern documentation: `CDL*.md` files
- TA-Lib API documentation: For language-specific usage
- Traditional candlestick analysis literature for pattern interpretation

