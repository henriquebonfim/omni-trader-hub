# ULTOSC - Ultimate Oscillator

## Description

The Ultimate Oscillator (ULTOSC) is a momentum indicator developed by Larry Williams that combines three different timeframes to measure momentum. It uses weighted averages of three different periods (typically 7, 14, and 28) to create a more reliable oscillator that reduces false signals compared to single-period oscillators like RSI.

## Category
Momentum Indicators

## Author
Larry Williams

## Calculation

ULTOSC combines three different timeframes:

### Step 1: Calculate True Range (TR)
```
TR = max(High - Low, |High - Previous Close|, |Low - Previous Close|)
```

### Step 2: Calculate Buying Pressure (BP)
```
BP = Close - min(Low, Previous Close)
```

### Step 3: Calculate Raw Ultimate Oscillator
```
Raw ULTOSC = (BP1/TR1 × 4) + (BP2/TR2 × 2) + (BP3/TR3 × 1)
```

Where:
- BP1, TR1 = 7-period sums
- BP2, TR2 = 14-period sums  
- BP3, TR3 = 28-period sums
- Weights: 4, 2, 1 (shortest period gets highest weight)

### Step 4: Calculate Ultimate Oscillator
```
ULTOSC = (Raw ULTOSC / (4 + 2 + 1)) × 100
```

## Parameters

- **optInTimePeriod1** (default: 7): First period
  - Valid range: 1 to 100000
  - Common values: 7 (standard)

- **optInTimePeriod2** (default: 14): Second period
  - Valid range: 1 to 100000
  - Common values: 14 (standard)

- **optInTimePeriod3** (default: 28): Third period
  - Valid range: 1 to 100000
  - Common values: 28 (standard)

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- ULTOSC values: `double[]` (range: 0 to 100)

## Interpretation

### ULTOSC Values
- **0-30**: Oversold territory
- **30-70**: Neutral territory
- **70-100**: Overbought territory
- **50**: Neutral center line

### Trading Signals

1. **Overbought/Oversold**:
   - **Oversold**: ULTOSC < 30 (potential buy)
   - **Overbought**: ULTOSC > 70 (potential sell)
   - **Neutral**: ULTOSC 30-70 (no clear signal)

2. **Divergence**:
   - **Bullish**: Price lower lows, ULTOSC higher lows
   - **Bearish**: Price higher highs, ULTOSC lower highs
   - **Best in**: Trend exhaustion points

3. **Center Line Crossovers**:
   - **Buy**: ULTOSC crosses above 50
   - **Sell**: ULTOSC crosses below 50
   - **Best in**: Momentum change detection

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double ultoscOutput[100];
int outBegIdx, outNBElement;

// Calculate Ultimate Oscillator (7, 14, 28)
TA_RetCode retCode = TA_ULTOSC(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    7,                    // first period
    14,                   // second period
    28,                   // third period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    ultoscOutput          // output: ULTOSC values
);
```

## Implementation Details

The TA-Lib ULTOSC implementation:

1. **True Range**: Calculates true range for each period
2. **Buying Pressure**: Calculates buying pressure for each period
3. **Weighted Sum**: Combines three periods with weights
4. **Normalization**: Converts to 0-100 scale
5. **Lookback**: Requires max(period1, period2, period3) for first output

## Trading Strategies

### 1. Overbought/Oversold Strategy
- **Buy**: ULTOSC < 30, then crosses above 30
- **Sell**: ULTOSC > 70, then crosses below 70
- **Confirmation**: Wait for price confirmation
- **Best in**: Range-bound markets

### 2. Divergence Strategy
- **Setup**: Identify divergence between price and ULTOSC
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 3. Center Line Strategy
- **Buy**: ULTOSC crosses above 50
- **Sell**: ULTOSC crosses below 50
- **Filter**: Only trade when |ULTOSC - 50| > 10
- **Best in**: Momentum change detection

### 4. ULTOSC + Trend Strategy
- **Setup**: Use ULTOSC for timing
- **Entry**: Trend direction with ULTOSC timing
- **Exit**: ULTOSC reversal or trend change
- **Best in**: Trending markets

## ULTOSC vs. RSI

| Aspect | ULTOSC | RSI |
|--------|--------|-----|
| Timeframes | Three (7, 14, 28) | Single (14) |
| Weights | Weighted (4, 2, 1) | Equal |
| Smoothing | More smoothing | Less smoothing |
| Signals | Fewer, more reliable | More, less reliable |
| Best For | Trend following | Short-term trading |

## Advantages

1. **Multi-Timeframe**: Combines three timeframes
2. **Weighted**: Shorter periods get higher weights
3. **Smooth**: Less noisy than single-period oscillators
4. **Reliable**: Fewer false signals than RSI
5. **Universal**: Works across all markets

## Limitations

1. **Complex**: More complex than RSI
2. **Still Lags**: Based on historical data
3. **Whipsaws**: Possible in choppy markets
4. **Period Sensitivity**: Results vary with periods
5. **Learning Curve**: Requires understanding of concept

## Period Selection

### Standard (7, 14, 28)
- **Characteristics**: Balanced approach
- **Use**: General momentum analysis
- **Trade-off**: Good balance
- **Best for**: Most applications

### Short (5, 10, 20)
- **Characteristics**: More responsive
- **Use**: Short-term trading
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Long (14, 28, 56)
- **Characteristics**: Smoother, less responsive
- **Use**: Long-term analysis
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Position trading

## Related Functions

- **RSI**: Relative Strength Index - single-period oscillator
- **STOCH**: Stochastic Oscillator - range-based oscillator
- **WILLR**: Williams %R - similar concept
- **MOM**: Momentum - absolute change oscillator

## References

- **Book**: *The Definitive Guide to Trading Systems* by Larry Williams
- [TA-Lib Source Code: ta_ULTOSC.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_ULTOSC.c)
- [Investopedia: Ultimate Oscillator](https://www.investopedia.com/terms/u/ultimateoscillator.asp)
- [StockCharts: Ultimate Oscillator](https://school.stockcharts.com/doku.php?id=technical_indicators:ultimate_oscillator)

## Additional Notes

Larry Williams developed the Ultimate Oscillator as an improvement over RSI, combining multiple timeframes to reduce false signals and provide more reliable momentum analysis.

### Key Insights

1. **Multi-Timeframe Approach**:
   - Combines three different periods
   - Shorter periods get higher weights
   - Reduces false signals
   - More reliable than single-period oscillators

2. **Weighted Calculation**:
   - 7-period gets weight of 4
   - 14-period gets weight of 2
   - 28-period gets weight of 1
   - Total weight = 7

3. **Best Applications**:
   - Trend following
   - Momentum analysis
   - Divergence trading
   - Overbought/oversold

4. **Signal Interpretation**:
   - < 30 = oversold
   - > 70 = overbought
   - 30-70 = neutral
   - 50 = center line

5. **Combination Strategies**:
   - Use with trend indicators
   - Combine with volume analysis
   - Use for divergence trading
   - Multiple timeframe confirmation

### Practical Tips

**For Overbought/Oversold Trading**:
- Use 30/70 levels as thresholds
- Wait for confirmation from price
- Use volume for validation
- Avoid in strong trends

**For Divergence Trading**:
- Identify price vs. ULTOSC divergence
- Wait for confirmation
- Use support/resistance
- Set stops beyond extremes

**For Trend Following**:
- Use ULTOSC for timing
- Combine with trend indicators
- Enter on pullbacks when trend confirmed
- Exit on ULTOSC reversal

**For Risk Management**:
- Use ULTOSC for position sizing
- Reduce size during extreme readings
- Use for stop placement
- Monitor ULTOSC trends

The Ultimate Oscillator is particularly valuable for traders who want a more reliable momentum indicator than RSI. It's excellent for trend following and provides fewer false signals than single-period oscillators.

