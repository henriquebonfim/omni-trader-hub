# TSF - Time Series Forecast

## Overview
Time Series Forecast (TSF) extends the linear regression line one period into the future. It projects where price is expected to be based on the current trend.

## Category
Statistic Functions

## Calculation
TSF calculates the forecasted value by extending the linear regression line:

### Formula
```
TSF = Intercept + Slope × (period + 1)

where:
Intercept = linear regression intercept
Slope = linear regression slope
period = current time period
```

## Parameters
- **optInTimePeriod** (default: 14): Number of periods for calculation
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- Forecasted price values: `double[]`

## What It Means
The Time Series Forecast represents:
- **Price Projection**: Expected price based on current trend
- **Trend Extension**: Where the trend line projects to next period
- **Target Price**: Statistical target for price movement
- **Trend Strength**: Distance from current price indicates trend strength

## How to Use
1. **Price Targets**: Use as a target price for next period
2. **Trend Following**: Enter in direction of TSF relative to current price
3. **Deviation Analysis**: Measure how far current price deviates from forecast
4. **Trend Confirmation**: Rising TSF confirms uptrend, falling TSF confirms downtrend

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate TSF
    TA_RetCode ret = TA_TSF(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        14,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        tsf                  // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use TSF array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (tsf[i] > close_prices[i]) {
                // Forecast above current price - bullish
            } else {
                // Forecast below current price - bearish
            }
            
            double deviation = (close_prices[i] - tsf[i]) / tsf[i];
            if (fabs(deviation) > 0.05) {
                // Price deviates significantly from forecast
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter positions toward the TSF direction
2. **Price Targets**: Use TSF as profit target
3. **Mean Reversion**: Trade when price significantly deviates from TSF
4. **Breakout**: Look for price breaking through TSF levels

## Advantages
- Provides forward-looking price projection
- Statistically derived and objective
- Useful for setting price targets
- Works well in trending markets

## Limitations
- Assumes trend will continue (may not in reversals)
- Lags in fast-moving markets
- Less accurate in choppy conditions
- One-period forecast may not be sufficient

## Related Functions
- `LINEARREG` - Linear Regression
- `LINEARREG_ANGLE` - Linear Regression Angle
- `LINEARREG_INTERCEPT` - Linear Regression Intercept
- `LINEARREG_SLOPE` - Linear Regression Slope
- `EMA` - Exponential Moving Average

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
