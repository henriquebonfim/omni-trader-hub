# MOM - Momentum

## Description

Momentum is one of the simplest and most fundamental indicators in technical analysis. It measures the rate of change in price over a specified period by comparing the current price to the price from n periods ago. Positive momentum indicates upward price movement, while negative momentum indicates downward movement.

## Category
Momentum Indicators

## Calculation

Momentum is calculated as the simple difference between the current price and the price n periods ago:

### Formula
```
MOM = Price(today) - Price(today - n)
```

Where:
- n = time period (lookback period)
- Price = typically closing price

### Example
If today's close is $52 and the close 10 days ago was $50:
```
MOM(10) = 52 - 50 = 2
```

## Parameters

- **optInTimePeriod** (default: 10): Number of periods to look back
  - Valid range: 1 to 100000
  - Common values: 10, 14, 20

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- Momentum values: `double[]` (unbounded, can be positive or negative)

## Interpretation

### Momentum Values
- **MOM > 0**: Price higher than n periods ago (upward momentum)
- **MOM = 0**: Price unchanged from n periods ago (no momentum)
- **MOM < 0**: Price lower than n periods ago (downward momentum)

### Magnitude
- **Increasing MOM**: Strengthening momentum
- **Decreasing MOM**: Weakening momentum
- **Large positive MOM**: Strong upward momentum
- **Large negative MOM**: Strong downward momentum

### Trading Signals

1. **Zero Line Crossovers**:
   - **Buy**: MOM crosses above zero
   - **Sell**: MOM crosses below zero

2. **Divergence**:
   - **Bullish**: Price lower lows, MOM higher lows
   - **Bearish**: Price higher highs, MOM lower highs

3. **Trend Strength**:
   - Accelerating MOM = Strong trend
   - Decelerating MOM = Weakening trend

4. **Extremes**:
   - Extremely high MOM = Potential exhaustion
   - Extremely low MOM = Potential reversal

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double momOutput[100];
int outBegIdx, outNBElement;

// Calculate 10-period Momentum
TA_RetCode retCode = TA_MOM(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    10,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    momOutput             // output: momentum values
);
```

## Implementation Details

- Very simple calculation: Price(t) - Price(t-n)
- Lookback period: n periods
- No smoothing or normalization
- Output in same units as price

## Advantages

1. **Simple**: Easiest momentum indicator to understand
2. **Fast**: No complex calculations
3. **Clear**: Straightforward interpretation
4. **Versatile**: Works on all markets and timeframes

## Limitations

1. **Not Normalized**: Values depend on price scale
2. **No Bounds**: No defined overbought/oversold levels
3. **Lagging**: Based on historical price comparison
4. **Whipsaws**: Can generate false signals

## Related Functions

- **ROC**: Rate of Change - percentage version of momentum
- **ROCP**: Rate of Change Percentage - another percentage version
- **RSI**: Relative Strength Index - normalized momentum
- **CMO**: Chande Momentum Oscillator - similar concept

## References

- [TA-Lib Source Code: ta_MOM.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_MOM.c)
- [Investopedia: Momentum](https://www.investopedia.com/terms/m/momentum.asp)
- [StockCharts: Momentum](https://school.stockcharts.com/doku.php?id=technical_indicators:rate_of_change_roc_and_momentum)

## Additional Notes

Momentum is the foundation for many more sophisticated indicators. While simple, it effectively captures the rate of price change. For comparing momentum across different securities or time periods, consider using ROC (percentage-based) instead.

