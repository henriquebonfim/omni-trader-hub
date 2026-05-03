# CMO - Chande Momentum Oscillator

## Description

The Chande Momentum Oscillator (CMO) is a momentum indicator developed by Tushar Chande that measures the momentum of price changes. Unlike RSI which uses smoothed gains and losses, CMO uses the sum of gains and losses over a period, making it more responsive to recent price changes. It oscillates between +100 and -100.

## Category
Momentum Indicators

## Author
Tushar Chande

## Calculation

CMO is calculated using the sum of gains and losses over a period:

### Formula
```
CMO = ((Sum of Gains - Sum of Losses) / (Sum of Gains + Sum of Losses)) × 100
```

Where:
- Sum of Gains = Sum of all positive price changes over period
- Sum of Losses = Sum of all negative price changes over period

### Detailed Steps
```
Step 1: Calculate price changes (Close - Previous Close)
Step 2: Separate gains (positive changes) and losses (negative changes)
Step 3: Sum all gains over the period
Step 4: Sum all losses over the period
Step 5: Apply CMO formula
```

### Example
For 5-period CMO with changes: [+2, -1, +3, -2, +1]
- Sum of Gains = 2 + 3 + 1 = 6
- Sum of Losses = 1 + 2 = 3
- CMO = ((6 - 3) / (6 + 3)) × 100 = (3/9) × 100 = 33.33

## Parameters

- **optInTimePeriod** (default: 14): Period for calculation
  - Valid range: 2 to 100000
  - Common values: 9, 14, 20

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- CMO values: `double[]` (range: -100 to +100)

## Interpretation

### CMO Values
- **+100**: All price changes were gains (strongest uptrend)
- **-100**: All price changes were losses (strongest downtrend)
- **0**: Equal gains and losses (no momentum)
- **+50 to +100**: Strong upward momentum
- **-50 to -100**: Strong downward momentum
- **-50 to +50**: Weak momentum or sideways

### Trading Signals

1. **Zero Line Crossovers**:
   - **Buy**: CMO crosses above 0
   - **Sell**: CMO crosses below 0
   - **Best in**: Momentum change detection

2. **Overbought/Oversold**:
   - **Overbought**: CMO > +50 (strong upward momentum)
   - **Oversold**: CMO < -50 (strong downward momentum)
   - **Extreme**: CMO > +80 or < -80

3. **Divergence**:
   - **Bullish**: Price lower lows, CMO higher lows
   - **Bearish**: Price higher highs, CMO lower highs
   - **Best in**: Trend exhaustion points

4. **Trend Strength**:
   - **Strong Uptrend**: CMO consistently positive
   - **Strong Downtrend**: CMO consistently negative
   - **Weak Trend**: CMO oscillating around zero

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double cmoOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period CMO
TA_RetCode retCode = TA_CMO(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    cmoOutput             // output: CMO values
);
```

## Implementation Details

The TA-Lib CMO implementation:

1. **Price Changes**: Calculates differences between consecutive closes
2. **Gain/Loss Separation**: Separates positive and negative changes
3. **Summation**: Sums gains and losses over period
4. **CMO Formula**: Applies the momentum formula
5. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Zero Line Strategy
- **Buy**: CMO crosses above 0
- **Sell**: CMO crosses below 0
- **Filter**: Only trade when |CMO| > 25
- **Best in**: Momentum change detection

### 2. Overbought/Oversold Strategy
- **Buy**: CMO < -50, then crosses above -50
- **Sell**: CMO > +50, then crosses below +50
- **Confirmation**: Wait for price confirmation
- **Best in**: Mean-reverting markets

### 3. Divergence Strategy
- **Setup**: Identify divergence between price and CMO
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 4. Trend Following Strategy
- **Uptrend**: CMO > 0, buy on pullbacks
- **Downtrend**: CMO < 0, sell on rallies
- **Exit**: CMO crosses zero
- **Best in**: Trending markets

## CMO vs. RSI

| Aspect | CMO | RSI |
|--------|-----|-----|
| Calculation | Sum of gains/losses | Smoothed gains/losses |
| Responsiveness | More responsive | Less responsive |
| Range | -100 to +100 | 0 to 100 |
| Zero Line | Yes (0) | No (50) |
| Smoothing | None | Wilder's smoothing |

## Advantages

1. **Responsive**: More responsive than RSI
2. **Zero Line**: Clear neutral point at 0
3. **Bounded**: Always between -100 and +100
4. **Momentum Focus**: Directly measures momentum
5. **Simple**: Easy to understand and use

## Limitations

1. **Noisy**: More volatile than RSI
2. **Whipsaws**: Can generate false signals
3. **Period Sensitivity**: Results vary with period choice
4. **No Smoothing**: Raw momentum without smoothing
5. **Choppy Markets**: Difficult in ranging conditions

## Period Selection

### Short Periods (5-9)
- **Characteristics**: Very responsive, noisy
- **Use**: Day trading, short-term momentum
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Standard Periods (14-20)
- **Characteristics**: Balanced responsiveness
- **Use**: Swing trading, general analysis
- **Trade-off**: Good balance
- **Best for**: Most trading styles

### Long Periods (25-50)
- **Characteristics**: Smoother, less responsive
- **Use**: Position trading, long-term trends
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Long-term analysis

## Related Functions

- **RSI**: Relative Strength Index - similar concept with smoothing
- **MOM**: Momentum - absolute change version
- **ROC**: Rate of Change - percentage change version
- **STOCH**: Stochastic Oscillator - range-based momentum

## References

- **Book**: *The New Technical Trader* by Tushar Chande and Stanley Kroll
- [TA-Lib Source Code: ta_CMO.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_CMO.c)
- [Investopedia: Chande Momentum Oscillator](https://www.investopedia.com/terms/c/chandemomentumoscillator.asp)
- [StockCharts: CMO](https://school.stockcharts.com/doku.php?id=technical_indicators:chande_momentum_oscillator)

## Additional Notes

Tushar Chande developed CMO as an improvement over RSI, making it more responsive to recent price changes by using raw sums instead of smoothed averages.

### Key Insights

1. **Momentum Measurement**:
   - Direct measurement of price momentum
   - No smoothing like RSI
   - More responsive to recent changes
   - Better for short-term analysis

2. **Zero Line Significance**:
   - Zero = equal gains and losses
   - Crossing zero = momentum change
   - Distance from zero = momentum strength
   - Most important level for signals

3. **Responsiveness vs. Smoothness**:
   - CMO: More responsive, more noisy
   - RSI: Less responsive, more smooth
   - Choose based on trading style
   - CMO better for short-term trading

4. **Best Applications**:
   - Short-term momentum analysis
   - Trend change detection
   - Overbought/oversold in trends
   - Divergence analysis

5. **Combination Strategies**:
   - Use CMO for momentum direction
   - Combine with trend indicators
   - Use volume for confirmation
   - Multiple timeframes for context

### Practical Tips

**For Momentum Trading**:
- Use zero line crossovers for signals
- Wait for confirmation from price action
- Use volume for validation
- Set stops beyond recent extremes

**For Trend Following**:
- CMO > 0 for uptrends
- CMO < 0 for downtrends
- Enter on pullbacks when trend confirmed
- Exit when CMO crosses zero

**For Overbought/Oversold**:
- Use ±50 as thresholds
- Wait for reversal signals
- Confirm with price patterns
- Avoid in strong trends

**Avoiding Whipsaws**:
- Use in trending markets
- Avoid in ranging conditions
- Combine with trend filter
- Require confirmation from other indicators

The CMO is particularly valuable for traders who need a more responsive momentum indicator than RSI. It's excellent for short-term momentum analysis and provides clear signals for momentum changes.

