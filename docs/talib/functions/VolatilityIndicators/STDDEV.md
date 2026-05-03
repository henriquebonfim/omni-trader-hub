# STDDEV - Standard Deviation

## Description

Standard Deviation is a statistical measure that quantifies the amount of variation or dispersion in a dataset. In technical analysis, it measures price volatility - how much prices deviate from their average. High standard deviation indicates high volatility (large price swings), while low standard deviation indicates low volatility (stable prices).

## Category
Statistical Functions / Volatility Indicators

## Calculation

Standard Deviation measures the average distance of data points from the mean:

### Formula (Population Standard Deviation)
```
STDDEV = sqrt(Σ(Price - Mean)² / n)
```

Where:
- Mean = Average price over n periods
- n = number of periods
- sqrt = square root

### Steps
```
Step 1: Calculate mean (average) of prices
Step 2: For each price, calculate squared difference from mean
Step 3: Average the squared differences
Step 4: Take square root of the result
```

### Example
For prices [10, 12, 14, 16, 18]:
```
Mean = (10+12+14+16+18)/5 = 14
Squared differences: 16, 4, 0, 4, 16
Average of squared differences: 40/5 = 8
STDDEV = sqrt(8) = 2.83
```

## Parameters

- **optInTimePeriod** (default: 5): Number of periods
  - Valid range: 2 to 100000
  - Common values: 10, 20, 30

- **optInNbDev** (default: 1.0): Number of deviations (multiplier)
  - Valid range: -3.0e+37 to 3.0e+37
  - Common values: 1.0, 2.0, 3.0

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- Standard Deviation values: `double[]` (in same units as price)

## Interpretation

### Volatility Assessment
- **High STDDEV**: High volatility, large price swings, risky
- **Low STDDEV**: Low volatility, stable prices, less risky
- **Rising STDDEV**: Volatility increasing
- **Falling STDDEV**: Volatility decreasing

### Application
1. **Risk Measurement**: Higher STDDEV = higher risk
2. **Volatility Analysis**: Track changes in volatility
3. **Bollinger Bands**: STDDEV defines band width
4. **Position Sizing**: Adjust size based on volatility
5. **Stop Loss**: Use STDDEV multiples for stops

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double stddevOutput[100];
int outBegIdx, outNBElement;

// Calculate 20-period Standard Deviation
TA_RetCode retCode = TA_STDDEV(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    20,                   // time period
    1.0,                  // number of deviations
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    stddevOutput          // output: STDDEV values
);
```

## Implementation Details

The TA-Lib STDDEV implementation:

1. **Mean Calculation**: Computes average over period
2. **Variance Calculation**: Calculates average squared deviation
3. **Standard Deviation**: Takes square root of variance
4. **Multiplier**: Applies nbDev parameter
5. **Rolling Window**: Efficiently updates for each bar

## Trading Applications

### 1. Volatility-Based Position Sizing
```
Position Size = Risk Amount / (Entry - Stop)
Stop Distance = Entry ± (STDDEV × Multiplier)
```

Adjust positions based on volatility.

### 2. Volatility Breakout
- **Setup**: STDDEV contracts to low levels
- **Signal**: Price breaks out with STDDEV expansion
- **Entry**: On breakout with rising STDDEV
- **Best in**: After consolidation periods

### 3. Bollinger Bands Application
Bollinger Bands use STDDEV:
```
Upper Band = SMA + (2 × STDDEV)
Lower Band = SMA - (2 × STDDEV)
```

### 4. Risk-Adjusted Stops
```
Stop Loss = Entry ± (2 × STDDEV)
```

Adapts to current volatility.

## Statistical Significance

### Normal Distribution
If prices follow normal distribution:
- **±1 STDDEV**: Contains ~68% of price data
- **±2 STDDEV**: Contains ~95% of price data
- **±3 STDDEV**: Contains ~99.7% of price data

Movements beyond 2-3 standard deviations are statistically rare.

## Advantages

1. **Objective**: Clear mathematical measure
2. **Volatility Quantification**: Precise volatility measurement
3. **Universal**: Works across all markets
4. **Risk Assessment**: Direct risk measurement
5. **Foundation**: Basis for many other indicators

## Limitations

1. **Lagging**: Based on historical data
2. **Assumes Normal Distribution**: Markets aren't always normal
3. **No Direction**: Doesn't indicate trend direction
4. **Outliers**: Sensitive to extreme values
5. **Period Dependent**: Results vary with period

## Related Functions

- **VAR**: Variance - STDDEV squared
- **BBANDS**: Bollinger Bands - uses STDDEV
- **ATR**: Average True Range - alternative volatility measure
- **NATR**: Normalized ATR - percentage-based volatility

## References

- [TA-Lib Source Code: ta_STDDEV.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_STDDEV.c)
- [Investopedia: Standard Deviation](https://www.investopedia.com/terms/s/standarddeviation.asp)
- [StockCharts: Standard Deviation](https://school.stockcharts.com/doku.php?id=technical_indicators:standard_deviation_volatility)

## Additional Notes

Standard Deviation is one of the most important statistical measures in trading and risk management. It's the foundation for:
- Bollinger Bands
- Sharpe Ratio
- Value at Risk (VaR)
- Portfolio optimization
- Risk-adjusted returns

John Bollinger popularized its use in technical analysis through Bollinger Bands, but STDDEV itself is useful for:
- Comparing volatility across securities
- Timing entries/exits based on volatility cycles
- Setting dynamic stops and targets
- Adjusting position sizes
- Assessing market conditions

