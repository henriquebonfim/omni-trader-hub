# TRIX - Triple Exponential Moving Average

## Description

The Triple Exponential Moving Average (TRIX) is a momentum indicator that uses a triple-smoothed exponential moving average to identify trend changes. It's calculated by applying an exponential moving average three times to the price data, then taking the rate of change of the final result. TRIX helps identify trend changes and momentum shifts while filtering out short-term noise.

## Category
Momentum Indicators

## Author
Jack Hutson

## Calculation

TRIX uses a triple-smoothed EMA approach:

### Step 1: First EMA
```
EMA1 = EMA(Price, period)
```

### Step 2: Second EMA
```
EMA2 = EMA(EMA1, period)
```

### Step 3: Third EMA
```
EMA3 = EMA(EMA2, period)
```

### Step 4: TRIX Calculation
```
TRIX = (EMA3 - EMA3[previous]) / EMA3[previous] × 100
```

Where:
- EMA3[previous] = previous value of triple-smoothed EMA
- Result is expressed as percentage change

## Parameters

- **optInTimePeriod** (default: 30): Period for EMAs
  - Valid range: 1 to 100000
  - Common values: 14, 30, 50

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- TRIX values: `double[]` (percentage change)

## Interpretation

### TRIX Values
- **Positive**: Triple-smoothed EMA is rising (uptrend)
- **Negative**: Triple-smoothed EMA is falling (downtrend)
- **Zero**: Triple-smoothed EMA is flat (no trend)
- **Increasing**: Momentum strengthening
- **Decreasing**: Momentum weakening

### Trading Signals

1. **Zero Line Crossovers**:
   - **Buy**: TRIX crosses above 0
   - **Sell**: TRIX crosses below 0
   - **Best in**: Trend change detection

2. **Momentum Changes**:
   - **Rising TRIX**: Momentum increasing
   - **Falling TRIX**: Momentum decreasing
   - **Peak TRIX**: Momentum peak (potential reversal)
   - **Trough TRIX**: Momentum trough (potential reversal)

3. **Divergence**:
   - **Bullish**: Price lower lows, TRIX higher lows
   - **Bearish**: Price higher highs, TRIX lower highs
   - **Best in**: Trend exhaustion points

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double trixOutput[100];
int outBegIdx, outNBElement;

// Calculate 30-period TRIX
TA_RetCode retCode = TA_TRIX(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    30,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    trixOutput            // output: TRIX values
);
```

## Implementation Details

The TA-Lib TRIX implementation:

1. **Triple Smoothing**: Applies EMA three times
2. **Rate of Change**: Calculates percentage change
3. **Smoothing**: Very smooth due to triple smoothing
4. **Lookback**: Requires 3×period + EMA lookback

## Trading Strategies

### 1. Zero Line Strategy
- **Buy**: TRIX crosses above 0
- **Sell**: TRIX crosses below 0
- **Filter**: Only trade when |TRIX| > 0.1%
- **Best in**: Trend change detection

### 2. Momentum Strategy
- **Buy**: TRIX rising and positive
- **Sell**: TRIX falling and negative
- **Exit**: TRIX momentum change
- **Best in**: Trend following

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and TRIX
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. TRIX + Trend Strategy
- **Setup**: Use TRIX for timing
- **Entry**: Trend direction with TRIX timing
- **Exit**: TRIX reversal or trend change
- **Best in**: Trending markets

## TRIX Characteristics

### 1. Very Smooth
- **Triple Smoothing**: Extremely smooth line
- **Noise Reduction**: Filters out short-term noise
- **Trend Clarity**: Clear trend identification
- **Best in**: Long-term analysis

### 2. Low Lag
- **Rate of Change**: Measures momentum directly
- **Early Signals**: Provides early trend changes
- **Responsive**: Reacts to momentum changes
- **Best in**: Trend change detection

### 3. Momentum Focus
- **Momentum Measurement**: Direct momentum indicator
- **Trend Strength**: Shows trend strength
- **Momentum Changes**: Identifies momentum shifts
- **Best in**: Momentum analysis

## Advantages

1. **Very Smooth**: Triple smoothing reduces noise
2. **Early Signals**: Provides early trend changes
3. **Momentum Focus**: Direct momentum measurement
4. **Universal**: Works across all markets
5. **Reliable**: Fewer false signals than faster indicators

## Limitations

1. **Complex**: More complex than simple MAs
2. **Still Lags**: Based on historical data
3. **Whipsaws**: Possible in choppy markets
4. **Period Sensitivity**: Results vary with period
5. **Learning Curve**: Requires understanding of concept

## Period Selection

### Short Periods (14-20)
- **Characteristics**: More responsive, more noise
- **Use**: Short-term trading
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Standard Periods (30-50)
- **Characteristics**: Balanced approach
- **Use**: General momentum analysis
- **Trade-off**: Good balance
- **Best for**: Most applications

### Long Periods (50-100)
- **Characteristics**: Smoother, less responsive
- **Use**: Long-term analysis
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Position trading

## Related Functions

- **EMA**: Exponential Moving Average - building block
- **DEMA**: Double Exponential Moving Average - similar concept
- **TEMA**: Triple Exponential Moving Average - similar concept
- **MOM**: Momentum - absolute change version

## References

- **Article**: "TRIX: A New Technical Indicator" by Jack Hutson (Technical Analysis of Stocks & Commodities, 1983)
- [TA-Lib Source Code: ta_TRIX.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_TRIX.c)
- [Investopedia: TRIX](https://www.investopedia.com/terms/t/trix.asp)
- [StockCharts: TRIX](https://school.stockcharts.com/doku.php?id=technical_indicators:trix)

## Additional Notes

Jack Hutson developed TRIX as a momentum indicator that combines the smoothing benefits of triple EMA with the responsiveness of rate of change. It's particularly useful for identifying trend changes while filtering out short-term noise.

### Key Insights

1. **Triple Smoothing Concept**:
   - Applies EMA three times for maximum smoothing
   - Reduces noise while maintaining trend information
   - Creates very smooth momentum line
   - Excellent for trend identification

2. **Rate of Change**:
   - Measures percentage change of triple-smoothed EMA
   - Positive = uptrend momentum
   - Negative = downtrend momentum
   - Zero = no trend momentum

3. **Best Applications**:
   - Trend change detection
   - Momentum analysis
   - Long-term trend following
   - Noise reduction

4. **Signal Interpretation**:
   - Zero line crossovers = trend changes
   - Rising/falling = momentum changes
   - Peaks/troughs = potential reversals
   - Divergences = trend exhaustion

5. **Combination Strategies**:
   - Use with trend indicators
   - Combine with volume analysis
   - Use for divergence trading
   - Multiple timeframe confirmation

### Practical Tips

**For Trend Change Detection**:
- Watch for zero line crossovers
- Confirm with price action
- Use volume for validation
- Set stops beyond recent extremes

**For Momentum Analysis**:
- Rising TRIX = strengthening momentum
- Falling TRIX = weakening momentum
- Peaks = potential reversals
- Troughs = potential reversals

**For Divergence Trading**:
- Identify price vs. TRIX divergence
- Wait for confirmation
- Use support/resistance
- Set stops beyond extremes

**For Risk Management**:
- Use TRIX for position sizing
- Reduce size during extreme readings
- Use for stop placement
- Monitor TRIX trends

TRIX is particularly valuable for traders who want a very smooth momentum indicator that provides early trend change signals while filtering out short-term noise. It's excellent for long-term trend analysis and momentum assessment.

