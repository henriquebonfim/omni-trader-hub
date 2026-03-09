# CDLSHOOTINGSTAR - Shooting Star

## Overview
The Shooting Star (CDLSHOOTINGSTAR) is a bearish reversal candlestick pattern that forms after an uptrend. It has a small body at the bottom with a long upper shadow and little to no lower shadow.

## Category
Pattern Recognition

## Calculation
The CDLSHOOTINGSTAR function identifies shooting star patterns:

### Shooting Star Criteria
- Small body near the bottom of the candle
- Long upper shadow (significantly longer than body - adaptive threshold)
- Little or no lower shadow
- Appears after an uptrend
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
- **Output**: Pattern recognition array (-100 for pattern, 0 for no pattern)

## What It Means
The Shooting Star indicates:
- **Bearish Reversal**: Potential downward reversal after uptrend
- **Rejection**: Shows rejection of higher prices
- **Momentum Shift**: Indicates potential shift in momentum
- **Confirmation Needed**: Requires next candle confirmation

## How to Use
1. **Reversal Signal**: Look for shooting star at uptrend tops
2. **Confirmation**: Wait for bearish candle confirmation
3. **Resistance Levels**: Most effective at key resistance levels
4. **Volume**: Higher volume strengthens the signal

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLSHOOTINGSTAR
    TA_RetCode ret = TA_CDLSHOOTINGSTAR(
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
            if (pattern[i] == -100) {
                // Shooting star pattern detected
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter short after pattern confirmation
2. **Stop Loss**: Place above pattern high
3. **Resistance Trading**: Combined with resistance level analysis
4. **Confirmation**: Wait for bearish follow-through

## Advantages
- Clear visual pattern
- Strong reversal signal at tops
- Works in all timeframes
- Well-documented pattern

## Limitations
- Requires confirmation
- May give false signals without confirmation
- Best at significant resistance levels
- Less reliable in ranging markets

## Related Functions
- `CDLINVERTEDHAMMER` - Inverted Hammer
- `CDLHANGINGMAN` - Hanging Man
- `CDLDOJI` - Doji
- `CDLGRAVESTONEDOJI` - Gravestone Doji

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
