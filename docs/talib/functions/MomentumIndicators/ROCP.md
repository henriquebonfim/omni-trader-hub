# ROCP - Rate of Change Percentage

## Description

The Rate of Change Percentage (ROCP) is a momentum indicator that measures the percentage change in price over a specified period. It's similar to ROC but expressed as a percentage, making it easier to compare across different securities and price levels. ROCP helps identify momentum changes and provides a normalized measure of price movement.

## Category
Momentum Indicators

## Author
Traditional Technical Analysis

## Calculation

ROCP is calculated as the fractional change in price over a period:

### Formula
```
ROCP = (Current Price - Price n periods ago) / Price n periods ago
```

Where:
- Current Price = current closing price
- Price n periods ago = price n periods back
- Result is expressed as a decimal (not percentage)

### Example
If current price is 110 and price 10 periods ago was 100:
```
ROCP = (110 - 100) / 100 = 0.10 (which represents 10%)
```

**Note**: Unlike ROC which multiplies by 100, ROCP returns the raw fractional change. For example, a 10% increase returns 0.10, not 10.0. This makes ROCP equivalent to ROC/100.

## Parameters

- **optInTimePeriod** (default: 10): Period for calculation
  - Valid range: 1 to 100000
  - Common values: 10, 14, 20

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- ROCP values: `double[]` (percentage)

## Interpretation

### ROCP Values
- **Positive**: Price appreciation (uptrend momentum)
- **Negative**: Price depreciation (downtrend momentum)
- **Zero**: No change in price (no momentum)
- **High Positive**: Strong uptrend momentum
- **High Negative**: Strong downtrend momentum

### Trading Signals

1. **Zero Line Crossovers**:
   - **Buy**: ROCP crosses above 0
   - **Sell**: ROCP crosses below 0
   - **Best in**: Momentum change detection

2. **Momentum Changes**:
   - **Rising ROCP**: Momentum increasing
   - **Falling ROCP**: Momentum decreasing
   - **Peak ROCP**: Momentum peak (potential reversal)
   - **Trough ROCP**: Momentum trough (potential reversal)

3. **Divergence**:
   - **Bullish**: Price lower lows, ROCP higher lows
   - **Bearish**: Price higher highs, ROCP lower highs
   - **Best in**: Trend exhaustion points

4. **Trend Strength**:
   - **Strong Uptrend**: ROCP consistently positive and rising
   - **Strong Downtrend**: ROCP consistently negative and falling
   - **Weak Trend**: ROCP oscillating around zero

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double rocpOutput[100];
int outBegIdx, outNBElement;

// Calculate 10-period ROCP
TA_RetCode retCode = TA_ROCP(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    10,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    rocpOutput            // output: ROCP values
);
```

## Implementation Details

The TA-Lib ROCP implementation:

1. **Price Difference**: Calculates difference between current and past price
2. **Percentage Calculation**: Converts to percentage
3. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Zero Line Strategy
- **Buy**: ROCP crosses above 0
- **Sell**: ROCP crosses below 0
- **Filter**: Only trade when |ROCP| > 5%
- **Best in**: Momentum change detection

### 2. Momentum Strategy
- **Buy**: ROCP rising and positive
- **Sell**: ROCP falling and negative
- **Exit**: ROCP momentum change
- **Best in**: Trend following

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and ROCP
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. ROCP + Trend Strategy
- **Setup**: Use ROCP for timing
- **Entry**: Trend direction with ROCP timing
- **Exit**: ROCP reversal or trend change
- **Best in**: Trending markets

## ROCP vs. ROC

| Aspect | ROCP | ROC |
|--------|------|-----|
| Units | Percentage | Absolute |
| Comparison | Easy across securities | Difficult across securities |
| Scaling | Automatic | Manual |
| Interpretation | Percentage change | Absolute change |
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
- **MOM**: Momentum - absolute change version
- **PERF**: Performance - similar concept
- **PPO**: Percentage Price Oscillator - similar concept

## References

- [TA-Lib Source Code: ta_ROCP.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_ROCP.c)
- [Investopedia: Rate of Change](https://www.investopedia.com/terms/r/rateofchange.asp)
- [StockCharts: ROC](https://school.stockcharts.com/doku.php?id=technical_indicators:rate_of_change_roc)

## Additional Notes

ROCP was developed as an improvement over ROC, making it easier to compare momentum across different securities by using percentages instead of absolute values.

### Key Insights

1. **Percentage Advantage**:
   - Easy to compare across securities
   - No manual scaling required
   - Universal interpretation
   - Portfolio analysis friendly

2. **Momentum Measurement**:
   - Measures percentage momentum
   - Positive = uptrend momentum
   - Negative = downtrend momentum
   - Zero = no momentum

3. **Best Applications**:
   - Cross-security momentum analysis
   - Portfolio momentum assessment
   - Trend change detection
   - Momentum strength assessment

4. **Signal Interpretation**:
   - Zero line crossovers = momentum changes
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
- Track ROCP over time
- Identify momentum regimes
- Use for momentum trading
- Monitor momentum changes

**For Trend Following**:
- Use ROCP for trend direction
- Enter on momentum confirmation
- Exit on momentum loss
- Use volume for confirmation

**For Divergence Trading**:
- Identify price vs. ROCP divergence
- Wait for confirmation
- Use support/resistance
- Set stops beyond extremes

**For Portfolio Analysis**:
- Compare ROCP across securities
- Rank by momentum strength
- Diversify by momentum
- Use for asset allocation

ROCP is particularly valuable for traders who need to compare momentum across multiple securities or want a normalized version of ROC. It's excellent for portfolio analysis and provides clear momentum signals.

