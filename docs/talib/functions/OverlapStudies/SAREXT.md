# SAREXT - Parabolic SAR - Extended

## Overview
SAREXT (Parabolic SAR Extended) is an enhanced version of the Parabolic SAR indicator that provides additional control over the acceleration factors for both uptrends and downtrends separately.

## Category
Overlap Studies

## Calculation
SAREXT calculates the Parabolic SAR with separate controls for uptrend and downtrend acceleration:

### Formula
```
SAR(today) = SAR(yesterday) + AF × (EP - SAR(yesterday))

where:
AF = Acceleration Factor (increases with each new extreme)
EP = Extreme Point (highest high in uptrend, lowest low in downtrend)
```

### Extended Parameters
- **Start AF**: Initial acceleration factor (default: 0.02)
- **Increment AF**: AF increment per new extreme (default: 0.02)
- **Maximum AF**: Maximum acceleration factor (default: 0.20)
- **Offset On Reverse**: Offset percentage on trend reversal
- **Start AF Offset**: Starting AF on new trend
- **Max AF Offset**: Maximum AF offset

## Parameters
- **Input**: High and Low prices
- **Start AF**: Initial acceleration factor
- **Max AF**: Maximum acceleration factor
- **Output**: SAR array

## What It Means
SAREXT interpretation:
- **SAR below price**: Uptrend (bullish)
- **SAR above price**: Downtrend (bearish)
- **SAR flips**: Trend reversal signal
- **SAR distance**: Indicates trend strength

## How to Use
1. **Trend Following**: Trade in direction indicated by SAR
2. **Stop Loss**: Use SAR as trailing stop loss
3. **Trend Reversals**: Enter/exit when SAR flips
4. **Custom Parameters**: Adjust acceleration factors for different markets

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate SAREXT
    TA_RetCode ret = TA_SAREXT(
        0,                    // startIdx
        99,                   // endIdx
        high_prices,         // inHigh
        low_prices,          // inLow
        0.02,                // startValue
        0.0,                 // offsetOnReverse
        0.02,                // accelerationInitLong
        0.02,                // accelerationLong
        0.20,                // accelerationMaxLong
        0.02,                // accelerationInitShort
        0.02,                // accelerationShort
        0.20,                // accelerationMaxShort
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        sar                  // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use SAR array for analysis
        for (int i = 1; i < outNBElement; i++) {
            if (close_prices[i] > sar[i] && close_prices[i-1] <= sar[i-1]) {
                // SAR flipped to below price - buy signal
            } else if (close_prices[i] < sar[i] && close_prices[i-1] >= sar[i-1]) {
                // SAR flipped to above price - sell signal
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter positions when SAR flips
2. **Trailing Stop**: Use SAR as dynamic stop loss
3. **Trend Confirmation**: Combine with other indicators
4. **Custom Optimization**: Adjust acceleration factors for specific markets or timeframes

## Advantages
- Highly customizable with separate long/short parameters
- Can be optimized for different market conditions
- Provides both trend direction and stop loss levels
- Works well in trending markets

## Limitations
- More complex than standard SAR
- Can be over-optimized
- Performs poorly in sideways markets
- Many parameters to tune

## Related Functions
- `SAR` - Parabolic SAR
- `HT_TRENDLINE` - Hilbert Transform Trendline
- `MAMA` - MESA Adaptive Moving Average
- `EMA` - Exponential Moving Average

## References
- Wilder, J. Welles (1978). "New Concepts in Technical Trading Systems"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
