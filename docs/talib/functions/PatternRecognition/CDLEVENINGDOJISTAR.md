# CDLEVENINGDOJISTAR - Evening Doji Star

## Overview
The Evening Doji Star (CDLEVENINGDOJISTAR) is a three-candle bearish reversal pattern similar to the Evening Star, but with a doji as the middle candle. This pattern is considered even more reliable than the regular Evening Star.

## Category
Pattern Recognition

## Calculation
The CDLEVENINGDOJISTAR function identifies evening doji star patterns:

### Evening Doji Star Criteria
- First candle: Large bullish candle
- Second candle: Doji that gaps up
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
The Evening Doji Star indicates:
- **Strong Bearish Reversal**: Very strong downward reversal signal
- **Market Indecision**: Doji shows equilibrium before reversal
- **Top Formation**: Often marks significant market tops
- **Very High Reliability**: More reliable than regular Evening Star

## How to Use
1. **Reversal Signal**: Enter short positions after pattern completion
2. **Resistance Levels**: Most powerful at key resistance levels
3. **Volume**: Higher volume strengthens signal
4. **Stop Loss**: Place above pattern high

## Usage Example
\`\`\`c
#include "ta_libc.h"

int main() {
    // Calculate CDLEVENINGDOJISTAR
    TA_RetCode ret = TA_CDLEVENINGDOJISTAR(
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
                // Evening doji star pattern
            }
        }
    }
}
\`\`\`

## Trading Strategies
1. **Reversal Trading**: Enter short at completion
2. **High Confidence**: Larger positions given reliability
3. **Resistance Trading**: Combined with resistance analysis
4. **Risk Management**: Tight stops above pattern high

## Advantages
- Very high reliability
- Clear indecision signal (doji)
- Strong reversal indicator
- Works in all timeframes

## Limitations
- Rare pattern
- Requires confirmation
- Three candles needed
- Best at key resistance levels

## Related Functions
- `CDLEVENINGSTAR` - Evening Star
- `CDLMORNINGDOJISTAR` - Morning Doji Star
- `CDLDOJI` - Doji
- `CDLDARKCLOUDCOVER` - Dark Cloud Cover

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
