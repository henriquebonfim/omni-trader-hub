# CDLMORNINGDOJISTAR - Morning Doji Star

## Overview
The Morning Doji Star (CDLMORNINGDOJISTAR) is a three-candle bullish reversal pattern similar to the Morning Star, but with a doji as the middle candle. This pattern is considered even more reliable than the regular Morning Star.

## Category
Pattern Recognition

## Calculation
The CDLMORNINGDOJISTAR function identifies morning doji star patterns:

### Morning Doji Star Criteria
- First candle: Large bearish candle
- Second candle: Doji that gaps down
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
The Morning Doji Star indicates:
- **Strong Bullish Reversal**: Very strong upward reversal signal
- **Market Indecision**: Doji shows equilibrium before reversal
- **Bottom Formation**: Often marks significant market bottoms
- **Very High Reliability**: More reliable than regular Morning Star

## How to Use
1. **Reversal Signal**: Enter long positions after pattern completion
2. **Support Levels**: Most powerful at key support levels
3. **Volume**: Higher volume strengthens signal
4. **Stop Loss**: Place below pattern low

## Usage Example
\`\`\`c
#include "ta_libc.h"

int main() {
    // Calculate CDLMORNINGDOJISTAR
    TA_RetCode ret = TA_CDLMORNINGDOJISTAR(
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
                // Morning doji star pattern
            }
        }
    }
}
\`\`\`

## Trading Strategies
1. **Reversal Trading**: Enter long at completion
2. **High Confidence**: Larger positions given reliability
3. **Support Trading**: Combined with support analysis
4. **Risk Management**: Tight stops below pattern low

## Advantages
- Very high reliability
- Clear indecision signal (doji)
- Strong reversal indicator
- Works in all timeframes

## Limitations
- Rare pattern
- Requires confirmation
- Three candles needed
- Best at key support levels

## Related Functions
- `CDLMORNINGSTAR` - Morning Star
- `CDLEVENINGDOJISTAR` - Evening Doji Star
- `CDLDOJI` - Doji
- `CDLPIERCING` - Piercing Pattern

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
