# NATR - Normalized Average True Range

## Description

The Normalized Average True Range (NATR) is a volatility indicator that measures the average true range as a percentage of the current price. It's similar to ATR but expressed as a percentage, making it easier to compare volatility across different securities and price levels. NATR helps identify relative volatility and provides a normalized measure of price volatility.

## Category
Volatility Indicators

## Author
J. Welles Wilder (adapted)

## Calculation

NATR is calculated as the percentage of ATR relative to the current price:

### Formula
```
NATR = (ATR / Close) × 100
```

Where:
- ATR = Average True Range
- Close = current closing price
- Result is expressed as percentage

### Example
If ATR = 2.5 and Close = 100:
```
NATR = (2.5 / 100) × 100 = 2.5%
```

## Parameters

- **optInTimePeriod** (default: 14): Period for ATR calculation
  - Valid range: 1 to 100000
  - Common values: 14 (standard), 20, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- NATR values: `double[]` (percentage)

## Interpretation

### NATR Values
- **High NATR**: High relative volatility
- **Low NATR**: Low relative volatility
- **Zero NATR**: No volatility (rare)
- **Increasing NATR**: Volatility increasing
- **Decreasing NATR**: Volatility decreasing

### Trading Applications

1. **Volatility Analysis**:
   - **High NATR**: High volatility periods
   - **Low NATR**: Low volatility periods
   - **NATR Trends**: Volatility trend analysis
   - **Best in**: Volatility-based strategies

2. **Risk Assessment**:
   - **High NATR**: High risk periods
   - **Low NATR**: Low risk periods
   - **NATR Patterns**: Risk pattern analysis
   - **Best in**: Risk management

3. **Market Analysis**:
   - **High NATR**: Unstable markets
   - **Low NATR**: Stable markets
   - **NATR Patterns**: Market regime identification
   - **Best in**: Market analysis

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double natrOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period NATR
TA_RetCode retCode = TA_NATR(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    natrOutput            // output: NATR values
);
```

## Implementation Details

The TA-Lib NATR implementation:

1. **ATR Calculation**: Calculates Average True Range
2. **Price Normalization**: Divides ATR by current price
3. **Percentage Conversion**: Converts to percentage
4. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Volatility-Based Strategy
- **Setup**: Track NATR over time
- **Entry**: When NATR reaches extremes
- **Exit**: When NATR returns to mean
- **Best in**: Volatility trading

### 2. Risk Management Strategy
- **Setup**: Use NATR for position sizing
- **Entry**: Reduce size during high NATR
- **Exit**: Increase size during low NATR
- **Best in**: Risk management

### 3. Market Regime Strategy
- **Setup**: Identify NATR regimes
- **Entry**: Different strategies for different regimes
- **Exit**: Switch strategies on regime change
- **Best in**: Adaptive trading

### 4. NATR Mean Reversion Strategy
- **Setup**: Track NATR mean reversion
- **Entry**: When NATR deviates from mean
- **Exit**: When NATR returns to mean
- **Best in**: Volatility trading

## NATR vs. ATR

| Aspect | NATR | ATR |
|--------|------|-----|
| Units | Percentage | Absolute |
| Comparison | Easy across securities | Difficult across securities |
| Scaling | Automatic | Manual |
| Interpretation | Relative volatility | Absolute volatility |
| Best For | Cross-security analysis | Single security |

## Advantages

1. **Normalized**: Percentage makes comparison easy
2. **Universal**: Works across all securities
3. **Scalable**: No manual scaling needed
4. **Clear**: Easy to understand percentage
5. **Portfolio**: Useful for portfolio analysis

## Limitations

1. **Still Lags**: Based on historical data
2. **Whipsaws**: Possible in choppy markets
3. **Period Sensitivity**: Results vary with period
4. **No Direction**: Doesn't indicate direction
5. **Context Dependent**: Needs interpretation

## Period Selection

### Short Periods (10-14)
- **Characteristics**: More responsive
- **Use**: Short-term trading
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Standard Periods (14-20)
- **Characteristics**: Balanced approach
- **Use**: General volatility analysis
- **Trade-off**: Good balance
- **Best for**: Most applications

### Long Periods (20-30)
- **Characteristics**: Smoother, less responsive
- **Use**: Long-term analysis
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Position trading

## Related Functions

- **ATR**: Average True Range - absolute version
- **TRANGE**: True Range - building block
- **STDDEV**: Standard Deviation - alternative volatility measure
- **VAR**: Variance - alternative volatility measure

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder
- [TA-Lib Source Code: ta_NATR.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_NATR.c)
- [Investopedia: Normalized Average True Range](https://www.investopedia.com/terms/n/natr.asp)
- [StockCharts: NATR](https://school.stockcharts.com/doku.php?id=technical_indicators:average_true_range_atr)

## Additional Notes

NATR was developed as an improvement over ATR, making it easier to compare volatility across different securities by using percentages instead of absolute values.

### Key Insights

1. **Percentage Advantage**:
   - Easy to compare across securities
   - No manual scaling required
   - Universal interpretation
   - Portfolio analysis friendly

2. **Volatility Measurement**:
   - Measures relative volatility
   - Higher NATR = higher volatility
   - Lower NATR = lower volatility
   - Always positive values

3. **Best Applications**:
   - Cross-security volatility analysis
   - Portfolio volatility assessment
   - Risk management
   - Market regime identification

4. **Trading Applications**:
   - Volatility-based strategies
   - Risk management
   - Position sizing
   - Stop placement

5. **Combination Strategies**:
   - Use with trend indicators
   - Combine with volume analysis
   - Use for volatility analysis
   - Multiple timeframe analysis

### Practical Tips

**For Volatility Analysis**:
- Track NATR over time
- Identify volatility regimes
- Use for volatility trading
- Monitor volatility changes

**For Risk Management**:
- Use NATR for position sizing
- Reduce size during high NATR
- Increase size during low NATR
- Monitor risk trends

**For Market Analysis**:
- Identify market regimes
- Use NATR for market classification
- Monitor NATR patterns
- Use for market timing

**For Portfolio Analysis**:
- Compare NATR across securities
- Rank by volatility
- Diversify by volatility
- Use for asset allocation

NATR is particularly valuable for traders who need to compare volatility across multiple securities or want a normalized version of ATR. It's excellent for portfolio analysis and provides clear volatility signals.

