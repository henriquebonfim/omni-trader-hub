# MINMAXINDEX - Indexes of lowest and highest values over a specified period

## Overview
MINMAXINDEX returns both the index (position) of the lowest and highest values over a specified period in a single function call. It combines MININDEX and MAXINDEX functionality.

## Category
Math Operators

## Calculation
MINMAXINDEX identifies the indexes of both the minimum and maximum values:

### Formula
```
MININDEX = index of min(price[0], price[1], ..., price[period-1])
MAXINDEX = index of max(price[0], price[1], ..., price[period-1])
```

Returns the number of periods ago where the extremes occurred (0 = current period).

## Parameters
- **optInTimePeriod** (default: 30): Number of periods to look back
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]`

## Outputs
- Minimum absolute index positions: `int[]` (0-based indices into the input series)
- Maximum absolute index positions: `int[]`
  - To convert either to "periods ago": use `currentIndex - outputValue`

## What It Means
MINMAXINDEX provides:
- **Timing of Extremes**: When highs and lows occurred
- **Trend Strength**: Recent extremes suggest strong trends
- **Range Position**: Where current price is relative to recent extremes

## How to Use
1. **Trend Strength**: Low indices indicate fresh extremes (strong trend)
2. **Weakness Detection**: High indices suggest old extremes (trend weakening)
3. **Breakout Confirmation**: Indices = 0 confirm new highs/lows
4. **Range Analysis**: Compare indices to assess range position

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate MINMAXINDEX
    TA_RetCode ret = TA_MINMAXINDEX(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        30,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        minIndex,            // outMinIdx
        maxIndex             // outMaxIdx
    );
    
    if (ret == TA_SUCCESS) {
        // Use minIndex and maxIndex arrays for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (maxIndex[i] == 0) {
                // New high - potential uptrend
            }
            if (minIndex[i] == 0) {
                // New low - potential downtrend
            }
            
            if (maxIndex[i] > 20 && minIndex[i] > 20) {
                // Both extremes are old - consolidation
            }
        }
    }
}
```

## Trading Strategies
1. **Breakout Trading**: Enter when either index = 0 (new extremes)
2. **Trend Strength**: Use indices to assess trend strength
3. **Consolidation Detection**: High indices on both suggest ranging market
4. **Reversal Signals**: Divergence in indices may signal reversals

## Advantages
- Provides timing information for both extremes
- Efficient (calculates both in single pass)
- Useful for trend strength assessment
- Helps identify fresh extremes vs old extremes

## Limitations
- Doesn't provide actual values (only indices)
- Interpretation requires context
- May be less intuitive than other indicators
- Best used with complementary indicators

## Related Functions
- `MININDEX` - Index of lowest value
- `MAXINDEX` - Index of highest value
- `MINMAX` - Both lowest and highest values
- `MIN` - Lowest value over a specified period
- `MAX` - Highest value over a specified period

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
