# ADX - Average Directional Movement Index

## Description

The Average Directional Movement Index (ADX) is a trend strength indicator developed by J. Welles Wilder. ADX quantifies trend strength regardless of direction, oscillating between 0 and 100. Higher values indicate stronger trends (up or down), while lower values suggest a weaker trend or ranging market.

## Category
Momentum Indicators / Trend Strength

## Author
J. Welles Wilder

## Calculation

ADX is derived from two other indicators: Plus Directional Indicator (+DI) and Minus Directional Indicator (-DI).

### Step 1: Calculate Directional Movement
```
+DM = High(today) - High(yesterday)  (if positive and > -DM, else 0)
-DM = Low(yesterday) - Low(today)    (if positive and > +DM, else 0)
```

### Step 2: Calculate True Range (TR)
```
TR = max[(High - Low), |High - Close(prev)|, |Low - Close(prev)|]
```

### Step 3: Smooth DM and TR (using Wilder's smoothing)
```
+DM(smoothed) = +DM(smoothed prev) - (+DM(smoothed prev)/n) + +DM(current)
-DM(smoothed) = -DM(smoothed prev) - (-DM(smoothed prev)/n) + -DM(current)
TR(smoothed) = TR(smoothed prev) - (TR(smoothed prev)/n) + TR(current)
```

### Step 4: Calculate Directional Indicators
```
+DI = (+DM(smoothed) / TR(smoothed)) × 100
-DI = (-DM(smoothed) / TR(smoothed)) × 100
```

### Step 5: Calculate DX (Directional Index)
```
DX = (|+DI - -DI| / |+DI + -DI|) × 100
```

### Step 6: Calculate ADX
```
ADX = Smoothed Average of DX over n periods
```

## Parameters

- **optInTimePeriod** (default: 14): Period for ADX calculation
  - Valid range: 2 to 100000
  - Common values: 14 (standard), 7 (shorter-term), 21 (longer-term)

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- ADX values: `double[]` (range: 0 to 100)

## Interpretation

### ADX Levels (Trend Strength)
- **0-25**: Absent or weak trend (ranging market)
- **25-50**: Strong trend
- **50-75**: Very strong trend
- **75-100**: Extremely strong trend

### Common Thresholds
- **ADX < 20**: Non-trending, choppy, ranging market
- **ADX 20-25**: Trend developing
- **ADX > 25**: Trending market (threshold varies by market)
- **ADX > 40**: Very strong trend
- **ADX > 50**: Extremely strong trend (rare)

### ADX Direction
- **Rising ADX**: Trend strengthening (regardless of direction)
- **Falling ADX**: Trend weakening or market ranging
- **Flat ADX**: Trend strength stable

### Key Insights
ADX does NOT indicate trend direction, only strength:
- High ADX can occur in uptrend or downtrend
- Use +DI and -DI to determine direction
- ADX focuses purely on trend strength

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double adxOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period ADX
TA_RetCode retCode = TA_ADX(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    adxOutput             // output: ADX values
);
```

## Implementation Details

The TA-Lib ADX implementation:

1. **Directional Movement**: Calculates +DM and -DM
2. **True Range**: Computes TR for normalization
3. **Wilder's Smoothing**: Applies special smoothing to DM and TR
4. **DI Calculation**: Computes directional indicators
5. **DX Calculation**: Derives directional index
6. **ADX Smoothing**: Final smoothing for ADX

**Lookback Period**: ADX requires significant data due to multiple smoothing steps.

## Trading Strategies

### 1. Trend Filter Strategy
- **Entry**: Only trade when ADX > 25 (confirming trend)
- **Direction**: Use +DI vs -DI for direction
- **Exit**: When ADX falls below 20
- **Best in**: Combining with trend-following systems

### 2. ADX Crossover Strategy
- **Buy**: ADX crosses above 20 or 25 (trend emerging)
- **Sell**: ADX crosses below 20 or 25 (trend dying)
- **Confirmation**: Use +DI and -DI for direction
- **Best in**: Catching emerging trends

### 3. DI Crossover with ADX Filter
- **Buy**: +DI crosses above -DI AND ADX > 25
- **Sell**: -DI crosses above +DI AND ADX > 25
- **Exit**: DI crossback or ADX < 20
- **Best in**: Trending markets

### 4. Extreme ADX (Exhaustion)
- **Setup**: ADX reaches very high levels (>50)
- **Signal**: ADX starts declining from extreme
- **Action**: Consider taking profits
- **Reason**: Trend may be exhausting
- **Best in**: End of strong trends

### 5. Range Trading with Low ADX
- **Setup**: ADX < 20 for extended period
- **Strategy**: Use oscillators (RSI, Stochastic)
- **Trades**: Buy support, sell resistance
- **Exit**: When ADX starts rising above 20
- **Best in**: Ranging, consolidating markets

## ADX Patterns

### 1. Rising ADX
- **Pattern**: ADX moving higher
- **Meaning**: Trend gaining strength
- **Action**: Stay with trend, add to positions
- **Confirmation**: +DI or -DI also rising

### 2. Falling ADX (from high level)
- **Pattern**: ADX declining from >40
- **Meaning**: Trend losing steam
- **Action**: Tighten stops, consider taking profits
- **Warning**: Potential reversal or consolidation

### 3. Low, Flat ADX
- **Pattern**: ADX < 20, not trending
- **Meaning**: No trend, ranging market
- **Action**: Avoid trend-following strategies
- **Alternative**: Use range trading strategies

### 4. ADX Peak
- **Pattern**: ADX makes a high then turns down
- **Meaning**: Trend exhaustion possible
- **Action**: Watch for reversal signals
- **Caution**: Can be followed by consolidation or reversal

## Advantages

1. **Trend Strength Quantification**: Objective measure of trend strength
2. **Universal**: Works on all markets and timeframes
3. **Filter False Signals**: Helps avoid choppy, trendless conditions
4. **Non-Directional**: Focuses on trend strength, not direction
5. **Well-Established**: Time-tested, widely used
6. **Versatile**: Useful for multiple strategy types

## Limitations and Considerations

1. **Lagging Indicator**: Multiple smoothing creates significant lag
2. **No Direction Info**: Doesn't tell you trend direction
3. **Complex Calculation**: More complex than simple indicators
4. **High Lookback**: Needs substantial data to stabilize
5. **Level Subjectivity**: Optimal threshold varies by market
6. **Extreme Rarity**: Very high ADX (>50) is rare

## +DI and -DI Usage

While ADX measures strength, +DI and -DI (available via PLUS_DI and MINUS_DI functions) show direction:

### Directional Signals
- **+DI > -DI**: Upward directional movement stronger
- **-DI > +DI**: Downward directional movement stronger
- **+DI crosses above -DI**: Potential buy signal (with ADX confirmation)
- **-DI crosses above +DI**: Potential sell signal (with ADX confirmation)

### Combined ADX + DI Strategy
```
Strong Buy: ADX > 25 AND +DI > -DI AND ADX rising
Strong Sell: ADX > 25 AND -DI > +DI AND ADX rising
```

## Parameter Selection

### Period Selection
- **7-period**: More sensitive, faster signals, more noise
- **14-period**: Standard, balanced (Wilder's original)
- **21-period**: Smoother, slower signals, less noise

### Threshold Selection
The "ADX > 25" rule is not universal:
- **Volatile markets** (e.g., crypto): May use 30 or 35
- **Stable markets** (e.g., bonds): May use 20
- **Stocks**: Usually 25
- **Forex**: Often 20-25

Backtest for your specific market!

## Related Functions

- **ADXR**: Average Directional Movement Index Rating - smoothed ADX
- **PLUS_DI**: Plus Directional Indicator - upward movement
- **MINUS_DI**: Minus Directional Indicator - downward movement
- **DX**: Directional Movement Index - component of ADX
- **PLUS_DM**: Plus Directional Movement - component
- **MINUS_DM**: Minus Directional Movement - component

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder (ISBN: 0894590278)
- [TA-Lib Source Code: ta_ADX.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_ADX.c)
- [Investopedia: ADX](https://www.investopedia.com/terms/a/adx.asp)
- [StockCharts: ADX](https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx)
- [Original TA-Doc: ADX](http://tadoc.org/indicator/ADX.htm)

## Additional Notes

J. Welles Wilder introduced ADX in his 1978 book alongside RSI, ATR, and Parabolic SAR. ADX remains one of the most important indicators for assessing trend strength.

### Key Insights

1. **Trend vs. Range Identification**:
   - Most traders lose money in ranging markets
   - ADX helps identify when market is trending (tradeable)
   - vs. ranging (difficult to trade with trend systems)
   - This alone makes ADX extremely valuable

2. **ADX Paradox**:
   - When ADX is very high, trend is strong BUT
   - May also be near exhaustion
   - Requires experience to interpret
   - Use with price action for best results

3. **Wilder's Smoothing**:
   - Special smoothing method (not EMA or SMA)
   - Creates more lag but smoother results
   - Better for trend identification
   - Less prone to whipsaws

4. **Multiple Timeframe Analysis**:
   - Check ADX on higher timeframe for trend
   - Use lower timeframe for entry timing
   - E.g., Daily ADX > 25, enter on hourly pullback

5. **Market Context**:
   - Some markets trend more than others
   - Adjust ADX threshold accordingly
   - Crypto tends to have high ADX more often
   - Traditional stocks may trend less

### Practical Application

**For Trend Traders**:
- Only trade when ADX > 25
- Enter in direction of +DI vs -DI
- Stay in trade while ADX rising
- Exit when ADX falls below 20

**For Range Traders**:
- Trade when ADX < 20
- Use oscillators and support/resistance
- Exit when ADX starts rising
- Wait for next low ADX period

**For Position Sizers**:
- Larger positions when ADX > 40 (strong trend)
- Smaller positions when ADX 25-40 (moderate trend)
- Minimal positions when ADX < 25 (weak/no trend)

ADX is best used as a filter rather than a signal generator. It tells you WHEN to trade (trending vs ranging) and HOW AGGRESSIVELY to trade (trend strength), but not necessarily WHICH DIRECTION (use +DI/-DI or other indicators for that).

