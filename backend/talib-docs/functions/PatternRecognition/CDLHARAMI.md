# CDLHARAMI - Harami Pattern

## Overview
The Harami Pattern (CDLHARAMI) is a candlestick pattern that consists of two candles where the second candle's body is completely contained within the first candle's body. It's a reversal pattern that can signal trend changes.

## Category
Pattern Recognition

## Calculation
The CDLHARAMI function identifies harami patterns by comparing the current and previous candles:

### Bullish Harami
- Previous candle is bearish (close < open)
- Current candle is bullish (close > open)
- Current candle's body is completely contained within previous candle's body
- Current open > previous close
- Current close < previous open

### Bearish Harami
- Previous candle is bullish (close > open)
- Current candle is bearish (close < open)
- Current candle's body is completely contained within previous candle's body
- Current open < previous close
- Current close > previous open

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
The Harami Pattern indicates:
- **Bullish Harami**: Potential upward reversal after a downtrend
- **Bearish Harami**: Potential downward reversal after an uptrend
- **Indecision**: Shows market indecision and potential trend change
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Reversal Signals**: Look for harami patterns at trend extremes
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLHARAMI
    TA_RetCode ret = TA_CDLHARAMI(
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
                // Bullish harami pattern
            } else if (pattern[i] == -100) {
                // Bearish harami pattern
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
- Shows market indecision
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
- `CDLSPINNINGTOP` - Spinning Top Pattern
- `CDLMARUBOZU` - Marubozu Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
