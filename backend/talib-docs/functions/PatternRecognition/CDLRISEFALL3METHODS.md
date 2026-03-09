# CDLRISEFALL3METHODS - R I S E F A L L3 M E T H O D S

## Overview
The Rising/Falling Three Methods is a continuation pattern showing a brief consolidation within a trend before continuation.

## Category
Pattern Recognition

## Calculation
The CDLRISEFALL3METHODS function identifies rising/falling three methods patterns:

### Rising Three Methods (Bullish) Criteria
- First candle: Long white (bullish) candlestick
- Next group: Small falling bodies (commonly black) that hold within first candle's range
- Final candle: White candle that closes above first candle's close

### Falling Three Methods (Bearish) Criteria
- First candle: Long black (bearish) candlestick
- Next group: Small rising bodies (commonly white) that hold within first candle's range
- Final candle: Black candle that closes below first candle's close

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
The R I S E F A L L3 M E T H O D S pattern indicates:
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
    // Calculate CDLRISEFALL3METHODS
    TA_RetCode ret = TA_CDLRISEFALL3METHODS(
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
