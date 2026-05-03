# CDLTRISTAR - Tristar Pattern

## Overview
The Tristar Pattern (CDLTRISTAR) is a three-candle reversal pattern that consists of three doji candles, indicating extreme market indecision and potential reversal.

## Category
Pattern Recognition

## Calculation
The CDLTRISTAR function identifies tristar patterns:

### Tristar Criteria
- First candle: Doji
- Second candle: Doji that gaps from the first
- Third candle: Doji that gaps from the second
- All three candles are doji
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
- **Output**: Pattern recognition array (100 for bullish, -100 for bearish, 0 for no pattern)

## What It Means
The Tristar Pattern indicates:
- **Extreme Indecision**: Maximum market uncertainty
- **Potential Reversal**: Often appears at major turning points
- **Market Exhaustion**: May signal trend exhaustion
- **High Reliability**: Very strong reversal signal

## How to Use
1. **Major Reversal Signal**: Look for at significant levels
2. **Volume Confirmation**: Higher volume strengthens signal
3. **Context Analysis**: Consider market conditions
4. **Follow-through**: Wait for next candle direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLTRISTAR
    TA_RetCode ret = TA_CDLTRISTAR(
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
                // Bullish tristar
            } else if (pattern[i] == -100) {
                // Bearish tristar
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Look for reversal after pattern
2. **Breakout Trading**: Trade the breakout from indecision
3. **Exhaustion Trading**: Trade trend exhaustion
4. **Major Levels**: Use at significant support/resistance

## Advantages
- Very strong reversal signal
- Clear indecision pattern
- Works at major levels
- High reliability

## Limitations
- Very rare pattern
- Requires strong confirmation
- May not provide clear direction
- Best used with other indicators

## Related Functions
- `CDLDOJI` - Doji
- `CDLSTAR` - Star patterns
- `CDLMORNINGSTAR` - Morning Star
- `CDLEVENINGSTAR` - Evening Star

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
