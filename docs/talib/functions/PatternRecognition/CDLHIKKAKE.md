# CDLHIKKAKE - H I K K A K E

## Overview
The Hikkake pattern is a trap-and-reverse pattern where an inside bar is followed by a breakout that may confirm within 3 days.

## Category
Pattern Recognition

## Calculation
The CDLHIKKAKE function identifies hikkake patterns:

### Bullish Hikkake Criteria
- First and second candles: Inside bar (2nd has lower high and higher low than 1st)
- Third candle: Higher high and higher low than 2nd (breakout)
- Confirmation within next 3 days: Close higher than 2nd candle's high

### Bearish Hikkake Criteria
- First and second candles: Inside bar (2nd has lower high and higher low than 1st)
- Third candle: Lower high and lower low than 2nd (breakout)
- Confirmation within next 3 days: Close lower than 2nd candle's low

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
The H I K K A K E pattern indicates:
- **Bullish Signal**: Potential upward movement
- **Bearish Signal**: Potential downward movement
- **Market Sentiment**: Shows current market psychology
- **Trading Opportunity**: Provides entry/exit signals

## How to Use
1. **Pattern Recognition**: Identify the specific candlestick formation
2. **Confirmation**: Wait for pattern completion
3. **Volume Analysis**: Confirm with volume
4. **Risk Management**: Use appropriate stop losses

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLHIKKAKE
    TA_RetCode ret = TA_CDLHIKKAKE(
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
                // Bullish pattern
            } else if (pattern[i] == -100) {
                // Bearish pattern
            }
        }
    }
}
```

## Trading Strategies
1. **Pattern Trading**: Trade based on pattern signals
2. **Confirmation**: Wait for pattern completion
3. **Volume Confirmation**: Use volume to confirm signals
4. **Risk Management**: Implement proper stop losses

## Advantages
- Clear visual pattern
- Easy to identify
- Works in all timeframes
- Can be combined with other indicators

## Limitations
- May give false signals
- Requires confirmation
- Best used with other indicators
- Market context important

## Related Functions
- Other candlestick pattern functions
- Volume indicators
- Momentum indicators
- Support/resistance analysis

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
