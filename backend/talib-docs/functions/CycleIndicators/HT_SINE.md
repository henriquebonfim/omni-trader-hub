# HT_SINE - Hilbert Transform - Sine Wave

## Overview
The Hilbert Transform - Sine Wave (HT_SINE) is a cycle indicator that calculates the sine component of the Hilbert Transform. It's part of the MESA (MESA Adaptive Moving Average) suite of indicators developed by John Ehlers.

## Category
Cycle Indicators

## Calculation
The HT_SINE function calculates the sine component of the Hilbert Transform, which represents the sine wave component of the cycle.

### Formula
```
Sine = sin(phase)
```

Where:
- `phase` is calculated from the in-phase and quadrature components
- `phase = arctan(quadrature / in-phase)`

## Parameters
- **Input**: Price data (typically close prices)
- **Output**: Sine component array

## What It Means
The HT_SINE represents the sine wave component of the cycle:
- **Values Range**: -1 to +1
- **Positive Values**: Indicate upward cycle phase
- **Negative Values**: Indicate downward cycle phase
- **Zero Crossings**: Often signal cycle turning points
- **Extreme Values**: Indicate cycle peaks and troughs

## How to Use
1. **Cycle Turning Points**: Look for zero crossings of the sine component
2. **Phase Analysis**: Use the sign and magnitude to assess cycle phase
3. **Trend Changes**: Combine with other Hilbert Transform indicators
4. **Cycle Strength**: Use amplitude to filter weak cycles

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate HT_SINE
    TA_RetCode ret = TA_HT_SINE(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        sine                 // outSine
    );
    
    if (ret == TA_SUCCESS) {
        // Use sine array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (sine[i] > 0.8) {
                // Near cycle peak
            } else if (sine[i] < -0.8) {
                // Near cycle trough
            } else if (sine[i] > 0) {
                // Upward cycle phase
            } else {
                // Downward cycle phase
            }
        }
    }
}
```

## Trading Strategies
1. **Zero Crossing Signals**: Enter positions when sine crosses zero
2. **Extreme Value Trading**: Trade against the cycle at extreme values
3. **Phase Following**: Follow the direction of sine momentum
4. **Cycle Filtering**: Only trade when sine amplitude is significant

## Advantages
- Provides clear cycle phase signals
- Works well in trending and ranging markets
- Can be combined with other Hilbert Transform indicators
- Offers objective cycle measurement

## Limitations
- Requires sufficient data for accurate calculation
- May be noisy in very short timeframes
- Best used in combination with other indicators
- Requires understanding of cycle analysis

## Related Functions
- `HT_DCPERIOD` - Dominant Cycle Period
- `HT_DCPHASE` - Dominant Cycle Phase
- `HT_PHASOR` - Phasor Components
- `HT_QUADRA` - Quadrature
- `HT_TRENDLINE` - Trendline
- `HT_TRENDMODE` - Trend Mode

## References
- Ehlers, J. F. (2001). "Rocket Science for Traders"
- Ehlers, J. F. (2004). "Cybernetic Analysis for Stocks and Futures"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
