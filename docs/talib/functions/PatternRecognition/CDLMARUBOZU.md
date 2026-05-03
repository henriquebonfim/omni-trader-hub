# CDLMARUBOZU - Marubozu Pattern

## Overview
The Marubozu Pattern (CDLMARUBOZU) is a candlestick pattern that consists of a candle with no shadows (or very small shadows) and a large body. It indicates strong directional movement and continuation of the current trend.

## Category
Pattern Recognition

## Calculation
The CDLMARUBOZU function identifies marubozu patterns by analyzing the candle's body and shadow characteristics:

### Bullish Marubozu
- Large bullish body (close > open)
- No or very small upper shadow
- No or very small lower shadow
- Strong buying pressure

### Bearish Marubozu
- Large bearish body (close < open)
- No or very small upper shadow
- No or very small lower shadow
- Strong selling pressure

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
The Marubozu Pattern indicates:
- **Bullish Marubozu**: Strong buying pressure and potential upward continuation
- **Bearish Marubozu**: Strong selling pressure and potential downward continuation
- **Trend Strength**: Shows strong directional movement
- **Continuation**: Often signals trend continuation

## How to Use
1. **Trend Continuation**: Look for marubozu patterns in trending markets
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLMARUBOZU
    TA_RetCode ret = TA_CDLMARUBOZU(
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
                // Bullish marubozu pattern
            } else if (pattern[i] == -100) {
                // Bearish marubozu pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter positions in the direction of the marubozu
2. **Breakout Trading**: Use to confirm breakout signals
3. **Trend Following**: Follow the direction of the marubozu
4. **Risk Management**: Use stop losses based on pattern size

## Advantages
- Shows strong directional movement
- Easy to identify visually
- Works in all timeframes
- Can be combined with other indicators

## Limitations
- May give false signals in choppy markets
- Requires confirmation from other indicators
- Best used in trending markets
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
