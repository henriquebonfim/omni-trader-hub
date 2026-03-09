# CDLDARKCLOUDCOVER - Dark Cloud Cover Pattern

## Overview
The Dark Cloud Cover Pattern (CDLDARKCLOUDCOVER) is a candlestick pattern that consists of two candles where the second candle opens above the first candle's high and closes below the midpoint of the first candle's body. It's a bearish reversal pattern that can signal trend changes.

## Category
Pattern Recognition

## Calculation
The CDLDARKCLOUDCOVER function identifies dark cloud cover patterns by comparing the current and previous candles:

### Dark Cloud Cover Criteria
- Previous candle is bullish (close > open)
- Current candle is bearish (close < open)
- Current candle opens above previous candle's high
- Current candle closes below the midpoint of previous candle's body
- Current candle closes above previous candle's open

### Formula
```
Previous Body Midpoint = (Previous Open + Previous Close) / 2
Current Close < Previous Body Midpoint
Current Open > Previous High
Current Close > Previous Open
```

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
- **Output**: Pattern recognition array (100 for dark cloud cover, 0 for no pattern)

## What It Means
The Dark Cloud Cover Pattern indicates:
- **Bearish Reversal**: Potential downward reversal after an uptrend
- **Selling Pressure**: Shows increased selling interest
- **Resistance Test**: Often appears at key resistance levels
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Reversal Signals**: Look for dark cloud cover patterns at trend extremes
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLDARKCLOUDCOVER
    TA_RetCode ret = TA_CDLDARKCLOUDCOVER(
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
                // Dark cloud cover pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter short positions after dark cloud cover
2. **Breakout Confirmation**: Use to confirm breakout signals
3. **Trend Change**: Look for pattern at trend change points
4. **Risk Management**: Use stop losses based on pattern size

## Advantages
- Shows potential bearish reversal
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
