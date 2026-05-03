# CDLLONGLEGGEDDOJI - Long Legged Doji

## Overview
The Long Legged Doji (CDLLONGLEGGEDDOJI) is a doji pattern with very long upper and lower shadows, indicating extreme market indecision and high volatility.

## Category
Pattern Recognition

## Calculation
The CDLLONGLEGGEDDOJI function identifies long legged doji patterns:

### Long Legged Doji Criteria
- Open and close are nearly equal (doji)
- Very long upper shadow
- Very long lower shadow
- Shows extreme indecision

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
The Long Legged Doji indicates:
- **Extreme Indecision**: Maximum uncertainty between buyers and sellers
- **High Volatility**: Significant price swings in both directions
- **Potential Reversal**: Often appears at major turning points
- **Market Exhaustion**: May signal trend exhaustion

## How to Use
1. **Major Reversal Signal**: Look for at significant levels
2. **Volume Confirmation**: Higher volume strengthens signal
3. **Context Analysis**: Consider market conditions
4. **Follow-through**: Wait for next candle direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLLONGLEGGEDDOJI
    TA_RetCode ret = TA_CDLLONGLEGGEDDOJI(
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
                // Long legged doji detected
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Look for reversal after pattern
2. **Breakout Trading**: Trade the breakout from indecision
3. **Volatility Trading**: Use for extreme volatility signals
4. **Exhaustion Trading**: Trade trend exhaustion

## Advantages
- Strong indecision signal
- Clear visual pattern
- Works at major levels
- Good for volatility analysis

## Limitations
- Rare pattern
- Requires strong confirmation
- May not provide clear direction
- Best used with other indicators

## Related Functions
- `CDLDOJI` - Doji
- `CDLHIGHWAVE` - High-Wave Candle
- `CDLSPINNINGTOP` - Spinning Top
- `CDLDRAGONFLYDOJI` - Dragonfly Doji

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
