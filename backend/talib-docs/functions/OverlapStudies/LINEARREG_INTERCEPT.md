# LINEARREG_INTERCEPT - Linear Regression Intercept

## Overview
Linear Regression Intercept calculates the y-intercept of the linear regression line. It represents where the regression line crosses the y-axis.

## Category
Statistic Functions

## Calculation
Linear Regression Intercept calculates the intercept of the best-fit line:

### Formula
```
Intercept = ȳ - slope × x̄

where:
ȳ = mean of y values (prices)
x̄ = mean of x values (time)
slope = linear regression slope
```

## Parameters
- **optInTimePeriod** (default: 14): Number of periods for calculation
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- Intercept values: `double[]`

## What It Means
The Linear Regression Intercept represents:
- **Starting Point**: Where the regression line begins
- **Baseline Value**: The theoretical price at time zero
- **Trend Context**: Combined with slope, defines the complete regression line
- **Price Level**: Provides context for price positioning

## How to Use
1. **Trend Analysis**: Combine with slope to understand full trend
2. **Price Levels**: Use as reference for price positioning
3. **Trend Changes**: Monitor changes in intercept over time
4. **Channel Construction**: Use with standard deviation for channels

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate LINEARREG_INTERCEPT
    TA_RetCode ret = TA_LINEARREG_INTERCEPT(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        14,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        intercept            // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use intercept array for analysis
        // Typically combined with slope and other regression functions
        for (int i = 0; i < outNBElement; i++) {
            printf("Intercept: %.2f\n", intercept[i]);
        }
    }
}
```

## Trading Strategies
1. **Trend Analysis**: Combine with slope for complete trend picture
2. **Channel Trading**: Use with standard deviation for channel construction
3. **Support/Resistance**: Use as dynamic support/resistance levels
4. **Price Forecasting**: Combine with slope to project future prices

## Advantages
- Part of complete linear regression analysis
- Statistically derived and objective
- Useful for trend analysis
- Can be combined with other regression indicators

## Limitations
- Less intuitive than other regression outputs
- Best used in combination with slope
- Lags in fast-moving markets
- Most useful as a component of broader analysis

## Related Functions
- `LINEARREG` - Linear Regression
- `LINEARREG_ANGLE` - Linear Regression Angle
- `LINEARREG_SLOPE` - Linear Regression Slope
- `TSF` - Time Series Forecast
- `STDDEV` - Standard Deviation

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
