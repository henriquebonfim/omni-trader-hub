# MACDFIX - Moving Average Convergence/Divergence Fix 12/26

## Overview
MACDFIX is a fixed-parameter version of the MACD indicator with the standard 12/26/9 periods. It's designed for quick calculation without the need to specify parameters.

## Category
Momentum Indicators

## Calculation
MACDFIX uses fixed periods for calculation:

### Formula
```
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(9) of MACD Line
Histogram = MACD Line - Signal Line
```

Where:
- **Fast EMA**: 12-period exponential moving average
- **Slow EMA**: 26-period exponential moving average
- **Signal**: 9-period EMA of the MACD line

## Parameters
- **optInSignalPeriod** (default: 9): Signal line period
  - Valid range: 1 to 100000

## Inputs
- Price data: `double[]`

## Outputs
- MACD line, Signal line, Histogram: `double[]`, `double[]`, `double[]`

## What It Means
MACDFIX interpretation:
- **MACD > 0**: Bullish momentum (12 EMA above 26 EMA)
- **MACD < 0**: Bearish momentum (12 EMA below 26 EMA)
- **MACD crosses above Signal**: Bullish signal
- **MACD crosses below Signal**: Bearish signal
- **Histogram expanding**: Increasing momentum
- **Histogram contracting**: Decreasing momentum

## How to Use
1. **Signal Line Crossovers**: Look for MACD/signal line crosses
2. **Zero Line Crossovers**: Monitor MACD crossing zero
3. **Divergences**: Compare MACD with price for divergences
4. **Histogram Analysis**: Monitor histogram for momentum changes

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate MACDFIX
    TA_RetCode ret = TA_MACDFIX(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        9,                    // signalPeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        macd,                // outMACD
        signal,              // outMACDSignal
        histogram            // outMACDHist
    );
    
    if (ret == TA_SUCCESS) {
        // Use MACD arrays for analysis
        for (int i = 1; i < outNBElement; i++) {
            if (macd[i] > signal[i] && macd[i-1] <= signal[i-1]) {
                // Bullish crossover
            } else if (macd[i] < signal[i] && macd[i-1] >= signal[i-1]) {
                // Bearish crossover
            }
        }
    }
}
```

## Trading Strategies
1. **Crossover Trading**: Enter on MACD/signal crossovers
2. **Trend Following**: Trade in direction of MACD
3. **Divergence Trading**: Look for price/MACD divergences
4. **Zero Line Trading**: Enter when MACD crosses zero
5. **Histogram Trading**: Enter when histogram changes direction

## Advantages
- Standard industry parameters
- Simple to use (minimal parameterization)
- Well-tested and widely accepted
- Fast calculation

## Limitations
- Fixed parameters may not suit all markets
- Less flexible than MACD or MACDEXT
- May lag in fast-moving markets
- Can give false signals in choppy markets

## Related Functions
- `MACD` - Moving Average Convergence/Divergence
- `MACDEXT` - MACD with controllable MA type
- `PPO` - Percentage Price Oscillator
- `APO` - Absolute Price Oscillator
- `EMA` - Exponential Moving Average

## References
- Appel, Gerald (1979). "The Moving Average Convergence-Divergence Method"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
