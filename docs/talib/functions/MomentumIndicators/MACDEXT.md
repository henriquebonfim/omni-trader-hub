# MACDEXT - MACD with controllable MA type

## Overview
MACDEXT (MACD Extended) is an enhanced version of the MACD indicator that allows you to specify the type of moving average to use for each component. This provides greater flexibility compared to the standard MACD which uses only exponential moving averages.

## Category
Momentum Indicators

## Calculation
MACDEXT calculates MACD using customizable moving average types:

### Formula
```
MACD Line = MA_Fast(price) - MA_Slow(price)
Signal Line = MA_Signal(MACD Line)
Histogram = MACD Line - Signal Line

where MA can be:
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- WMA (Weighted Moving Average)
- DEMA, TEMA, TRIMA, KAMA, MAMA, T3, etc.
```

## Parameters
- **optInFastPeriod** (default: 12): Period for fast MA
  - Valid range: 2 to 100000
- **optInFastMAType** (default: EMA): MA type for fast line
  - Valid range: 0 to 8
- **optInSlowPeriod** (default: 26): Period for slow MA
  - Valid range: 2 to 100000
- **optInSlowMAType** (default: EMA): MA type for slow line
  - Valid range: 0 to 8
- **optInSignalPeriod** (default: 9): Period for signal line
  - Valid range: 1 to 100000
- **optInSignalMAType** (default: SMA): MA type for signal line
  - Valid range: 0 to 8

## Inputs
- Price data: `double[]`

## Outputs
- MACD line, Signal line, Histogram: `double[]`, `double[]`, `double[]`

## What It Means
MACDEXT interpretation depends on the MA types chosen, but generally:
- **MACD > 0**: Bullish momentum
- **MACD < 0**: Bearish momentum
- **MACD crosses above Signal**: Bullish signal
- **MACD crosses below Signal**: Bearish signal
- **Histogram expanding**: Increasing momentum
- **Histogram contracting**: Decreasing momentum

## How to Use
1. **MA Type Selection**: Choose MA types based on market conditions
2. **Signal Line Crossovers**: Look for MACD/signal line crosses
3. **Zero Line Crossovers**: Monitor MACD crossing zero
4. **Divergences**: Compare MACD with price for divergences
5. **Histogram Analysis**: Monitor histogram for momentum changes

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate MACDEXT
    TA_RetCode ret = TA_MACDEXT(
        0,                    // startIdx
        99,                   // endIdx
        close_prices,         // inReal
        12,                   // fastPeriod
        TA_MAType_EMA,       // fastMAType
        26,                   // slowPeriod
        TA_MAType_EMA,       // slowMAType
        9,                    // signalPeriod
        TA_MAType_SMA,       // signalMAType
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
5. **Custom MA Combinations**: Experiment with different MA types for different markets

## Advantages
- Highly customizable with different MA types
- Can be optimized for different market conditions
- Provides flexibility standard MACD lacks
- Useful for testing different MA combinations

## Limitations
- More complex than standard MACD
- Requires understanding of different MA types
- Can be over-optimized
- May give false signals in choppy markets

## Related Functions
- `MACD` - Moving Average Convergence/Divergence
- `MACDFIX` - MACD Fix 12/26
- `PPO` - Percentage Price Oscillator
- `APO` - Absolute Price Oscillator
- `EMA` - Exponential Moving Average

## References
- Appel, Gerald (1979). "The Moving Average Convergence-Divergence Method"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
