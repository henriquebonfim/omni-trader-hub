# CDLEVENINGSTAR - Evening Star

## Overview
The Evening Star (CDLEVENINGSTAR) is a three-candle bearish reversal pattern that appears at the top of an uptrend. It consists of a large bullish candle, a small-bodied candle (the "star"), and a large bearish candle.

## Category
Pattern Recognition

## Calculation
The CDLEVENINGSTAR function identifies evening star patterns:

### Evening Star Criteria
- First candle: Large bullish candle
- Second candle: Small body (star) that gaps up
- Third candle: Large bearish candle that closes well into the first candle's body
- Pattern appears after uptrend

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
- **Output**: Pattern recognition array (-100 for pattern, 0 for no pattern)

## What It Means
The Evening Star indicates:
- **Bearish Reversal**: Strong downward reversal signal
- **Top Formation**: Often marks market tops
- **Momentum Shift**: Clear shift from bullish to bearish momentum
- **High Reliability**: One of the most reliable reversal patterns

## How to Use
1. **Reversal Signal**: Enter short positions after pattern completion
2. **Resistance Levels**: Most powerful at key resistance levels
3. **Volume Confirmation**: Higher volume on third candle strengthens signal
4. **Stop Loss**: Place above pattern high

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLEVENINGSTAR
    TA_RetCode ret = TA_CDLEVENINGSTAR(
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
            if (pattern[i] == -100) {
                // Evening star pattern detected
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter short at pattern completion
2. **Trend Change**: Exit long positions
3. **Resistance Trading**: Combine with resistance analysis
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
- Best at significant resistance levels

## Related Functions
- `CDLMORNINGSTAR` - Morning Star
- `CDLEVENINGDOJISTAR` - Evening Doji Star
- `CDL3BLACKCROWS` - Three Black Crows
- `CDLDARKCLOUDCOVER` - Dark Cloud Cover

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
