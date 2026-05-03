# CDL3INSIDE - Three Inside Pattern

## Overview
The Three Inside Pattern (CDL3INSIDE) is a candlestick reversal pattern. Three Inside Up is bullish (harami pattern followed by confirmation), and Three Inside Down is bearish (bearish harami followed by confirmation).

## Category
Pattern Recognition

## Calculation
The CDL3INSIDE function identifies three inside patterns by analyzing three consecutive candles:

### Three Inside Up (Bullish) Criteria
- First candle: Long black (bearish) body
- Second candle: Short body engulfed by first candle (harami pattern)
- Third candle: White (bullish) candle that closes higher than first candle's open

### Three Inside Down (Bearish) Criteria
- First candle: Long white (bullish) body
- Second candle: Short body engulfed by first candle (harami pattern)
- Third candle: Black (bearish) candle that closes lower than first candle's open

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
The Three Inside Pattern indicates:
- **Bullish Three Inside**: Potential upward continuation or reversal
- **Bearish Three Inside**: Potential downward continuation or reversal
- **Consolidation**: Shows market consolidation
- **Confirmation**: Should be confirmed by other indicators

## How to Use
1. **Consolidation Signals**: Look for three inside patterns in consolidating markets
2. **Volume Confirmation**: Confirm with volume analysis
3. **Support/Resistance**: Use at key support/resistance levels
4. **Trend Context**: Consider the overall trend direction

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDL3INSIDE
    TA_RetCode ret = TA_CDL3INSIDE(
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
                // Bullish three inside pattern
            } else if (pattern[i] == -100) {
                // Bearish three inside pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Consolidation Trading**: Enter positions after consolidation
2. **Breakout Confirmation**: Use to confirm breakout signals
3. **Trend Continuation**: Look for pattern in trending markets
4. **Risk Management**: Use stop losses based on pattern size

## Advantages
- Shows market consolidation
- Easy to identify visually
- Works in all timeframes
- Can be combined with other indicators

## Limitations
- May give false signals in choppy markets
- Requires confirmation from other indicators
- Best used in consolidating markets
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
