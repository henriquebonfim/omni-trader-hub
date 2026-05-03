# AROON - Aroon

## Description

The Aroon indicator, developed by Tushar Chande, is a trend-following indicator that measures the time since the highest high and lowest low over a given period. It consists of two lines: Aroon Up and Aroon Down, which oscillate between 0 and 100. Aroon helps identify trend changes and strength by measuring how long it has been since the highest high and lowest low occurred.

## Category
Momentum Indicators

## Author
Tushar Chande

## Calculation

Aroon consists of two components:

### Aroon Up
```
Aroon Up = ((n - Periods Since Highest High) / n) × 100
```

### Aroon Down
```
Aroon Down = ((n - Periods Since Lowest Low) / n) × 100
```

Where:
- n = lookback period
- Periods Since Highest High = Number of periods since the highest high
- Periods Since Lowest Low = Number of periods since the lowest low

### Example
For a 14-period Aroon:
- If highest high was 3 periods ago: Aroon Up = ((14-3)/14) × 100 = 78.6
- If lowest low was 1 period ago: Aroon Down = ((14-1)/14) × 100 = 92.9

## Parameters

- **optInTimePeriod** (default: 14): Lookback period
  - Valid range: 2 to 100000
  - Common values: 14, 25, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`

## Outputs
- **outAroonDown**: Aroon Down values: `double[]` (0-100)
- **outAroonUp**: Aroon Up values: `double[]` (0-100)

## Interpretation

### Aroon Values
- **100**: New high/low just occurred (strong trend)
- **0**: High/low occurred n periods ago (weak trend)
- **50**: High/low occurred n/2 periods ago (moderate trend)

### Trend Identification
1. **Strong Uptrend**: Aroon Up > 70, Aroon Down < 30
2. **Strong Downtrend**: Aroon Down > 70, Aroon Up < 30
3. **Sideways**: Both Aroon values between 30-70
4. **Trend Change**: Aroon lines cross

### Trading Signals

1. **Aroon Crossovers**:
   - **Buy**: Aroon Up crosses above Aroon Down
   - **Sell**: Aroon Down crosses above Aroon Up
   - **Best in**: Trend change detection

2. **Extreme Values**:
   - **Aroon Up = 100**: New high just made (bullish)
   - **Aroon Down = 100**: New low just made (bearish)
   - **Both = 100**: New high and low (consolidation)

3. **Trend Strength**:
   - **Strong Trend**: One Aroon > 70, other < 30
   - **Weak Trend**: Both Aroon values 30-70
   - **No Trend**: Both Aroon values < 30

## Usage Example

```c
// C/C++ Example
double high[100], low[100];
double aroonUp[100], aroonDown[100];
int outBegIdx, outNBElement;

// Calculate 14-period Aroon
TA_RetCode retCode = TA_AROON(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    aroonUp,              // output: Aroon Up
    aroonDown             // output: Aroon Down
);
```

## Implementation Details

The TA-Lib Aroon implementation:

1. **High/Low Tracking**: Finds highest high and lowest low over period
2. **Period Calculation**: Counts periods since extremes
3. **Aroon Calculation**: Applies formula to both components
4. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Aroon Crossover Strategy
- **Buy**: Aroon Up crosses above Aroon Down
- **Sell**: Aroon Down crosses above Aroon Up
- **Filter**: Only trade when one Aroon > 70
- **Best in**: Trend change detection

### 2. Aroon + Trend Filter
- **Filter**: Use ADX for trend strength
- **Entry**: Aroon signal only if ADX > 25
- **Exit**: Aroon reversal or ADX < 20
- **Best in**: Avoiding ranging markets

### 3. Aroon Oscillator Strategy
- **Setup**: Calculate Aroon Oscillator (Aroon Up - Aroon Down)
- **Buy**: Oscillator crosses above 0
- **Sell**: Oscillator crosses below 0
- **Best in**: Simplified Aroon signals

### 4. Extreme Aroon Strategy
- **Buy**: Aroon Up = 100 (new high)
- **Sell**: Aroon Down = 100 (new low)
- **Confirmation**: Wait for price confirmation
- **Best in**: Breakout trading

## Aroon Oscillator

The Aroon Oscillator is the difference between Aroon Up and Aroon Down:

```
Aroon Oscillator = Aroon Up - Aroon Down
```

- **Positive**: Aroon Up > Aroon Down (uptrend)
- **Negative**: Aroon Down > Aroon Up (downtrend)
- **Zero**: Equal Aroon values (sideways)

## Advantages

1. **Trend Identification**: Excellent for trend detection
2. **Early Signals**: Provides early trend change signals
3. **Clear Levels**: 0-100 scale is intuitive
4. **Dual Component**: Two lines provide confirmation
5. **Universal**: Works across all markets and timeframes

## Limitations

1. **Lagging**: Based on historical extremes
2. **Whipsaws**: Can generate false signals
3. **Period Sensitivity**: Results vary with period choice
4. **No Magnitude**: Doesn't measure price movement size
5. **Choppy Markets**: Difficult in ranging conditions

## Period Selection

### Short Periods (5-10)
- **Characteristics**: More sensitive, frequent signals
- **Use**: Day trading, short-term trends
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Standard Periods (14-25)
- **Characteristics**: Balanced sensitivity
- **Use**: Swing trading, general analysis
- **Trade-off**: Good balance
- **Best for**: Most trading styles

### Long Periods (30-50)
- **Characteristics**: Less sensitive, fewer signals
- **Use**: Position trading, long-term trends
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Long-term analysis

## Related Functions

- **AROONOSC**: Aroon Oscillator - difference between Aroon Up and Down
- **ADX**: Average Directional Index - trend strength
- **PLUS_DI**: Plus Directional Indicator - upward movement
- **MINUS_DI**: Minus Directional Indicator - downward movement

## References

- **Book**: *The New Technical Trader* by Tushar Chande and Stanley Kroll
- [TA-Lib Source Code: ta_AROON.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_AROON.c)
- [Investopedia: Aroon](https://www.investopedia.com/terms/a/aroon.asp)
- [StockCharts: Aroon](https://school.stockcharts.com/doku.php?id=technical_indicators:aroon)

## Additional Notes

Tushar Chande developed Aroon as part of his work on trend-following systems. The key insight is that the time since the last extreme (high or low) is more important than the magnitude of price movement for trend identification.

### Key Insights

1. **Time-Based Analysis**:
   - Focuses on when extremes occurred
   - Not how much price moved
   - Time decay concept
   - Unique approach to trend analysis

2. **Trend Strength Measurement**:
   - Aroon Up = 100: Strong uptrend (recent high)
   - Aroon Down = 100: Strong downtrend (recent low)
   - Both high: Consolidation (recent highs and lows)
   - Both low: Weak trend (old extremes)

3. **Early Warning System**:
   - Aroon changes before price extremes
   - Can signal trend exhaustion
   - Useful for exit timing
   - Complements price-based indicators

4. **Best Applications**:
   - Trend identification
   - Trend change detection
   - Trend strength assessment
   - Breakout confirmation

5. **Combination Strategies**:
   - Use Aroon for trend direction
   - Use price action for entry timing
   - Use volume for confirmation
   - Use multiple timeframes for context

### Practical Tips

**For Trend Following**:
- Wait for Aroon Up > 70 for uptrends
- Wait for Aroon Down > 70 for downtrends
- Enter on pullbacks when trend confirmed
- Exit when Aroon lines cross

**For Trend Changes**:
- Watch for Aroon crossovers
- Confirm with price action
- Use volume for validation
- Set stops beyond recent extremes

**For Range Trading**:
- Avoid when both Aroon values < 30
- Use oscillators instead
- Wait for Aroon to show trend
- Trade breakouts when Aroon confirms

Aroon is particularly valuable for identifying trend changes and measuring trend strength. It's one of the few indicators that focuses on time rather than price magnitude, providing a unique perspective on market behavior.

