# ROC - Rate of Change

## Description

The Rate of Change (ROC) is a momentum indicator that measures the percentage change in price between the current price and the price n periods ago. Unlike the Momentum indicator which shows absolute change, ROC shows relative (percentage) change, making it easier to compare across different securities and time periods.

## Category
Momentum Indicators

## Calculation

ROC calculates the percentage change from n periods ago:

### Formula
```
ROC = ((Price(today) / Price(today - n)) - 1) × 100
```

Or equivalently:
```
ROC = ((Price(today) - Price(today - n)) / Price(today - n)) × 100
```

### Example
If today's close is $55 and the close 10 days ago was $50:
```
ROC(10) = ((55 / 50) - 1) × 100 = 0.10 × 100 = 10%
```

## Parameters

- **optInTimePeriod** (default: 10): Number of periods to look back
  - Valid range: 1 to 100000
  - Common values: 10, 12, 20, 25

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- ROC values: `double[]` (percentage, unbounded)

## Interpretation

### ROC Values
- **ROC > 0**: Price higher than n periods ago (positive momentum)
- **ROC = 0**: Price unchanged from n periods ago
- **ROC < 0**: Price lower than n periods ago (negative momentum)

### Common Thresholds (vary by security)
- **ROC > +5%**: Strong positive momentum
- **ROC < -5%**: Strong negative momentum
- Can adjust based on volatility of security

### Trading Signals

1. **Zero Line Crossovers**:
   - **Buy**: ROC crosses above zero
   - **Sell**: ROC crosses below zero

2. **Overbought/Oversold** (thresholds vary):
   - **Overbought**: ROC > +10% (or higher)
   - **Oversold**: ROC < -10% (or lower)

3. **Divergence**:
   - **Bullish**: Price lower lows, ROC higher lows
   - **Bearish**: Price higher highs, ROC lower highs

4. **Trend Strength**:
   - Increasing ROC = Accelerating trend
   - Decreasing ROC = Decelerating trend

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double rocOutput[100];
int outBegIdx, outNBElement;

// Calculate 10-period ROC
TA_RetCode retCode = TA_ROC(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    10,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    rocOutput             // output: ROC values
);
```

## Implementation Details

- Calculates percentage change
- Output as percentage (e.g., 10.5 means 10.5%)
- Lookback period: n periods
- Can be used to compare different securities

## Advantages

1. **Normalized**: Percentage makes comparison easier
2. **Universal**: Works across all securities
3. **Clear**: Easy to understand (percentage change)
4. **Versatile**: Multiple trading applications

## Limitations

1. **Whipsaws**: Can generate false signals
2. **Lagging**: Based on historical comparison
3. **No Standard Levels**: Overbought/oversold vary by security
4. **Zero Division**: Undefined if past price is zero

## Related Functions

- **MOM**: Momentum - absolute change version
- **ROCP**: Rate of Change Percentage - slightly different formula
- **ROCR**: Rate of Change Ratio - ratio version
- **ROCR100**: Rate of Change Ratio 100 scale
- **RSI**: Relative Strength Index - normalized alternative

## References

- [TA-Lib Source Code: ta_ROC.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_ROC.c)
- [Investopedia: Rate of Change](https://www.investopedia.com/terms/p/pricerateofchange.asp)
- [StockCharts: Rate of Change](https://school.stockcharts.com/doku.php?id=technical_indicators:rate_of_change_roc_and_momentum)

## Additional Notes

ROC is preferred over Momentum when comparing multiple securities or when the price scale differs significantly across time periods. The percentage basis provides a normalized view of momentum that's easier to interpret and compare.

