# CDL3LINESTRIKE - Three Line Strike Pattern

## Overview
The Three Line Strike Pattern (CDL3LINESTRIKE) is a candlestick pattern that consists of four candles where the first three are in the same direction and the fourth candle reverses the trend. It's a reversal pattern that can signal trend changes.

## Category
Pattern Recognition

## Calculation
The CDL3LINESTRIKE function identifies three line strike patterns by analyzing four consecutive candles:

### Bullish Three Line Strike Criteria
- First three candles: Three black crows (three consecutive declining black candles, each opening within/near previous body)
- Fourth candle: White candle that opens below third's close and closes above first candle's open

### Bearish Three Line Strike Criteria
- First three candles: Three white soldiers (three consecutive rising white candles, each opening within/near previous body)
- Fourth candle: Black candle that opens above third's close and closes below first candle's open

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
The Three Line Strike Pattern indicates:
- **Bullish Three Line Strike**: Strong upward reversal after three bearish candles
- **Bearish Three Line Strike**: Strong downward reversal after three bullish candles
- **Trend Reversal**: Shows strong reversal momentum
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Reversal Signals**: Look for three line strike patterns at trend extremes
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDL3LINESTRIKE
    TA_RetCode ret = TA_CDL3LINESTRIKE(
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
                // Bullish three line strike pattern
            } else if (pattern[i] == -100) {
                // Bearish three line strike pattern
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
