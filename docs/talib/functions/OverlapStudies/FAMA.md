# FAMA - Following Adaptive Moving Average

## Description

The Following Adaptive Moving Average (FAMA) is a companion indicator to MAMA that provides a more stable, less responsive version of the adaptive moving average. It's developed by John Ehlers as part of the MESA Adaptive Moving Average system and uses the same cycle-based adaptive smoothing but with different parameters to provide a smoother, more stable trend line.

## Category
Overlap Studies

## Author
John Ehlers

## Calculation

FAMA uses the same cycle-based adaptive smoothing as MAMA but with different limits:

### Step 1: Calculate Dominant Cycle Period
```
Period = HT_DCPERIOD(Price)
```

### Step 2: Calculate Dominant Cycle Phase
```
Phase = HT_DCPHASE(Price)
```

### Step 3: Calculate Adaptive Smoothing
```
Smoothing = 2 / (Period + 1)
```

### Step 4: Calculate FAMA
```
FAMA = FAMA(previous) + Smoothing × [Price - FAMA(previous)]
```

Where:
- HT_DCPERIOD = Hilbert Transform Dominant Cycle Period
- HT_DCPHASE = Hilbert Transform Dominant Cycle Phase
- Uses different limits than MAMA for more stability

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
- FAMA values: `double[]`

## Interpretation

### Adaptive Behavior
- **Fast Cycles**: More responsive than MAMA
- **Slow Cycles**: More smoothing than MAMA
- **Stability**: More stable than MAMA
- **Automatic Adjustment**: No manual parameter changes needed

### Cycle Analysis
- **Short Cycles**: High frequency, high volatility
- **Long Cycles**: Low frequency, trending
- **Cycle Changes**: Market regime changes

### Trading Signals
1. **Trend Following**:
   - Price above FAMA = Uptrend
   - Price below FAMA = Downtrend
   - FAMA slope indicates trend strength

2. **Crossovers**:
   - Price crossing FAMA = Trend change signal
   - More reliable than fixed-period MAs

3. **Adaptive Nature**:
   - Responds to market cycles
   - Smooths out noise in ranges
   - Self-adjusting to market conditions

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double famaOutput[100];
int outBegIdx, outNBElement;

// Calculate FAMA (0.5, 0.05)
TA_RetCode retCode = TA_FAMA(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    0.5,                  // fast limit
    0.05,                 // slow limit
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    famaOutput            // output: FAMA values
);
```

## Implementation Details

The TA-Lib FAMA implementation:

1. **Cycle Detection**: Uses Hilbert Transform to identify cycles
2. **Adaptive Smoothing**: Adjusts smoothing based on cycle period
3. **FAMA Calculation**: Applies adaptive smoothing with different limits
4. **Lookback**: Requires significant lookback for cycle detection

## Trading Strategies

### 1. Pure FAMA Strategy
- **Buy**: Price crosses above FAMA
- **Sell**: Price crosses below FAMA
- **Stop**: Below/above FAMA
- **Best in**: All market conditions (adaptive)

### 2. FAMA + MAMA Strategy
- **Setup**: Use FAMA and MAMA together
- **Buy**: FAMA crosses above MAMA
- **Sell**: FAMA crosses below MAMA
- **Best in**: Trend change detection

### 3. FAMA + Cycle Analysis
- **Setup**: Use FAMA for trend, cycle for timing
- **Entry**: Trend direction with cycle timing
- **Exit**: FAMA reversal or cycle change
- **Best in**: Cycle-based trading

### 4. FAMA + Volatility
- **Context**: Use ATR for volatility
- **Entry**: FAMA signal with expanding ATR
- **Exit**: FAMA reversal or contracting ATR
- **Best in**: Volatility-based entries

## FAMA vs. MAMA

| Aspect | FAMA | MAMA |
|--------|------|------|
| Smoothing | Adaptive | Adaptive |
| Responsiveness | Less responsive | More responsive |
| Stability | More stable | Less stable |
| Signals | Fewer, more reliable | More, less reliable |
| Best For | Long-term trend following | Short-term trend following |

## Advantages

1. **Adaptive**: Automatically adjusts to market cycles
2. **Stable**: More stable than MAMA
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

- **MAMA**: MESA Adaptive Moving Average - more responsive version
- **HT_DCPERIOD**: Hilbert Transform - Dominant Cycle Period
- **HT_DCPHASE**: Hilbert Transform - Dominant Cycle Phase
- **KAMA**: Kaufman Adaptive Moving Average - efficiency-based adaptive

## References

- **Book**: *Rocket Science for Traders* by John Ehlers
- [TA-Lib Source Code: ta_FAMA.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_FAMA.c)
- [Investopedia: MESA Adaptive Moving Average](https://www.investopedia.com/terms/m/mesa-adaptive-moving-average.asp)
- [MESA Software](http://www.mesasoftware.com/)

## Additional Notes

John Ehlers developed FAMA as a companion to MAMA, providing a more stable, less responsive version of the adaptive moving average.

### Key Insights

1. **Cycle-Based Adaptation**:
   - Uses Hilbert Transform to identify cycles
   - Fast cycles = more responsive
   - Slow cycles = more smoothing
   - Automatically adapts to market conditions

2. **Stability Focus**:
   - More stable than MAMA
   - Less responsive than MAMA
   - Better for long-term trends
   - Good for trend confirmation

3. **Best Applications**:
   - Long-term trend following
   - Trend confirmation
   - Market regime identification
   - Stable trend analysis

4. **Limit Selection**:
   - Fast limit: 0.3-0.7 for responsiveness
   - Slow limit: 0.03-0.1 for stability
   - Balance based on trading style
   - Test different limits for your market

5. **Combination Strategies**:
   - Use FAMA for trend direction
   - Use MAMA for confirmation
   - Use cycle analysis for timing
   - Use multiple timeframes for context

### Practical Tips

**For Long-term Trend Following**:
- Use FAMA for trend direction
- More stable than MAMA
- Good for position trading
- Use for trend confirmation

**For Trend Confirmation**:
- Use FAMA with MAMA
- FAMA = trend direction
- MAMA = trend confirmation
- Enter when both align

**For Market Regime Identification**:
- Short cycles = high volatility
- Long cycles = trending markets
- Cycle changes = regime changes
- Use for market classification

**For Risk Management**:
- Use FAMA for position sizing
- Reduce size during cycle changes
- Use for stop placement
- Monitor cycle trends

FAMA is particularly valuable for traders who want a more stable adaptive moving average than MAMA. It's excellent for long-term trend following and provides stable trend signals based on market cycles.
