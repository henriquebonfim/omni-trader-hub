# ROCR - Rate of Change Ratio

## Description

The Rate of Change Ratio (ROCR) is a momentum indicator that measures the ratio of current price to price n periods ago. It's similar to ROC but expressed as a ratio rather than absolute change, making it easier to compare across different securities and price levels. ROCR helps identify momentum changes and provides a normalized measure of price movement.

## Category
Momentum Indicators

## Author
Traditional Technical Analysis

## Calculation

ROCR is calculated as the ratio of current price to past price:

### Formula
```
ROCR = Current Price / Price n periods ago
```

Where:
- Current Price = current closing price
- Price n periods ago = price n periods back
- Result is expressed as ratio

### Example
If current price is 110 and price 10 periods ago was 100:
```
ROCR = 110 / 100 = 1.1
```

## Parameters

- **optInTimePeriod** (default: 10): Period for calculation
  - Valid range: 1 to 100000
  - Common values: 10, 14, 20

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- ROCR values: `double[]` (ratio)

## Interpretation

### ROCR Values
- **> 1.0**: Price appreciation (uptrend momentum)
- **< 1.0**: Price depreciation (downtrend momentum)
- **= 1.0**: No change in price (no momentum)
- **High Values**: Strong uptrend momentum
- **Low Values**: Strong downtrend momentum

### Trading Signals

1. **1.0 Line Crossovers**:
   - **Buy**: ROCR crosses above 1.0
   - **Sell**: ROCR crosses below 1.0
   - **Best in**: Momentum change detection

2. **Momentum Changes**:
   - **Rising ROCR**: Momentum increasing
   - **Falling ROCR**: Momentum decreasing
   - **Peak ROCR**: Momentum peak (potential reversal)
   - **Trough ROCR**: Momentum trough (potential reversal)

3. **Divergence**:
   - **Bullish**: Price lower lows, ROCR higher lows
   - **Bearish**: Price higher highs, ROCR lower highs
   - **Best in**: Trend exhaustion points

4. **Trend Strength**:
   - **Strong Uptrend**: ROCR consistently above 1.0 and rising
   - **Strong Downtrend**: ROCR consistently below 1.0 and falling
   - **Weak Trend**: ROCR oscillating around 1.0

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double rocrOutput[100];
int outBegIdx, outNBElement;

// Calculate 10-period ROCR
TA_RetCode retCode = TA_ROCR(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    10,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    rocrOutput            // output: ROCR values
);
```

## Implementation Details

The TA-Lib ROCR implementation:

1. **Price Ratio**: Calculates ratio of current to past price
2. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. 1.0 Line Strategy
- **Buy**: ROCR crosses above 1.0
- **Sell**: ROCR crosses below 1.0
- **Filter**: Only trade when |ROCR - 1.0| > 0.05
- **Best in**: Momentum change detection

### 2. Momentum Strategy
- **Buy**: ROCR rising and above 1.0
- **Sell**: ROCR falling and below 1.0
- **Exit**: ROCR momentum change
- **Best in**: Trend following

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and ROCR
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. ROCR + Trend Strategy
- **Setup**: Use ROCR for timing
- **Entry**: Trend direction with ROCR timing
- **Exit**: ROCR reversal or trend change
- **Best in**: Trending markets

## ROCR vs. ROC

| Aspect | ROCR | ROC |
|--------|------|-----|
| Units | Ratio | Absolute |
| Comparison | Easy across securities | Difficult across securities |
| Scaling | Automatic | Manual |
| Interpretation | Ratio change | Absolute change |
| Best For | Cross-security analysis | Single security |

## Advantages

1. **Normalized**: Ratio makes comparison easy
2. **Universal**: Works across all securities
3. **Scalable**: No manual scaling needed
4. **Clear**: Easy to understand ratio
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

- **ROC**: Rate of Change - absolute version
- **ROCP**: Rate of Change Percentage - percentage version
- **MOM**: Momentum - absolute change version

## References

- [TA-Lib Source Code: ta_ROCR.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_ROCR.c)
- [Investopedia: Rate of Change](https://www.investopedia.com/terms/r/rateofchange.asp)
- [StockCharts: ROC](https://school.stockcharts.com/doku.php?id=technical_indicators:rate_of_change_roc)

## Additional Notes

ROCR was developed as an improvement over ROC, making it easier to compare momentum across different securities by using ratios instead of absolute values.

### Key Insights

1. **Ratio Advantage**:
   - Easy to compare across securities
   - No manual scaling required
   - Universal interpretation
   - Portfolio analysis friendly

2. **Momentum Measurement**:
   - Measures ratio momentum
   - > 1.0 = uptrend momentum
   - < 1.0 = downtrend momentum
   - 1.0 = no momentum

3. **Best Applications**:
   - Cross-security momentum analysis
   - Portfolio momentum assessment
   - Trend change detection
   - Momentum strength assessment

4. **Signal Interpretation**:
   - 1.0 line crossovers = momentum changes
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
- Track ROCR over time
- Identify momentum regimes
- Use for momentum trading
- Monitor momentum changes

**For Trend Following**:
- Use ROCR for trend direction
- Enter on momentum confirmation
- Exit on momentum loss
- Use volume for confirmation

**For Divergence Trading**:
- Identify price vs. ROCR divergence
- Wait for confirmation
- Use support/resistance
- Set stops beyond extremes

**For Portfolio Analysis**:
- Compare ROCR across securities
- Rank by momentum strength
- Diversify by momentum
- Use for asset allocation

ROCR is particularly valuable for traders who need to compare momentum across multiple securities or want a normalized version of ROC. It's excellent for portfolio analysis and provides clear momentum signals.

