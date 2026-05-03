# CDLLONGLINE - Long Line Candle

## Overview
The Long Line Candle (CDLLONGLINE) is a single-candle pattern that represents a strong directional move with a large body and small shadows, indicating strong conviction in one direction.

## Category
Pattern Recognition

## Calculation
The CDLLONGLINE function identifies long line candles:

### Long Line Criteria
- Large body relative to total range
- Small or no upper shadow
- Small or no lower shadow
- Shows strong directional conviction

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
- **Output**: Pattern recognition array (100 for bullish, -100 for bearish, 0 for no pattern)

## What It Means
The Long Line Candle indicates:
- **Strong Direction**: Powerful move in one direction
- **High Conviction**: Strong belief in price direction
- **Trend Continuation**: Often continues in same direction
- **Momentum**: Shows strong momentum

## How to Use
1. **Trend Following**: Enter in direction of long line
2. **Momentum Trading**: Use for momentum confirmation
3. **Breakout Trading**: Enter on breakout long lines
4. **Volume Confirmation**: Higher volume strengthens signal

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLLONGLINE
    TA_RetCode ret = TA_CDLLONGLINE(
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
                // Bullish long line
            } else if (pattern[i] == -100) {
                // Bearish long line
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Follow the direction of long line
2. **Momentum Trading**: Use for momentum confirmation
3. **Breakout Trading**: Enter on breakout
4. **Continuation Trading**: Expect continuation

## Advantages
- Clear directional signal
- Strong conviction indicator
- Easy to identify
- Good for momentum trading

## Limitations
- May be late signal
- Can give false signals in choppy markets
- Best in trending markets
- Requires volume confirmation

## Related Functions
- `CDLMARUBOZU` - Marubozu
- `CDLSHORTLINE` - Short Line Candle
- `CDLSPINNINGTOP` - Spinning Top
- `CDLDOJI` - Doji

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
