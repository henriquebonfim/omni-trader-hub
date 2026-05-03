# TRANGE - True Range

## Description

The True Range (TRANGE) is a volatility indicator that measures the true range of price movement over a single period. It's the building block for the Average True Range (ATR) indicator and provides insight into the volatility of price movements. TRANGE considers gaps between periods and provides a more accurate measure of volatility than simple high-low ranges.

## Category
Volatility Indicators

## Author
J. Welles Wilder

## Calculation

TRANGE is calculated as the maximum of three values:

### Formula
```
TRANGE = max(High - Low, |High - Previous Close|, |Low - Previous Close|)
```

Where:
- High = current period high
- Low = current period low
- Previous Close = previous period close
- | | = absolute value

### Example
For a period with:
- High = 105
- Low = 100
- Previous Close = 102

```
TRANGE = max(105 - 100, |105 - 102|, |100 - 102|)
       = max(5, 3, 2)
       = 5
```

## Parameters

None - TRANGE is calculated for each period

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- True range values: `double[]` (always positive)

## Interpretation

### TRANGE Values
- **High TRANGE**: High volatility period
- **Low TRANGE**: Low volatility period
- **Zero TRANGE**: No price movement (rare)
- **Increasing TRANGE**: Volatility increasing
- **Decreasing TRANGE**: Volatility decreasing

### Trading Applications

1. **Volatility Analysis**:
   - **High TRANGE**: High volatility periods
   - **Low TRANGE**: Low volatility periods
   - **TRANGE Trends**: Volatility trend analysis
   - **Best in**: Volatility-based strategies

2. **Risk Assessment**:
   - **High TRANGE**: High risk periods
   - **Low TRANGE**: Low risk periods
   - **TRANGE Patterns**: Risk pattern analysis
   - **Best in**: Risk management

3. **Market Analysis**:
   - **High TRANGE**: Unstable markets
   - **Low TRANGE**: Stable markets
   - **TRANGE Patterns**: Market regime identification
   - **Best in**: Market analysis

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double trangeOutput[100];
int outBegIdx, outNBElement;

// Calculate True Range
TA_RetCode retCode = TA_TRANGE(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    trangeOutput          // output: True Range values
);
```

## Implementation Details

The TA-Lib TRANGE implementation:

1. **Gap Consideration**: Considers gaps between periods
2. **Maximum Calculation**: Finds maximum of three values
3. **Absolute Values**: Uses absolute values for gaps
4. **Lookback**: Requires 1 period for first output

## Trading Strategies

### 1. Volatility-Based Strategy
- **Setup**: Track TRANGE over time
- **Entry**: When TRANGE reaches extremes
- **Exit**: When TRANGE returns to mean
- **Best in**: Volatility trading

### 2. Risk Management Strategy
- **Setup**: Use TRANGE for position sizing
- **Entry**: Reduce size during high TRANGE
- **Exit**: Increase size during low TRANGE
- **Best in**: Risk management

### 3. Market Regime Strategy
- **Setup**: Identify TRANGE regimes
- **Entry**: Different strategies for different regimes
- **Exit**: Switch strategies on regime change
- **Best in**: Adaptive trading

### 4. TRANGE Mean Reversion Strategy
- **Setup**: Track TRANGE mean reversion
- **Entry**: When TRANGE deviates from mean
- **Exit**: When TRANGE returns to mean
- **Best in**: Volatility trading

## TRANGE vs. High-Low Range

| Aspect | TRANGE | High-Low Range |
|--------|--------|----------------|
| Gaps | Considers gaps | Ignores gaps |
| Accuracy | More accurate | Less accurate |
| Volatility | Better volatility measure | Limited volatility measure |
| Best For | Volatility analysis | Simple range analysis |

## Advantages

1. **Accurate**: More accurate than simple ranges
2. **Gap Consideration**: Considers gaps between periods
3. **Universal**: Works across all markets
4. **Simple**: Easy to understand and calculate
5. **Versatile**: Many applications

## Limitations

1. **Single Period**: Only measures one period
2. **No Smoothing**: Raw volatility measure
3. **Noisy**: Can be very noisy
4. **Context Dependent**: Needs interpretation
5. **No Direction**: Doesn't indicate direction

## Related Functions

- **ATR**: Average True Range - smoothed version
- **NATR**: Normalized Average True Range - percentage version
- **STDDEV**: Standard Deviation - alternative volatility measure
- **VAR**: Variance - alternative volatility measure

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder
- [TA-Lib Source Code: ta_TRANGE.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_TRANGE.c)
- [Investopedia: True Range](https://www.investopedia.com/terms/t/truerange.asp)
- [StockCharts: True Range](https://school.stockcharts.com/doku.php?id=technical_indicators:average_true_range_atr)

## Additional Notes

J. Welles Wilder developed the True Range as part of his work on volatility indicators. The key insight is that gaps between periods can significantly affect volatility measurement and should be considered.

### Key Insights

1. **Gap Consideration**:
   - Considers gaps between periods
   - More accurate volatility measure
   - Better for gap analysis
   - Essential for ATR calculation

2. **Volatility Measurement**:
   - Measures true price volatility
   - Higher TRANGE = higher volatility
   - Lower TRANGE = lower volatility
   - Always positive values

3. **Best Applications**:
   - Volatility analysis
   - Risk assessment
   - Market regime identification
   - ATR calculation

4. **Trading Applications**:
   - Volatility-based strategies
   - Risk management
   - Position sizing
   - Stop placement

5. **Combination Strategies**:
   - Use with ATR for smoothing
   - Combine with trend indicators
   - Use for volatility analysis
   - Multiple timeframe analysis

### Practical Tips

**For Volatility Analysis**:
- Track TRANGE over time
- Identify volatility regimes
- Use for volatility trading
- Monitor volatility changes

**For Risk Management**:
- Use TRANGE for position sizing
- Reduce size during high TRANGE
- Increase size during low TRANGE
- Monitor risk trends

**For Market Analysis**:
- Identify market regimes
- Use TRANGE for market classification
- Monitor TRANGE patterns
- Use for market timing

**For ATR Calculation**:
- Use TRANGE as building block
- Apply smoothing for ATR
- Use for volatility analysis
- Combine with other indicators

TRANGE is particularly valuable for volatility analysis, risk assessment, and as a building block for the Average True Range indicator. It's an essential tool for understanding price volatility and market behavior.

