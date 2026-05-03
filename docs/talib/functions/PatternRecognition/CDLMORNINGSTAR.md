# CDLMORNINGSTAR - Morning Star

## Overview
The Morning Star (CDLMORNINGSTAR) is a three-candle bullish reversal pattern that appears at the bottom of a downtrend. It consists of a large bearish candle, a small-bodied candle (the "star"), and a large bullish candle.

## Category
Pattern Recognition

## Calculation
The CDLMORNINGSTAR function identifies morning star patterns:

### Morning Star Criteria
- First candle: Large bearish candle
- Second candle: Small body (star) that gaps down
- Third candle: Large bullish candle that closes well into the first candle's body
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
- **Penetration**: How far third candle must close into first candle (default: 0.3 = 30%)
- **Output**: Pattern recognition array (100 for pattern, 0 for no pattern)

## What It Means
The Morning Star indicates:
- **Bullish Reversal**: Strong upward reversal signal
- **Bottom Formation**: Often marks market bottoms
- **Momentum Shift**: Clear shift from bearish to bullish momentum
- **High Reliability**: One of the most reliable reversal patterns

## How to Use
1. **Reversal Signal**: Enter long positions after pattern completion
2. **Support Levels**: Most powerful at key support levels
3. **Volume Confirmation**: Higher volume on third candle strengthens signal
4. **Stop Loss**: Place below pattern low

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLMORNINGSTAR
    TA_RetCode ret = TA_CDLMORNINGSTAR(
        0,                    // startIdx
        99,                   // endIdx
        open_prices,          // open
        high_prices,         // high
        low_prices,          // low
        close_prices,        // close
        0.3,                 // penetration
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        pattern              // outInteger
    );
    
    if (ret == TA_SUCCESS) {
        for (int i = 0; i < outNBElement; i++) {
            if (pattern[i] == 100) {
                // Morning star pattern detected
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
- `CDLEVENINGSTAR` - Evening Star
- `CDLMORNINGDOJISTAR` - Morning Doji Star
- `CDL3WHITESOLDIERS` - Three White Soldiers
- `CDLPIERCING` - Piercing Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
