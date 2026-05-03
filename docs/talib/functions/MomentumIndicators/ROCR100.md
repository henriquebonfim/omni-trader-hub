# ROCR100 - Rate of Change Ratio 100

## Description

The Rate of Change Ratio 100 (ROCR100) is a momentum indicator that measures the ratio of current price to price n periods ago, then multiplies by 100. It's similar to ROCR but expressed as a percentage, making it easier to interpret and compare across different securities. ROCR100 helps identify momentum changes and provides a normalized measure of price movement.

## Category
Momentum Indicators

## Author
Traditional Technical Analysis

## Calculation

ROCR100 is calculated as the ratio of current price to past price, multiplied by 100:

### Formula
```
ROCR100 = (Current Price / Price n periods ago) × 100
```

Where:
- Current Price = current closing price
- Price n periods ago = price n periods back
- Result is expressed as percentage

### Example
If current price is 110 and price 10 periods ago was 100:
```
ROCR100 = (110 / 100) × 100 = 110%
```

## Parameters

- **optInTimePeriod** (default: 10): Period for calculation
  - Valid range: 1 to 100000
  - Common values: 10, 14, 20

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- ROCR100 values: `double[]` (percentage)

## Interpretation

### ROCR100 Values
- **> 100**: Price appreciation (uptrend momentum)
- **< 100**: Price depreciation (downtrend momentum)
- **= 100**: No change in price (no momentum)
- **High Values**: Strong uptrend momentum
- **Low Values**: Strong downtrend momentum

### Trading Signals

1. **100 Line Crossovers**:
   - **Buy**: ROCR100 crosses above 100
   - **Sell**: ROCR100 crosses below 100
   - **Best in**: Momentum change detection

2. **Momentum Changes**:
   - **Rising ROCR100**: Momentum increasing
   - **Falling ROCR100**: Momentum decreasing
   - **Peak ROCR100**: Momentum peak (potential reversal)
   - **Trough ROCR100**: Momentum trough (potential reversal)

3. **Divergence**:
   - **Bullish**: Price lower lows, ROCR100 higher lows
   - **Bearish**: Price higher highs, ROCR100 lower highs
   - **Best in**: Trend exhaustion points

4. **Trend Strength**:
   - **Strong Uptrend**: ROCR100 consistently above 100 and rising
   - **Strong Downtrend**: ROCR100 consistently below 100 and falling
   - **Weak Trend**: ROCR100 oscillating around 100

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double rocr100Output[100];
int outBegIdx, outNBElement;

// Calculate 10-period ROCR100
TA_RetCode retCode = TA_ROCR100(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    10,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    rocr100Output         // output: ROCR100 values
);
```

## Implementation Details

The TA-Lib ROCR100 implementation:

1. **Price Ratio**: Calculates ratio of current to past price
2. **Percentage Conversion**: Multiplies by 100
3. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. 100 Line Strategy
- **Buy**: ROCR100 crosses above 100
- **Sell**: ROCR100 crosses below 100
- **Filter**: Only trade when |ROCR100 - 100| > 5
- **Best in**: Momentum change detection

### 2. Momentum Strategy
- **Buy**: ROCR100 rising and above 100
- **Sell**: ROCR100 falling and below 100
- **Exit**: ROCR100 momentum change
- **Best in**: Trend following

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and ROCR100
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. ROCR100 + Trend Strategy
- **Setup**: Use ROCR100 for timing
- **Entry**: Trend direction with ROCR100 timing
- **Exit**: ROCR100 reversal or trend change
- **Best in**: Trending markets

## ROCR100 vs. ROCR

| Aspect | ROCR100 | ROCR |
|--------|---------|------|
| Units | Percentage | Ratio |
| Comparison | Easy across securities | Easy across securities |
| Scaling | Automatic | Automatic |
| Interpretation | Percentage change | Ratio change |
| Best For | Cross-security analysis | Cross-security analysis |

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
4. **No Direction**: Doesn't indicate future direction
5. **Context Dependent**: Needs interpretation

## Period Selection

### Short Periods (5-10)
- **Characteristics**: More responsive
- **Use**: Short-term trading
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Standard Periods (10-20)
- **Characteristics**: Balanced approach
- **Use**: General momentum analysis
- **Trade-off**: Good balance
- **Best for**: Most applications

### Long Periods (20-50)
- **Characteristics**: Smoother, less responsive
- **Use**: Long-term analysis
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Position trading

## Related Functions

- **ROCR**: Rate of Change Ratio - ratio version
- **ROCP**: Rate of Change Percentage - percentage version
- **ROC**: Rate of Change - absolute version
- **MOM**: Momentum - absolute change version

## References

- [TA-Lib Source Code: ta_ROCR100.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_ROCR100.c)
- [Investopedia: Rate of Change](https://www.investopedia.com/terms/r/rateofchange.asp)
- [StockCharts: ROC](https://school.stockcharts.com/doku.php?id=technical_indicators:rate_of_change_roc)

## Additional Notes

ROCR100 was developed as an improvement over ROCR, making it easier to interpret by using percentages instead of ratios.

### Key Insights

1. **Percentage Advantage**:
   - Easy to compare across securities
   - No manual scaling required
   - Universal interpretation
   - Portfolio analysis friendly

2. **Momentum Measurement**:
   - Measures percentage momentum
   - > 100 = uptrend momentum
   - < 100 = downtrend momentum
   - 100 = no momentum

3. **Best Applications**:
   - Cross-security momentum analysis
   - Portfolio momentum assessment
   - Trend change detection
   - Momentum strength assessment

4. **Signal Interpretation**:
   - 100 line crossovers = momentum changes
   - Rising/falling = momentum changes
   - Peaks/troughs = potential reversals
   - Divergences = trend exhaustion

5. **Combination Strategies**:
   - Use with trend indicators
   - Combine with volume analysis
   - Use for momentum analysis
   - Multiple timeframe analysis

### Practical Tips

**For Momentum Analysis**:
- Track ROCR100 over time
- Identify momentum regimes
- Use for momentum trading
- Monitor momentum changes

**For Trend Following**:
- Use ROCR100 for trend direction
- Enter on momentum confirmation
- Exit on momentum loss
- Use volume for confirmation

**For Divergence Trading**:
- Identify price vs. ROCR100 divergence
- Wait for confirmation
- Use support/resistance
- Set stops beyond extremes

**For Portfolio Analysis**:
- Compare ROCR100 across securities
- Rank by momentum strength
- Diversify by momentum
- Use for asset allocation

ROCR100 is particularly valuable for traders who need to compare momentum across multiple securities or want a normalized version of ROC. It's excellent for portfolio analysis and provides clear momentum signals.

