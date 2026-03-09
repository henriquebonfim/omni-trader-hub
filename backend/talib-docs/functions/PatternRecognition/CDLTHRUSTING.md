# CDLTHRUSTING - Thrusting Pattern

## Overview
The Thrusting Pattern (CDLTHRUSTING) is a two-candle bearish continuation pattern where the second candle opens below the first candle's close but closes within the first candle's body, showing bearish weakness.

## Category
Pattern Recognition

## Calculation
The CDLTHRUSTING function identifies thrusting patterns:

### Thrusting Criteria
- First candle: Large bearish candle
- Second candle: Opens below first candle's close
- Second candle: Closes within first candle's body
- Shows bearish continuation

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
The Thrusting Pattern indicates:
- **Bearish Continuation**: Potential downward continuation
- **Weakness**: Shows inability to recover significantly
- **Resistance**: First candle's body acts as resistance
- **Confirmation Needed**: Requires bearish follow-through

## How to Use
1. **Continuation Signal**: Look for bearish continuation
2. **Resistance Trading**: Use first candle's body as resistance
3. **Confirmation**: Wait for bearish follow-through
4. **Stop Loss**: Place above pattern high

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLTHRUSTING
    TA_RetCode ret = TA_CDLTHRUSTING(
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
                // Thrusting pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Continuation Trading**: Enter short after pattern
2. **Resistance Trading**: Use as resistance level
3. **Weakness Trading**: Trade the weakness
4. **Confirmation**: Wait for bearish follow-through

## Advantages
- Clear continuation signal
- Easy to identify
- Good resistance level
- Works in downtrends

## Limitations
- Requires confirmation
- May give false signals
- Best in downtrends
- Needs bearish follow-through

## Related Functions
- `CDLINNECK` - In-Neck Pattern
- `CDLONNECK` - On-Neck Pattern
- `CDLENGULFING` - Engulfing Pattern
- `CDLHARAMI` - Harami Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
