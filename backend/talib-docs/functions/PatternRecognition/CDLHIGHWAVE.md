# CDLHIGHWAVE - High-Wave Candle

## Overview
The High-Wave Candle (CDLHIGHWAVE) is a single-candle pattern that indicates market indecision. It has a small body with long upper and lower shadows, showing that both buyers and sellers were active.

## Category
Pattern Recognition

## Calculation
The CDLHIGHWAVE function identifies high-wave candles:

### High-Wave Criteria
- Small body relative to total range
- Long upper shadow
- Long lower shadow
- Shows high volatility and indecision

## Implementation Note

**This pattern uses TA-Lib's adaptive threshold system** for determining candle characteristics like "long body", "short body", "doji", etc. These thresholds automatically adjust based on recent market behavior rather than using fixed percentages.

For detailed information about:
- How adaptive thresholds work
- Configuring pattern detection sensitivity  
- Understanding output values
- Technical implementation details

See: [Candlestick Pattern Recognition Overview](CANDLESTICK_PATTERNS_OVERVIEW.md)


## Parameters
- **Input**: OHLC data (Open, High, Low, Close)
- **Output**: Pattern recognition array (100 for pattern, 0 for no pattern)

## What It Means
The High-Wave Candle indicates:
- **Market Indecision**: Strong uncertainty between buyers and sellers
- **High Volatility**: Significant price movement in both directions
- **Potential Reversal**: Often appears at trend extremes
- **Consolidation**: May signal consolidation phase

## How to Use
1. **Indecision Signal**: Look for high-wave candles at extremes
2. **Volume Analysis**: Combine with volume for confirmation
3. **Context**: Consider preceding trend
4. **Follow-through**: Wait for next candle direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLHIGHWAVE
    TA_RetCode ret = TA_CDLHIGHWAVE(
        0,                    // startIdx
        99,                   // endIdx
        open_prices,          // open
        high_prices,         // high
        low_prices,          // low
        close_prices,        // close
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        pattern              // outInteger
    );
    
    if (ret == TA_SUCCESS) {
        for (int i = 0; i < outNBElement; i++) {
            if (pattern[i] == 100) {
                // High-wave candle detected
            }
        }
    }
}
```

## Trading Strategies
1. **Indecision Trading**: Wait for breakout from indecision
2. **Reversal Trading**: Look for reversal after high-wave
3. **Volatility Trading**: Use for volatility assessment
4. **Consolidation**: Trade range after high-wave

## Advantages
- Clear indecision signal
- Easy to identify
- Shows market uncertainty
- Good for volatility analysis

## Limitations
- Requires confirmation
- May not provide clear direction
- Best used with other indicators
- Can be noisy in some markets

## Related Functions
- `CDLSPINNINGTOP` - Spinning Top
- `CDLDOJI` - Doji
- `CDLLONGLEGGEDDOJI` - Long Legged Doji
- `CDLHAMMER` - Hammer

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
