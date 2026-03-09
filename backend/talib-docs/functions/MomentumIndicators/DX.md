# DX - Directional Movement

## Description

The Directional Movement (DX) is a trend strength indicator that measures the strength of directional movement without smoothing. It's the raw calculation used to derive ADX and provides a more responsive measure of trend strength. DX helps identify trend strength and provides early signals for trend changes.

## Category
Momentum Indicators

## Author
J. Welles Wilder

## Calculation

DX is calculated using directional movement components:

### Step 1: Calculate Plus Directional Movement (+DM)
```
+DM = High - Previous High (if positive, otherwise 0)
```

### Step 2: Calculate Minus Directional Movement (-DM)
```
-DM = Previous Low - Low (if positive, otherwise 0)
```

### Step 3: Calculate True Range (TR)
```
TR = max(High - Low, |High - Previous Close|, |Low - Previous Close|)
```

### Step 4: Calculate Smoothed Components
```
Smoothed +DM = EMA(+DM, period)
Smoothed -DM = EMA(-DM, period)
Smoothed TR = EMA(TR, period)
```

### Step 5: Calculate DX
```
DX = |Smoothed +DM - Smoothed -DM| / (Smoothed +DM + Smoothed -DM) × 100
```

## Parameters

- **optInTimePeriod** (default: 14): Period for calculation
  - Valid range: 2 to 100000
  - Common values: 14 (standard), 21, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- DX values: `double[]` (range: 0 to 100)

## Interpretation

### DX Values
- **0-25**: Weak directional movement
- **25-50**: Moderate directional movement
- **50-75**: Strong directional movement
- **75-100**: Very strong directional movement

### Trading Signals

1. **Trend Strength**:
   - **Weak Trend**: DX < 25
   - **Moderate Trend**: DX 25-50
   - **Strong Trend**: DX 50-75
   - **Very Strong Trend**: DX > 75

2. **Trend Changes**:
   - **Rising DX**: Trend strengthening
   - **Falling DX**: Trend weakening
   - **Peak DX**: Trend peak (potential reversal)
   - **Trough DX**: Trend trough (potential reversal)

3. **Divergence**:
   - **Bullish**: Price lower lows, DX higher lows
   - **Bearish**: Price higher highs, DX lower highs
   - **Best in**: Trend exhaustion points

4. **Trend Confirmation**:
   - **High DX**: Strong trend confirmation
   - **Low DX**: Weak trend or sideways
   - **Rising DX**: Trend strengthening
   - **Falling DX**: Trend weakening

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double dxOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period DX
TA_RetCode retCode = TA_DX(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    dxOutput              // output: DX values
);
```

## Implementation Details

The TA-Lib DX implementation:

1. **Directional Movement**: Calculates +DM and -DM for each period
2. **True Range**: Calculates TR for each period
3. **Smoothing**: Applies EMA to all components
4. **DX Calculation**: Calculates ratio and converts to percentage
5. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Trend Strength Strategy
- **Setup**: Track DX over time
- **Entry**: When DX indicates strong trend
- **Exit**: When DX indicates weak trend
- **Best in**: Trend following

### 2. Trend Change Strategy
- **Setup**: Identify DX changes
- **Entry**: On trend strengthening
- **Exit**: On trend weakening
- **Best in**: Trend change detection

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and DX
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. DX + Direction Strategy
- **Setup**: Use DX for trend strength
- **Entry**: Direction with DX confirmation
- **Exit**: DX reversal or direction change
- **Best in**: Trend following

## DX vs. ADX

| Aspect | DX | ADX |
|--------|----|----|
| Smoothing | Single smoothing | Double smoothing |
| Responsiveness | More responsive | Less responsive |
| Signals | More signals | Fewer signals |
| Noise | More noisy | Less noisy |
| Best For | Short-term analysis | Long-term analysis |

## Advantages

1. **Responsive**: More responsive than ADX
2. **Early Signals**: Provides early trend changes
3. **Universal**: Works across all markets
4. **Clear**: Easy to interpret
5. **Versatile**: Many applications

## Limitations

1. **Noisy**: More volatile than ADX
2. **Whipsaws**: Can generate false signals
3. **Period Sensitivity**: Results vary with period
4. **Context Dependent**: Needs interpretation
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

- **ADX**: Average Directional Index - smoothed version
- **ADXR**: Average Directional Index Rating - double smoothed
- **PLUS_DI**: Plus Directional Indicator - upward movement
- **MINUS_DI**: Minus Directional Indicator - downward movement

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder
- [TA-Lib Source Code: ta_DX.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_DX.c)
- [Investopedia: Directional Movement](https://www.investopedia.com/terms/d/dx.asp)
- [StockCharts: Directional Movement](https://school.stockcharts.com/doku.php?id=technical_indicators:average_directional_index_adx)

## Additional Notes

J. Welles Wilder developed DX as the raw calculation for directional movement strength, which is then smoothed to create ADX.

### Key Insights

1. **Raw Calculation**:
   - Measures directional movement strength
   - Higher DX = stronger trend
   - Lower DX = weaker trend
   - Rising DX = trend strengthening

2. **Trend Strength Measurement**:
   - Measures absolute trend strength
   - No direction indication
   - Use with PLUS_DI/MINUS_DI for direction
   - Good for trend confirmation

3. **Best Applications**:
   - Trend strength analysis
   - Trend change detection
   - Trend confirmation
   - Early trend signals

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
- Track DX over time
- Identify trend strength regimes
- Use for trend confirmation
- Monitor trend changes

**For Trend Change Detection**:
- Watch for DX changes
- Rising DX = trend strengthening
- Falling DX = trend weakening
- Use for early signals

**For Trend Confirmation**:
- Use DX for trend strength
- Combine with direction indicators
- Enter on strong trend confirmation
- Exit on trend weakening

**For Risk Management**:
- Use DX for position sizing
- Reduce size during weak trends
- Increase size during strong trends
- Use for stop placement

DX is particularly valuable for traders who want a more responsive trend strength indicator than ADX. It's excellent for short-term trend analysis and provides early signals for trend changes.
