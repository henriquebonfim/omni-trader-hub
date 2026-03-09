# MIDPOINT - MidPoint over period

## Overview
The MidPoint calculates the midpoint (average) of the highest and lowest values over a specified period. It provides a simple representation of the central tendency of price over time.

## Category
Overlap Studies

## Calculation
The MIDPOINT function calculates the midpoint of the range over the specified period:

### Formula
```
MidPoint = (Highest Value + Lowest Value) / 2
```

Over the specified time period.

## Parameters
- **optInTimePeriod** (default: 14): Number of periods for calculation
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]`

## Outputs
- Midpoint values: `double[]`

## What It Means
The MidPoint represents:
- **Central Tendency**: Shows the middle of the price range over the period
- **Support/Resistance**: Can act as dynamic support or resistance
- **Price Balance**: Indicates the equilibrium point of price over time
- **Trend Reference**: Provides a reference line for trend analysis

## How to Use
1. **Trend Identification**: Price above midpoint suggests uptrend, below suggests downtrend
2. **Support/Resistance**: Use as dynamic support/resistance levels
3. **Mean Reversion**: Trade when price deviates significantly from midpoint
4. **Breakout**: Look for price breaking through the midpoint

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate MIDPOINT
    TA_RetCode ret = TA_MIDPOINT(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        14,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        midpoint             // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use midpoint array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (close_prices[i] > midpoint[i]) {
                // Price above midpoint - bullish
            } else {
                // Price below midpoint - bearish
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter positions when price crosses the midpoint
2. **Mean Reversion**: Trade against extremes back to the midpoint
3. **Support/Resistance**: Use midpoint as dynamic levels
4. **Range Trading**: Trade between high, low, and midpoint

## Advantages
- Simple and intuitive calculation
- Provides clear support/resistance levels
- Works well in ranging markets
- Useful for mean reversion strategies

## Limitations
- Lags in trending markets
- May give false signals in choppy conditions
- Doesn't consider volume or momentum
- Best used with other indicators

## Related Functions
- `MIDPRICE` - Midpoint Price over period
- `MAX` - Highest value over a specified period
- `MIN` - Lowest value over a specified period
- `MEDPRICE` - Median Price
- `SMA` - Simple Moving Average

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
