# CDL3WHITESOLDIERS - Three White Soldiers Pattern

## Overview
The Three White Soldiers Pattern (CDL3WHITESOLDIERS) is a candlestick pattern that consists of three consecutive bullish candles with similar characteristics. It's a strong bullish continuation pattern that can signal trend continuation.

## Category
Pattern Recognition

## Calculation
The CDL3WHITESOLDIERS function identifies three white soldiers patterns by analyzing three consecutive candles:

### Three White Soldiers Criteria
- First white candle: Bullish with very short upper shadow
- Second white candle: Bullish with very short upper shadow, opens within or near first's body
- Third white candle: Bullish with very short upper shadow, opens within or near second's body
- Three consecutive higher closes (each closes higher than previous)
- Each candle not far shorter than the previous (avoids "advance block" pattern)

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
- **Output**: Pattern recognition array (100 for three white soldiers, 0 for no pattern)

## What It Means
The Three White Soldiers Pattern indicates:
- **Bullish Continuation**: Strong upward continuation
- **Buying Pressure**: Shows persistent buying interest
- **Trend Strength**: Indicates strong bullish momentum
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Continuation Signals**: Look for three white soldiers in uptrends
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDL3WHITESOLDIERS
    TA_RetCode ret = TA_CDL3WHITESOLDIERS(
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
                // Three white soldiers pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Trend Following**: Enter long positions in uptrends
2. **Breakout Confirmation**: Use to confirm breakout signals
3. **Trend Continuation**: Look for pattern in trending markets
4. **Risk Management**: Use stop losses based on pattern size

## Advantages
- Shows strong bullish continuation
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
