# SAR - Parabolic SAR

## Description

The Parabolic SAR (Stop and Reverse) is a trend-following indicator developed by J. Welles Wilder that provides entry and exit points. SAR stands for "Stop and Reverse," meaning when the indicator gives a signal, it suggests closing the current position and opening a new one in the opposite direction. The indicator appears as dots above or below price, moving progressively closer to price as the trend continues.

## Category
Overlap Studies / Trend Following

## Author
J. Welles Wilder

## Calculation

The Parabolic SAR calculation is complex and iterative:

### Basic Concept
- **SAR dots above price**: Downtrend (short position)
- **SAR dots below price**: Uptrend (long position)

### Formula
```
SAR(tomorrow) = SAR(today) + AF × (EP - SAR(today))
```

Where:
- **AF** = Acceleration Factor (starts at 0.02, increases by 0.02 each time EP makes new high/low, max usually 0.20)
- **EP** = Extreme Point (highest high in uptrend, lowest low in downtrend)
- **SAR** = Stop and Reverse point

### Calculation Rules
1. **Start**: SAR initialized at significant high (for downtrend) or low (for uptrend)
2. **AF increments**: Increases when new EP is made
3. **SAR limits**: Cannot be above prior two lows (uptrend) or below prior two highs (downtrend)
4. **Reversal**: When price touches SAR, trend reverses

## Parameters

- **optInAcceleration** (default: 0.02): Starting acceleration factor
  - Valid range: 0 to 3.0e+37
  - Standard: 0.02

- **optInMaximum** (default: 0.20): Maximum acceleration factor
  - Valid range: 0 to 3.0e+37
  - Standard: 0.20

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`

## Outputs
- SAR values: `double[]` (price levels for stops)

## Interpretation

### SAR Position
- **SAR below price**: Uptrend, hold long positions
- **SAR above price**: Downtrend, hold short positions
- **Price touches SAR**: Reverse position

### Trading Signals
1. **Buy Signal**: SAR flips from above to below price
2. **Sell Signal**: SAR flips from below to above price
3. **Trailing Stop**: Use SAR level as stop loss

### Acceleration Factor
- **Low AF (0.02-0.10)**: Wider stops, fewer reversals, trend following
- **High AF (0.15-0.30)**: Tighter stops, more reversals, quicker exits

## Usage Example

```c
// C/C++ Example
double high[100], low[100];
double sarOutput[100];
int outBegIdx, outNBElement;

// Calculate Parabolic SAR
TA_RetCode retCode = TA_SAR(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    0.02,                 // acceleration factor
    0.20,                 // maximum acceleration
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    sarOutput             // output: SAR values
);
```

## Implementation Details

The TA-Lib SAR implementation:

1. **Initialization**: Determines initial trend direction
2. **AF Management**: Tracks and increments acceleration factor
3. **EP Tracking**: Updates extreme point when new highs/lows made
4. **SAR Calculation**: Applies formula with constraints
5. **Reversal Detection**: Identifies when price touches SAR

### Complex Rules
- SAR cannot reverse into prior bars' range
- AF resets to 0.02 on each reversal
- EP resets on reversals
- Multiple edge cases handled

## Trading Strategies

### 1. Pure SAR Strategy
- **Long**: When SAR below price
- **Short**: When SAR above price
- **Reverse**: When SAR flips
- **Stop**: At SAR level
- **Best in**: Strongly trending markets

### 2. SAR + Trend Filter
- **Filter**: Use ADX or MA for trend confirmation
- **Entry**: SAR signal only if trend confirmed
- **Exit**: SAR reversal or trend filter exit
- **Best in**: Avoids ranging markets

### 3. SAR + Momentum
- **Setup**: SAR for direction
- **Confirmation**: RSI or MACD for momentum
- **Entry**: When both align
- **Exit**: SAR reversal
- **Best in**: High probability trend entries

### 4. SAR Trailing Stop
- **Entry**: Use other indicators for entry
- **Stop**: Place stop at SAR level
- **Trail**: Move stop as SAR moves
- **Exit**: When SAR hit or other signal
- **Best in**: Protecting profits in trends

## Advantages

1. **Clear Signals**: Unambiguous entry/exit points
2. **Always in Market**: Continuous long or short position
3. **Trailing Stops**: Automatically trailing stop levels
4. **Visual**: Easy to see on charts
5. **Objective**: No interpretation needed
6. **Trend Following**: Excellent for capturing trends

## Limitations

1. **Whipsaws**: Frequent reversals in ranging markets
2. **Lag**: Follows price, doesn't predict
3. **Fixed Logic**: Doesn't adapt to volatility changes
4. **Not for Ranging Markets**: Poor performance in sideways markets
5. **Always in Position**: Requires active management
6. **Parameter Sensitivity**: Results vary with AF settings

## Parameter Tuning

### Acceleration Factor (AF)
- **Conservative (0.01, 0.10)**:
  - Wider stops
  - Fewer reversals
  - Better for long-term trends
  - Less responsive

- **Standard (0.02, 0.20)**:
  - Wilder's original
  - Balanced approach
  - Most common

- **Aggressive (0.03, 0.30)**:
  - Tighter stops
  - More reversals
  - Better for short-term trading
  - More responsive

### Market-Specific Tuning
- **Volatile markets**: Lower AF to avoid whipsaws
- **Trending markets**: Standard or higher AF
- **Ranging markets**: Avoid SAR or use very low AF

## Market Application

### Best Markets for SAR
- **Trending stocks**: Works excellently
- **Commodities**: Originally designed for
- **Forex major pairs**: Generally good
- **Indices**: Works well on strong trends

### Poor Markets for SAR
- **Ranging markets**: Generates many false signals
- **Low liquidity**: Gaps can trigger premature reversals
- **Very volatile markets**: Too many reversals

## Related Functions

- **SAREXT**: Parabolic SAR Extended - more parameters
- **ADX**: Average Directional Index - trend strength filter
- **ATR**: Average True Range - can be used for stop placement

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder (ISBN: 0894590278)
- [TA-Lib Source Code: ta_SAR.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_SAR.c)
- [Investopedia: Parabolic SAR](https://www.investopedia.com/terms/p/parabolic-indicator-sar-stop-and-reverse.asp)
- [StockCharts: Parabolic SAR](https://school.stockcharts.com/doku.php?id=technical_indicators:parabolic_sar)

## Additional Notes

J. Welles Wilder introduced the Parabolic SAR in 1978. It's one of his most popular indicators alongside RSI and ATR. The "parabolic" name comes from the curved shape of the SAR dots as they accelerate toward price.

### Key Insights

1. **Stop and Reverse Philosophy**:
   - Always in the market (long or short)
   - Not suitable for all traders/strategies
   - Original commodities approach
   - Modern traders often use for stops only

2. **Acceleration is Key**:
   - SAR accelerates as trend continues
   - Represents trailing stop tightening
   - Forces profit taking on strong moves
   - Protects against sudden reversals

3. **Visual Power**:
   - One of the most visual indicators
   - Dots clearly show trend and stops
   - Easy for beginners to understand
   - No complex interpretation needed

4. **Combination Strategies**:
   - SAR alone generates too many signals
   - Best combined with trend filters (ADX, MA)
   - Use for position management, not just entry
   - Effective as trailing stop mechanism

5. **SAREXT vs. SAR**:
   - SAR: Standard, simple parameters
   - SAREXT: Extended version with more control
   - SAREXT allows different start values for AF
   - Most traders use standard SAR

### Practical Tips

**For Trend Following**:
- Use standard parameters (0.02, 0.20)
- Combine with ADX > 25 filter
- Ignore SAR signals when ADX < 25
- Take profits at SAR reversals

**For Stop Placement**:
- Enter on other signals
- Place stop at SAR level
- Move stop as SAR moves
- Never move stop against position

**For Volatile Markets**:
- Reduce max AF to 0.15 or 0.10
- Reduces number of reversals
- Wider stops accommodate volatility
- Fewer whipsaws

**For Quiet Markets**:
- Can increase max AF to 0.25-0.30
- Tighter stops appropriate
- More responsive to smaller moves
- Quick exits on reversals

The Parabolic SAR is most effective when used as a trend-following system with additional filters to avoid ranging markets, or as a trailing stop mechanism within a broader trading strategy.

