# CDLUNIQUE3RIVER - Unique 3 River

## Overview
The Unique 3 River (CDLUNIQUE3RIVER) is a three-candle bullish reversal pattern that appears at the bottom of a downtrend. It consists of a bearish candle, a doji, and a bullish candle that doesn't close above the first candle's high.

## Category
Pattern Recognition

## Calculation
The CDLUNIQUE3RIVER function identifies unique 3 river patterns:

### Unique 3 River Criteria
- First candle: Large bearish candle
- Second candle: Doji that gaps down
- Third candle: Bullish candle that doesn't close above first candle's high
- Pattern appears after downtrend

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
The Unique 3 River indicates:
- **Bullish Reversal**: Potential upward reversal after downtrend
- **Bottom Formation**: Often marks market bottoms
- **Momentum Shift**: Clear shift from bearish to bullish momentum
- **High Reliability**: Strong reversal signal

## How to Use
1. **Reversal Signal**: Enter long positions after pattern completion
2. **Support Levels**: Most powerful at key support levels
3. **Volume Confirmation**: Higher volume strengthens signal
4. **Stop Loss**: Place below pattern low

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLUNIQUE3RIVER
    TA_RetCode ret = TA_CDLUNIQUE3RIVER(
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
                // Unique 3 river pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter long at pattern completion
2. **Trend Change**: Exit short positions
3. **Support Trading**: Combine with support analysis
4. **Position Sizing**: Increase position size given pattern reliability

## Advantages
- Highly reliable reversal pattern
- Clear visual identification
- Works in all timeframes
- Strong historical track record

## Limitations
- Relatively rare pattern
- Requires three candles to complete
- May have false signals without confirmation
- Best at significant support levels

## Related Functions
- `CDLMORNINGSTAR` - Morning Star
- `CDLMORNINGDOJISTAR` - Morning Doji Star
- `CDL3WHITESOLDIERS` - Three White Soldiers
- `CDLPIERCING` - Piercing Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
