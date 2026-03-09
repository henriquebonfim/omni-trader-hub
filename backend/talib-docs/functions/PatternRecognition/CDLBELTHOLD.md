# CDLBELTHOLD - Belt-hold

## Overview
The Belt-hold (CDLBELTHOLD) is a single-candle pattern that can be either bullish or bearish. It has a large body with no shadow on one side, showing strong directional conviction.

## Category
Pattern Recognition

## Calculation
The CDLBELTHOLD function identifies belt-hold patterns:

### Bullish Belt-hold Criteria
- Long white (bullish) body
- No or very short lower shadow
- May have upper shadow

### Bearish Belt-hold Criteria  
- Long black (bearish) body
- No or very short upper shadow
- May have lower shadow

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
The Belt-hold indicates:
- **Bullish Belt-hold**: Strong upward conviction
- **Bearish Belt-hold**: Strong downward conviction
- **High Conviction**: Strong belief in direction
- **Trend Continuation**: Often continues in same direction

## How to Use
1. **Trend Following**: Enter in direction of belt-hold
2. **Momentum Trading**: Use for momentum confirmation
3. **Breakout Trading**: Enter on breakout
4. **Volume Confirmation**: Higher volume strengthens signal

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLBELTHOLD
    TA_RetCode ret = TA_CDLBELTHOLD(
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
                // Bullish belt-hold
            } else if (pattern[i] == -100) {
                // Bearish belt-hold
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
