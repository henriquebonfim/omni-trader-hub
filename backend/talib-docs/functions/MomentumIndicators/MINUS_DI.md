# MINUS_DI - Minus Directional Indicator

## Description

The Minus Directional Indicator (MINUS_DI) is a trend indicator that measures the strength of downward price movement. It's part of the Directional Movement System developed by J. Welles Wilder and works alongside PLUS_DI to identify trend direction and strength. MINUS_DI helps identify bearish trends and provides signals for downward price movement.

## Category
Momentum Indicators

## Author
J. Welles Wilder

## Calculation

MINUS_DI is calculated using directional movement:

### Step 1: Calculate Minus Directional Movement (-DM)
```
-DM = Previous Low - Low (if positive, otherwise 0)
```

### Step 2: Calculate True Range (TR)
```
TR = max(High - Low, |High - Previous Close|, |Low - Previous Close|)
```

### Step 3: Calculate Smoothed -DM
```
Smoothed -DM = EMA(-DM, period)
```

### Step 4: Calculate Smoothed TR
```
Smoothed TR = EMA(TR, period)
```

### Step 5: Calculate MINUS_DI
```
MINUS_DI = (Smoothed -DM / Smoothed TR) × 100
```

## Parameters

- **optInTimePeriod** (default: 14): Period for calculation
  - Valid range: 1 to 100000
  - Common values: 14 (standard), 21, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- MINUS_DI values: `double[]` (range: 0 to 100)

## Interpretation

### MINUS_DI Values
- **0-25**: Weak downward movement
- **25-50**: Moderate downward movement
- **50-75**: Strong downward movement
- **75-100**: Very strong downward movement

### Trading Signals

1. **Trend Direction**:
   - **MINUS_DI > PLUS_DI**: Downtrend
   - **MINUS_DI < PLUS_DI**: Uptrend
   - **MINUS_DI = PLUS_DI**: Sideways

2. **Trend Strength**:
   - **High MINUS_DI**: Strong downward movement
   - **Low MINUS_DI**: Weak downward movement
   - **Rising MINUS_DI**: Downward movement strengthening
   - **Falling MINUS_DI**: Downward movement weakening

3. **Crossovers**:
   - **Buy**: MINUS_DI crosses below PLUS_DI
   - **Sell**: MINUS_DI crosses above PLUS_DI
   - **Best in**: Trend change detection

4. **Divergence**:
   - **Bullish**: Price lower lows, MINUS_DI higher lows
   - **Bearish**: Price higher highs, MINUS_DI lower highs
   - **Best in**: Trend exhaustion points

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double minusDiOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period MINUS_DI
TA_RetCode retCode = TA_MINUS_DI(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    minusDiOutput         // output: MINUS_DI values
);
```

## Implementation Details

The TA-Lib MINUS_DI implementation:

1. **Directional Movement**: Calculates -DM for each period
2. **True Range**: Calculates TR for each period
3. **Smoothing**: Applies EMA to both -DM and TR
4. **MINUS_DI**: Calculates ratio and converts to percentage
5. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Trend Direction Strategy
- **Buy**: MINUS_DI < PLUS_DI
- **Sell**: MINUS_DI > PLUS_DI
- **Hold**: When MINUS_DI = PLUS_DI
- **Best in**: Trend following

### 2. Crossover Strategy
- **Buy**: MINUS_DI crosses below PLUS_DI
- **Sell**: MINUS_DI crosses above PLUS_DI
- **Filter**: Only trade when |MINUS_DI - PLUS_DI| > 5
- **Best in**: Trend change detection

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and MINUS_DI
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. MINUS_DI + ADX Strategy
- **Setup**: Use MINUS_DI for direction, ADX for strength
- **Entry**: Direction with strength confirmation
- **Exit**: Direction change or strength loss
- **Best in**: Trend following

## MINUS_DI vs. PLUS_DI

| Aspect | MINUS_DI | PLUS_DI |
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

- **PLUS_DI**: Plus Directional Indicator - upward movement
- **ADX**: Average Directional Index - trend strength
- **ADXR**: Average Directional Index Rating - smoothed ADX
- **DX**: Directional Movement - raw calculation

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder
- [TA-Lib Source Code: ta_MINUS_DI.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_MINUS_DI.c)
- [Investopedia: Minus Directional Indicator](https://www.investopedia.com/terms/m/minusdi.asp)
- [StockCharts: Minus Directional Indicator](https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx)

## Additional Notes

J. Welles Wilder developed MINUS_DI as part of the Directional Movement System to measure downward price movement strength.

### Key Insights

1. **Directional Movement**:
   - Measures downward price movement
   - Higher MINUS_DI = stronger downtrend
   - Lower MINUS_DI = weaker downtrend
   - Rising MINUS_DI = downtrend strengthening

2. **Trend Identification**:
   - MINUS_DI > PLUS_DI = downtrend
   - MINUS_DI < PLUS_DI = uptrend
   - MINUS_DI = PLUS_DI = sideways
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
   - Use with PLUS_DI for direction
   - Combine with ADX for strength
   - Use for trend confirmation
   - Multiple timeframe analysis

### Practical Tips

**For Trend Direction**:
- Use MINUS_DI vs. PLUS_DI for direction
- MINUS_DI > PLUS_DI = downtrend
- MINUS_DI < PLUS_DI = uptrend
- Watch for crossovers

**For Trend Strength**:
- Track MINUS_DI over time
- Rising MINUS_DI = strengthening
- Falling MINUS_DI = weakening
- Use for trend confirmation

**For Trend Changes**:
- Watch for MINUS_DI crossovers
- Confirm with price action
- Use volume for validation
- Set stops beyond recent extremes

**For Risk Management**:
- Use MINUS_DI for position sizing
- Reduce size during weak trends
- Increase size during strong trends
- Use for stop placement

MINUS_DI is particularly valuable for traders who want to identify trend direction and strength. It's excellent for trend following and provides clear signals for downward price movement.
