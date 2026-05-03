# STOCH - Stochastic Oscillator (Slow)

## Description

The Stochastic Oscillator is a momentum indicator that compares a security's closing price to its price range over a given time period. The oscillator's sensitivity to market movements can be reduced by adjusting the time period or by taking a moving average of the result. It generates values between 0 and 100.

## Category
Momentum Indicators

## Author
George Lane

## Calculation

The Stochastic Oscillator consists of four different lines: FASTK, FASTD, SLOWK, and SLOWD. The STOCH function returns SLOWK and SLOWD (the slow stochastic).

### Fast %K (FASTK)
```
%K = ((Close - LowestLow) / (HighestHigh - LowestLow)) × 100
```

Where:
- Close = Most recent closing price
- LowestLow = Lowest low over the K period
- HighestHigh = Highest high over the K period

### Fast %D (FASTD)
```
%D = SMA(Fast %K, FastD period)
```
Moving average smoothing of Fast %K

### Slow %K (SLOWK)
```
Slow %K = SMA(Fast %K, SlowK period)
```
This is equivalent to Fast %D when using the same period

### Slow %D (SLOWD)
```
Slow %D = SMA(Slow %K, SlowD period)
```
Signal line - moving average of Slow %K

## Parameters

- **optInFastK_Period** (default: 5): Period for calculating %K
  - Valid range: 1 to 100000
  - Common values: 5, 9, 14

- **optInSlowK_Period** (default: 3): Smoothing period for Slow %K
  - Valid range: 1 to 100000
  - Common values: 1, 3, 5

- **optInSlowK_MAType** (default: SMA): MA type for Slow %K smoothing
  - Valid range: 0 to 8
  - Options: SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, T3

- **optInSlowD_Period** (default: 3): Smoothing period for Slow %D
  - Valid range: 1 to 100000
  - Common values: 3, 5

- **optInSlowD_MAType** (default: SMA): MA type for Slow %D smoothing
  - Valid range: 0 to 8
  - Options: SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, T3

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- **outSlowK**: Slow %K values: `double[]` (range: 0 to 100)
- **outSlowD**: Slow %D values: `double[]` (range: 0 to 100)

## Interpretation

### Overbought/Oversold Levels
- **Overbought**: %K or %D > 80 (some traders use 75 or 70)
- **Oversold**: %K or %D < 20 (some traders use 25 or 30)
- **Neutral**: Between 20 and 80

### Trading Signals

1. **Crossovers** (Most Common):
   - **Buy Signal**: %K crosses above %D
   - **Sell Signal**: %K crosses below %D
   - More reliable in oversold/overbought zones

2. **Overbought/Oversold**:
   - **Buy**: When oscillator drops below 20 then rises back above
   - **Sell**: When oscillator rises above 80 then falls back below
   - Wait for confirmation from crossover

3. **Divergence**:
   - **Bullish Divergence**: Price makes lower lows, Stochastic makes higher lows
   - **Bearish Divergence**: Price makes higher highs, Stochastic makes lower highs
   - Often precedes trend reversals

4. **Bull/Bear Setup**:
   - **Bull Setup**: %K crosses above %D below 20 line
   - **Bear Setup**: %K crosses below %D above 80 line
   - Higher probability setups

5. **Hinge**:
   - Both lines flatten at extremes
   - Indicates consolidation before move
   - Direction of break from hinge gives signal

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double slowK[100], slowD[100];
int outBegIdx, outNBElement;

// Calculate Slow Stochastic (5, 3, 3)
TA_RetCode retCode = TA_STOCH(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    5,                    // fast K period
    3,                    // slow K period
    TA_MAType_SMA,        // slow K MA type
    3,                    // slow D period
    TA_MAType_SMA,        // slow D MA type
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    slowK,                // output: slow %K
    slowD                 // output: slow %D
);
```

## Implementation Details

The TA-Lib STOCH implementation:

1. **Range Calculation**: Finds highest high and lowest low over K period
2. **%K Calculation**: Computes position of close within range
3. **Smoothing**: Applies moving averages for Slow %K and Slow %D
4. **Flexibility**: Supports multiple MA types for smoothing
5. **Boundary Handling**: Properly handles extreme values (0 and 100)

### Calculation Steps
```
Step 1: Calculate Fast %K using high/low/close
Step 2: Apply SlowK_Period MA to Fast %K → Slow %K
Step 3: Apply SlowD_Period MA to Slow %K → Slow %D
Step 4: Both values normalized to 0-100 range
```

## Slow Stochastic vs. Fast Stochastic

| Characteristic | Fast Stochastic | Slow Stochastic |
|---------------|-----------------|-----------------|
| Calculation | FASTK & FASTD | SLOWK & SLOWD |
| Smoothing | Less | More |
| Sensitivity | High | Moderate |
| Signals | More frequent | More reliable |
| Whipsaws | More | Fewer |
| Best For | Volatile markets | Trending markets |

The Slow Stochastic (STOCH) is more widely used because it reduces false signals through additional smoothing.

## Trading Strategies

### 1. Classic Crossover Strategy
- **Entry**: %K crosses %D
- **Filter**: Only take signals in oversold (<20) or overbought (>80)
- **Exit**: Opposite crossover or opposite zone
- **Best in**: Ranging markets

### 2. Overbought/Oversold Strategy
- **Buy**: Stochastic < 20, then crosses back above 20
- **Sell**: Stochastic > 80, then crosses back below 80
- **Confirmation**: Wait for %K/%D crossover
- **Best in**: Mean-reverting markets

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and Stochastic
- **Entry**: Wait for confirmation (crossover or support/resistance)
- **Stop**: Beyond recent high/low
- **Target**: Previous swing or opposite zone
- **Best in**: Trend exhaustion points

### 4. Bull/Bear Setup
- **Bull**: Wait for Stochastic < 20, then %K crosses above %D
- **Bear**: Wait for Stochastic > 80, then %K crosses below %D
- **Advantage**: Higher probability setups
- **Best in**: After pullbacks in trends

### 5. Trend Filter Strategy
- **Trend**: Use longer-term MA to determine trend
- **Entry**: Only take Stochastic signals in trend direction
- **Exit**: Stochastic opposite signal or trend change
- **Best in**: Trending markets

## Parameter Selection

### Fast K Period
- **Shorter (3-5)**: More sensitive, more signals, more noise
- **Standard (5-9)**: Balanced responsiveness
- **Longer (14-21)**: Smoother, fewer signals, less noise

### Slow K Period
- **No Smoothing (1)**: Equivalent to Fast Stochastic
- **Light Smoothing (3)**: Standard, reduces noise moderately
- **Heavy Smoothing (5)**: Very smooth, slower signals

### Slow D Period
- **Standard (3)**: Most common
- **Longer (5-7)**: Even smoother signal line

## Advantages

1. **Clear Overbought/Oversold**: Explicit 0-100 scale
2. **Leading Indicator**: Can signal before price turns
3. **Divergence Detection**: Effective at spotting divergences
4. **Flexible**: Adjustable parameters for different markets
5. **Visual**: Easy to interpret on charts
6. **Popular**: Widely understood and available

## Limitations and Considerations

1. **False Signals in Trends**: Can remain overbought/oversold during strong trends
2. **Whipsaws**: Generates false signals in choppy markets
3. **No Price Context**: Doesn't consider absolute price levels
4. **Parameter Sensitivity**: Results vary significantly with settings
5. **Lagging Element**: Smoothing creates lag
6. **Range Dependency**: Sensitive to price range selection

## Market Application

### Different Market Conditions

**Trending Markets**:
- Use as divergence indicator
- Ignore overbought/oversold in trend direction
- Only fade trend with strong divergence + confirmation

**Ranging Markets**:
- Trade overbought/oversold levels
- Use crossovers for entry/exit
- Most effective application of Stochastic

**Volatile Markets**:
- Consider shorter periods for faster signals
- Or use Fast Stochastic (STOCHF)
- Wider stop losses

**Low Volatility Markets**:
- Standard settings work well
- Can use tighter overbought/oversold levels (25/75)

## Related Functions

- **STOCHF**: Fast Stochastic - more sensitive version
- **STOCHRSI**: Stochastic RSI - applies Stochastic formula to RSI
- **RSI**: Relative Strength Index - another momentum oscillator
- **CCI**: Commodity Channel Index - similar overbought/oversold indicator
- **WILLR**: Williams %R - similar calculation, inverted scale

## References

- [TA-Lib Source Code: ta_STOCH.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_STOCH.c)
- [Investopedia: Stochastic Oscillator](https://www.investopedia.com/terms/s/stochasticoscillator.asp)
- [StockCharts: Stochastic Oscillator](https://school.stockcharts.com/doku.php?id=technical_indicators:stochastic_oscillator_fast_slow_and_full)
- [Original TA-Doc: STOCH](http://tadoc.org/indicator/STOCH.htm)

## Additional Notes

The Stochastic Oscillator was developed by George Lane in the late 1950s. His original insight was that in uptrends, prices tend to close near their high, and in downtrends, they close near their low. The oscillator tracks this relationship to identify momentum changes.

### Key Insights

1. **Fast vs. Slow**: Most traders prefer Slow Stochastic because:
   - Fewer false signals
   - Smoother, more reliable crossovers
   - Better for position trading

2. **Standard Settings**: The default 5,3,3 or 14,3,3 work well:
   - 5,3,3 for shorter-term trading
   - 14,3,3 for longer-term analysis
   - Some traders use 14,1,3 for faster signals

3. **Multiple Timeframe Analysis**:
   - Higher timeframe for trend
   - Lower timeframe for entry timing
   - Both must align for best setups

4. **Confirmation is Critical**:
   - Don't trade Stochastic alone
   - Confirm with:
     * Price action and chart patterns
     * Support and resistance levels
     * Volume analysis
     * Trend indicators (MAs, MACD)

5. **Zone Trading**: Instead of fixed 20/80 levels:
   - 30/70 in strong trends
   - 25/75 in moderate conditions
   - 20/80 in ranging markets

The Stochastic Oscillator is best used as a confirming indicator rather than a primary signal generator. It's particularly effective when combined with trend-following indicators and price action analysis.

