# CDLXSIDEGAP3METHODS - Upside/Downside Gap Three Methods

## Overview
The Upside/Downside Gap Three Methods (CDLXSIDEGAP3METHODS) is a five-candle continuation pattern that can be either bullish or bearish. It shows a gap followed by three small candles in the opposite direction, then a gap in the original direction.

## Category
Pattern Recognition

## Calculation
The CDLXSIDEGAP3METHODS function identifies gap three methods patterns:

### Gap Three Methods Criteria
- First candle: Large candle in one direction
- Second candle: Gaps in same direction
- Third, fourth, fifth candles: Small candles in opposite direction
- Sixth candle: Gaps back in original direction
- Shows continuation of original trend

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
The Gap Three Methods indicates:
- **Bullish Continuation**: Strong upward continuation after consolidation
- **Bearish Continuation**: Strong downward continuation after consolidation
- **Trend Strength**: Shows strong underlying trend
- **High Reliability**: Strong continuation signal

## How to Use
1. **Continuation Signal**: Enter in direction of original trend
2. **Trend Strength**: Use to confirm trend strength
3. **Volume Confirmation**: Higher volume strengthens signal
4. **Stop Loss**: Place beyond the gap

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLXSIDEGAP3METHODS
    TA_RetCode ret = TA_CDLXSIDEGAP3METHODS(
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
                // Bullish gap three methods
            } else if (pattern[i] == -100) {
                // Bearish gap three methods
            }
        }
    }
}
```

## Trading Strategies
1. **Continuation Trading**: Enter in direction of original trend
2. **Trend Following**: Use to confirm trend strength
3. **Gap Trading**: Trade the gap continuation
4. **Position Sizing**: Increase position size given pattern reliability

## Advantages
- Highly reliable continuation pattern
- Clear visual identification
- Works in all timeframes
- Strong historical track record

## Limitations
- Requires six candles to complete
- Relatively rare pattern
- May have false signals without confirmation
- Best in strong trending markets

## Related Functions
- `CDL3WHITESOLDIERS` - Three White Soldiers
- `CDL3BLACKCROWS` - Three Black Crows
- `CDLENGULFING` - Engulfing Pattern
- `CDLMARUBOZU` - Marubozu

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
