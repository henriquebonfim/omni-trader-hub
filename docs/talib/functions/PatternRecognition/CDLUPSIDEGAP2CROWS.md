# CDLUPSIDEGAP2CROWS - Upside Gap Two Crows

## Overview
The Upside Gap Two Crows (CDLUPSIDEGAP2CROWS) is a three-candle bearish reversal pattern that appears at the top of an uptrend. It consists of a large bullish candle, a bearish candle that gaps up, and another bearish candle.

## Category
Pattern Recognition

## Calculation
The CDLUPSIDEGAP2CROWS function identifies upside gap two crows patterns:

### Upside Gap Two Crows Criteria
- First candle: Large bullish candle
- Second candle: Bearish candle that gaps up
- Third candle: Bearish candle that opens within second candle's body
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
- **Output**: Pattern recognition array (-100 for pattern, 0 for no pattern)

## What It Means
The Upside Gap Two Crows indicates:
- **Bearish Reversal**: Potential downward reversal after uptrend
- **Top Formation**: Often marks market tops
- **Momentum Shift**: Clear shift from bullish to bearish momentum
- **High Reliability**: Strong reversal signal

## How to Use
1. **Reversal Signal**: Enter short positions after pattern completion
2. **Resistance Levels**: Most powerful at key resistance levels
3. **Volume Confirmation**: Higher volume strengthens signal
4. **Stop Loss**: Place above pattern high

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLUPSIDEGAP2CROWS
    TA_RetCode ret = TA_CDLUPSIDEGAP2CROWS(
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
            if (pattern[i] == -100) {
                // Upside gap two crows pattern
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
- `CDLEVENINGSTAR` - Evening Star
- `CDLEVENINGDOJISTAR` - Evening Doji Star
- `CDL3BLACKCROWS` - Three Black Crows
- `CDLDARKCLOUDCOVER` - Dark Cloud Cover

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
