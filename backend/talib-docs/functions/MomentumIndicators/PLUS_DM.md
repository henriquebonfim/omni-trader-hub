# PLUS_DM - Plus Directional Movement

## Description

The Plus Directional Movement (PLUS_DM) is a trend indicator that measures the amount of upward price movement over a specified period. It's part of the Directional Movement System developed by J. Welles Wilder and works alongside MINUS_DM to identify trend direction and strength. PLUS_DM helps identify bullish trends and provides signals for upward price movement.

## Category
Momentum Indicators

## Author
J. Welles Wilder

## Calculation

PLUS_DM is calculated using directional movement:

### Step 1: Calculate Plus Delta
```
diffP = Current High - Previous High
diffM = Previous Low - Current Low
```

### Step 2: Determine +DM for Current Bar
```
If (diffP > 0) AND (diffP > diffM):
    +DM = diffP
Else:
    +DM = 0
```

### Step 3: Apply Smoothing (when period > 1)
```
For first period bars:
    Sum all +DM values

For subsequent bars:
    Smoothed +DM = Previous Smoothed +DM - (Previous Smoothed +DM / period) + Current +DM
```

This uses Wilder's smoothing method, which is similar to an exponential moving average but with the smoothing factor = 1/period.

### Output
```
PLUS_DM = Smoothed +DM
```

**Note**: PLUS_DM returns the raw directional movement value (not normalized). For the normalized indicator (0-100 scale), use PLUS_DI which divides by True Range.

## Parameters

- **optInTimePeriod** (default: 14): Period for calculation
  - Valid range: 1 to 100000
  - Common values: 14 (standard), 21, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- PLUS_DM values: `double[]` (range: 0 to 100)

## Interpretation

### PLUS_DM Values
- **0-25**: Weak upward movement
- **25-50**: Moderate upward movement
- **50-75**: Strong upward movement
- **75-100**: Very strong upward movement

### Trading Signals

1. **Trend Direction**:
   - **PLUS_DM > MINUS_DM**: Uptrend
   - **PLUS_DM < MINUS_DM**: Downtrend
   - **PLUS_DM = MINUS_DM**: Sideways

2. **Trend Strength**:
   - **High PLUS_DM**: Strong upward movement
   - **Low PLUS_DM**: Weak upward movement
   - **Rising PLUS_DM**: Upward movement strengthening
   - **Falling PLUS_DM**: Upward movement weakening

3. **Crossovers**:
   - **Buy**: PLUS_DM crosses above MINUS_DM
   - **Sell**: PLUS_DM crosses below MINUS_DM
   - **Best in**: Trend change detection

4. **Divergence**:
   - **Bullish**: Price lower lows, PLUS_DM higher lows
   - **Bearish**: Price higher highs, PLUS_DM lower highs
   - **Best in**: Trend exhaustion points

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double plusDmOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period PLUS_DM
TA_RetCode retCode = TA_PLUS_DM(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    plusDmOutput         // output: PLUS_DM values
);
```

## Implementation Details

The TA-Lib PLUS_DM implementation:

1. **Directional Movement**: Calculates +DM for each period
2. **True Range**: Calculates TR for each period
3. **Smoothing**: Applies EMA to both +DM and TR
4. **PLUS_DM**: Calculates ratio and converts to percentage
5. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Trend Direction Strategy
- **Buy**: PLUS_DM > MINUS_DM
- **Sell**: PLUS_DM < MINUS_DM
- **Hold**: When PLUS_DM = MINUS_DM
- **Best in**: Trend following

### 2. Crossover Strategy
- **Buy**: PLUS_DM crosses above MINUS_DM
- **Sell**: PLUS_DM crosses below MINUS_DM
- **Filter**: Only trade when |PLUS_DM - MINUS_DM| > 5
- **Best in**: Trend change detection

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and PLUS_DM
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. PLUS_DM + ADX Strategy
- **Setup**: Use PLUS_DM for direction, ADX for strength
- **Entry**: Direction with strength confirmation
- **Exit**: Direction change or strength loss
- **Best in**: Trend following

## PLUS_DM vs. MINUS_DM

| Aspect | PLUS_DM | MINUS_DM |
|--------|---------|----------|
| Direction | Upward movement | Downward movement |
| Signal | Bullish | Bearish |
| Crossover | Above = uptrend | Above = downtrend |
| Best For | Uptrend identification | Downtrend identification |

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

- **MINUS_DM**: Minus Directional Movement - downward movement
- **ADX**: Average Directional Index - trend strength
- **ADXR**: Average Directional Index Rating - smoothed ADX
- **DX**: Directional Movement - raw calculation

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder
- [TA-Lib Source Code: ta_PLUS_DM.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_PLUS_DM.c)
- [Investopedia: Plus Directional Movement](https://www.investopedia.com/terms/p/plusdm.asp)
- [StockCharts: Plus Directional Movement](https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx)

## Additional Notes

J. Welles Wilder developed PLUS_DM as part of the Directional Movement System to measure upward price movement strength.

### Key Insights

1. **Directional Movement**:
   - Measures upward price movement
   - Higher PLUS_DM = stronger uptrend
   - Lower PLUS_DM = weaker uptrend
   - Rising PLUS_DM = uptrend strengthening

2. **Trend Identification**:
   - PLUS_DM > MINUS_DM = uptrend
   - PLUS_DM < MINUS_DM = downtrend
   - PLUS_DM = MINUS_DM = sideways
   - Use for trend direction

3. **Best Applications**:
   - Trend direction identification
   - Trend strength analysis
   - Trend change detection
   - Trend confirmation

4. **Signal Interpretation**:
   - < 25 = weak upward movement
   - 25-50 = moderate upward movement
   - 50-75 = strong upward movement
   - > 75 = very strong upward movement

5. **Combination Strategies**:
   - Use with MINUS_DM for direction
   - Combine with ADX for strength
   - Use for trend confirmation
   - Multiple timeframe analysis

### Practical Tips

**For Trend Direction**:
- Use PLUS_DM vs. MINUS_DM for direction
- PLUS_DM > MINUS_DM = uptrend
- PLUS_DM < MINUS_DM = downtrend
- Watch for crossovers

**For Trend Strength**:
- Track PLUS_DM over time
- Rising PLUS_DM = strengthening
- Falling PLUS_DM = weakening
- Use for trend confirmation

**For Trend Changes**:
- Watch for PLUS_DM crossovers
- Confirm with price action
- Use volume for validation
- Set stops beyond recent extremes

**For Risk Management**:
- Use PLUS_DM for position sizing
- Reduce size during weak trends
- Increase size during strong trends
- Use for stop placement

PLUS_DM is particularly valuable for traders who want to identify trend direction and strength. It's excellent for trend following and provides clear signals for upward price movement.
