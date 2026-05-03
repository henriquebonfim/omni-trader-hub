# CDLADVANCEBLOCK - Advance Block Pattern

## Overview
The Advance Block Pattern (CDLADVANCEBLOCK) is a bearish reversal pattern consisting of three white (bullish) candles with consecutively higher closes, but showing signs of weakening momentum. It signals potential exhaustion of the uptrend.

## Category
Pattern Recognition

## Calculation
The CDLADVANCEBLOCK function identifies advance block patterns by analyzing three consecutive candles:

### Advance Block Criteria
- Three white (bullish) candles with consecutively higher closes
- Each candle opens within or near the previous white body
- First candle: Long white with short or no upper shadow
- Second and third candles show weakening: progressively smaller bodies and/or relatively long upper shadows
- Pattern differentiates from Three White Soldiers by showing signs of exhaustion

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
- **Output**: Pattern recognition array (100 for advance block, 0 for no pattern)

## What It Means
The Advance Block Pattern indicates:
- **Bearish Reversal**: Potential downward reversal after an uptrend
- **Weakening Momentum**: Shows decreasing bullish momentum
- **Resistance Test**: Often appears at key resistance levels
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Reversal Signals**: Look for advance block patterns at trend extremes
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLADVANCEBLOCK
    TA_RetCode ret = TA_CDLADVANCEBLOCK(
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
                // Advance block pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter short positions after advance block
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
