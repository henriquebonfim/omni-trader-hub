# CDLHARAMICROSS - Harami Cross Pattern

## Overview
The Harami Cross (CDLHARAMICROSS) is a two-candle reversal pattern where the second candle is a doji that is completely contained within the body of the first candle. It's a variation of the Harami pattern.

## Category
Pattern Recognition

## Calculation
The CDLHARAMICROSS function identifies harami cross patterns:

### Harami Cross Criteria
- First candle: Large body candle
- Second candle: Doji completely contained within first candle's body
- Pattern can be bullish or bearish
- Shows market indecision

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
The Harami Cross indicates:
- **Bullish Harami Cross**: Potential upward reversal after downtrend
- **Bearish Harami Cross**: Potential downward reversal after uptrend
- **Market Indecision**: Doji shows uncertainty
- **Reversal Signal**: Potential trend change

## How to Use
1. **Reversal Signal**: Look for pattern at trend extremes
2. **Confirmation**: Wait for next candle confirmation
3. **Volume**: Higher volume strengthens signal
4. **Support/Resistance**: Use at key levels

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLHARAMICROSS
    TA_RetCode ret = TA_CDLHARAMICROSS(
        0,                    // startIdx
        99,                   // endIdx
        open_prices,          // open
        high_prices,         // high
        low_prices,          // low
        close_prices,        // close
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        pattern              // outInteger
    );
    
    if (ret == TA_SUCCESS) {
        for (int i = 0; i < outNBElement; i++) {
            if (pattern[i] == 100) {
                // Bullish harami cross
            } else if (pattern[i] == -100) {
                // Bearish harami cross
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter opposite to previous trend
2. **Confirmation**: Wait for follow-through
3. **Indecision Trading**: Trade the breakout from indecision
4. **Risk Management**: Use tight stops

## Advantages
- Shows clear market indecision
- Easy to identify
- Works in both directions
- Good reversal signal

## Limitations
- Requires confirmation
- May give false signals
- Best at key levels
- Less reliable than engulfing patterns

## Related Functions
- `CDLHARAMI` - Harami Pattern
- `CDLDOJI` - Doji
- `CDLENGULFING` - Engulfing Pattern
- `CDLSPINNINGTOP` - Spinning Top

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
