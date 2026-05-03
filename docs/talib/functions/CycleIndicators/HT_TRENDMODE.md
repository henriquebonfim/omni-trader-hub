# HT_TRENDMODE - Hilbert Transform - Trend Mode

## Overview
The Hilbert Transform - Trend Mode (HT_TRENDMODE) is a cycle indicator that determines whether the market is in trending or ranging mode. It's part of the MESA (MESA Adaptive Moving Average) suite of indicators developed by John Ehlers.

## Category
Cycle Indicators

## Calculation
The HT_TRENDMODE function calculates a binary value (0 or 1) indicating whether the market is in trending or ranging mode.

### Output Values
- **1**: Trending mode
- **0**: Ranging/Cycle mode

### Algorithm
The function uses multiple criteria to determine trend vs cycle mode:

1. **Sine Wave Analysis**: Calculate Sine and LeadSine from DCPhase
   ```
   Sine = sin(DCPhase)
   LeadSine = sin(DCPhase + 45°)
   ```

2. **Default Assumption**: Start with trend = 1

3. **Check for Sine Wave Crossover**:
   - If Sine crosses LeadSine (either direction), reset daysInTrend = 0 and set trend = 0

4. **Check Days in Trend**:
   - If daysInTrend < 0.5 × smoothPeriod, set trend = 0

5. **Check Phase Change Rate**:
   - Calculate Delta Phase = DCPhase - Previous DCPhase
   - If Delta Phase is within expected range for the cycle period, set trend = 0

6. **Check Price Deviation from Trendline**:
   - If |Price - Trendline| / Trendline >= 0.015 (1.5%), set trend = 1

**Note**: The function returns a binary indicator, not a continuous value. It uses sine wave crossovers and phase analysis to distinguish between trending markets (where directional strategies work) and cycling markets (where oscillating strategies work).

## Parameters
- **Input**: Price data (typically close prices)
- **Output**: Trend mode array (0.0 to 1.0)

## What It Means
The HT_TRENDMODE indicates the market mode:
- **1.0 (Trending)**: Market is in a clear trend
- **0.0 (Ranging)**: Market is in a ranging/consolidation phase
- **Intermediate Values**: Mixed or transitioning modes

## How to Use
1. **Mode Identification**: Use to identify current market mode
2. **Strategy Selection**: Choose appropriate trading strategy based on mode
3. **Filter Signals**: Filter other indicators based on market mode
4. **Risk Management**: Adjust position sizing based on market mode

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate HT_TRENDMODE
    TA_RetCode ret = TA_HT_TRENDMODE(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        trendmode           // outTrendMode
    );
    
    if (ret == TA_SUCCESS) {
        // Use trendmode array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (trendmode[i] > 0.8) {
                // Trending mode - use trend following strategies
            } else if (trendmode[i] < 0.2) {
                // Ranging mode - use mean reversion strategies
            } else {
                // Mixed mode - use caution
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Use trend following strategies when mode > 0.8
2. **Mean Reversion**: Use mean reversion strategies when mode < 0.2
3. **Mode Filtering**: Filter other indicators based on market mode
4. **Strategy Switching**: Switch strategies based on mode changes

## Advantages
- Provides clear market mode identification
- Helps select appropriate trading strategies
- Works well in all market conditions
- Can be combined with other indicators

## Limitations
- Requires sufficient data for accurate calculation
- May lag in fast-changing markets
- Best used in combination with other indicators
- Requires understanding of cycle analysis

## Related Functions
- `HT_DCPERIOD` - Dominant Cycle Period
- `HT_DCPHASE` - Dominant Cycle Phase
- `HT_PHASOR` - Phasor Components
- `HT_QUADRA` - Quadrature
- `HT_SINE` - Sine Wave
- `HT_TRENDLINE` - Trendline

## References
- Ehlers, J. F. (2001). "Rocket Science for Traders"
- Ehlers, J. F. (2004). "Cybernetic Analysis for Stocks and Futures"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
