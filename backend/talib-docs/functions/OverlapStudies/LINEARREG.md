# LINEARREG - Linear Regression

## Overview
Linear Regression fits a straight line to price data over a specified period using the least squares method. It provides a statistically derived trendline that minimizes the distance between the line and the data points.

## Category
Statistic Functions

## Calculation
Linear Regression calculates the best-fit line through the price data:

### Formula
```
y = a + b × x

where:
b (slope) = Σ((x - x̄)(y - ȳ)) / Σ((x - x̄)²)
a (intercept) = ȳ - b × x̄
```

The output is the value of the regression line at the current point.

## Parameters
- **optInTimePeriod** (default: 14): Number of periods for calculation
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- Linear regression line values: `double[]`

## What It Means
The Linear Regression line represents:
- **Trend Direction**: Shows the overall trend direction
- **Statistical Trendline**: Objectively determined trendline
- **Support/Resistance**: Can act as dynamic support or resistance
- **Price Prediction**: Projects where price "should" be based on the trend

## How to Use
1. **Trend Identification**: Use the slope of the line to identify trend direction
2. **Support/Resistance**: Use as dynamic support/resistance levels
3. **Deviation Analysis**: Measure how far price deviates from the regression line
4. **Trend Strength**: Steeper slopes indicate stronger trends

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate LINEARREG
    TA_RetCode ret = TA_LINEARREG(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        14,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        linearReg            // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use linearReg array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (close_prices[i] > linearReg[i]) {
                // Price above regression line - bullish
            } else {
                // Price below regression line - bearish
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter positions in the direction of the regression line
2. **Mean Reversion**: Trade when price deviates significantly from the line
3. **Breakout**: Look for price breaking through the regression line
4. **Channel Trading**: Combine with standard deviation bands for channels

## Advantages
- Statistically derived and objective
- Removes subjectivity from trendline drawing
- Works well in trending markets
- Can be combined with other regression indicators

## Limitations
- Lags in fast-moving markets
- Assumes linear relationship (may not always be appropriate)
- Best used in trending markets
- Can give false signals in choppy conditions

## Related Functions
- `LINEARREG_ANGLE` - Linear Regression Angle
- `LINEARREG_INTERCEPT` - Linear Regression Intercept
- `LINEARREG_SLOPE` - Linear Regression Slope
- `TSF` - Time Series Forecast
- `STDDEV` - Standard Deviation

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
