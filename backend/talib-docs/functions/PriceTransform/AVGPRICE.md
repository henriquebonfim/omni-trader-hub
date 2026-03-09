# AVGPRICE - Average Price

## Overview
The Average Price (AVGPRICE) calculates the average of the open, high, low, and close prices for each period. It provides a simple representation of the typical price for a period.

## Category
Price Transform

## Calculation
The AVGPRICE function calculates the average of all four price values:

### Formula
```
Average Price = (Open + High + Low + Close) / 4
```

## Parameters
- **Input**: OHLC data (Open, High, Low, Close)
- **Output**: Average price array

## What It Means
The Average Price represents:
- **Central Tendency**: Shows the central point of the price range
- **Price Balance**: Balances all four price components equally
- **Smoothing**: Provides a smoothed representation of price movement
- **Support/Resistance**: Can act as a reference for support and resistance levels

## How to Use
1. **Trend Analysis**: Use as a smoothed price reference
2. **Support/Resistance**: Identify key levels using average price
3. **Comparison**: Compare with other price transforms (typical, weighted, median)
4. **Indicator Input**: Use as input for other technical indicators

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate AVGPRICE
    TA_RetCode ret = TA_AVGPRICE(
        0,                    // startIdx
        99,                   // endIdx
        open_prices,          // open
        high_prices,         // high
        low_prices,          // low
        close_prices,        // close
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        avgPrice             // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use avgPrice array for analysis
        for (int i = 0; i < outNBElement; i++) {
            printf("Average Price: %.2f\n", avgPrice[i]);
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Use as a baseline for trend identification
2. **Mean Reversion**: Trade when price deviates from average
3. **Support/Resistance**: Use as dynamic support/resistance levels
4. **Indicator Input**: Use as input for moving averages and oscillators

## Advantages
- Simple and intuitive calculation
- Balances all four price components
- Useful for smoothing price data
- Can be used as input for other indicators

## Limitations
- Weights all price components equally (may not reflect importance)
- Provides less information than OHLC individually
- May not be suitable for all market conditions
- Simpler than more sophisticated price transforms

## Related Functions
- `TYPPRICE` - Typical Price
- `MEDPRICE` - Median Price
- `WCLPRICE` - Weighted Close Price
- `SMA` - Simple Moving Average
- `EMA` - Exponential Moving Average

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
