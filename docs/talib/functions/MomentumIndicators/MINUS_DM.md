# MINUS_DM - Minus Directional Movement

## Description

The Minus Directional Movement (MINUS_DM) is a trend indicator that measures the amount of downward price movement over a specified period. It's part of the Directional Movement System developed by J. Welles Wilder and works alongside PLUS_DM to identify trend direction and strength. MINUS_DM helps identify bearish trends and provides signals for downward price movement.

## Category
Momentum Indicators

## Author
J. Welles Wilder

## Calculation

MINUS_DM is calculated using directional movement:

### Step 1: Calculate Minus Delta
```
diffP = Current High - Previous High
diffM = Previous Low - Current Low
```

### Step 2: Determine -DM for Current Bar
```
If (diffM > 0) AND (diffP < diffM):
    -DM = diffM
Else:
    -DM = 0
```

### Step 3: Apply Smoothing (when period > 1)
```
For first period bars:
    Sum all -DM values

For subsequent bars:
    Smoothed -DM = Previous Smoothed -DM - (Previous Smoothed -DM / period) + Current -DM
```

This uses Wilder's smoothing method, which is similar to an exponential moving average but with the smoothing factor = 1/period.

### Output
```
MINUS_DM = Smoothed -DM
```

**Note**: MINUS_DM returns the raw directional movement value (not normalized). For the normalized indicator (0-100 scale), use MINUS_DI which divides by True Range.

## Parameters

- **optInTimePeriod** (default: 14): Period for calculation
  - Valid range: 1 to 100000
  - Common values: 14 (standard), 21, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- MINUS_DM values: `double[]` (range: 0 to 100)

## Interpretation

### MINUS_DM Values
- **0-25**: Weak downward movement
- **25-50**: Moderate downward movement
- **50-75**: Strong downward movement
- **75-100**: Very strong downward movement

### Trading Signals

1. **Trend Direction**:
   - **MINUS_DM > PLUS_DM**: Downtrend
   - **MINUS_DM < PLUS_DM**: Uptrend
   - **MINUS_DM = PLUS_DM**: Sideways

2. **Trend Strength**:
   - **High MINUS_DM**: Strong downward movement
   - **Low MINUS_DM**: Weak downward movement
   - **Rising MINUS_DM**: Downward movement strengthening
   - **Falling MINUS_DM**: Downward movement weakening

3. **Crossovers**:
   - **Buy**: MINUS_DM crosses below PLUS_DM
   - **Sell**: MINUS_DM crosses above PLUS_DM
   - **Best in**: Trend change detection

4. **Divergence**:
   - **Bullish**: Price lower lows, MINUS_DM higher lows
   - **Bearish**: Price higher highs, MINUS_DM lower highs
   - **Best in**: Trend exhaustion points

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double minusDmOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period MINUS_DM
TA_RetCode retCode = TA_MINUS_DM(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    minusDmOutput        // output: MINUS_DM values
);
```

## Implementation Details

The TA-Lib MINUS_DM implementation:

1. **Directional Movement**: Calculates -DM for each period
2. **True Range**: Calculates TR for each period
3. **Smoothing**: Applies EMA to both -DM and TR
4. **MINUS_DM**: Calculates ratio and converts to percentage
5. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Trend Direction Strategy
- **Buy**: MINUS_DM < PLUS_DM
- **Sell**: MINUS_DM > PLUS_DM
- **Hold**: When MINUS_DM = PLUS_DM
- **Best in**: Trend following

### 2. Crossover Strategy
- **Buy**: MINUS_DM crosses below PLUS_DM
- **Sell**: MINUS_DM crosses above PLUS_DM
- **Filter**: Only trade when |MINUS_DM - PLUS_DM| > 5
- **Best in**: Trend change detection

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and MINUS_DM
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. MINUS_DM + ADX Strategy
- **Setup**: Use MINUS_DM for direction, ADX for strength
- **Entry**: Direction with strength confirmation
- **Exit**: Direction change or strength loss
- **Best in**: Trend following

## MINUS_DM vs. PLUS_DM

| Aspect | MINUS_DM | PLUS_DM |
|--------|----------|---------|
| Direction | Downward movement | Upward movement |
| Signal | Bearish | Bullish |
| Crossover | Above = downtrend | Above = uptrend |
| Best For | Downtrend identification | Uptrend identification |

## Advantages

1. **Directional**: Clear trend direction signals
2. **Universal**: Works across all markets
3. **Clear**: Easy to interpret
4. **Versatile**: Many applications
5. **Reliable**: Fewer false signals

## Limitations

1. **Still Lags**: Based on historical data
2. **Whipsaws**: Possible in choppy markets
3. **Period Sensitivity**: Results vary with period
4. **No Magnitude**: Doesn't measure price movement size
5. **Context Dependent**: Needs interpretation

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

- **PLUS_DM**: Plus Directional Movement - upward movement
- **ADX**: Average Directional Index - trend strength
- **ADXR**: Average Directional Index Rating - smoothed ADX
- **DX**: Directional Movement - raw calculation

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder
- [TA-Lib Source Code: ta_MINUS_DM.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_MINUS_DM.c)
- [Investopedia: Minus Directional Movement](https://www.investopedia.com/terms/m/minusdm.asp)
- [StockCharts: Minus Directional Movement](https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx)

## Additional Notes

J. Welles Wilder developed MINUS_DM as part of the Directional Movement System to measure downward price movement strength.

### Key Insights

1. **Directional Movement**:
   - Measures downward price movement
   - Higher MINUS_DM = stronger downtrend
   - Lower MINUS_DM = weaker downtrend
   - Rising MINUS_DM = downtrend strengthening

2. **Trend Identification**:
   - MINUS_DM > PLUS_DM = downtrend
   - MINUS_DM < PLUS_DM = uptrend
   - MINUS_DM = PLUS_DM = sideways
   - Use for trend direction

3. **Best Applications**:
   - Trend direction identification
   - Trend strength analysis
   - Trend change detection
   - Trend confirmation

4. **Signal Interpretation**:
   - < 25 = weak downward movement
   - 25-50 = moderate downward movement
   - 50-75 = strong downward movement
   - > 75 = very strong downward movement

5. **Combination Strategies**:
   - Use with PLUS_DM for direction
   - Combine with ADX for strength
   - Use for trend confirmation
   - Multiple timeframe analysis

### Practical Tips

**For Trend Direction**:
- Use MINUS_DM vs. PLUS_DM for direction
- MINUS_DM > PLUS_DM = downtrend
- MINUS_DM < PLUS_DM = uptrend
- Watch for crossovers

**For Trend Strength**:
- Track MINUS_DM over time
- Rising MINUS_DM = strengthening
- Falling MINUS_DM = weakening
- Use for trend confirmation

**For Trend Changes**:
- Watch for MINUS_DM crossovers
- Confirm with price action
- Use volume for validation
- Set stops beyond recent extremes

**For Risk Management**:
- Use MINUS_DM for position sizing
- Reduce size during weak trends
- Increase size during strong trends
- Use for stop placement

MINUS_DM is particularly valuable for traders who want to identify trend direction and strength. It's excellent for trend following and provides clear signals for downward price movement.
