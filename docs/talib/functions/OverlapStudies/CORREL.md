# CORREL - Pearson's Correlation Coefficient

## Description

The Pearson's Correlation Coefficient (CORREL) measures the linear relationship between two data series. It ranges from -1 to +1, where +1 indicates perfect positive correlation, -1 indicates perfect negative correlation, and 0 indicates no linear relationship. CORREL is useful for analyzing relationships between different securities, indicators, or market data.

## Category
Statistical Functions

## Author
Karl Pearson

## Calculation

CORREL is calculated using the Pearson correlation formula:

### Formula
```
CORREL = Σ[(X - X̄)(Y - Ȳ)] / √[Σ(X - X̄)² × Σ(Y - Ȳ)²]
```

Where:
- X, Y = data series
- X̄, Ȳ = means of X and Y
- Σ = summation over the period

### Alternative Formula
```
CORREL = Covariance(X,Y) / (σX × σY)
```

Where:
- Covariance(X,Y) = covariance between X and Y
- σX, σY = standard deviations of X and Y

## Parameters

- **optInTimePeriod** (default: 30): Period for calculation
  - Valid range: 1 to 100000
  - Common values: 20, 30, 50

## Inputs
- **First** data series: `double[]`
- **Second** data series: `double[]`

## Outputs
- Correlation values: `double[]` (range: -1 to +1)

## Interpretation

### Correlation Values
- **+1.0**: Perfect positive correlation
- **+0.7 to +1.0**: Strong positive correlation
- **+0.3 to +0.7**: Moderate positive correlation
- **-0.3 to +0.3**: Weak correlation
- **-0.7 to -0.3**: Moderate negative correlation
- **-1.0 to -0.7**: Strong negative correlation
- **-1.0**: Perfect negative correlation

### Trading Applications

1. **Portfolio Analysis**:
   - **High Positive**: Securities move together
   - **High Negative**: Securities move opposite
   - **Low Correlation**: Independent movements
   - **Best in**: Portfolio diversification

2. **Indicator Analysis**:
   - **High Positive**: Indicators agree
   - **High Negative**: Indicators disagree
   - **Low Correlation**: Independent indicators
   - **Best in**: Indicator validation

3. **Market Analysis**:
   - **High Positive**: Markets move together
   - **High Negative**: Markets move opposite
   - **Low Correlation**: Independent markets
   - **Best in**: Market relationship analysis

## Usage Example

```c
// C/C++ Example
double series1[100], series2[100];
double correlation[100];
int outBegIdx, outNBElement;

// Calculate 30-period correlation
TA_RetCode retCode = TA_CORREL(
    0,                    // start index
    99,                   // end index
    series1,              // first data series
    series2,              // second data series
    30,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    correlation           // output: correlation values
);
```

## Implementation Details

The TA-Lib CORREL implementation:

1. **Data Validation**: Ensures both series have data
2. **Mean Calculation**: Calculates means for both series
3. **Covariance**: Calculates covariance between series
4. **Standard Deviations**: Calculates standard deviations
5. **Correlation**: Applies Pearson correlation formula

## Trading Strategies

### 1. Portfolio Diversification Strategy
- **Setup**: Calculate correlation between securities
- **Entry**: Low correlation securities
- **Exit**: When correlation increases
- **Best in**: Portfolio management

### 2. Indicator Validation Strategy
- **Setup**: Calculate correlation between indicators
- **Entry**: When indicators agree (high correlation)
- **Exit**: When indicators disagree (low correlation)
- **Best in**: Signal confirmation

### 3. Market Relationship Strategy
- **Setup**: Calculate correlation between markets
- **Entry**: When correlation breaks down
- **Exit**: When correlation re-establishes
- **Best in**: Market analysis

### 4. Correlation Mean Reversion Strategy
- **Setup**: Track correlation over time
- **Entry**: When correlation reaches extremes
- **Exit**: When correlation returns to mean
- **Best in**: Correlation trading

## Correlation Analysis

### 1. Strong Positive Correlation (+0.7 to +1.0)
- **Characteristics**: Securities move together
- **Trading**: Similar trading strategies
- **Risk**: High correlation risk
- **Best in**: Trend following

### 2. Moderate Positive Correlation (+0.3 to +0.7)
- **Characteristics**: Some relationship
- **Trading**: Partial diversification
- **Risk**: Moderate correlation risk
- **Best in**: Balanced portfolios

### 3. Weak Correlation (-0.3 to +0.3)
- **Characteristics**: Independent movements
- **Trading**: Independent strategies
- **Risk**: Low correlation risk
- **Best in**: Diversification

### 4. Strong Negative Correlation (-1.0 to -0.7)
- **Characteristics**: Opposite movements
- **Trading**: Hedge strategies
- **Risk**: Negative correlation risk
- **Best in**: Hedging

## Advantages

1. **Objective**: Mathematical relationship measure
2. **Universal**: Works with any data series
3. **Bounded**: Always between -1 and +1
4. **Clear**: Easy to interpret
5. **Versatile**: Many applications

## Limitations

1. **Linear Only**: Only measures linear relationships
2. **Lagging**: Based on historical data
3. **Period Dependent**: Results vary with period
4. **No Causation**: Correlation ≠ causation
5. **Outliers**: Sensitive to extreme values

## Related Functions

- **COVAR**: Covariance - related measure
- **STDDEV**: Standard Deviation - building block
- **VAR**: Variance - building block
- **LINEARREG**: Linear Regression - related analysis

## References

- **Book**: *Statistical Methods* by Karl Pearson
- [TA-Lib Source Code: ta_CORREL.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_CORREL.c)
- [Investopedia: Correlation](https://www.investopedia.com/terms/c/correlation.asp)
- [Statistics How To: Pearson Correlation](https://www.statisticshowto.com/probability-and-statistics/correlation-coefficient-formula/)

## Additional Notes

Karl Pearson developed the correlation coefficient as a measure of linear relationship between variables. It's one of the most important statistical measures in finance and technical analysis.

### Key Insights

1. **Relationship Measurement**:
   - Measures linear relationship strength
   - Range from -1 to +1
   - +1 = perfect positive correlation
   - -1 = perfect negative correlation

2. **Portfolio Applications**:
   - Diversification analysis
   - Risk management
   - Portfolio optimization
   - Asset allocation

3. **Indicator Applications**:
   - Indicator validation
   - Signal confirmation
   - Indicator selection
   - System optimization

4. **Market Applications**:
   - Market relationship analysis
   - Sector analysis
   - Currency correlation
   - Commodity correlation

5. **Trading Applications**:
   - Pair trading
   - Hedging strategies
   - Diversification
   - Risk management

### Practical Tips

**For Portfolio Analysis**:
- Calculate correlation between securities
- Use low correlation for diversification
- Monitor correlation changes
- Rebalance when correlation increases

**For Indicator Analysis**:
- Calculate correlation between indicators
- Use high correlation for confirmation
- Avoid redundant indicators
- Optimize indicator selection

**For Market Analysis**:
- Calculate correlation between markets
- Use for market relationship analysis
- Identify correlation breakdowns
- Use for hedging strategies

**For Risk Management**:
- Monitor correlation changes
- Use for position sizing
- Diversify across low correlation assets
- Hedge with negative correlation assets

CORREL is particularly valuable for portfolio management, risk analysis, and understanding relationships between different market data. It's an essential tool for quantitative analysis and systematic trading strategies.

