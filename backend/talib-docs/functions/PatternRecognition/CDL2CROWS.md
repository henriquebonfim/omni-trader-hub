# CDL2CROWS - Two Crows

## Overview
The Two Crows pattern (CDL2CROWS) is a three-candle bearish reversal pattern that appears at the top of an uptrend. It signals potential trend reversal from bullish to bearish.

## Category
Pattern Recognition

## Calculation
The CDL2CROWS function identifies two crows patterns:

### Two Crows Criteria
- First candle: Strong bullish candle (white/green)
- Second candle: Bearish candle that gaps up but closes within first candle's body
- Third candle: Bearish candle that opens within second candle's body and closes within first candle's body
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
The Two Crows Pattern indicates:
- **Bearish Reversal**: Potential downward reversal after uptrend
- **Weakening Bulls**: Despite gap up, bears take control
- **Top Formation**: Often marks market tops
- **Confirmation Needed**: Should be confirmed by other indicators

## How to Use
1. **Reversal Signal**: Look for two crows at trend tops
2. **Volume Confirmation**: Confirm with increasing volume
3. **Resistance Levels**: Use at key resistance levels
4. **Risk Management**: Set stop losses above pattern high

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDL2CROWS
    TA_RetCode ret = TA_CDL2CROWS(
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
                // Two crows pattern detected
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter short positions after pattern
2. **Trend Change**: Exit long positions
3. **Confirmation**: Wait for next candle confirmation
4. **Stop Loss**: Place above pattern high

## Advantages
- Clear visual pattern
- Strong reversal signal
- Works in all timeframes
- Well-documented pattern

## Limitations
- Relatively rare pattern
- Requires confirmation
- May give false signals
- Best at significant resistance levels

## Related Functions
- `CDL3BLACKCROWS` - Three Black Crows
- `CDLEVENINGSTAR` - Evening Star
- `CDLDARKCLOUDCOVER` - Dark Cloud Cover
- `CDLENGULFING` - Engulfing Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
