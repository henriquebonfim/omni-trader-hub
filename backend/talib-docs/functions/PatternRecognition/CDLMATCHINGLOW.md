# CDLMATCHINGLOW - Matching Low

## Overview
The Matching Low (CDLMATCHINGLOW) is a two-candle bullish reversal pattern where two candles have the same low price, indicating potential support and reversal.

## Category
Pattern Recognition

## Calculation
The CDLMATCHINGLOW function identifies matching low patterns:

### Matching Low Criteria
- First candle: Bearish candle
- Second candle: Bearish candle with same low as first
- Pattern appears after downtrend
- Shows potential support level

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
The Matching Low indicates:
- **Support Level**: Same low shows support
- **Bullish Reversal**: Potential upward reversal
- **Double Bottom**: Similar to double bottom pattern
- **Confirmation Needed**: Requires bullish follow-through

## How to Use
1. **Support Trading**: Look for support at matching low
2. **Reversal Signal**: Enter long after pattern
3. **Confirmation**: Wait for bullish follow-through
4. **Stop Loss**: Place below matching low

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLMATCHINGLOW
    TA_RetCode ret = TA_CDLMATCHINGLOW(
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
                // Matching low pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Support Trading**: Trade the support level
2. **Reversal Trading**: Enter long after pattern
3. **Double Bottom**: Similar to double bottom trading
4. **Confirmation**: Wait for bullish follow-through

## Advantages
- Clear support level
- Easy to identify
- Good reversal signal
- Works at key levels

## Limitations
- Requires confirmation
- May give false signals
- Best at significant support
- Needs bullish follow-through

## Related Functions
- `CDLDOJI` - Doji
- `CDLHAMMER` - Hammer
- `CDLENGULFING` - Engulfing Pattern
- `CDLPIERCING` - Piercing Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
