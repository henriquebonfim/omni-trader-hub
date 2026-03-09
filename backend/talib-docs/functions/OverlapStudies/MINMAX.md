# MINMAX - Lowest and highest values over a specified period

## Overview
MINMAX returns both the lowest and highest values over a specified period in a single function call. It's a convenience function that combines MIN and MAX.

## Category
Math Operators

## Calculation
MINMAX identifies both the minimum and maximum values within the specified period:

### Formula
```
MIN = min(price[0], price[1], ..., price[period-1])
MAX = max(price[0], price[1], ..., price[period-1])
```

## Parameters
- **optInTimePeriod** (default: 30): Number of periods to look back
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]`

## Outputs
- Minimum values: `double[]`
- Maximum values: `double[]`

## What It Means
MINMAX provides:
- **Range**: The difference between MAX and MIN shows price range
- **Support**: MIN acts as support level
- **Resistance**: MAX acts as resistance level
- **Volatility**: Large range indicates high volatility

## How to Use
1. **Range Trading**: Trade between MIN (support) and MAX (resistance)
2. **Breakout Trading**: Enter when price breaks above MAX or below MIN
3. **Volatility Assessment**: Use range for volatility measurement
4. **Channel Construction**: Use MIN and MAX as channel boundaries

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate MINMAX
    TA_RetCode ret = TA_MINMAX(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        30,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        min,                 // outMin
        max                  // outMax
    );
    
    if (ret == TA_SUCCESS) {
        // Use min and max arrays for analysis
        for (int i = 0; i < outNBElement; i++) {
            double range = max[i] - min[i];
            double midpoint = (max[i] + min[i]) / 2.0;
            
            if (close_prices[i] > max[i]) {
                // Breakout above range
            } else if (close_prices[i] < min[i]) {
                // Breakdown below range
            } else if (close_prices[i] > midpoint) {
                // Upper half of range
            }
        }
    }
}
```

## Trading Strategies
1. **Range Trading**: Buy near MIN, sell near MAX
2. **Breakout Trading**: Enter when price breaks out of range
3. **Mean Reversion**: Trade from extremes toward midpoint
4. **Channel Trading**: Use MIN/MAX as dynamic channel boundaries

## Advantages
- Provides both support and resistance in one call
- Efficient (calculates both in single pass)
- Useful for range and channel trading
- Clear support/resistance levels

## Limitations
- Doesn't indicate timing of extremes
- May lag in trending markets
- Best suited for ranging markets
- Doesn't consider volume

## Related Functions
- `MIN` - Lowest value over a specified period
- `MAX` - Highest value over a specified period
- `MININDEX` - Index of lowest value
- `MAXINDEX` - Index of highest value
- `MINMAXINDEX` - Indexes of both lowest and highest values

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
