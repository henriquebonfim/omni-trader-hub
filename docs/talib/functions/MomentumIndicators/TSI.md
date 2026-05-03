# TSI - True Strength Index

## Description

The True Strength Index (TSI) is a momentum oscillator developed by William Blau that uses double smoothing to reduce noise and provide a more reliable momentum indicator. It's similar to RSI but uses exponential moving averages instead of simple averages, making it more responsive to recent price changes while maintaining smoothness.

## Category
Momentum Indicators

## Author
William Blau

## Calculation

TSI uses double smoothing with exponential moving averages:

### Step 1: Calculate Price Changes
```
PC = Close - Previous Close
```

### Step 2: First Smoothing (EMA)
```
EMA1 = EMA(PC, period1)
```

### Step 3: Second Smoothing (EMA)
```
EMA2 = EMA(EMA1, period2)
```

### Step 4: Calculate Absolute Price Changes
```
APC = |Close - Previous Close|
```

### Step 5: First Smoothing of Absolute Changes
```
EMA3 = EMA(APC, period1)
```

### Step 6: Second Smoothing of Absolute Changes
```
EMA4 = EMA(EMA3, period2)
```

### Step 7: TSI Calculation
```
TSI = (EMA2 / EMA4) × 100
```

Where:
- period1 = first smoothing period (default: 25)
- period2 = second smoothing period (default: 13)

## Parameters

- **optInTimePeriod** (default: 25): First smoothing period
  - Valid range: 2 to 100000
  - Common values: 25 (standard), 20, 30

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- TSI values: `double[]` (range: -100 to +100)

## Interpretation

### TSI Values
- **+100**: Strongest possible uptrend
- **-100**: Strongest possible downtrend
- **0**: No momentum
- **+50 to +100**: Strong upward momentum
- **-50 to -100**: Strong downward momentum
- **-50 to +50**: Weak momentum or sideways

### Trading Signals

1. **Zero Line Crossovers**:
   - **Buy**: TSI crosses above 0
   - **Sell**: TSI crosses below 0
   - **Best in**: Momentum change detection

2. **Overbought/Oversold**:
   - **Overbought**: TSI > +50 (strong upward momentum)
   - **Oversold**: TSI < -50 (strong downward momentum)
   - **Extreme**: TSI > +80 or < -80

3. **Divergence**:
   - **Bullish**: Price lower lows, TSI higher lows
   - **Bearish**: Price higher highs, TSI lower highs
   - **Best in**: Trend exhaustion points

4. **Momentum Changes**:
   - **Rising TSI**: Momentum increasing
   - **Falling TSI**: Momentum decreasing
   - **Peak TSI**: Momentum peak (potential reversal)
   - **Trough TSI**: Momentum trough (potential reversal)

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double tsiOutput[100];
int outBegIdx, outNBElement;

// Calculate 25-period TSI
TA_RetCode retCode = TA_TSI(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    25,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    tsiOutput             // output: TSI values
);
```

## Implementation Details

The TA-Lib TSI implementation:

1. **Price Changes**: Calculates differences between consecutive closes
2. **Double Smoothing**: Applies EMA twice to price changes
3. **Absolute Changes**: Calculates absolute price changes
4. **Double Smoothing**: Applies EMA twice to absolute changes
5. **TSI Formula**: Calculates TSI as ratio of smoothed changes
6. **Lookback**: Requires 2×period + EMA lookback

## Trading Strategies

### 1. Zero Line Strategy
- **Buy**: TSI crosses above 0
- **Sell**: TSI crosses below 0
- **Filter**: Only trade when |TSI| > 25
- **Best in**: Momentum change detection

### 2. Overbought/Oversold Strategy
- **Buy**: TSI < -50, then crosses above -50
- **Sell**: TSI > +50, then crosses below +50
- **Confirmation**: Wait for price confirmation
- **Best in**: Range-bound markets

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and TSI
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. TSI + Trend Strategy
- **Setup**: Use TSI for timing
- **Entry**: Trend direction with TSI timing
- **Exit**: TSI reversal or trend change
- **Best in**: Trending markets

## TSI vs. RSI

| Aspect | TSI | RSI |
|--------|-----|-----|
| Smoothing | Double EMA | Single smoothing |
| Responsiveness | More responsive | Less responsive |
| Noise | Less noisy | More noisy |
| Signals | More reliable | Less reliable |
| Best For | Trend following | Short-term trading |

## Advantages

1. **Smooth**: Double smoothing reduces noise
2. **Responsive**: More responsive than RSI
3. **Reliable**: Fewer false signals than RSI
4. **Universal**: Works across all markets
5. **Clear**: Easy to interpret

## Limitations

1. **Complex**: More complex than RSI
2. **Still Lags**: Based on historical data
3. **Whipsaws**: Possible in choppy markets
4. **Period Sensitivity**: Results vary with period
5. **Learning Curve**: Requires understanding of concept

## Period Selection

### Short Periods (15-20)
- **Characteristics**: More responsive, more noise
- **Use**: Short-term trading
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Standard Periods (25-30)
- **Characteristics**: Balanced approach
- **Use**: General momentum analysis
- **Trade-off**: Good balance
- **Best for**: Most applications

### Long Periods (30-50)
- **Characteristics**: Smoother, less responsive
- **Use**: Long-term analysis
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Position trading

## Related Functions

- **RSI**: Relative Strength Index - similar concept
- **CMO**: Chande Momentum Oscillator - similar concept
- **MOM**: Momentum - absolute change version
- **ROC**: Rate of Change - percentage change version

## References

- **Book**: *Momentum, Direction, and Divergence* by William Blau
- [TA-Lib Source Code: ta_TSI.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_TSI.c)
- [Investopedia: True Strength Index](https://www.investopedia.com/terms/t/true-strength-index.asp)
- [StockCharts: TSI](https://school.stockcharts.com/doku.php?id=technical_indicators:true_strength_index)

## Additional Notes

William Blau developed TSI as an improvement over RSI, using double smoothing to reduce noise while maintaining responsiveness. It's particularly useful for trend following and momentum analysis.

### Key Insights

1. **Double Smoothing Concept**:
   - Applies EMA twice for maximum smoothing
   - Reduces noise while maintaining responsiveness
   - More responsive than RSI
   - Better for trend following

2. **Momentum Measurement**:
   - Measures momentum as ratio of changes
   - Positive = upward momentum
   - Negative = downward momentum
   - Zero = no momentum

3. **Best Applications**:
   - Trend following
   - Momentum analysis
   - Divergence trading
   - Overbought/oversold

4. **Signal Interpretation**:
   - Zero line crossovers = momentum changes
   - Rising/falling = momentum changes
   - Peaks/troughs = potential reversals
   - Divergences = trend exhaustion

5. **Combination Strategies**:
   - Use with trend indicators
   - Combine with volume analysis
   - Use for divergence trading
   - Multiple timeframe confirmation

### Practical Tips

**For Trend Following**:
- Use zero line crossovers for signals
- Confirm with price action
- Use volume for validation
- Set stops beyond recent extremes

**For Momentum Analysis**:
- Rising TSI = strengthening momentum
- Falling TSI = weakening momentum
- Peaks = potential reversals
- Troughs = potential reversals

**For Divergence Trading**:
- Identify price vs. TSI divergence
- Wait for confirmation
- Use support/resistance
- Set stops beyond extremes

**For Overbought/Oversold**:
- Use ±50 as thresholds
- Wait for reversal signals
- Confirm with price patterns
- Avoid in strong trends

TSI is particularly valuable for traders who want a more reliable momentum indicator than RSI. It's excellent for trend following and provides fewer false signals while maintaining good responsiveness.

