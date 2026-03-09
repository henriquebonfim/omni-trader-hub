# BOP - Balance Of Power

## Overview
The Balance Of Power (BOP) measures the strength of buyers versus sellers by assessing the ability of each side to drive prices to an extreme level. It's calculated using the relationship between the close, open, high, and low prices.

## Category
Momentum Indicators

## Calculation
The BOP function calculates the balance between buying and selling pressure:

### Formula
```
BOP = (Close - Open) / (High - Low)
```

Where:
- **Close - Open**: Measures the strength of the close relative to the open
- **High - Low**: Represents the total range of price movement

## Parameters
- **Input**: OHLC data (Open, High, Low, Close)
- **Output**: BOP array (values range from -1 to +1)

## What It Means
The BOP indicator shows:
- **Values near +1**: Strong buying pressure (close near high)
- **Values near -1**: Strong selling pressure (close near low)
- **Values near 0**: Balance between buyers and sellers
- **Trend**: Positive values indicate bullish pressure, negative values indicate bearish pressure

## How to Use
1. **Trend Confirmation**: Use to confirm the strength of a trend
2. **Divergence**: Look for divergences between price and BOP
3. **Overbought/Oversold**: Extreme values may indicate potential reversals
4. **Zero Line**: Crossings of the zero line can signal trend changes

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate BOP
    TA_RetCode ret = TA_BOP(
        0,                    // startIdx
        99,                   // endIdx
        open_prices,          // open
        high_prices,         // high
        low_prices,          // low
        close_prices,        // close
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        bop                  // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use BOP array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (bop[i] > 0.5) {
                // Strong buying pressure
            } else if (bop[i] < -0.5) {
                // Strong selling pressure
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter trades in the direction of BOP
2. **Divergence Trading**: Trade divergences between price and BOP
3. **Zero Line Crossover**: Enter positions when BOP crosses zero
4. **Extreme Values**: Look for reversals at extreme BOP values

## Advantages
- Simple and intuitive interpretation
- Works well for intraday trading
- Can identify buying/selling pressure
- Useful for confirming trends

## Limitations
- Can give false signals in choppy markets
- Best used with other indicators
- May be noisy in low-volatility periods
- Doesn't consider volume

## Related Functions
- `MFI` - Money Flow Index
- `CCI` - Commodity Channel Index
- `RSI` - Relative Strength Index
- `ADX` - Average Directional Movement Index
- `OBV` - On Balance Volume

## References
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
