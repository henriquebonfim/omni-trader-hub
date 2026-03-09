# MAMA - MESA Adaptive Moving Average

## Description

The MESA Adaptive Moving Average (MAMA) is an adaptive moving average that automatically adjusts its smoothing based on market cycles. Developed by John Ehlers, it uses the Hilbert Transform to identify the dominant cycle period and phase, then adjusts the smoothing accordingly. MAMA helps identify trend changes and provides adaptive smoothing based on market cycles.

## Category
Overlap Studies

## Author
John Ehlers

## Calculation

MAMA uses cycle-based adaptive smoothing with Hilbert Transform:

### Step 1: Smooth Price (WMA)
```
Smoothed Price = 4-period Weighted Moving Average of price
```

### Step 2: Apply Hilbert Transform
Uses Hilbert Transform to calculate:
- Detrender (removes trend component)
- In-phase (I) and Quadrature (Q) components
- Period and Phase from I/Q analysis

### Step 3: Calculate Delta Phase
```
Delta Phase = Current Phase - Previous Phase
If Delta Phase < 1, set to 1
```

### Step 4: Calculate Alpha (Adaptive Factor)
```
If Delta Phase > 1:
    alpha = Fast Limit / Delta Phase
    If alpha < Slow Limit, alpha = Slow Limit
Else:
    alpha = Fast Limit
```

### Step 5: Calculate MAMA and FAMA
```
MAMA = alpha × Price + (1 - alpha) × Previous MAMA
FAMA = (alpha/2) × MAMA + (1 - alpha/2) × Previous FAMA
```

**Note**: The algorithm is complex and uses Hilbert Transform mathematics to detect cycle period and phase. Alpha dynamically adjusts between Fast Limit (max responsiveness) and Slow Limit (min responsiveness) based on detected phase changes.

## Parameters

- **optInFastLimit** (default: 0.5): Fast limit for smoothing
  - Valid range: 0.01 to 0.99
  - Common values: 0.5 (standard), 0.3, 0.7

- **optInSlowLimit** (default: 0.05): Slow limit for smoothing
  - Valid range: 0.01 to 0.99
  - Common values: 0.05 (standard), 0.03, 0.1

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- **outMAMA**: MAMA values: `double[]`
- **outFAMA**: FAMA values: `double[]`

## Interpretation

### Adaptive Behavior
- **Fast Cycles**: High responsiveness (like fast EMA)
- **Slow Cycles**: More smoothing (like slow EMA)
- **Automatic Adjustment**: No manual parameter changes needed

### Cycle Analysis
- **Short Cycles**: High frequency, high volatility
- **Long Cycles**: Low frequency, trending
- **Cycle Changes**: Market regime changes

### Trading Signals
1. **Trend Following**:
   - Price above MAMA = Uptrend
   - Price below MAMA = Downtrend
   - MAMA slope indicates trend strength

2. **Crossovers**:
   - Price crossing MAMA = Trend change signal
   - More reliable than fixed-period MAs

3. **Adaptive Nature**:
   - Responds quickly to new trends
   - Smooths out noise in ranges
   - Self-adjusting to market conditions

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double mamaOutput[100], famaOutput[100];
int outBegIdx, outNBElement;

// Calculate MAMA (0.5, 0.05)
TA_RetCode retCode = TA_MAMA(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    0.5,                  // fast limit
    0.05,                 // slow limit
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    mamaOutput,           // output: MAMA values
    famaOutput            // output: FAMA values
);
```

## Implementation Details

The TA-Lib MAMA implementation:

1. **Cycle Detection**: Uses Hilbert Transform to identify cycles
2. **Adaptive Smoothing**: Adjusts smoothing based on cycle period
3. **MAMA Calculation**: Applies adaptive smoothing
4. **FAMA Calculation**: Calculates FAMA as alternative
5. **Lookback**: Requires significant lookback for cycle detection

## Trading Strategies

### 1. Pure MAMA Strategy
- **Buy**: Price crosses above MAMA
- **Sell**: Price crosses below MAMA
- **Stop**: Below/above MAMA
- **Best in**: All market conditions (adaptive)

### 2. MAMA + FAMA Strategy
- **Setup**: Use MAMA and FAMA together
- **Buy**: MAMA crosses above FAMA
- **Sell**: MAMA crosses below FAMA
- **Best in**: Trend change detection

### 3. MAMA + Cycle Analysis
- **Setup**: Use MAMA for trend, cycle for timing
- **Entry**: Trend direction with cycle timing
- **Exit**: MAMA reversal or cycle change
- **Best in**: Cycle-based trading

### 4. MAMA + Volatility
- **Context**: Use ATR for volatility
- **Entry**: MAMA signal with expanding ATR
- **Exit**: MAMA reversal or contracting ATR
- **Best in**: Volatility-based entries

## MAMA vs. FAMA

| Aspect | MAMA | FAMA |
|--------|------|------|
| Smoothing | Adaptive | Fixed |
| Responsiveness | Variable | Consistent |
| Signals | More adaptive | More stable |
| Best For | Cycle-based trading | General trend following |

## Advantages

1. **Adaptive**: Automatically adjusts to market cycles
2. **Cycle-Based**: Uses market cycle information
3. **Self-Optimizing**: No manual parameter adjustment
4. **Universal**: Works across all markets and timeframes
5. **Sophisticated**: Advanced cycle analysis

## Limitations

1. **Complex**: Most complex MA calculation
2. **Still Lags**: Based on historical data
3. **Parameter Sensitivity**: Limit choices affect results
4. **Whipsaws**: Possible in very choppy conditions
5. **Learning Curve**: Requires understanding of cycles

## Limit Selection

### Fast Limit (0.3-0.7)
- **Characteristics**: More responsive
- **Use**: Short-term trading
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Standard Limits (0.5, 0.05)
- **Characteristics**: Balanced approach
- **Use**: General trend analysis
- **Trade-off**: Good balance
- **Best for**: Most applications

### Slow Limit (0.7-0.9)
- **Characteristics**: Smoother, less responsive
- **Use**: Long-term analysis
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Position trading

## Related Functions

- **HT_DCPERIOD**: Hilbert Transform - Dominant Cycle Period
- **HT_DCPHASE**: Hilbert Transform - Dominant Cycle Phase
- **KAMA**: Kaufman Adaptive Moving Average - efficiency-based adaptive
- **T3**: T3 Moving Average - smooth with low lag

## References

- **Book**: *Rocket Science for Traders* by John Ehlers
- [TA-Lib Source Code: ta_MAMA.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_MAMA.c)
- [Investopedia: MESA Adaptive Moving Average](https://www.investopedia.com/terms/m/mesa-adaptive-moving-average.asp)
- [MESA Software](http://www.mesasoftware.com/)

## Additional Notes

John Ehlers developed MAMA as part of his work on cycle-based trading systems. The key insight is that market cycles should determine how much smoothing to apply.

### Key Insights

1. **Cycle-Based Adaptation**:
   - Uses Hilbert Transform to identify cycles
   - Fast cycles = more responsive
   - Slow cycles = more smoothing
   - Automatically adapts to market conditions

2. **Cycle Analysis**:
   - Short cycles = high volatility
   - Long cycles = trending markets
   - Cycle changes = regime changes
   - Use for market classification

3. **Best Applications**:
   - Cycle-based trading
   - Adaptive trend following
   - Market regime identification
   - Volatile instruments

4. **Limit Selection**:
   - Fast limit: 0.3-0.7 for responsiveness
   - Slow limit: 0.03-0.1 for stability
   - Balance based on trading style
   - Test different limits for your market

5. **Combination Strategies**:
   - Use MAMA for trend direction
   - Use FAMA for confirmation
   - Use cycle analysis for timing
   - Use multiple timeframes for context

### Practical Tips

**For Cycle-Based Trading**:
- Use MAMA for trend direction
- Use cycle analysis for timing
- Enter at cycle bottoms
- Exit at cycle tops

**For Adaptive Trend Following**:
- MAMA adapts to market conditions
- More responsive in trends
- Smoother in ranges
- Self-optimizing for current conditions

**For Market Regime Identification**:
- Short cycles = high volatility
- Long cycles = trending markets
- Cycle changes = regime changes
- Use for market classification

**For Risk Management**:
- Use MAMA for position sizing
- Reduce size during cycle changes
- Use for stop placement
- Monitor cycle trends

MAMA is particularly valuable for traders who want to incorporate cycle analysis into their trend following strategies. It's excellent for cycle-based trading and provides adaptive smoothing based on market cycles.
