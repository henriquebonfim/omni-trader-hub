# CDLCONCEALBABYSWALL - Concealing Baby Swallow

## Overview
The Concealing Baby Swallow (CDLCONCEALBABYSWALL) is a four-candle bearish reversal pattern that appears at the top of an uptrend. It consists of four bearish candles with specific characteristics.

## Category
Pattern Recognition

## Calculation
The CDLCONCEALBABYSWALL function identifies concealing baby swallow patterns:

### Concealing Baby Swallow Criteria
- First candle: Black marubozu (very short shadows)
- Second candle: Black marubozu (very short shadows)
- Third candle: Black candle that opens gapping down, has upper shadow extending into prior body
- Fourth candle: Black candle that completely engulfs third candle, including shadows
- Pattern appears in downtrend (bullish reversal)

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
The Concealing Baby Swallow indicates:
- **Bearish Reversal**: Strong downward reversal after uptrend
- **Top Formation**: Often marks market tops
- **Momentum Shift**: Clear shift from bullish to bearish momentum
- **High Reliability**: Strong reversal signal

## How to Use
1. **Reversal Signal**: Enter short positions after pattern completion
2. **Resistance Levels**: Most powerful at key resistance levels
3. **Volume Confirmation**: Higher volume strengthens signal
4. **Stop Loss**: Place above pattern high

## Usage Example
\`\`\`c
#include "ta_libc.h"

int main() {
    // Calculate CDLCONCEALBABYSWALL
    TA_RetCode ret = TA_CDLCONCEALBABYSWALL(
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
                // Concealing baby swallow pattern
            }
        }
    }
}
\`\`\`

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
- Requires four candles to complete
- May have false signals without confirmation
- Best at significant resistance levels

## Related Functions
- `CDLEVENINGSTAR` - Evening Star
- `CDL3BLACKCROWS` - Three Black Crows
- `CDLDARKCLOUDCOVER` - Dark Cloud Cover
- `CDLENGULFING` - Engulfing Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
