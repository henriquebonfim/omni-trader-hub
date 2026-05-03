# AROONOSC - Aroon Oscillator

## Description

The Aroon Oscillator is the difference between Aroon Up and Aroon Down, providing a single line that oscillates around zero. It simplifies the Aroon indicator by combining both components into one oscillator, making it easier to interpret trend changes and strength.

## Category
Momentum Indicators

## Author
Tushar Chande

## Calculation

The Aroon Oscillator is simply the difference between Aroon Up and Aroon Down:

### Formula
```
Aroon Oscillator = Aroon Up - Aroon Down
```

Where:
- Aroon Up = ((n - Periods Since Highest High) / n) × 100
- Aroon Down = ((n - Periods Since Lowest Low) / n) × 100

### Range
- **+100 to -100**: Full range of oscillation
- **Positive**: Aroon Up > Aroon Down (uptrend bias)
- **Negative**: Aroon Down > Aroon Up (downtrend bias)
- **Zero**: Equal Aroon values (sideways)

## Parameters

- **optInTimePeriod** (default: 14): Lookback period
  - Valid range: 2 to 100000
  - Common values: 14, 25, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`

## Outputs
- Aroon Oscillator values: `double[]` (range: -100 to +100)

## Interpretation

### Oscillator Values
- **+100**: Aroon Up = 100, Aroon Down = 0 (strongest uptrend)
- **-100**: Aroon Up = 0, Aroon Down = 100 (strongest downtrend)
- **0**: Aroon Up = Aroon Down (sideways/transition)
- **+50 to +100**: Strong uptrend
- **-50 to -100**: Strong downtrend
- **-50 to +50**: Weak trend or sideways

### Trading Signals

1. **Zero Line Crossovers**:
   - **Buy**: Oscillator crosses above 0
   - **Sell**: Oscillator crosses below 0
   - **Best in**: Trend change detection

2. **Extreme Values**:
   - **+100**: New high just made, strongest uptrend
   - **-100**: New low just made, strongest downtrend
   - **Both extremes**: Consolidation (recent highs and lows)

3. **Trend Strength**:
   - **Strong Uptrend**: Oscillator > +50
   - **Strong Downtrend**: Oscillator < -50
   - **Weak Trend**: Oscillator between -50 and +50

4. **Divergence**:
   - **Bullish**: Price lower lows, Oscillator higher lows
   - **Bearish**: Price higher highs, Oscillator lower highs

## Usage Example

```c
// C/C++ Example
double high[100], low[100];
double aroonOsc[100];
int outBegIdx, outNBElement;

// Calculate 14-period Aroon Oscillator
TA_RetCode retCode = TA_AROONOSC(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    aroonOsc              // output: Aroon Oscillator
);
```

## Implementation Details

The TA-Lib AROONOSC implementation:

1. **Aroon Calculation**: Calculates both Aroon Up and Down
2. **Oscillator**: Subtracts Aroon Down from Aroon Up
3. **Lookback**: Requires n periods for first output
4. **Range**: Output bounded between -100 and +100

## Trading Strategies

### 1. Zero Line Strategy
- **Buy**: Oscillator crosses above 0
- **Sell**: Oscillator crosses below 0
- **Filter**: Only trade when |Oscillator| > 25
- **Best in**: Trend change detection

### 2. Extreme Value Strategy
- **Buy**: Oscillator reaches +100 (new high)
- **Sell**: Oscillator reaches -100 (new low)
- **Confirmation**: Wait for price confirmation
- **Best in**: Breakout trading

### 3. Trend Strength Strategy
- **Strong Buy**: Oscillator > +50
- **Strong Sell**: Oscillator < -50
- **Neutral**: Oscillator between -50 and +50
- **Best in**: Trend strength assessment

### 4. Divergence Strategy
- **Setup**: Identify divergence between price and oscillator
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

## Advantages

1. **Simplified**: Single line easier to interpret
2. **Clear Signals**: Zero line crossovers are obvious
3. **Trend Strength**: Magnitude shows trend strength
4. **Bounded**: Always between -100 and +100
5. **Early Warning**: Can signal trend changes early

## Limitations

1. **Lagging**: Based on historical extremes
2. **Whipsaws**: Possible in choppy markets
3. **No Magnitude**: Doesn't measure price movement size
4. **Period Sensitivity**: Results vary with period choice
5. **Choppy Markets**: Difficult in ranging conditions

## Comparison with Aroon

| Aspect | Aroon | Aroon Oscillator |
|--------|-------|-----------------|
| Lines | Two (Up/Down) | One (difference) |
| Interpretation | More complex | Simpler |
| Signals | Crossover between lines | Zero line crossover |
| Trend Strength | Compare two values | Single magnitude |
| Best For | Detailed analysis | Quick signals |

## Related Functions

- **AROON**: Aroon - original two-line version
- **ADX**: Average Directional Index - trend strength
- **PLUS_DI**: Plus Directional Indicator - upward movement
- **MINUS_DI**: Minus Directional Indicator - downward movement

## References

- **Book**: *The New Technical Trader* by Tushar Chande and Stanley Kroll
- [TA-Lib Source Code: ta_AROONOSC.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_AROONOSC.c)
- [Investopedia: Aroon Oscillator](https://www.investopedia.com/terms/a/aroonoscillator.asp)
- [StockCharts: Aroon Oscillator](https://school.stockcharts.com/doku.php?id=technical_indicators:aroon_oscillator)

## Additional Notes

The Aroon Oscillator simplifies the Aroon indicator by combining both components into a single oscillator. This makes it easier to use for traders who prefer single-line indicators.

### Key Insights

1. **Simplified Analysis**:
   - Single line instead of two
   - Zero line as neutral point
   - Positive/negative for trend direction
   - Magnitude for trend strength

2. **Zero Line Significance**:
   - Zero = equal Aroon Up and Down
   - Crossing zero = trend change
   - Distance from zero = trend strength
   - Most important level for signals

3. **Extreme Values**:
   - +100 = strongest possible uptrend
   - -100 = strongest possible downtrend
   - Rare to reach extremes
   - Indicates trend exhaustion when reached

4. **Best Applications**:
   - Trend change detection
   - Trend strength measurement
   - Breakout confirmation
   - Divergence analysis

5. **Combination Strategies**:
   - Use for trend direction
   - Combine with price action
   - Use volume for confirmation
   - Multiple timeframes for context

### Practical Tips

**For Trend Changes**:
- Watch for zero line crossovers
- Confirm with price action
- Use volume for validation
- Set stops beyond recent extremes

**For Trend Strength**:
- Distance from zero shows strength
- > +50 = strong uptrend
- < -50 = strong downtrend
- -50 to +50 = weak trend

**For Breakouts**:
- Oscillator at extremes = new highs/lows
- Wait for price confirmation
- Use volume for validation
- Set stops beyond breakout level

**Avoiding Whipsaws**:
- Use in trending markets
- Avoid in ranging conditions
- Combine with trend filter (ADX)
- Require confirmation from other indicators

The Aroon Oscillator is particularly valuable for traders who want the benefits of Aroon analysis but prefer a simpler, single-line indicator. It's excellent for trend change detection and provides clear, objective signals.

