# BBANDS - Bollinger Bands

## Description

Bollinger Bands are volatility bands placed above and below a moving average. The bands automatically widen when volatility increases and narrow when volatility decreases. This makes them useful for identifying overbought/oversold conditions and potential breakouts.

## Category
Volatility Indicators / Overlap Studies

## Author
John A. Bollinger

## Calculation

Bollinger Bands consist of three lines:

### Middle Band
```
Middle Band = SMA(price, period)
```
Typically a 20-period Simple Moving Average

### Upper Band
```
Upper Band = Middle Band + (K × Standard Deviation)
```

### Lower Band
```
Lower Band = Middle Band - (K × Standard Deviation)
```

Where:
- K = number of standard deviations (typically 2)
- Standard Deviation is calculated over the same period as the SMA

### Standard Formula
```
Middle Band = 20-day SMA
Upper Band = 20-day SMA + (2 × 20-day standard deviation)
Lower Band = 20-day SMA - (2 × 20-day standard deviation)
```

## Parameters

- **optInTimePeriod** (default: 5): Period for moving average and standard deviation
  - Valid range: 2 to 100000
  - Common value: 20

- **optInNbDevUp** (default: 2.0): Number of standard deviations for upper band
  - Valid range: -3.0e+37 to 3.0e+37
  - Common values: 2.0 to 3.0

- **optInNbDevDn** (default: 2.0): Number of standard deviations for lower band
  - Valid range: -3.0e+37 to 3.0e+37
  - Common values: 2.0 to 3.0

- **optInMAType** (default: SMA): Type of moving average
  - Valid range: 0 to 8
  - Options: SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, T3

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- **outRealUpperBand**: Upper band values: `double[]`
- **outRealMiddleBand**: Middle band values: `double[]`
- **outRealLowerBand**: Lower band values: `double[]`

## Interpretation

### Price Position
- **Near Upper Band**: May indicate overbought conditions
- **Near Lower Band**: May indicate oversold conditions
- **Middle Band**: Acts as support in uptrends, resistance in downtrends

### Band Width
- **Wide Bands**: High volatility, large price swings
- **Narrow Bands**: Low volatility, consolidation
- **Squeeze**: Bands contract to historically narrow levels - often precedes significant move

### Price Action Relative to Bands

1. **Walking the Bands**:
   - In strong uptrend: Price repeatedly touches/exceeds upper band
   - In strong downtrend: Price repeatedly touches/exceeds lower band

2. **Band Bounces**:
   - Price bounces off lower band in uptrend (support)
   - Price rejected at upper band in downtrend (resistance)

3. **Band Breakouts**:
   - Price closes outside bands may signal strong momentum
   - Breakouts often lead to continuation moves

### Common Patterns

1. **The Squeeze**:
   - Bands narrow significantly
   - Indicates consolidation and low volatility
   - Often followed by sharp move (breakout)
   - Direction of breakout determines trade direction

2. **M-Tops and W-Bottoms**:
   - **M-Top**: Two pushes to upper band, second fails to reach band - bearish
   - **W-Bottom**: Two pushes to lower band, second fails to reach band - bullish

3. **Riding the Bands**:
   - Strong trends can "walk" along a band
   - Price hugging upper band = strong uptrend
   - Price hugging lower band = strong downtrend

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double upperBand[100];
double middleBand[100];
double lowerBand[100];
int outBegIdx, outNBElement;

// Calculate Bollinger Bands (20, 2, 2, SMA)
TA_RetCode retCode = TA_BBANDS(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    20,                   // time period
    2.0,                  // upper deviation
    2.0,                  // lower deviation
    TA_MAType_SMA,        // MA type
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    upperBand,            // output: upper band
    middleBand,           // output: middle band
    lowerBand             // output: lower band
);
```

## Implementation Details

The TA-Lib BBANDS implementation:

1. **Moving Average**: Calculates the specified MA type over the period
2. **Standard Deviation**: Computes population standard deviation
3. **Band Calculation**: Adds/subtracts standard deviation multiples
4. **Flexible MA Types**: Supports various moving average types
5. **Asymmetric Bands**: Can use different deviations for upper and lower bands

### Calculation Steps
```
Step 1: Calculate Middle Band (MA of specified type)
Step 2: Calculate Standard Deviation over same period
Step 3: Upper Band = Middle + (NbDevUp × StdDev)
Step 4: Lower Band = Middle - (NbDevDn × StdDev)
```

## Trading Strategies

### 1. Mean Reversion Strategy
- **Buy**: When price touches lower band in uptrend
- **Sell**: When price touches upper band in downtrend
- **Exit**: At middle band or opposite band
- **Best in**: Range-bound markets

### 2. Breakout Strategy
- **Buy**: When price closes above upper band with volume
- **Sell**: When price closes below lower band with volume
- **Exit**: When price returns inside bands
- **Best in**: After consolidation (squeeze)

### 3. Trend Following
- **Buy**: When price walks along upper band
- **Sell**: When price walks along lower band
- **Exit**: When price crosses middle band
- **Best in**: Strong trending markets

### 4. Double Bollinger Bands
- Use two sets: (20,1) and (20,2)
- Four zones created: Strong Buy, Buy, Sell, Strong Sell
- More nuanced overbought/oversold readings

### 5. Bollinger Band Squeeze
- **Setup**: Bands narrow to multi-period low
- **Entry**: On breakout in either direction
- **Stop**: Opposite band
- **Target**: Multiple of band width
- **Best in**: After prolonged consolidation

## Statistical Background

### Why 2 Standard Deviations?
- In normal distribution, ~95% of data falls within 2 standard deviations
- Prices outside bands are statistically significant
- Suggests price may be overextended

### Volatility Measurement
Band width = (Upper Band - Lower Band) / Middle Band × 100

This normalized measure allows comparison across:
- Different securities
- Different time periods
- Different price levels

## Advantages

1. **Adaptive**: Automatically adjusts to volatility changes
2. **Visual**: Easy to interpret on charts
3. **Versatile**: Works for various strategies and timeframes
4. **Statistical Foundation**: Based on standard deviation
5. **Multi-Purpose**: Identifies trends, reversals, and volatility
6. **Self-Adjusting**: No fixed overbought/oversold levels

## Limitations and Considerations

1. **Not a Standalone System**: Best used with other indicators
2. **Lagging Component**: MA in middle creates lag
3. **Whipsaws**: Can generate false signals in choppy markets
4. **No Direction Prediction**: Shows volatility, not direction
5. **Parameter Sensitivity**: Different settings produce different results
6. **Normal Distribution Assumption**: Markets don't always follow normal distribution

## Common Variations

### 1. Different Periods
- **Short-term**: 10-period (more sensitive)
- **Standard**: 20-period (original)
- **Long-term**: 50-period (smoother)

### 2. Different Deviations
- **Wider Bands**: 3 standard deviations (99.7% of data)
- **Narrower Bands**: 1 standard deviation (68% of data)

### 3. Different MA Types
- **EMA**: More responsive to recent prices
- **WMA**: Linear weight to recent prices
- **SMA**: Original, equal weighting (most common)

## Related Functions

- **STDDEV**: Standard Deviation - component of Bollinger Bands
- **SMA**: Simple Moving Average - default middle band
- **EMA**: Exponential Moving Average - alternative middle band
- **ATR**: Average True Range - another volatility measure
- **KELTNER**: Keltner Channels - similar bands using ATR

## References

- **Book**: *Bollinger on Bollinger Bands* by John A. Bollinger (ISBN: 0071373683)
- [TA-Lib Source Code: ta_BBANDS.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_BBANDS.c)
- [John Bollinger's Official Site](https://www.bollingerbands.com)
- [Investopedia: Bollinger Bands](https://www.investopedia.com/terms/b/bollingerbands.asp)
- [StockCharts: Bollinger Bands](https://school.stockcharts.com/doku.php?id=technical_indicators:bollinger_bands)
- [Original TA-Doc: BBANDS](http://tadoc.org/indicator/BBANDS.htm)

## Additional Notes

John Bollinger introduced Bollinger Bands in the early 1980s, and they have become one of the most popular technical indicators. The indicator is unique in that it adapts to market conditions rather than using fixed levels.

### Key Insights

1. **The 95% Rule**: While bands represent 2 standard deviations (95% confidence interval), actual touches of the bands occur more than 5% of the time because:
   - Markets don't perfectly follow normal distribution
   - Serial correlation in prices
   - The MA itself is derived from the data

2. **Band Width Analysis**:
   - Track historical band width
   - Current width vs. historical average
   - Narrow width suggests volatility expansion ahead
   - Wide width suggests volatility contraction ahead

3. **Confirmation is Key**:
   - Use volume to confirm breakouts
   - Use other indicators (RSI, MACD) for confirmation
   - Consider price patterns and support/resistance

4. **Timeframe Considerations**:
   - Daily charts: Standard 20-period works well
   - Intraday: May need to adjust period (shorter)
   - Weekly/Monthly: Consider longer periods

Bollinger Bands are most effective when combined with other analytical tools and always in the context of overall market structure and trend.

