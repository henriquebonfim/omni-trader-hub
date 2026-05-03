# TRIMA - Triangular Moving Average

## Description

The Triangular Moving Average (TRIMA) is a double-smoothed moving average that applies a simple moving average to another simple moving average. This creates a very smooth line that reduces noise and lag compared to a single SMA, but with more lag than a single SMA. It's particularly useful for identifying long-term trends.

## Category
Overlap Studies

## Calculation

TRIMA is calculated by applying SMA twice:

### Formula
```
TRIMA = SMA(SMA(Price, n), n)
```

Where:
- First SMA = Simple Moving Average of price over n periods
- Second SMA = Simple Moving Average of the first SMA over n periods
- n = period (typically same for both SMAs)

### Example
For a 5-period TRIMA:
```
Step 1: Calculate 5-period SMA of prices
Step 2: Calculate 5-period SMA of the first SMA
Result: TRIMA value
```

## Parameters

- **optInTimePeriod** (default: 30): Period for both SMAs
  - Valid range: 2 to 100000
  - Common values: 20, 30, 50

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- TRIMA values: `double[]`

## Interpretation

### Characteristics
- **Very Smooth**: Double smoothing creates very smooth line
- **High Lag**: More lag than single SMA
- **Trend Identification**: Excellent for long-term trends
- **Noise Reduction**: Filters out short-term fluctuations

### Usage
1. **Long-term Trends**:
   - TRIMA slope indicates trend direction
   - Price above TRIMA = uptrend
   - Price below TRIMA = downtrend

2. **Support/Resistance**:
   - TRIMA acts as dynamic support in uptrends
   - TRIMA acts as dynamic resistance in downtrends

3. **Trend Changes**:
   - Price crossing TRIMA signals major trend change
   - More reliable than faster MAs for major reversals

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double trimaOutput[100];
int outBegIdx, outNBElement;

// Calculate 20-period TRIMA
TA_RetCode retCode = TA_TRIMA(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    20,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    trimaOutput           // output: TRIMA values
);
```

## Implementation Details

The TA-Lib TRIMA implementation:

1. **First SMA**: Calculates SMA of prices
2. **Second SMA**: Calculates SMA of first SMA
3. **Double Smoothing**: Creates very smooth result
4. **Lookback**: Requires 2n-1 periods for first output

## Trading Strategies

### 1. Long-term Trend Following
- **Buy**: Price crosses above TRIMA
- **Sell**: Price crosses below TRIMA
- **Hold**: Stay in position while price on correct side
- **Best in**: Long-term position trading

### 2. TRIMA Slope Strategy
- **Buy**: TRIMA slope positive and price above TRIMA
- **Sell**: TRIMA slope negative and price below TRIMA
- **Exit**: When slope changes or price crosses
- **Best in**: Confirming trend direction

### 3. Multiple Timeframe
- **Higher TF**: Use TRIMA for major trend
- **Lower TF**: Use faster MA for entry timing
- **Rule**: Only trade in direction of higher TF TRIMA
- **Best in**: All timeframes

### 4. TRIMA + Price Action
- **Context**: TRIMA for trend
- **Entry**: Price patterns at TRIMA touches
- **Example**: Bull flag pullback to TRIMA
- **Confirmation**: Candlestick patterns
- **Best in**: Combining technical analysis

## Advantages

1. **Very Smooth**: Excellent noise reduction
2. **Trend Clarity**: Clear trend identification
3. **Reliable**: Fewer false signals than faster MAs
4. **Long-term Focus**: Perfect for position trading
5. **Simple**: Easy to understand and use

## Limitations

1. **High Lag**: Significant lag behind price
2. **Late Signals**: Misses early trend changes
3. **Not for Day Trading**: Too slow for short-term trading
4. **Whipsaws**: Still possible in choppy markets
5. **Period Sensitivity**: Results vary with period choice

## Comparison with Other MAs

| MA Type | Smoothness | Lag | Responsiveness | Best Use |
|---------|------------|-----|----------------|----------|
| SMA | Medium | Medium | Medium | General |
| TRIMA | High | High | Low | Long-term trends |
| EMA | Low | Low | High | Short-term |
| DEMA | Low | Very Low | Very High | Day trading |
| TEMA | Very Low | Very Low | Very High | Scalping |

## Related Functions

- **SMA**: Simple Moving Average - building block
- **EMA**: Exponential Moving Average - alternative smoothing
- **KAMA**: Kaufman Adaptive Moving Average - adaptive approach
- **MAMA**: MESA Adaptive Moving Average - cycle-based
- **T3**: T3 Moving Average - smooth with low lag

## References

- [TA-Lib Source Code: ta_TRIMA.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_TRIMA.c)
- [Investopedia: Triangular Moving Average](https://www.investopedia.com/terms/t/triangular-moving-average.asp)
- [StockCharts: Moving Averages](https://school.stockcharts.com/doku.php?id=technical_indicators:moving_averages)

## Additional Notes

The Triangular Moving Average gets its name from the triangular weighting pattern that results from double smoothing. While it's calculated as SMA(SMA(price)), the effective weighting pattern resembles a triangle.

### Key Insights

1. **Double Smoothing Effect**:
   - First SMA smooths price data
   - Second SMA smooths the first SMA
   - Result: Very smooth, lagging indicator
   - Excellent for major trend identification

2. **Period Selection**:
   - Longer periods = smoother, more lag
   - Shorter periods = less smooth, less lag
   - Balance based on trading timeframe
   - Common: 20-50 for daily charts

3. **Best Applications**:
   - Long-term trend identification
   - Position trading
   - Filtering out market noise
   - Confirming major trend changes

4. **Not Suitable For**:
   - Day trading (too slow)
   - Scalping (excessive lag)
   - Short-term reversals
   - Quick entry/exit strategies

5. **Combination Strategies**:
   - Use TRIMA for trend direction
   - Use faster MA for entry timing
   - Use oscillators for overbought/oversold
   - Use volume for confirmation

TRIMA is particularly valuable for investors and position traders who need to identify major trend changes while filtering out short-term market noise. It's one of the smoothest moving averages available and provides excellent clarity for long-term trend analysis.