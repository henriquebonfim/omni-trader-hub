# WCLPRICE - Weighted Close Price

## Overview
The Weighted Close Price (WCLPRICE) calculates a weighted average that emphasizes the close price, giving it double the weight of the high and low prices. It provides a price representation that prioritizes the closing value.

## Category
Price Transform

## Calculation
The WCLPRICE function calculates a weighted average with emphasis on the close:

### Formula
```
Weighted Close Price = (High + Low + Close + Close) / 4
                     = (High + Low + 2 × Close) / 4
```

## Parameters
- **Input**: HLC data (High, Low, Close)
- **Output**: Weighted close price array

## What It Means
The Weighted Close Price represents:
- **Close Emphasis**: Gives double weight to the closing price
- **Price Balance**: Balances high, low, and close with emphasis on close
- **Market Sentiment**: Reflects the importance of where price closes
- **Smoothing**: Provides a smoothed representation of price movement

## How to Use
1. **Trend Analysis**: Use as a smoothed price reference
2. **Support/Resistance**: Identify key levels using weighted close price
3. **Comparison**: Compare with other price transforms
4. **Indicator Input**: Use as input for other technical indicators

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate WCLPRICE
    TA_RetCode ret = TA_WCLPRICE(
        0,                    // startIdx
        99,                   // endIdx
        high_prices,         // high
        low_prices,          // low
        close_prices,        // close
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        wclPrice             // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use wclPrice array for analysis
        for (int i = 0; i < outNBElement; i++) {
            printf("Weighted Close Price: %.2f\n", wclPrice[i]);
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Use as a baseline for trend identification
2. **Mean Reversion**: Trade when price deviates from weighted close
3. **Support/Resistance**: Use as dynamic support/resistance levels
4. **Indicator Input**: Use as input for moving averages and oscillators

## Advantages
- Emphasizes the close price (most important for many traders)
- Simple calculation
- Useful for smoothing price data
- Can be used as input for other indicators

## Limitations
- Arbitrary weighting scheme
- May not be suitable for all market conditions
- Simpler than more sophisticated price transforms
- Does not consider open price

## Related Functions
- `TYPPRICE` - Typical Price
- `MEDPRICE` - Median Price
- `AVGPRICE` - Average Price
- `SMA` - Simple Moving Average
- `EMA` - Exponential Moving Average

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
