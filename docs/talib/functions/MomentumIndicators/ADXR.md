# ADXR - Average Directional Movement Index Rating

## Description

The Average Directional Movement Index Rating (ADXR) is a trend strength indicator that measures the average of the current ADX and the ADX from a specified number of periods ago. It's developed by J. Welles Wilder as a smoothed version of ADX that reduces noise and provides more stable trend strength readings. ADXR helps identify trend strength and provides a more reliable measure of directional movement.

## Category
Momentum Indicators

## Author
J. Welles Wilder

## Calculation

ADXR is calculated as the average of current ADX and past ADX:

### Formula
```
ADXR = (ADX + ADX[n periods ago]) / 2
```

Where:
- ADX = current Average Directional Index
- ADX[n periods ago] = ADX from n periods back
- n = smoothing period (default: 14)

### Example
If current ADX = 25 and ADX 14 periods ago = 20:
```
ADXR = (25 + 20) / 2 = 22.5
```

## Parameters

- **optInTimePeriod** (default: 14): Period for ADX calculation
  - Valid range: 2 to 100000
  - Common values: 14 (standard), 21, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- ADXR values: `double[]` (range: 0 to 100)

## Interpretation

### ADXR Values
- **0-25**: Weak trend
- **25-50**: Moderate trend
- **50-75**: Strong trend
- **75-100**: Very strong trend

### Trading Signals

1. **Trend Strength**:
   - **Weak Trend**: ADXR < 25
   - **Moderate Trend**: ADXR 25-50
   - **Strong Trend**: ADXR 50-75
   - **Very Strong Trend**: ADXR > 75

2. **Trend Changes**:
   - **Rising ADXR**: Trend strengthening
   - **Falling ADXR**: Trend weakening
   - **Peak ADXR**: Trend peak (potential reversal)
   - **Trough ADXR**: Trend trough (potential reversal)

3. **Divergence**:
   - **Bullish**: Price lower lows, ADXR higher lows
   - **Bearish**: Price higher highs, ADXR lower highs
   - **Best in**: Trend exhaustion points

4. **Trend Confirmation**:
   - **High ADXR**: Strong trend confirmation
   - **Low ADXR**: Weak trend or sideways
   - **Rising ADXR**: Trend strengthening
   - **Falling ADXR**: Trend weakening

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double adxrOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period ADXR
TA_RetCode retCode = TA_ADXR(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    adxrOutput            // output: ADXR values
);
```

## Implementation Details

The TA-Lib ADXR implementation:

1. **ADX Calculation**: Calculates current ADX
2. **Past ADX**: Retrieves ADX from n periods ago
3. **Averaging**: Averages current and past ADX
4. **Lookback**: Requires 2×n periods for first output

## Trading Strategies

### 1. Trend Strength Strategy
- **Setup**: Track ADXR over time
- **Entry**: When ADXR indicates strong trend
- **Exit**: When ADXR indicates weak trend
- **Best in**: Trend following

### 2. Trend Change Strategy
- **Setup**: Identify ADXR changes
- **Entry**: On trend strengthening
- **Exit**: On trend weakening
- **Best in**: Trend change detection

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and ADXR
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. ADXR + Direction Strategy
- **Setup**: Use ADXR for trend strength
- **Entry**: Direction with ADXR confirmation
- **Exit**: ADXR reversal or direction change
- **Best in**: Trend following

## ADXR vs. ADX

| Aspect | ADXR | ADX |
|--------|------|-----|
| Smoothing | Double smoothing | Single smoothing |
| Stability | More stable | Less stable |
| Signals | Fewer, more reliable | More, less reliable |
| Noise | Less noisy | More noisy |
| Best For | Trend following | Short-term analysis |

## Advantages

1. **Stable**: Double smoothing reduces noise
2. **Reliable**: Fewer false signals than ADX
3. **Universal**: Works across all markets
4. **Clear**: Easy to interpret
5. **Versatile**: Many applications

## Limitations

1. **Less Responsive**: Slower than ADX
2. **Still Lags**: Based on historical data
3. **Whipsaws**: Possible in choppy markets
4. **Period Sensitivity**: Results vary with period
5. **Learning Curve**: Requires understanding of concept

## Period Selection

### Short Periods (10-14)
- **Characteristics**: More responsive
- **Use**: Short-term trading
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Standard Periods (14-21)
- **Characteristics**: Balanced approach
- **Use**: General trend analysis
- **Trade-off**: Good balance
- **Best for**: Most applications

### Long Periods (21-30)
- **Characteristics**: Smoother, less responsive
- **Use**: Long-term analysis
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Position trading

## Related Functions

- **ADX**: Average Directional Index - building block
- **PLUS_DI**: Plus Directional Indicator - upward movement
- **MINUS_DI**: Minus Directional Indicator - downward movement
- **DX**: Directional Movement - raw calculation

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder
- [TA-Lib Source Code: ta_ADXR.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_ADXR.c)
- [Investopedia: ADXR](https://www.investopedia.com/terms/a/adxr.asp)
- [StockCharts: ADXR](https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx)

## Additional Notes

J. Welles Wilder developed ADXR as a smoothed version of ADX to reduce noise and provide more stable trend strength readings.

### Key Insights

1. **Double Smoothing**:
   - Averages current and past ADX
   - Reduces noise while maintaining trend information
   - More stable than ADX
   - Better for trend following

2. **Trend Strength Measurement**:
   - Measures average trend strength
   - Higher ADXR = stronger trend
   - Lower ADXR = weaker trend
   - Rising ADXR = trend strengthening

3. **Best Applications**:
   - Trend strength analysis
   - Trend following
   - Trend change detection
   - Trend confirmation

4. **Signal Interpretation**:
   - < 25 = weak trend
   - 25-50 = moderate trend
   - 50-75 = strong trend
   - > 75 = very strong trend

5. **Combination Strategies**:
   - Use with direction indicators
   - Combine with price analysis
   - Use for trend confirmation
   - Multiple timeframe analysis

### Practical Tips

**For Trend Strength Analysis**:
- Track ADXR over time
- Identify trend strength regimes
- Use for trend confirmation
- Monitor trend changes

**For Trend Following**:
- Use ADXR for trend strength
- Enter on strong trend confirmation
- Exit on trend weakening
- Use direction indicators for direction

**For Trend Change Detection**:
- Watch for ADXR changes
- Rising ADXR = trend strengthening
- Falling ADXR = trend weakening
- Use for trend reversal signals

**For Risk Management**:
- Use ADXR for position sizing
- Reduce size during weak trends
- Increase size during strong trends
- Use for stop placement

ADXR is particularly valuable for traders who want a more stable trend strength indicator than ADX. It's excellent for trend following and provides more reliable signals for trend strength changes.
