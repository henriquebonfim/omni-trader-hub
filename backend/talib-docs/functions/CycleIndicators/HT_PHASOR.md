# HT_PHASOR - Hilbert Transform - Phasor Components

## Overview
The Hilbert Transform - Phasor Components (HT_PHASOR) is a cycle indicator that decomposes price data into in-phase and quadrature components using the Hilbert Transform. It's part of the MESA (MESA Adaptive Moving Average) suite of indicators developed by John Ehlers.

## Category
Cycle Indicators

## Calculation
The HT_PHASOR function calculates two components:
- **In-Phase Component (I)**: The real part of the complex phasor
- **Quadrature Component (Q)**: The imaginary part of the complex phasor

### Formula
```
I = 0.5 * (price - price[2])
Q = 0.5 * (price[1] - price[3])
```

Where:
- `price` is the current price
- `price[1]`, `price[2]`, `price[3]` are previous prices

## Parameters
- **Input**: Price data (typically close prices)
- **Output**: Two arrays - In-Phase and Quadrature components

## What It Means
The HT_PHASOR decomposes price movement into two orthogonal components:
- **In-Phase (I)**: Represents the "real" or "in-phase" component of the cycle
- **Quadrature (Q)**: Represents the "imaginary" or "quadrature" component of the cycle

Together, these components can be used to:
- Determine cycle phase
- Calculate cycle amplitude
- Identify cycle turning points
- Measure cycle strength

## How to Use
1. **Cycle Analysis**: Use I and Q components to understand the current phase of market cycles
2. **Amplitude Calculation**: Calculate cycle amplitude as √(I² + Q²)
3. **Phase Calculation**: Calculate phase as arctan(Q/I)
4. **Trend Identification**: Use the relationship between I and Q to identify trend changes

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate HT_PHASOR
    TA_RetCode ret = TA_HT_PHASOR(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        inPhase,             // outInPhase
        quadrature           // outQuadrature
    );
    
    if (ret == TA_SUCCESS) {
        // Use inPhase and quadrature arrays for analysis
        for (int i = 0; i < outNBElement; i++) {
            double amplitude = sqrt(inPhase[i] * inPhase[i] + 
                                  quadrature[i] * quadrature[i]);
            double phase = atan2(quadrature[i], inPhase[i]);
        }
    }
}
```

## Trading Strategies
1. **Cycle Phase Trading**: Enter positions when phase changes indicate cycle turning points
2. **Amplitude Filtering**: Only trade when cycle amplitude is above a threshold
3. **Trend Following**: Use the relationship between I and Q to follow trends
4. **Mean Reversion**: Trade against the cycle when amplitude is high

## Advantages
- Provides mathematical foundation for cycle analysis
- Works well in trending and ranging markets
- Can be combined with other Hilbert Transform indicators
- Offers objective cycle measurement

## Limitations
- Requires sufficient data for accurate calculation
- May be noisy in very short timeframes
- Best used in combination with other indicators
- Requires understanding of complex number theory

## Related Functions
- `HT_DCPERIOD` - Dominant Cycle Period
- `HT_DCPHASE` - Dominant Cycle Phase
- `HT_SINE` - Sine Wave
- `HT_TRENDLINE` - Trendline
- `HT_TRENDMODE` - Trend Mode
- `MAMA` - MESA Adaptive Moving Average

## References
- Ehlers, J. F. (2001). "Rocket Science for Traders"
- Ehlers, J. F. (2004). "Cybernetic Analysis for Stocks and Futures"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
