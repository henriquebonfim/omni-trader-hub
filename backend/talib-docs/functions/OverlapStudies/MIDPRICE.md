# MIDPRICE - Midpoint Price over period

## Overview
The Midpoint Price calculates the average of the highest high and lowest low over a specified period. It's similar to MIDPOINT but specifically uses high and low prices rather than a single price series.

## Category
Overlap Studies

## Calculation
The MIDPRICE function calculates the midpoint of the high-low range over the specified period:

### Formula
```
MidPrice = (Highest High + Lowest Low) / 2
```

Over the specified time period.

## Parameters
- **optInTimePeriod** (default: 14): Number of periods for calculation
  - Valid range: 2 to 100000

## Inputs
- High prices: `double[]`
- Low prices: `double[]`

## Outputs
- Midprice values: `double[]`

## What It Means
The MidPrice represents:
- **Central Tendency**: Shows the middle of the high-low range over the period
- **Support/Resistance**: Can act as dynamic support or resistance
- **Price Balance**: Indicates the equilibrium point of price extremes
- **Trend Reference**: Provides a reference line for trend analysis

## How to Use
1. **Trend Identification**: Price above midprice suggests uptrend, below suggests downtrend
2. **Support/Resistance**: Use as dynamic support/resistance levels
3. **Mean Reversion**: Trade when price deviates significantly from midprice
4. **Breakout**: Look for price breaking through the midprice

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate MIDPRICE
    TA_RetCode ret = TA_MIDPRICE(
        0,                    // startIdx
        99,                   // endIdx
        high_prices,         // inHigh
        low_prices,          // inLow
        14,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        midprice             // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use midprice array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (close_prices[i] > midprice[i]) {
                // Price above midprice - bullish
            } else {
                // Price below midprice - bearish
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter positions when price crosses the midprice
2. **Mean Reversion**: Trade against extremes back to the midprice
3. **Support/Resistance**: Use midprice as dynamic levels
4. **Range Trading**: Trade between high, low, and midprice

## Advantages
- Simple and intuitive calculation
- Uses high and low prices (captures full range)
- Provides clear support/resistance levels
- Works well in ranging markets

## Limitations
- Lags in trending markets
- May give false signals in choppy conditions
- Doesn't consider volume or momentum
- Best used with other indicators

## Related Functions
- `MIDPOINT` - MidPoint over period
- `MAX` - Highest value over a specified period
- `MIN` - Lowest value over a specified period
- `MEDPRICE` - Median Price
- `SAR` - Parabolic SAR

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
