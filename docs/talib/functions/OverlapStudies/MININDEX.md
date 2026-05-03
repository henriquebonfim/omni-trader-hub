# MININDEX - Index of lowest value over a specified period

## Overview
MININDEX returns the index (position) of the lowest value over a specified period. Unlike MIN which returns the value itself, MININDEX tells you when (how many periods ago) the minimum occurred.

## Category
Math Operators

## Calculation
MININDEX identifies the index of the minimum value within the specified period:

### Formula
```
MININDEX = index of min(price[0], price[1], ..., price[period-1])
```

Returns the number of periods ago where the minimum value occurred (0 = current period).

## Parameters
- **optInTimePeriod** (default: 30): Number of periods to look back
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]`

## Outputs
- Absolute index positions: `int[]` (0-based indices into the input series)
  - To convert to "periods ago": use `currentIndex - outputValue`

## What It Means
MININDEX indicates:
- **Low Index (near 0)**: Recent low (minimum is recent)
- **High Index (near period)**: Old low (minimum was long ago)
- **Index = 0**: Current period is the lowest
- **Index = period-1**: The low is at the beginning of the period

## How to Use
1. **Trough Identification**: Identify when troughs occurred
2. **Trend Strength**: Recent minima (low index) suggest strong downtrend
3. **Strength Detection**: Old minima (high index) suggest downtrend weakness
4. **Breakout Confirmation**: Index = 0 confirms new lows being made

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate MININDEX
    TA_RetCode ret = TA_MININDEX(
        0,                    // startIdx
        99,                   // endIdx
        low_prices,          // inReal
        30,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        minIndex             // outInteger
    );
    
    if (ret == TA_SUCCESS) {
        // Use minIndex array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (minIndex[i] == 0) {
                // New low - strong downtrend
            } else if (minIndex[i] > 20) {
                // Low is old - potential downtrend weakening
            }
        }
    }
}
```

## Trading Strategies
1. **Breakdown Trading**: Exit when index = 0 (new lows)
2. **Trend Strength**: Use low indices to confirm trend strength
3. **Reversal Signals**: High indices may signal potential reversals
4. **Support/Resistance**: Combine with MAXINDEX for range identification

## Advantages
- Identifies timing of extremes
- Useful for trend strength assessment
- Complements MIN function
- Helps identify fresh lows vs old lows

## Limitations
- Doesn't provide the actual value (only index)
- Interpretation requires context
- May be less intuitive than other indicators
- Best used with other indicators

## Related Functions
- `MIN` - Lowest value over a specified period
- `MAXINDEX` - Index of highest value over a specified period
- `MAX` - Highest value over a specified period
- `MINMAXINDEX` - Indexes of both lowest and highest values
- `MINMAX` - Both lowest and highest values

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
