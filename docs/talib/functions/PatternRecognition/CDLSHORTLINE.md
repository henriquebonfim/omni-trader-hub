# CDLSHORTLINE - Short Line Candle

## Overview
The Short Line Candle (CDLSHORTLINE) is a single-candle pattern that represents a small price movement with a small body and small shadows, indicating low volatility and indecision.

## Category
Pattern Recognition

## Calculation
The CDLSHORTLINE function identifies short line candles:

### Short Line Criteria
- Small body relative to total range
- Small upper shadow
- Small lower shadow
- Shows low volatility and indecision

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
The Short Line Candle indicates:
- **Low Volatility**: Minimal price movement
- **Market Indecision**: Lack of conviction
- **Consolidation**: May signal consolidation phase
- **Potential Breakout**: Often precedes significant moves

## How to Use
1. **Consolidation Signal**: Look for consolidation phases
2. **Breakout Preparation**: Prepare for potential breakout
3. **Volatility Assessment**: Use for volatility analysis
4. **Range Trading**: Trade within the range

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLSHORTLINE
    TA_RetCode ret = TA_CDLSHORTLINE(
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
                // Short line candle detected
            }
        }
    }
}
```

## Trading Strategies
1. **Consolidation Trading**: Trade within range
2. **Breakout Preparation**: Prepare for breakout
3. **Volatility Trading**: Use for low volatility signals
4. **Range Trading**: Trade the range

## Advantages
- Clear consolidation signal
- Easy to identify
- Good for range trading
- Useful for volatility analysis

## Limitations
- May not provide clear direction
- Best in ranging markets
- Requires breakout confirmation
- Can be noisy in some markets

## Related Functions
- `CDLLONGLINE` - Long Line Candle
- `CDLSPINNINGTOP` - Spinning Top
- `CDLDOJI` - Doji
- `CDLHIGHWAVE` - High-Wave Candle

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
