# CDLKICKING - Kicking Pattern

## Overview
The Kicking Pattern (CDLKICKING) is a candlestick pattern that consists of two candles where the second candle gaps in the opposite direction of the first candle and continues in that direction. It's a strong reversal pattern that can signal trend changes.

## Category
Pattern Recognition

## Calculation
The CDLKICKING function identifies kicking patterns by comparing the current and previous candles:

### Bullish Kicking
- Previous candle is bearish (close < open)
- Current candle is bullish (close > open)
- Current candle gaps up from previous candle
- Both candles have large bodies
- Current candle continues in bullish direction

### Bearish Kicking
- Previous candle is bullish (close > open)
- Current candle is bearish (close < open)
- Current candle gaps down from previous candle
- Both candles have large bodies
- Current candle continues in bearish direction

## Implementation Note

**This pattern uses TA-Lib's adaptive threshold system** for determining candle characteristics like "long body", "short body", "doji", etc. These thresholds automatically adjust based on recent market behavior rather than using fixed percentages.

For detailed information about:
- How adaptive thresholds work
- Configuring pattern detection sensitivity  
- Understanding output values
- Technical implementation details

See: [Candlestick Pattern Recognition Overview](CANDLESTICK_PATTERNS_OVERVIEW.md)


## Parameters
- **Input**: OHLC data (Open, High, Low, Close)
- **Output**: Pattern recognition array (100 for bullish, -100 for bearish, 0 for no pattern)

## What It Means
The Kicking Pattern indicates:
- **Bullish Kicking**: Strong upward reversal after a downtrend
- **Bearish Kicking**: Strong downward reversal after an uptrend
- **Gap Reversal**: Shows strong reversal with gap
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Reversal Signals**: Look for kicking patterns at trend extremes
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLKICKING
    TA_RetCode ret = TA_CDLKICKING(
        0,                    // startIdx
        99,                   // endIdx
        open_prices,          // open
        high_prices,         // high
        low_prices,          // low
        close_prices,        // close
        &outBegIdx,          // outBegIdx
        &outNBElement,      // outNBElement
        pattern              // outInteger
    );
    
    if (ret == TA_SUCCESS) {
        // Use pattern array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (pattern[i] == 100) {
                // Bullish kicking pattern
            } else if (pattern[i] == -100) {
                // Bearish kicking pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter positions opposite to the previous trend
2. **Breakout Confirmation**: Use to confirm breakout signals
3. **Trend Change**: Look for pattern at trend change points
4. **Risk Management**: Use stop losses based on pattern size

## Advantages
- Shows strong reversal signals
- Easy to identify visually
- Works in all timeframes
- Can be combined with other indicators

## Limitations
- May give false signals in choppy markets
- Requires confirmation from other indicators
- Best used at key support/resistance levels
- May lag in fast-moving markets

## Related Functions
- `CDLHAMMER` - Hammer Pattern
- `CDLDOJI` - Doji Pattern
- `CDLENGULFING` - Engulfing Pattern
- `CDLHARAMI` - Harami Pattern
- `CDLSPINNINGTOP` - Spinning Top Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
