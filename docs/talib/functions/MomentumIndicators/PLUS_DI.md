# PLUS_DI - Plus Directional Indicator

## Description

The Plus Directional Indicator (PLUS_DI) is a trend indicator that measures the strength of upward price movement. It's part of the Directional Movement System developed by J. Welles Wilder and works alongside MINUS_DI to identify trend direction and strength. PLUS_DI helps identify bullish trends and provides signals for upward price movement.

## Category
Momentum Indicators

## Author
J. Welles Wilder

## Calculation

PLUS_DI is calculated using directional movement:

### Step 1: Calculate Plus Directional Movement (+DM)
```
+DM = High - Previous High (if positive, otherwise 0)
```

### Step 2: Calculate True Range (TR)
```
TR = max(High - Low, |High - Previous Close|, |Low - Previous Close|)
```

### Step 3: Calculate Smoothed +DM
```
Smoothed +DM = EMA(+DM, period)
```

### Step 4: Calculate Smoothed TR
```
Smoothed TR = EMA(TR, period)
```

### Step 5: Calculate PLUS_DI
```
PLUS_DI = (Smoothed +DM / Smoothed TR) × 100
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
- PLUS_DI values: `double[]` (range: 0 to 100)

## Interpretation

### PLUS_DI Values
- **0-25**: Weak upward movement
- **25-50**: Moderate upward movement
- **50-75**: Strong upward movement
- **75-100**: Very strong upward movement

### Trading Signals

1. **Trend Direction**:
   - **PLUS_DI > MINUS_DI**: Uptrend
   - **PLUS_DI < MINUS_DI**: Downtrend
   - **PLUS_DI = MINUS_DI**: Sideways

2. **Trend Strength**:
   - **High PLUS_DI**: Strong upward movement
   - **Low PLUS_DI**: Weak upward movement
   - **Rising PLUS_DI**: Upward movement strengthening
   - **Falling PLUS_DI**: Upward movement weakening

3. **Crossovers**:
   - **Buy**: PLUS_DI crosses above MINUS_DI
   - **Sell**: PLUS_DI crosses below MINUS_DI
   - **Best in**: Trend change detection

4. **Divergence**:
   - **Bullish**: Price lower lows, PLUS_DI higher lows
   - **Bearish**: Price higher highs, PLUS_DI lower highs
   - **Best in**: Trend exhaustion points

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double plusDiOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period PLUS_DI
TA_RetCode retCode = TA_PLUS_DI(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    plusDiOutput          // output: PLUS_DI values
);
```

## Implementation Details

The TA-Lib PLUS_DI implementation:

1. **Directional Movement**: Calculates +DM for each period
2. **True Range**: Calculates TR for each period
3. **Smoothing**: Applies EMA to both +DM and TR
4. **PLUS_DI**: Calculates ratio and converts to percentage
5. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Trend Direction Strategy
- **Buy**: PLUS_DI > MINUS_DI
- **Sell**: PLUS_DI < MINUS_DI
- **Hold**: When PLUS_DI = MINUS_DI
- **Best in**: Trend following

### 2. Crossover Strategy
- **Buy**: PLUS_DI crosses above MINUS_DI
- **Sell**: PLUS_DI crosses below MINUS_DI
- **Filter**: Only trade when |PLUS_DI - MINUS_DI| > 5
- **Best in**: Trend change detection

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and PLUS_DI
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. PLUS_DI + ADX Strategy
- **Setup**: Use PLUS_DI for direction, ADX for strength
- **Entry**: Direction with strength confirmation
- **Exit**: Direction change or strength loss
- **Best in**: Trend following

## PLUS_DI vs. MINUS_DI

| Aspect | PLUS_DI | MINUS_DI |
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

- **MINUS_DI**: Minus Directional Indicator - downward movement
- **ADX**: Average Directional Index - trend strength
- **ADXR**: Average Directional Index Rating - smoothed ADX
- **DX**: Directional Movement - raw calculation

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder
- [TA-Lib Source Code: ta_PLUS_DI.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_PLUS_DI.c)
- [Investopedia: Plus Directional Indicator](https://www.investopedia.com/terms/p/plusdi.asp)
- [StockCharts: Plus Directional Indicator](https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx)

## Additional Notes

J. Welles Wilder developed PLUS_DI as part of the Directional Movement System to measure upward price movement strength.

### Key Insights

1. **Directional Movement**:
   - Measures upward price movement
   - Higher PLUS_DI = stronger uptrend
   - Lower PLUS_DI = weaker uptrend
   - Rising PLUS_DI = uptrend strengthening

2. **Trend Identification**:
   - PLUS_DI > MINUS_DI = uptrend
   - PLUS_DI < MINUS_DI = downtrend
   - PLUS_DI = MINUS_DI = sideways
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
   - Use with MINUS_DI for direction
   - Combine with ADX for strength
   - Use for trend confirmation
   - Multiple timeframe analysis

### Practical Tips

**For Trend Direction**:
- Use PLUS_DI vs. MINUS_DI for direction
- PLUS_DI > MINUS_DI = uptrend
- PLUS_DI < MINUS_DI = downtrend
- Watch for crossovers

**For Trend Strength**:
- Track PLUS_DI over time
- Rising PLUS_DI = strengthening
- Falling PLUS_DI = weakening
- Use for trend confirmation

**For Trend Changes**:
- Watch for PLUS_DI crossovers
- Confirm with price action
- Use volume for validation
- Set stops beyond recent extremes

**For Risk Management**:
- Use PLUS_DI for position sizing
- Reduce size during weak trends
- Increase size during strong trends
- Use for stop placement

PLUS_DI is particularly valuable for traders who want to identify trend direction and strength. It's excellent for trend following and provides clear signals for upward price movement.
