# LINEARREG_ANGLE - Linear Regression Angle

## Overview
Linear Regression Angle calculates the angle (in degrees) of the linear regression line. It provides a measure of the steepness and direction of the trend.

## Category
Statistic Functions

## Calculation
Linear Regression Angle calculates the angle of the best-fit line:

### Formula
```
Angle = arctan(slope) × (180 / π)

where slope is the linear regression slope
```

The angle is expressed in degrees from -90 to +90.

## Parameters
- **optInTimePeriod** (default: 14): Number of periods for calculation
  - Valid range: 2 to 100000

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- Angle values in degrees: `double[]`

## What It Means
The Linear Regression Angle represents:
- **Positive Angles**: Uptrend (0° to +90°)
- **Negative Angles**: Downtrend (-90° to 0°)
- **Angle near 0°**: Sideways/flat trend
- **Steep Angles**: Strong trend (|angle| > 45°)
- **Shallow Angles**: Weak trend (|angle| < 15°)

## How to Use
1. **Trend Strength**: Higher absolute angles indicate stronger trends
2. **Trend Direction**: Positive/negative angles indicate up/downtrends
3. **Trend Changes**: Look for angle reversals
4. **Filtering**: Only trade when angle exceeds a threshold

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate LINEARREG_ANGLE
    TA_RetCode ret = TA_LINEARREG_ANGLE(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        14,                   // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        angle                // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use angle array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (angle[i] > 45) {
                // Strong uptrend
            } else if (angle[i] < -45) {
                // Strong downtrend
            } else if (fabs(angle[i]) < 15) {
                // Weak trend / sideways
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Strength Filter**: Only trade when angle exceeds threshold
2. **Trend Following**: Enter in direction of angle
3. **Angle Reversals**: Look for angle changing direction
4. **Momentum Confirmation**: Combine with momentum indicators

## Advantages
- Intuitive measurement of trend strength
- Easy to interpret (degrees)
- Objective and systematic
- Useful for filtering weak trends

## Limitations
- Lags in fast-moving markets
- Sensitive to period selection
- May give false signals in choppy conditions
- Best used with other indicators

## Related Functions
- `LINEARREG` - Linear Regression
- `LINEARREG_INTERCEPT` - Linear Regression Intercept
- `LINEARREG_SLOPE` - Linear Regression Slope
- `TSF` - Time Series Forecast
- `ADX` - Average Directional Movement Index

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
