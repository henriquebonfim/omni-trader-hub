# WMA - Weighted Moving Average

## Description

The Weighted Moving Average (WMA) is a moving average that gives more weight to recent data points and less weight to older data points. Unlike the Simple Moving Average (SMA) which weights all data equally, WMA uses a linear weighting scheme where the most recent value has the highest weight.

## Category
Overlap Studies

## Calculation

In a WMA, each price is multiplied by a weighting factor. The most recent price has the highest weight (n), the next has (n-1), and so on:

### Formula
```
WMA = (P1 × n + P2 × (n-1) + P3 × (n-2) + ... + Pn × 1) / (n + (n-1) + (n-2) + ... + 1)
```

Or more concisely:
```
WMA = Σ(Price[i] × Weight[i]) / Σ(Weight[i])
```

Where:
- n = period
- P1 = most recent price
- Pn = oldest price in the period
- Sum of weights = n × (n+1) / 2

### Example
For a 5-period WMA with prices [10, 11, 12, 13, 14]:
```
WMA = (14×5 + 13×4 + 12×3 + 11×2 + 10×1) / (5+4+3+2+1)
    = (70 + 52 + 36 + 22 + 10) / 15
    = 190 / 15
    = 12.67
```

## Parameters

- **optInTimePeriod** (default: 30): Number of periods for the weighted moving average
  - Valid range: 2 to 100000
  - Common values: 10, 20, 50

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- WMA values: `double[]`

## Interpretation

### Compared to SMA and EMA
- **More Responsive than SMA**: Reacts faster to price changes
- **Less Responsive than EMA**: Slower than exponential moving average
- **Predictable Weighting**: Linear weight decay is intuitive

### Usage
Same as other moving averages:
- **Trend Direction**: Slope indicates trend
- **Support/Resistance**: Acts as dynamic levels
- **Crossovers**: Generate trading signals

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double wmaOutput[100];
int outBegIdx, outNBElement;

// Calculate 20-period WMA
TA_RetCode retCode = TA_WMA(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    20,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    wmaOutput             // output: WMA values
);
```

## Implementation Details

The TA-Lib WMA implementation uses an efficient algorithm:

1. **Weighted Sum**: Calculates weighted sum of prices
2. **Divisor**: Uses triangular number n×(n+1)/2
3. **Sliding Calculation**: Efficiently updates for each new bar
4. **Lookback**: Requires period-1 bars before first output

## Advantages

1. **More Responsive**: Than SMA, captures recent changes better
2. **Smoother than EMA**: Less whipsaw than exponential
3. **Linear Logic**: Weighting scheme is intuitive
4. **Balanced**: Good middle ground between SMA and EMA

## Limitations

1. **Still Lags**: Less than SMA but more than EMA
2. **Less Popular**: Not as widely used as SMA or EMA
3. **Finite Memory**: Unlike EMA, completely drops old data
4. **Computation**: Slightly more complex than SMA

## Comparison of Moving Averages

| Type | Weighting | Responsiveness | Lag | Smoothness |
|------|-----------|----------------|-----|------------|
| SMA | Equal | Low | High | High |
| WMA | Linear | Medium | Medium | Medium |
| EMA | Exponential | High | Low | Low |
| DEMA | Double Exponential | Very High | Very Low | Very Low |

## Related Functions

- **SMA**: Simple Moving Average - equal weighting
- **EMA**: Exponential Moving Average - exponential weighting
- **DEMA**: Double Exponential Moving Average - reduced lag
- **TEMA**: Triple Exponential Moving Average - minimal lag
- **TRIMA**: Triangular Moving Average - double smoothed

## References

- [TA-Lib Source Code: ta_WMA.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_WMA.c)
- [Investopedia: Weighted Moving Average](https://www.investopedia.com/articles/technical/060401.asp)
- [StockCharts: Moving Averages](https://school.stockcharts.com/doku.php?id=technical_indicators:moving_averages)
- [Original TA-Doc: WMA](http://tadoc.org/indicator/WMA.htm)

## Additional Notes

The WMA provides a good compromise between the smoothness of SMA and the responsiveness of EMA. It's particularly useful for traders who want more weight on recent data but prefer the linear, predictable weighting scheme over the exponential approach of EMA.

The weighting scheme makes intuitive sense: if you're looking at a 10-period WMA, today's price has 10 times the influence of the price from 10 days ago. This gradual, linear reduction in weight is easier to understand than the exponential decay of EMA.

