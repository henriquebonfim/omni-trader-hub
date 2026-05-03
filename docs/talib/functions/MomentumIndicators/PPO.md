# PPO - Percentage Price Oscillator

## Description

The Percentage Price Oscillator (PPO) is a momentum indicator that measures the percentage difference between two exponential moving averages (EMAs). It's similar to MACD but expressed as a percentage rather than absolute values, making it easier to compare across different securities and price levels.

## Category
Momentum Indicators

## Author
Gerald Appel (adapted from MACD)

## Calculation

PPO is calculated as the percentage difference between two EMAs:

### Formula
```
PPO = ((Fast EMA - Slow EMA) / Slow EMA) × 100
```

Where:
- Fast EMA = Shorter period EMA (default: 12)
- Slow EMA = Longer period EMA (default: 26)

### Example
If Fast EMA = 102 and Slow EMA = 100:
```
PPO = ((102 - 100) / 100) × 100 = 2%
```

## Parameters

- **optInFastPeriod** (default: 12): Period for fast EMA
  - Valid range: 2 to 100000
  - Common values: 12 (standard), 9, 10

- **optInSlowPeriod** (default: 26): Period for slow EMA
  - Valid range: 2 to 100000
  - Common values: 26 (standard), 21, 30

- **optInMAType** (default: SMA): Moving average type used for EMAs
  - Valid range: 0 to 8
  - Options: SMA, EMA, WMA, DEMA, TEMA, TRIMA, KAMA, MAMA, T3

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- PPO values: `double[]` (percentage, unbounded)

## Interpretation

### PPO Values
- **Positive**: Fast EMA above slow EMA (uptrend momentum)
- **Negative**: Fast EMA below slow EMA (downtrend momentum)
- **Zero**: Fast EMA equals slow EMA (no momentum)
- **Increasing**: Momentum strengthening
- **Decreasing**: Momentum weakening

### Trading Signals

1. **Zero Line Crossovers**:
   - **Buy**: PPO crosses above 0
   - **Sell**: PPO crosses below 0
   - **Best in**: Trend change detection

2. **Momentum Changes**:
   - **Rising PPO**: Momentum increasing
   - **Falling PPO**: Momentum decreasing
   - **Peak PPO**: Momentum peak (potential reversal)
   - **Trough PPO**: Momentum trough (potential reversal)

3. **Divergence**:
   - **Bullish**: Price lower lows, PPO higher lows
   - **Bearish**: Price higher highs, PPO lower highs
   - **Best in**: Trend exhaustion points

4. **Trend Strength**:
   - **Strong Uptrend**: PPO consistently positive and rising
   - **Strong Downtrend**: PPO consistently negative and falling
   - **Weak Trend**: PPO oscillating around zero

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double ppoOutput[100];
int outBegIdx, outNBElement;

// Calculate PPO (12, 26)
TA_RetCode retCode = TA_PPO(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    12,                   // fast period
    26,                   // slow period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    ppoOutput             // output: PPO values
);
```

## Implementation Details

The TA-Lib PPO implementation:

1. **Fast EMA**: Calculates shorter period EMA
2. **Slow EMA**: Calculates longer period EMA
3. **Percentage Calculation**: Computes percentage difference
4. **Lookback**: Requires slow period + EMA lookback

## Trading Strategies

### 1. Zero Line Strategy
- **Buy**: PPO crosses above 0
- **Sell**: PPO crosses below 0
- **Filter**: Only trade when |PPO| > 0.5%
- **Best in**: Trend change detection

### 2. Momentum Strategy
- **Buy**: PPO rising and positive
- **Sell**: PPO falling and negative
- **Exit**: PPO momentum change
- **Best in**: Trend following

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and PPO
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. PPO + Signal Line
- **Setup**: Calculate signal line (EMA of PPO)
- **Buy**: PPO crosses above signal line
- **Sell**: PPO crosses below signal line
- **Best in**: Smoothed signals

## PPO vs. MACD

| Aspect | PPO | MACD |
|--------|-----|------|
| Units | Percentage | Absolute |
| Comparison | Easy across securities | Difficult across securities |
| Scaling | Automatic | Manual |
| Interpretation | Percentage change | Absolute difference |
| Best For | Portfolio analysis | Single security |

## Advantages

1. **Normalized**: Percentage makes comparison easy
2. **Universal**: Works across all securities
3. **Scalable**: No manual scaling needed
4. **Clear**: Easy to understand percentage
5. **Portfolio**: Useful for portfolio analysis

## Limitations

1. **No Bounds**: Unbounded percentage values
2. **Still Lags**: Based on EMAs, inherent lag
3. **Whipsaws**: Possible in choppy markets
4. **Period Sensitivity**: Results vary with periods
5. **No Standard Levels**: No defined overbought/oversold

## Period Selection

### Standard (12, 26)
- **Characteristics**: MACD equivalent
- **Use**: General momentum analysis
- **Trade-off**: Balanced approach
- **Best for**: Most applications

### Short (9, 21)
- **Characteristics**: More responsive
- **Use**: Short-term trading
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Long (21, 50)
- **Characteristics**: Smoother, less responsive
- **Use**: Long-term analysis
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Position trading

## Related Functions

- **MACD**: Moving Average Convergence/Divergence - absolute version
- **APO**: Absolute Price Oscillator - absolute difference
- **EMA**: Exponential Moving Average - building block
- **RSI**: Relative Strength Index - another momentum indicator

## References

- **Book**: *Stock Market Trading Systems* by Gerald Appel
- [TA-Lib Source Code: ta_PPO.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_PPO.c)
- [Investopedia: Percentage Price Oscillator](https://www.investopedia.com/terms/p/ppo.asp)
- [StockCharts: PPO](https://school.stockcharts.com/doku.php?id=technical_indicators:percentage_price_oscillator_ppo)

## Additional Notes

PPO was developed as an improvement over MACD, making it easier to compare momentum across different securities by using percentages instead of absolute values.

### Key Insights

1. **Percentage Advantage**:
   - Easy to compare across securities
   - No manual scaling required
   - Universal interpretation
   - Portfolio analysis friendly

2. **Momentum Measurement**:
   - Direct percentage momentum
   - Zero line as neutral
   - Distance from zero = strength
   - Direction = trend bias

3. **Best Applications**:
   - Portfolio momentum analysis
   - Cross-security comparison
   - Trend change detection
   - Momentum strength assessment

4. **Signal Interpretation**:
   - Zero line crossovers = trend changes
   - Rising/falling = momentum changes
   - Peaks/troughs = potential reversals
   - Divergences = trend exhaustion

5. **Combination Strategies**:
   - Use PPO for momentum direction
   - Combine with trend indicators
   - Use volume for confirmation
   - Multiple timeframes for context

### Practical Tips

**For Portfolio Analysis**:
- Compare PPO across securities
- Rank by PPO strength
- Rotate to strongest PPO
- Diversify by PPO correlation

**For Single Security**:
- Use zero line crossovers
- Watch for momentum changes
- Look for divergences
- Combine with price action

**For Trend Following**:
- PPO > 0 for uptrends
- PPO < 0 for downtrends
- Enter on momentum confirmation
- Exit on momentum loss

**For Divergence Trading**:
- Identify price vs. PPO divergence
- Wait for confirmation
- Use support/resistance
- Set stops beyond extremes

The PPO is particularly valuable for traders who need to compare momentum across multiple securities or want a normalized version of MACD. It's excellent for portfolio analysis and provides clear momentum signals.

