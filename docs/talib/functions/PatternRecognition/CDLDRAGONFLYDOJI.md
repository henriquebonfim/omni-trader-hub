# CDLDRAGONFLYDOJI - Dragonfly Doji Pattern

## Overview
The Dragonfly Doji Pattern (CDLDRAGONFLYDOJI) is a candlestick pattern that consists of a candle with a small body at the top of the range and a long lower shadow. It's a bullish reversal pattern that can signal trend changes.

## Category
Pattern Recognition

## Calculation
The CDLDRAGONFLYDOJI function identifies dragonfly doji patterns by analyzing the candle's body and shadow characteristics:

### Dragonfly Doji Criteria
- Small body at the top of the range
- Long lower shadow (significantly longer than body - adaptive threshold)
- Little or no upper shadow
- Appears after a downtrend
- Body can be bullish or bearish

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
- **Output**: Pattern recognition array (100 for dragonfly doji, 0 for no pattern)

## What It Means
The Dragonfly Doji Pattern indicates:
- **Bullish Reversal**: Potential upward reversal after a downtrend
- **Market Indecision**: Shows uncertainty between buyers and sellers
- **Support Test**: Often appears at key support levels
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Reversal Signals**: Look for dragonfly doji patterns at trend extremes
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLDRAGONFLYDOJI
    TA_RetCode ret = TA_CDLDRAGONFLYDOJI(
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
                // Dragonfly doji pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter long positions after dragonfly doji
2. **Breakout Confirmation**: Use to confirm breakout signals
3. **Trend Change**: Look for pattern at trend change points
4. **Risk Management**: Use stop losses based on pattern size

## Advantages
- Shows potential bullish reversal
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
