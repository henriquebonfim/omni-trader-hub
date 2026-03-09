# CDL3STARSINSOUTH - Three Stars in the South Pattern

## Overview
The Three Stars in the South Pattern (CDL3STARSINSOUTH) is a candlestick pattern that consists of three candles with specific characteristics. It's a bullish reversal pattern that can signal trend changes.

## Category
Pattern Recognition

## Calculation
The CDL3STARSINSOUTH function identifies three stars in the south patterns by analyzing three consecutive candles:

### Three Stars in the South Criteria
- First candle: Long black body with long lower shadow
- Second candle: Smaller black body, opens higher than first's close (within first's range), trades lower than first's close but not below first's low, closes off low (has shadow)
- Third candle: Small black marubozu (very short shadows) engulfed by second candle's range
- Pattern appears after downtrend (bullish reversal)

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
- **Output**: Pattern recognition array (100 for three stars in the south, 0 for no pattern)

## What It Means
The Three Stars in the South Pattern indicates:
- **Bullish Reversal**: Potential upward reversal after a downtrend
- **Support Test**: Shows testing of support levels
- **Buying Interest**: Indicates potential buying interest
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Reversal Signals**: Look for three stars in the south patterns at trend extremes
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDL3STARSINSOUTH
    TA_RetCode ret = TA_CDL3STARSINSOUTH(
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
                // Three stars in the south pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter long positions after three stars in the south
2. **Breakout Confirmation**: Use to confirm breakout signals
3. **Trend Change**: Look for pattern at trend change points
4. **Risk Management**: Use stop losses based on pattern size

## Advantages
- Shows potential bullish reversal
- Easy to identify visually
- Works in all timeframes
- Can be combined with other indicators

## Limitations
- May give false signals in choppy markets
- Requires confirmation from other indicators
- Best used at key support/resistance levels
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