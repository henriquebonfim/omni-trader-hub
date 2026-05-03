# CDLABANDONEDBABY - Abandoned Baby

## Overview
The Abandoned Baby (CDLABANDONEDBABY) is a three-candle reversal pattern that can be either bullish or bearish. It consists of a large candle, a doji that gaps away, and another large candle in the opposite direction.

## Category
Pattern Recognition

## Calculation
The CDLABANDONEDBABY function identifies abandoned baby patterns:

### Bullish Abandoned Baby Criteria
- First candle: Long black (bearish) body
- Second candle: Doji with upside gap (shadows don't touch first candle)
- Third candle: White (bullish) body with downside gap from doji (shadows don't touch), closes well within first candle's body

### Bearish Abandoned Baby Criteria
- First candle: Long white (bullish) body
- Second candle: Doji with downside gap (shadows don't touch first candle)
- Third candle: Black (bearish) body with upside gap from doji (shadows don't touch), closes well within first candle's body

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
- **Output**: Pattern recognition array (100 for bullish, -100 for bearish, 0 for no pattern)

## What It Means
The Abandoned Baby indicates:
- **Bullish Abandoned Baby**: Strong upward reversal after downtrend
- **Bearish Abandoned Baby**: Strong downward reversal after uptrend
- **Market Exhaustion**: Shows trend exhaustion and reversal
- **High Reliability**: Very strong reversal signal

## How to Use
1. **Reversal Signal**: Look for abandoned baby at trend extremes
2. **Volume Confirmation**: Higher volume strengthens signal
3. **Context Analysis**: Consider market conditions
4. **Follow-through**: Wait for pattern completion

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLABANDONEDBABY
    TA_RetCode ret = TA_CDLABANDONEDBABY(
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
                // Bullish abandoned baby
            } else if (pattern[i] == -100) {
                // Bearish abandoned baby
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter opposite to previous trend
2. **Exhaustion Trading**: Trade trend exhaustion
3. **Major Levels**: Use at significant support/resistance
4. **Position Sizing**: Increase size given reliability

## Advantages
- Very high reliability
- Clear exhaustion signal
- Works at major levels
- Strong reversal indicator

## Limitations
- Very rare pattern
- Requires three candles
- May have false signals
- Best at significant levels

## Related Functions
- `CDLMORNINGSTAR` - Morning Star
- `CDLEVENINGSTAR` - Evening Star
- `CDLDOJI` - Doji
- `CDLSTAR` - Star patterns

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
