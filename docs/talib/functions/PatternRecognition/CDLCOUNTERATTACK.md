# CDLCOUNTERATTACK - Counterattack

## Overview
The Counterattack (CDLCOUNTERATTACK) is a two-candle reversal pattern that can be either bullish or bearish. It consists of two candles with the same close price but opposite directions.

## Category
Pattern Recognition

## Calculation
The CDLCOUNTERATTACK function identifies counterattack patterns:

### Bullish Counterattack Criteria
- First candle: Long black (bearish) body
- Second candle: Long white (bullish) body with close equal to first candle's close

### Bearish Counterattack Criteria
- First candle: Long white (bullish) body
- Second candle: Long black (bearish) body with close equal to first candle's close

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
The Counterattack indicates:
- **Bullish Counterattack**: Potential upward reversal
- **Bearish Counterattack**: Potential downward reversal
- **Market Equilibrium**: Shows balance between buyers and sellers
- **Reversal Signal**: Potential trend change

## How to Use
1. **Reversal Signal**: Look for counterattack at trend extremes
2. **Equilibrium Trading**: Trade the breakout from equilibrium
3. **Volume Confirmation**: Higher volume strengthens signal
4. **Context Analysis**: Consider market conditions

## Usage Example
\`\`\`c
#include "ta_libc.h"

int main() {
    // Calculate CDLCOUNTERATTACK
    TA_RetCode ret = TA_CDLCOUNTERATTACK(
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
                // Bullish counterattack
            } else if (pattern[i] == -100) {
                // Bearish counterattack
            }
        }
    }
}
\`\`\`

## Trading Strategies
1. **Reversal Trading**: Enter opposite to previous trend
2. **Equilibrium Trading**: Trade the breakout
3. **Trend Change**: Look for trend reversal
4. **Risk Management**: Use appropriate stops

## Advantages
- Clear equilibrium signal
- Easy to identify
- Works in both directions
- Good reversal signal

## Limitations
- Requires confirmation
- May give false signals
- Best at key levels
- Needs follow-through

## Related Functions
- `CDLDOJI` - Doji
- `CDLENGULFING` - Engulfing Pattern
- `CDLHARAMI` - Harami Pattern
- `CDLSPINNINGTOP` - Spinning Top

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
