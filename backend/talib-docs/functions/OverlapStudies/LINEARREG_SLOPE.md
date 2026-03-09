# LINEARREG_SLOPE - Linear Regression Slope

## Overview
Linear Regression Slope calculates the slope of the linear regression line. It measures the rate of change of the trend over the specified period.

## Category
Statistic Functions

## Calculation
Linear Regression Slope calculates the slope of the best-fit line:

### Formula
```
Slope = Σ((x - x̄)(y - ȳ)) / Σ((x - x̄)²)

where:
x = time period
y = price
x̄ = mean of time periods
ȳ = mean of prices
```

## Parameters
- **optInTimePeriod** (default: 14): Number of periods for calculation
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- Slope values: `double[]`

## What It Means
The Linear Regression Slope represents:
- **Positive Slope**: Uptrend (rising prices)
- **Negative Slope**: Downtrend (falling prices)
- **Slope near 0**: Sideways/flat trend
- **Large Absolute Slope**: Strong trend
- **Small Absolute Slope**: Weak trend

## How to Use
1. **Trend Direction**: Positive/negative slope indicates up/downtrend
2. **Trend Strength**: Larger absolute slopes indicate stronger trends
3. **Trend Changes**: Look for slope reversals
4. **Rate of Change**: Measures how fast prices are changing

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate LINEARREG_SLOPE
    TA_RetCode ret = TA_LINEARREG_SLOPE(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        14,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        slope                // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use slope array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (slope[i] > 0.5) {
                // Strong uptrend
            } else if (slope[i] < -0.5) {
                // Strong downtrend
            } else if (fabs(slope[i]) < 0.1) {
                // Weak trend / sideways
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter in direction of slope
2. **Trend Strength Filter**: Only trade when slope exceeds threshold
3. **Slope Reversals**: Look for slope changing direction
4. **Divergence**: Compare slope with price action for divergences

## Advantages
- Direct measurement of trend strength
- Statistically derived and objective
- Easy to interpret
- Useful for filtering weak trends

## Limitations
- Lags in fast-moving markets
- Sensitive to period selection
- May give false signals in choppy conditions
- Best used with other indicators

## Related Functions
- `LINEARREG` - Linear Regression
- `LINEARREG_ANGLE` - Linear Regression Angle
- `LINEARREG_INTERCEPT` - Linear Regression Intercept
- `TSF` - Time Series Forecast
- `MOM` - Momentum

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
