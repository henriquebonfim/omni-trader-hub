# CDLCLOSINGMARUBOZU - Closing Marubozu

## Overview
The Closing Marubozu (CDLCLOSINGMARUBOZU) is a candlestick pattern with a large body and no upper shadow, but may have a lower shadow. It shows strong closing conviction.

## Category
Pattern Recognition

## Calculation
The CDLCLOSINGMARUBOZU function identifies closing marubozu patterns:

### White Closing Marubozu (Bullish) Criteria
- Long white (bullish) body
- No or very short upper shadow
- May have lower shadow
- Closes at or near the high

### Black Closing Marubozu (Bearish) Criteria
- Long black (bearish) body
- No or very short lower shadow  
- May have upper shadow
- Closes at or near the low

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
The Closing Marubozu indicates:
- **Strong Closing**: Powerful close at the high/low
- **High Conviction**: Strong belief in direction
- **Trend Continuation**: Often continues in same direction
- **Momentum**: Shows strong closing momentum

## How to Use
1. **Trend Following**: Enter in direction of marubozu
2. **Momentum Trading**: Use for momentum confirmation
3. **Breakout Trading**: Enter on breakout
4. **Volume Confirmation**: Higher volume strengthens signal

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLCLOSINGMARUBOZU
    TA_RetCode ret = TA_CDLCLOSINGMARUBOZU(
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
                // Bullish closing marubozu
            } else if (pattern[i] == -100) {
                // Bearish closing marubozu
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Follow the direction
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
- `CDLLONGLINE` - Long Line Candle
- `CDLSPINNINGTOP` - Spinning Top
- `CDLDOJI` - Doji

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
