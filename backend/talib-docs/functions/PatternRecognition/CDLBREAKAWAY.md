# CDLBREAKAWAY - Breakaway

## Overview
The Breakaway (CDLBREAKAWAY) is a five-candle reversal pattern that can be either bullish or bearish. It shows a gap followed by three small candles in the opposite direction, then a gap in the original direction.

## Category
Pattern Recognition

## Calculation
The CDLBREAKAWAY function identifies breakaway patterns:

### Bullish Breakaway Criteria
- First candle: Long black (bearish)
- Second candle: Black body that gaps down
- Third candle: Black or white, lower high and lower low than second
- Fourth candle: Black or white, lower high and lower low than third
- Fifth candle: White (bullish) that closes inside the gap, erasing prior 3 days

### Bearish Breakaway Criteria
- First candle: Long white (bullish)
- Second candle: White body that gaps up
- Third candle: Black or white, higher high and higher low than second
- Fourth candle: Black or white, higher high and higher low than third
- Fifth candle: Black (bearish) that closes inside the gap, erasing prior 3 days
- Shows trend reversal

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
The Breakaway indicates:
- **Bullish Breakaway**: Strong upward reversal after consolidation
- **Bearish Breakaway**: Strong downward reversal after consolidation
- **Trend Reversal**: Shows clear trend change
- **High Reliability**: Strong reversal signal

## How to Use
1. **Reversal Signal**: Enter opposite to previous trend
2. **Trend Change**: Look for clear trend reversal
3. **Volume Confirmation**: Higher volume strengthens signal
4. **Position Sizing**: Increase size given reliability

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate CDLBREAKAWAY
    TA_RetCode ret = TA_CDLBREAKAWAY(
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
                // Bullish breakaway
            } else if (pattern[i] == -100) {
                // Bearish breakaway
            }
        }
    }
}
```

## Trading Strategies
1. **Reversal Trading**: Enter opposite to previous trend
2. **Trend Change**: Look for clear trend reversal
3. **Gap Trading**: Trade the gap reversal
4. **Position Sizing**: Increase position size given reliability

## Advantages
- Highly reliable reversal pattern
- Clear trend change signal
- Works in all timeframes
- Strong historical track record

## Limitations
- Requires six candles to complete
- Relatively rare pattern
- May have false signals without confirmation
- Best at significant levels

## Related Functions
- `CDL3WHITESOLDIERS` - Three White Soldiers
- `CDL3BLACKCROWS` - Three Black Crows
- `CDLENGULFING` - Engulfing Pattern
- `CDLMARUBOZU` - Marubozu

## References
- Nison, S. (1991). "Japanese Candlestick Charting Techniques"
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
