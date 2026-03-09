# MA - All Moving Average

## Overview
MA (Moving Average) is a versatile function that can calculate any type of moving average supported by TA-Lib. It provides a single interface to access all moving average types.

## Category
Overlap Studies

## Calculation
MA calculates the specified type of moving average:

### Available MA Types
- **SMA**: Simple Moving Average
- **EMA**: Exponential Moving Average
- **WMA**: Weighted Moving Average
- **DEMA**: Double Exponential Moving Average
- **TEMA**: Triple Exponential Moving Average
- **TRIMA**: Triangular Moving Average
- **KAMA**: Kaufman Adaptive Moving Average
- **MAMA**: MESA Adaptive Moving Average
- **T3**: Triple Exponential Moving Average (T3)

## Parameters
- **optInTimePeriod** (default: 30): Number of periods for calculation
  - Valid range: 1 to 100000
- **optInMAType** (default: SMA): Type of moving average
  - Valid range: 0 to 8
  - Options: SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, T3

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- Moving average values: `double[]`

## What It Means
The interpretation depends on the MA type selected, but generally:
- **Price > MA**: Bullish trend
- **Price < MA**: Bearish trend
- **MA slope up**: Uptrend
- **MA slope down**: Downtrend
- **MA crossovers**: Trend changes

## How to Use
1. **Trend Identification**: Use to identify overall trend direction
2. **Support/Resistance**: MA acts as dynamic support/resistance
3. **Crossovers**: Look for price or MA crossovers
4. **MA Type Selection**: Choose MA type based on market conditions

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate MA (EMA example)
    TA_RetCode ret = TA_MA(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        20,                   // timePeriod
        TA_MAType_EMA,       // maType
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        ma                   // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use MA array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (close_prices[i] > ma[i]) {
                // Price above MA - bullish
            } else {
                // Price below MA - bearish
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter positions in direction of MA
2. **MA Crossovers**: Trade when price crosses MA
3. **Multiple MAs**: Use multiple periods for confirmation
4. **Support/Resistance**: Use MA as dynamic levels
5. **MA Type Optimization**: Test different MA types for different markets

## Advantages
- Single interface for all MA types
- Highly flexible and customizable
- Allows easy comparison of different MA types
- Well-tested and reliable

## Limitations
- Requires understanding of different MA types
- Performance varies by MA type and market condition
- Can lag in fast-moving markets
- May give false signals in choppy markets

## Related Functions
- `SMA` - Simple Moving Average
- `EMA` - Exponential Moving Average
- `WMA` - Weighted Moving Average
- `DEMA` - Double Exponential Moving Average
- `TEMA` - Triple Exponential Moving Average
- `TRIMA` - Triangular Moving Average
- `KAMA` - Kaufman Adaptive Moving Average
- `T3` - Triple Exponential Moving Average (T3)

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
