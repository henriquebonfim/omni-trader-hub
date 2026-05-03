# WILLR - Williams' %R

## Description

Williams %R, also called Williams Percent Range, is a momentum indicator that measures overbought and oversold levels. It's similar to the Stochastic Oscillator but is plotted on an inverted scale from 0 to -100. Developed by Larry Williams, it shows the relationship between the current close and the highest high over a lookback period.

## Category
Momentum Indicators

## Author
Larry Williams

## Calculation

Williams %R compares the current closing price to the high-low range over a period:

### Formula
```
%R = (Highest High - Close) / (Highest High - Lowest Low) × -100
```

Where:
- Highest High = Highest high over n periods
- Lowest Low = Lowest low over n periods
- Close = Current closing price

The result ranges from 0 to -100 (inverted scale).

## Parameters

- **optInTimePeriod** (default: 14): Lookback period
  - Valid range: 2 to 100000
  - Common values: 14 (standard), 10, 20

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- Williams %R values: `double[]` (range: 0 to -100)

## Interpretation

### Levels (Inverted Scale)
- **-20 to 0**: Overbought (price near top of range)
- **-50**: Midpoint
- **-80 to -100**: Oversold (price near bottom of range)

### Trading Signals

1. **Overbought/Oversold**:
   - **Overbought**: %R > -20 (price near highs)
   - **Oversold**: %R < -80 (price near lows)
   - **Sell**: When %R exits overbought zone (crosses below -20)
   - **Buy**: When %R exits oversold zone (crosses above -80)

2. **Failure Swings**:
   - **Bullish**: %R fails to reach oversold, then rallies
   - **Bearish**: %R fails to reach overbought, then declines

3. **Divergence**:
   - **Bullish**: Price lower lows, %R higher lows (less oversold)
   - **Bearish**: Price higher highs, %R lower highs (less overbought)

4. **Momentum Changes**:
   - Sharp moves in %R indicate strong momentum
   - Flattening %R suggests weakening momentum

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double willrOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period Williams %R
TA_RetCode retCode = TA_WILLR(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    willrOutput           // output: Williams %R values
);
```

## Implementation Details

The TA-Lib WILLR implementation:

1. **Range Calculation**: Finds highest high and lowest low over period
2. **Position Calculation**: Determines close position within range
3. **Inversion**: Multiplies by -100 (inverted scale)
4. **Lookback**: Requires n periods of data

## Relationship to Stochastic

Williams %R is closely related to the Fast Stochastic %K:

```
Williams %R = -100 - Stochastic %K (unsmoothed)

Or:
Stochastic %K = Williams %R + 100
```

The main differences:
- **Scale**: Williams %R: 0 to -100, Stochastic: 0 to 100
- **Smoothing**: Stochastic typically smoothed, Williams %R raw
- **Levels**: Inverted thresholds

## Trading Strategies

### 1. Overbought/Oversold Strategy
- **Buy**: %R crosses above -80 from below
- **Sell**: %R crosses below -20 from above
- **Stop**: Recent swing high/low
- **Target**: Opposite extreme
- **Best in**: Range-bound markets

### 2. Trend Following with Williams %R
- **Uptrend**: Only take buy signals (%R from oversold)
- **Downtrend**: Only take sell signals (%R from overbought)
- **Filter**: Use MA or trendline for trend
- **Best in**: Trending markets

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and %R
- **Confirmation**: Wait for support/resistance break
- **Entry**: On confirmation
- **Stop**: Beyond recent swing
- **Best in**: Trend exhaustion points

### 4. Multiple Timeframe
- **Higher TF**: Determine overall trend
- **Lower TF**: Time entries using %R
- **Rule**: Trade only when timeframes align
- **Best in**: All market conditions

## Advantages

1. **Clear Levels**: Defined overbought/oversold zones
2. **Fast**: Reacts quickly to price changes
3. **Simple**: Easy to understand and use
4. **Bounded**: Always between 0 and -100
5. **Versatile**: Works on all timeframes

## Limitations

1. **False Signals in Trends**: Can stay overbought/oversold during strong trends
2. **Whipsaws**: Multiple crossings in choppy markets
3. **No Direction Info**: Only shows relative position in range
4. **Lagging Component**: Based on historical high/low
5. **Period Sensitivity**: Results vary with period selection

## Period Selection

### Different Periods
- **Short (5-10)**: More sensitive, more signals
  - Day trading
  - Quick reversals
  - More false signals

- **Standard (14)**: Balanced approach
  - Larry Williams' original
  - Most common
  - General trading

- **Long (20-28)**: Smoother, fewer signals
  - Swing trading
  - Position trading
  - More reliable signals

## Related Functions

- **STOCH**: Stochastic Oscillator - similar concept, different scale
- **STOCHF**: Fast Stochastic - nearly identical to %R
- **RSI**: Relative Strength Index - another overbought/oversold indicator
- **CCI**: Commodity Channel Index - similar application

## References

- **Book**: *How I Made One Million Dollars... Last Year... Trading Commodities* by Larry Williams
- [TA-Lib Source Code: ta_WILLR.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_WILLR.c)
- [Investopedia: Williams %R](https://www.investopedia.com/terms/w/williamsr.asp)
- [StockCharts: Williams %R](https://school.stockcharts.com/doku.php?id=technical_indicators:williams_r)

## Additional Notes

Larry Williams developed Williams %R in the 1960s. It quickly became popular due to its simplicity and effectiveness. Williams himself is a legendary trader who won the World Cup Championship of Futures Trading with a return of +11,376% in 12 months.

### Key Insights

1. **Inverted Scale Psychology**:
   - Values are negative for historical reasons
   - Some traders find this confusing
   - Think of -20 as "high" and -80 as "low"
   - Alternatively, add 100 to convert to 0-100 scale

2. **Fast vs. Slow Stochastic**:
   - Williams %R = Fast Stochastic unsmoothed
   - Fast signals but more noise
   - No signal line like Stochastic
   - More suitable for short-term trading

3. **Strong Trends**:
   - In uptrends, %R can stay above -20 (overbought)
   - In downtrends, %R can stay below -80 (oversold)
   - Don't fade strong trends
   - Use for entry timing, not reversal trading

4. **Confirmation is Key**:
   - Don't trade %R signals alone
   - Confirm with:
     * Price patterns
     * Support/resistance
     * Trend indicators
     * Volume

5. **Multiple Williams %R**:
   - Use multiple periods simultaneously
   - E.g., 14-period and 28-period
   - Strongest signals when both align
   - Helps filter false signals

### Practical Tips

**For Long Entries**:
- Wait for %R < -80 (oversold)
- Enter when %R crosses back above -80
- Or wait for %R to reach -50 (momentum confirmation)
- Set stop below recent low

**For Short Entries**:
- Wait for %R > -20 (overbought)
- Enter when %R crosses back below -20
- Or wait for %R to fall to -50 (momentum confirmation)
- Set stop above recent high

**Avoiding Whipsaws**:
- Use in conjunction with trend indicator
- Only trade overbought in downtrends
- Only trade oversold in uptrends
- Require volume confirmation

Williams %R is particularly effective for timing entries in established trends and for identifying short-term overbought/oversold conditions in ranging markets.

