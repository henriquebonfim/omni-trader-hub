# CDL3BLACKCROWS - Three Black Crows Pattern

## Overview
The Three Black Crows Pattern (CDL3BLACKCROWS) is a candlestick pattern that consists of three consecutive bearish candles with similar characteristics. It's a strong bearish continuation pattern that can signal trend continuation.

## Category
Pattern Recognition

## Calculation
The CDL3BLACKCROWS function identifies three black crows patterns by analyzing three consecutive candles:

### Three Black Crows Criteria
- Prior candle: Bullish (white) candle
- First black candle: Bearish with very short lower shadow, closes below prior white candle's high
- Second black candle: Bearish with very short lower shadow, opens within first black's body
- Third black candle: Bearish with very short lower shadow, opens within second black's body
- Three consecutive declining closes (each closes lower than previous)

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
- **Output**: Pattern recognition array (100 for three black crows, 0 for no pattern)

## What It Means
The Three Black Crows Pattern indicates:
- **Bearish Continuation**: Strong downward continuation
- **Selling Pressure**: Shows persistent selling interest
- **Trend Strength**: Indicates strong bearish momentum
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Continuation Signals**: Look for three black crows in downtrends
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDL3BLACKCROWS
    TA_RetCode ret = TA_CDL3BLACKCROWS(
        0,                    // startIdx
        99,                   // endIdx
        open_prices,          // open
        high_prices,         // high
        low_prices,          // low
        close_prices,        // close
        &outBegIdx,          // outBegIdx
        &outNBElement,      // outNBElement
        pattern              // outInteger
    );
    
    if (ret == TA_SUCCESS) {
        // Use pattern array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (pattern[i] == 100) {
                // Three black crows pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter short positions in downtrends
2. **Breakout Confirmation**: Use to confirm breakout signals
3. **Trend Continuation**: Look for pattern in trending markets
4. **Risk Management**: Use stop losses based on pattern size

## Advantages
- Shows strong bearish continuation
- Easy to identify visually
- Works in all timeframes
- Can be combined with other indicators

## Limitations
- May give false signals in choppy markets
- Requires confirmation from other indicators
- Best used in trending markets
- May lag in fast-moving markets

## Related Functions
- `CDLHAMMER` - Hammer Pattern
- `CDLDOJI` - Doji Pattern
- `CDLENGULFING` - Engulfing Pattern
- `CDLHARAMI` - Harami Pattern
- `CDLSPINNINGTOP` - Spinning Top Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
