# MAXINDEX - Index of highest value over a specified period

## Overview
MAXINDEX returns the index (position) of the highest value over a specified period. Unlike MAX which returns the value itself, MAXINDEX tells you when (how many periods ago) the maximum occurred.

## Category
Math Operators

## Calculation
MAXINDEX identifies the index of the maximum value within the specified period:

### Formula
```
MAXINDEX = index of max(price[0], price[1], ..., price[period-1])
```

Returns the number of periods ago where the maximum value occurred (0 = current period).

## Parameters
- **optInTimePeriod** (default: 30): Number of periods to look back
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]`

## Outputs
- Absolute index positions: `int[]` (0-based indices into the input series)
  - To convert to "periods ago": use `currentIndex - outputValue`

## What It Means
MAXINDEX indicates:
- **Low Index (near 0)**: Recent high (maximum is recent)
- **High Index (near period)**: Old high (maximum was long ago)
- **Index = 0**: Current period is the highest
- **Index = period-1**: The high is at the beginning of the period

## How to Use
1. **Peak Identification**: Identify when peaks occurred
2. **Trend Strength**: Recent maxima (low index) suggest strong uptrend
3. **Weakness Detection**: Old maxima (high index) suggest trend weakness
4. **Breakout Confirmation**: Index = 0 confirms new highs being made

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate MAXINDEX
    TA_RetCode ret = TA_MAXINDEX(
        0,                    // startIdx
        99,                   // endIdx
        high_prices,         // inReal
        30,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        maxIndex             // outInteger
    );
    
    if (ret == TA_SUCCESS) {
        // Use maxIndex array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (maxIndex[i] == 0) {
                // New high - strong uptrend
            } else if (maxIndex[i] > 20) {
                // High is old - potential trend weakening
            }
        }
    }
}
```

## Trading Strategies
1. **Breakout Trading**: Enter when index = 0 (new highs)
2. **Trend Strength**: Use low indices to confirm trend strength
3. **Reversal Signals**: High indices may signal potential reversals
4. **Support/Resistance**: Combine with MININDEX for range identification

## Advantages
- Identifies timing of extremes
- Useful for trend strength assessment
- Complements MAX function
- Helps identify fresh highs vs old highs

## Limitations
- Doesn't provide the actual value (only index)
- Interpretation requires context
- May be less intuitive than other indicators
- Best used with other indicators

## Related Functions
- `MAX` - Highest value over a specified period
- `MININDEX` - Index of lowest value over a specified period
- `MIN` - Lowest value over a specified period
- `MINMAXINDEX` - Indexes of both lowest and highest values
- `MINMAX` - Both lowest and highest values

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
