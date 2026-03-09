# CDLINVERTEDHAMMER - Inverted Hammer

## Overview
The Inverted Hammer (CDLINVERTEDHAMMER) is a bullish reversal candlestick pattern that forms after a downtrend. It has a small body at the bottom with a long upper shadow and little to no lower shadow.

## Category
Pattern Recognition

## Calculation
The CDLINVERTEDHAMMER function identifies inverted hammer patterns:

### Inverted Hammer Criteria
- Small body near the bottom of the candle
- Long upper shadow (significantly longer than body - adaptive threshold)
- Little or no lower shadow
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
- **Output**: Pattern recognition array (100 for pattern, 0 for no pattern)

## What It Means
The Inverted Hammer indicates:
- **Bullish Reversal**: Potential upward reversal after downtrend
- **Buyer Interest**: Shows buyers testing higher prices
- **Momentum Shift**: Indicates potential shift in momentum
- **Confirmation Needed**: Requires next candle confirmation

## How to Use
1. **Reversal Signal**: Look for inverted hammer at downtrend bottoms
2. **Confirmation**: Wait for bullish candle confirmation
3. **Support Levels**: Most effective at key support levels
4. **Volume**: Higher volume strengthens the signal

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLINVERTEDHAMMER
    TA_RetCode ret = TA_CDLINVERTEDHAMMER(
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
                // Inverted hammer pattern detected
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter long after pattern confirmation
2. **Stop Loss**: Place below pattern low
3. **Support Trading**: Combined with support level analysis
4. **Confirmation**: Wait for bullish follow-through

## Advantages
- Clear visual pattern
- Strong reversal signal at bottoms
- Works in all timeframes
- Well-documented pattern

## Limitations
- Requires confirmation
- May give false signals without confirmation
- Best at significant support levels
- Less reliable in ranging markets

## Related Functions
- `CDLHAMMER` - Hammer
- `CDLSHOOTINGSTAR` - Shooting Star
- `CDLDOJI` - Doji
- `CDLDRAGONFLYDOJI` - Dragonfly Doji

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
