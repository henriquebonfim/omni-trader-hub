# CCI - Commodity Channel Index

## Description

The Commodity Channel Index (CCI) is a versatile indicator that can be used to identify cyclical trends, overbought/oversold levels, and divergences. Originally developed for commodities, CCI works equally well on stocks, indices, and other securities. It measures the deviation of price from its statistical mean.

## Category
Momentum Indicators

## Author
Donald Lambert

## Calculation

CCI measures how far price has deviated from its average price relative to normal deviations:

### Formula
```
CCI = (Typical Price - SMA of Typical Price) / (0.015 × Mean Deviation)
```

Where:
- **Typical Price** = (High + Low + Close) / 3
- **SMA** = Simple Moving Average of Typical Price over period
- **Mean Deviation** = Average of absolute deviations from SMA

### Detailed Steps
```
Step 1: Calculate Typical Price for each period
        TP = (H + L + C) / 3

Step 2: Calculate SMA of Typical Price
        SMA_TP = SMA(TP, period)

Step 3: Calculate Mean Deviation
        MD = SMA(|TP - SMA_TP|, period)

Step 4: Calculate CCI
        CCI = (TP - SMA_TP) / (0.015 × MD)
```

The constant 0.015 ensures approximately 70-80% of CCI values fall between -100 and +100.

## Parameters

- **optInTimePeriod** (default: 14): Period for calculating SMA and mean deviation
  - Valid range: 2 to 100000
  - Common values: 14 (standard), 20, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- CCI values: `double[]` (typically range: -300 to +300, but unbounded)

## Interpretation

### Overbought/Oversold Levels
- **Above +100**: Overbought (price unusually high vs. average)
- **Below -100**: Oversold (price unusually low vs. average)
- **Between -100 and +100**: Normal range

### Key Levels
- **+200**: Extremely overbought
- **+100**: Overbought threshold
- **0**: Centerline (equilibrium)
- **-100**: Oversold threshold
- **-200**: Extremely oversold

### Trading Signals

1. **Overbought/Oversold**:
   - **Buy**: CCI crosses above -100 from below (oversold recovery)
   - **Sell**: CCI crosses below +100 from above (overbought decline)
   - More reliable with trend confirmation

2. **Centerline Crossovers**:
   - **Bullish**: CCI crosses above 0 (gaining momentum)
   - **Bearish**: CCI crosses below 0 (losing momentum)
   - Indicates momentum shifts

3. **Extreme Levels**:
   - **Buy**: CCI moves below -200 then recovers
   - **Sell**: CCI moves above +200 then declines
   - Indicates extreme exhaustion

4. **Divergence**:
   - **Bullish**: Price lower lows, CCI higher lows
   - **Bearish**: Price higher highs, CCI lower highs
   - Signals potential trend reversal

5. **Trend Identification**:
   - **Strong Uptrend**: CCI consistently above 0
   - **Strong Downtrend**: CCI consistently below 0
   - **Weak Trend**: CCI oscillates around 0

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double cciOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period CCI
TA_RetCode retCode = TA_CCI(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    cciOutput             // output: CCI values
);
```

## Implementation Details

The TA-Lib CCI implementation:

1. **Typical Price**: Calculates average of high, low, close
2. **SMA Calculation**: Computes simple moving average
3. **Mean Deviation**: Calculates average absolute deviation
4. **Scaling**: Applies 0.015 constant for normalization
5. **Unbounded Output**: CCI can exceed ±300 in extreme cases

### Calculation Steps
```
Step 1: For each bar, TP = (H + L + C) / 3
Step 2: Calculate SMA of TP over period
Step 3: Calculate mean deviation from SMA
Step 4: CCI = (TP - SMA_TP) / (0.015 × Mean Deviation)
```

## Trading Strategies

### 1. Classic Overbought/Oversold
- **Buy**: CCI < -100, then crosses back above -100
- **Sell**: CCI > +100, then crosses back below +100
- **Stop**: Recent swing low/high
- **Target**: Opposite extreme or centerline
- **Best in**: Range-bound markets

### 2. Trend Trading with CCI
- **Uptrend Entry**: Buy when CCI dips to -100 in uptrend
- **Downtrend Entry**: Sell when CCI rises to +100 in downtrend
- **Filter**: Use MA or trendline to confirm trend
- **Exit**: Opposite CCI signal or trend break
- **Best in**: Trending markets

### 3. Divergence Strategy
- **Setup**: Identify CCI divergence with price
- **Confirmation**: Wait for price pattern (double top/bottom)
- **Entry**: On pattern completion
- **Stop**: Beyond pattern extreme
- **Target**: 1:2 or 1:3 risk/reward
- **Best in**: Trend exhaustion points

### 4. Zero Line Strategy
- **Buy**: CCI crosses above 0
- **Sell**: CCI crosses below 0
- **Confirmation**: Can wait for close above/below 0
- **Exit**: Opposite signal
- **Best in**: Shorter timeframes, momentum trading

### 5. Extreme CCI (>200 or <-200)
- **Mean Reversion**: Fade extreme levels
- **Entry**: When CCI starts returning to normal
- **Stop**: Beyond recent extreme
- **Target**: Return to ±100 or 0
- **Best in**: Volatile markets with mean reversion

## Period Selection

### Different Periods
- **Short (5-10)**: More sensitive, frequent signals
  - Day trading
  - Volatile markets
  - More false signals

- **Standard (14-20)**: Balanced approach
  - Swing trading
  - Most markets
  - Lambert's original

- **Long (30-50)**: Smoother, fewer signals
  - Position trading
  - Less volatile markets
  - Fewer false signals

## Advantages

1. **Versatile**: Works in trending and ranging markets
2. **Clear Levels**: Defined overbought/oversold zones
3. **Unbounded**: Can signal extremely strong moves (>±200)
4. **Leading Component**: Can precede price turns
5. **Universal**: Effective across all markets
6. **Multiple Uses**: Overbought/oversold, trend, divergence

## Limitations and Considerations

1. **False Signals in Trends**: Can stay overbought/oversold during strong trends
2. **Whipsaws**: Generates false signals in choppy markets
3. **No Volume**: Doesn't incorporate volume data
4. **Subjective Levels**: Optimal thresholds vary by market
5. **Period Sensitivity**: Results vary with period selection
6. **Lagging Element**: Uses SMA, which lags

## CCI Patterns and Behaviors

### In Trending Markets
- **Strong Uptrend**: CCI often stays above +100
- **Strong Downtrend**: CCI often stays below -100
- **Don't fade the trend**: Overbought can stay overbought
- **Use for entries**: Buy dips to -100 in uptrend

### In Ranging Markets
- **Regular Oscillation**: CCI moves between ±100
- **Mean Reversion**: Extremes tend to reverse
- **Best CCI Application**: Trade the range extremes
- **Clear Signals**: More reliable overbought/oversold

### Extreme Readings
- **Above +200**: Exceptionally strong momentum
  - Can continue or signal exhaustion
  - Watch for divergence
  - Consider profit-taking

- **Below -200**: Exceptionally weak momentum
  - Can continue or signal capitulation
  - Watch for reversal signals
  - Consider contrarian entry

## Related Functions

- **RSI**: Relative Strength Index - another overbought/oversold oscillator
- **STOCH**: Stochastic Oscillator - similar momentum tool
- **WILLR**: Williams %R - similar range-based oscillator
- **MOM**: Momentum - simpler momentum indicator

## References

- **Article**: "Commodities Channel Index: Tools for Trading Cyclic Trends" by Donald Lambert (Commodities Magazine, 1980)
- [TA-Lib Source Code: ta_CCI.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_CCI.c)
- [Investopedia: CCI](https://www.investopedia.com/terms/c/commoditychannelindex.asp)
- [StockCharts: CCI](https://school.stockcharts.com/doku.php?id=technical_indicators:commodity_channel_index_cci)
- [Original TA-Doc: CCI](http://tadoc.org/indicator/CCI.htm)

## Additional Notes

Donald Lambert introduced CCI in 1980, originally designed to identify cyclical turns in commodities. Despite its name, it's effective on all security types.

### Key Insights

1. **The 0.015 Constant**:
   - Chosen to ensure ~70-80% of values between ±100
   - Makes ±100 statistically significant
   - Values outside ±100 represent unusual price action
   - Not a hard limit - values can exceed ±300

2. **Unlike RSI or Stochastic**:
   - CCI is unbounded (no 0-100 limit)
   - Can show extreme strength/weakness beyond standard levels
   - This is a feature, not a bug
   - Extreme readings signal exceptional conditions

3. **Typical Price Usage**:
   - Uses (H+L+C)/3 instead of just Close
   - Incorporates full price range
   - More comprehensive than close-only indicators
   - Better captures intraday volatility

4. **Mean Reversion vs. Trend**:
   - Range markets: CCI mean-reverts (±100 reliable)
   - Trending markets: CCI can stay extended (±100 less reliable)
   - Key is identifying market type
   - Combine with trend indicator (ADX, MA)

5. **Multiple Timeframe Analysis**:
   - Higher timeframe for trend context
   - Lower timeframe for entry timing
   - E.g., Daily CCI for trend, Hourly for entry
   - Both should align for best trades

### Practical Tips

**For Range Trading**:
- Use CCI ±100 levels strictly
- Enter on crosses back into normal range
- Tight stops beyond recent high/low
- Target opposite extreme

**For Trend Trading**:
- Ignore overbought in uptrend
- Ignore oversold in downtrend
- Use CCI extremes as entry points
- Trade in trend direction only

**For All Trading**:
- CCI > +100 = bullish bias
- CCI < -100 = bearish bias
- CCI oscillating around 0 = no clear trend
- Divergences more reliable than absolute levels

**Divergence Trading**:
- Most powerful CCI signal
- Wait for confirmation (support/resistance)
- Best at major highs/lows
- Don't trade every divergence

CCI is particularly effective when used as a multi-purpose tool: trend filter (centerline), momentum gauge (absolute level), and reversal indicator (divergences). The key is adapting its interpretation to current market conditions.

