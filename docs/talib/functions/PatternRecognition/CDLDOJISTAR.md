# CDLDOJISTAR - Doji Star

## Overview
The Doji Star (CDLDOJISTAR) is a three-candle reversal pattern that can be either bullish or bearish depending on the context. It consists of a large candle, a doji (the "star"), and another large candle in the opposite direction.

## Category
Pattern Recognition

## Calculation
The CDLDOJISTAR function identifies doji star patterns:

### Bullish Doji Star Criteria
- First candle: Long white (bullish) body
- Second candle: Doji that gaps up

### Bearish Doji Star Criteria
- First candle: Long black (bearish) body
- Second candle: Doji that gaps down
- Pattern can be bullish or bearish

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
- **Penetration**: How far third candle must close into first candle (default: 0.3 = 30%)
- **Output**: Pattern recognition array (100 for bullish, -100 for bearish, 0 for no pattern)

## What It Means
The Doji Star indicates:
- **Bullish Doji Star**: Potential upward reversal after downtrend
- **Bearish Doji Star**: Potential downward reversal after uptrend
- **Market Indecision**: Doji shows equilibrium before reversal
- **High Reliability**: Strong reversal signal

## How to Use
1. **Context Analysis**: Determine if pattern is bullish or bearish based on preceding trend
2. **Confirmation**: Wait for pattern completion
3. **Volume**: Higher volume strengthens signal
4. **Support/Resistance**: Use at key levels

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLDOJISTAR
    TA_RetCode ret = TA_CDLDOJISTAR(
        0,                    // startIdx
        99,                   // endIdx
        open_prices,          // open
        high_prices,         // high
        low_prices,          // low
        close_prices,        // close
        0.3,                 // penetration
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        pattern              // outInteger
    );
    
    if (ret == TA_SUCCESS) {
        for (int i = 0; i < outNBElement; i++) {
            if (pattern[i] == 100) {
                // Bullish doji star
            } else if (pattern[i] == -100) {
                // Bearish doji star
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter in direction of third candle
2. **Context Trading**: Consider preceding trend
3. **Confirmation**: Wait for pattern completion
4. **Risk Management**: Use appropriate stops

## Advantages
- High reliability
- Clear indecision signal
- Works in both directions
- Strong reversal indicator

## Limitations
- Requires three candles
- Context-dependent interpretation
- May give false signals
- Best at key levels

## Related Functions
- `CDLDOJI` - Doji
- `CDLMORNINGDOJISTAR` - Morning Doji Star
- `CDLEVENINGDOJISTAR` - Evening Doji Star
- `CDLSTAR` - Star patterns

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
