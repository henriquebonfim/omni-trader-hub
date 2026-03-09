# CDLHANGINGMAN - Hanging Man Pattern

## Overview
The Hanging Man Pattern (CDLHANGINGMAN) is a candlestick pattern that consists of a candle with a small body at the top of the range and a long lower shadow. It's a bearish reversal pattern that can signal trend changes.

## Category
Pattern Recognition

## Calculation
The CDLHANGINGMAN function identifies hanging man patterns by analyzing the candle's body and shadow characteristics:

### Hanging Man Criteria
- Small body at the top of the range
- Long lower shadow (significantly longer than body - adaptive threshold)
- Little or no upper shadow
- Appears after an uptrend
- Body can be bullish or bearish

### Formula
```
Body Size = |Close - Open|
Lower Shadow = Open - Low (or Close - Low)
Shadow Ratio = Lower Shadow / Body Size
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
- **Output**: Pattern recognition array (100 for hanging man, 0 for no pattern)

## What It Means
The Hanging Man Pattern indicates:
- **Bearish Reversal**: Potential downward reversal after an uptrend
- **Market Indecision**: Shows uncertainty between buyers and sellers
- **Support Test**: Often appears at key resistance levels
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Reversal Signals**: Look for hanging man patterns at trend extremes
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLHANGINGMAN
    TA_RetCode ret = TA_CDLHANGINGMAN(
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
                // Hanging man pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter short positions after hanging man
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
