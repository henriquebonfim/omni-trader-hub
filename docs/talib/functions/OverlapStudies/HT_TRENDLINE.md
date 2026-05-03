# HT_TRENDLINE - Hilbert Transform - Trendline

## Overview
The Hilbert Transform - Trendline (HT_TRENDLINE) is a cycle indicator that calculates a trendline based on the Hilbert Transform. It's part of the MESA (MESA Adaptive Moving Average) suite of indicators developed by John Ehlers.

## Category
Cycle Indicators

## Calculation
The HT_TRENDLINE function calculates an adaptive trendline using Hilbert Transform to identify the dominant cycle period and then smooth price over that cycle.

### Steps
1. **Smooth Price**: Apply 4-period WMA to input price
2. **Apply Hilbert Transform**: Calculate detrender, I and Q components, period
3. **Calculate Dominant Cycle Period (DCP)**: From Hilbert Transform analysis
4. **Average Price over DCP**: Calculate mean price over dominant cycle period
5. **Calculate ITrend**: Weighted average of current and previous trend values

### Formula
```
PeriodAvg = Mean(Price, Dominant Cycle Period)
Trendline = (4.0×PeriodAvg + 3.0×ITrend[1] + 2.0×ITrend[2] + ITrend[3]) / 10.0
```

Where:
- `PeriodAvg` = Average price over the dominant cycle period
- `ITrend[1]` = Previous trendline value
- `ITrend[2]` = Trendline 2 bars ago
- `ITrend[3]` = Trendline 3 bars ago

**Note**: The trendline uses a weighted moving average that emphasizes recent cycle-based averages, providing smooth adaptive trend following.

## Parameters
- **Input**: Price data (typically close prices)
- **Output**: Trendline array

## What It Means
The HT_TRENDLINE represents an adaptive trendline that:
- **Adapts to Cycle**: Changes with the dominant cycle period
- **Smooths Price**: Provides a smoothed representation of price movement
- **Trend Direction**: Indicates the overall trend direction
- **Support/Resistance**: Can act as dynamic support or resistance

## How to Use
1. **Trend Identification**: Use the trendline to identify overall trend direction
2. **Support/Resistance**: Use as dynamic support or resistance levels
3. **Entry/Exit Signals**: Enter positions when price crosses the trendline
4. **Trend Changes**: Look for trendline slope changes

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate HT_TRENDLINE
    TA_RetCode ret = TA_HT_TRENDLINE(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        trendline            // outTrendline
    );
    
    if (ret == TA_SUCCESS) {
        // Use trendline array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (close_prices[i] > trendline[i]) {
                // Price above trendline - bullish
            } else if (close_prices[i] < trendline[i]) {
                // Price below trendline - bearish
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter positions in the direction of the trendline
2. **Mean Reversion**: Trade against the trendline when price deviates significantly
3. **Breakout Trading**: Enter positions when price breaks through the trendline
4. **Trend Confirmation**: Use with other indicators for trend confirmation

## Advantages
- Adapts to changing market cycles
- Provides clear trend signals
- Works well in trending markets
- Can be combined with other Hilbert Transform indicators

## Limitations
- Requires sufficient data for accurate calculation
- May lag in fast-moving markets
- Best used in combination with other indicators
- Requires understanding of cycle analysis

## Related Functions
- `HT_DCPERIOD` - Dominant Cycle Period
- `HT_DCPHASE` - Dominant Cycle Phase
- `HT_PHASOR` - Phasor Components
- `HT_SINE` - Sine Wave
- `HT_TRENDMODE` - Trend Mode

## References
- Ehlers, J. F. (2001). "Rocket Science for Traders"
- Ehlers, J. F. (2004). "Cybernetic Analysis for Stocks and Futures"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
