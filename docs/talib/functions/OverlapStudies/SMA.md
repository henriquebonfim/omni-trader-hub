# SMA - Simple Moving Average

## Description

The Simple Moving Average (SMA) is the most basic type of moving average. It calculates the arithmetic mean of prices over a specified period. The SMA smooths price data to identify trends by filtering out short-term fluctuations.

## Category
Overlap Studies

## Calculation

The SMA is calculated by summing the prices over a specified period and dividing by the number of periods:

### Formula
```
SMA = (P1 + P2 + P3 + ... + Pn) / n
```

Where:
- P1, P2, ..., Pn are the prices (typically closing prices) for each period
- n is the number of periods

### Example
For a 5-day SMA with closing prices [10, 11, 12, 13, 14]:
```
SMA = (10 + 11 + 12 + 13 + 14) / 5 = 60 / 5 = 12
```

## Parameters

- **optInTimePeriod** (default: 30): The number of periods for the moving average
  - Valid range: 2 to 100000
  - Common values: 10, 20, 50, 100, 200

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- SMA values: `double[]`

## Interpretation

### Trend Identification
- **Uptrend**: Price above SMA, SMA sloping upward
- **Downtrend**: Price below SMA, SMA sloping downward
- **Crossover**: Price crossing SMA can signal trend changes

### Trading Signals
1. **Price Crossovers**:
   - **Buy Signal**: Price crosses above SMA
   - **Sell Signal**: Price crosses below SMA

2. **Moving Average Crossovers** (using multiple SMAs):
   - **Golden Cross**: Shorter SMA (e.g., 50-day) crosses above longer SMA (e.g., 200-day) - bullish
   - **Death Cross**: Shorter SMA crosses below longer SMA - bearish

3. **Support and Resistance**:
   - SMA can act as dynamic support in uptrends
   - SMA can act as dynamic resistance in downtrends

### Common Periods
- **10-day SMA**: Very short-term, sensitive to price changes
- **20-day SMA**: Short-term trend
- **50-day SMA**: Intermediate-term trend
- **100-day SMA**: Medium-term trend
- **200-day SMA**: Long-term trend (most watched by institutional investors)

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double smaOutput[100];
int outBegIdx, outNBElement;

// Calculate 20-period SMA
TA_RetCode retCode = TA_SMA(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    20,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    smaOutput             // output: SMA values
);
```

## Implementation Details

The TA-Lib implementation uses an efficient sliding window algorithm:

1. **Initial Sum**: Calculates the sum of the first `period` values
2. **Sliding Window**: For each subsequent value:
   - Add the new value to the sum
   - Subtract the oldest value from the sum
   - Divide by the period

This approach is computationally efficient with O(n) complexity.

### Characteristics
- **Lookback Period**: Requires `timePeriod - 1` bars before producing the first output
- **Equal Weighting**: All prices in the period have equal weight
- **Lag**: SMA lags price action more than exponential moving averages

## Advantages

1. **Simple to Calculate**: Easy to understand and compute
2. **Smooth**: Effectively filters out short-term noise
3. **Widely Used**: Standard in technical analysis, easy to compare with others
4. **Objective**: No subjective interpretation in calculation

## Limitations and Considerations

1. **Lagging Indicator**: By nature, moving averages lag price action
2. **Equal Weighting**: Treats old data the same as recent data, which may not be ideal
3. **Whipsaws**: Can generate false signals in choppy, sideways markets
4. **Not Predictive**: Only describes past price action, doesn't predict future moves
5. **Period Sensitivity**: Results vary significantly based on chosen period

## Comparison with Other Moving Averages

| Moving Average | Weighting | Responsiveness | Smoothness |
|---------------|-----------|----------------|------------|
| SMA | Equal | Low | High |
| EMA | Exponential | High | Medium |
| WMA | Linear | Medium | Medium |
| DEMA | Double Exponential | Very High | Low |
| TEMA | Triple Exponential | Very High | Low |

## Related Functions

- **EMA**: Exponential Moving Average - gives more weight to recent prices
- **WMA**: Weighted Moving Average - linear weighting scheme
- **DEMA**: Double Exponential Moving Average - faster response to price changes
- **TEMA**: Triple Exponential Moving Average - even faster response
- **TRIMA**: Triangular Moving Average - double-smoothed
- **KAMA**: Kaufman Adaptive Moving Average - adjusts to market volatility

## References

- [TA-Lib Source Code: ta_SMA.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_SMA.c)
- [Investopedia: Simple Moving Average](https://www.investopedia.com/terms/s/sma.asp)
- [StockCharts: Moving Averages](https://school.stockcharts.com/doku.php?id=technical_indicators:moving_averages)
- [Original TA-Doc: SMA](http://tadoc.org/indicator/SMA.htm)

## Additional Notes

The Simple Moving Average is one of the oldest and most widely used technical indicators. It forms the foundation for many other technical analysis tools and strategies. While it has limitations due to its lagging nature and equal weighting, it remains highly effective for:

- Identifying the overall trend direction
- Providing support and resistance levels
- Smoothing price data to see the bigger picture
- Serving as a component in more complex indicators

The 200-day SMA is particularly significant in financial markets and is closely watched by institutional investors and traders as a key indicator of long-term trend health. When major indices trade above their 200-day SMA, it's generally considered a bull market; below it is considered a bear market.

