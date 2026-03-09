# CDLHAMMER - Hammer

## Description

The Hammer is a bullish reversal candlestick pattern that typically appears at the bottom of downtrends. It has a small body at the top of the candle with a long lower shadow and little to no upper shadow. The Hammer suggests that sellers pushed prices down significantly, but buyers stepped in to push prices back up, creating a potential reversal signal.

## Category
Pattern Recognition / Candlestick Patterns

## Author
Traditional Japanese Candlestick Analysis

## Calculation

A Hammer is identified by specific criteria:

### Criteria
1. **Small Body**: Body at top of candle
2. **Long Lower Shadow**: Significantly longer than the body (adaptive threshold)
3. **Little Upper Shadow**: Minimal or no upper shadow
4. **Position**: Appears after downtrend

### Visual Characteristics
- **Small Body**: Small real body at top
- **Long Lower Shadow**: Long lower wick
- **No Upper Shadow**: Minimal upper wick
- **Reversal Signal**: Bullish reversal pattern

## Implementation Note

**This pattern uses TA-Lib's adaptive threshold system** for determining candle characteristics like "long body", "short body", "doji", etc. These thresholds automatically adjust based on recent market behavior rather than using fixed percentages.

For detailed information about:
- How adaptive thresholds work
- Configuring pattern detection sensitivity  
- Understanding output values
- Technical implementation details

See: [Candlestick Pattern Recognition Overview](CANDLESTICK_PATTERNS_OVERVIEW.md)


## Parameters

None - CDLHAMMER is a pattern recognition function

## Inputs
- **Open** prices: `double[]`
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- Pattern values: `int[]` (100 = Hammer, 0 = No Hammer)

## Interpretation

### Hammer Characteristics
1. **Small Body**: Body size relative to range
2. **Long Lower Shadow**: At least 2x body size
3. **Minimal Upper Shadow**: Little to no upper wick
4. **Bullish Signal**: Potential reversal upward

### Trading Signals

1. **Bullish Reversal**:
   - **Setup**: Hammer after downtrend
   - **Signal**: Potential bottom formation
   - **Confirmation**: Next candle up
   - **Best in**: Downtrend bottoms

2. **Support Level**:
   - **Setup**: Hammer at support
   - **Signal**: Strong support confirmation
   - **Entry**: On bounce from support
   - **Best in**: Key support levels

3. **Volume Confirmation**:
   - **Setup**: Hammer with high volume
   - **Signal**: Strong buying interest
   - **Entry**: On volume confirmation
   - **Best in**: High conviction setups

## Usage Example

```c
// C/C++ Example
double open[100], high[100], low[100], close[100];
int hammerPattern[100];
int outBegIdx, outNBElement;

// Detect Hammer patterns
TA_RetCode retCode = TA_CDLHAMMER(
    0,                    // start index
    99,                   // end index
    open,                 // open prices
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    hammerPattern         // output: Hammer patterns
);
```

## Implementation Details

The TA-Lib CDLHAMMER implementation:

1. **Body Calculation**: Determines body size and position
2. **Shadow Analysis**: Measures lower and upper shadows
3. **Ratio Check**: Ensures lower shadow is 2x body size
4. **Pattern Recognition**: Returns 100 for Hammer, 0 otherwise

## Trading Strategies

### 1. Hammer Reversal Strategy
- **Setup**: Hammer after downtrend
- **Entry**: On next candle up
- **Stop**: Below Hammer low
- **Target**: Previous resistance
- **Best in**: Trend reversals

### 2. Hammer + Support Strategy
- **Setup**: Hammer at support level
- **Entry**: On bounce from support
- **Stop**: Below support
- **Target**: Next resistance
- **Best in**: Support trading

### 3. Hammer + Volume Strategy
- **Setup**: Hammer with high volume
- **Entry**: On volume confirmation
- **Stop**: Below Hammer low
- **Target**: Measured move
- **Best in**: High conviction setups

### 4. Multiple Hammer Strategy
- **Setup**: Multiple Hammers in sequence
- **Entry**: On clear direction
- **Stop**: Below all Hammer lows
- **Target**: Previous resistance
- **Best in**: Strong support areas

## Hammer Variations

### 1. Standard Hammer
- **Characteristics**: Small body, long lower shadow
- **Meaning**: Buyers stepped in at lows
- **Signal**: Bullish reversal
- **Best in**: Downtrend bottoms

### 2. Inverted Hammer
- **Characteristics**: Small body, long upper shadow
- **Meaning**: Buyers tried to push up
- **Signal**: Potential reversal
- **Best in**: Downtrend bottoms

### 3. Dragonfly Doji
- **Characteristics**: No body, long lower shadow
- **Meaning**: Strong rejection of lows
- **Signal**: Very bullish
- **Best in**: Strong support levels

## Advantages

1. **Clear Signal**: Obvious reversal pattern
2. **High Success Rate**: Reliable when confirmed
3. **Risk Management**: Clear stop level
4. **Universal**: Works across all markets
5. **Simple**: Easy to identify

## Limitations

1. **Requires Confirmation**: Not a standalone signal
2. **False Signals**: Can occur without reversal
3. **Context Dependent**: Needs downtrend context
4. **Volume Important**: Volume confirmation needed
5. **Timing**: Entry timing can be difficult

## Related Functions

- **CDLINVERTEDHAMMER**: Inverted Hammer - similar pattern
- **CDLDRAGONFLYDOJI**: Dragonfly Doji - related pattern
- **CDLHANGINGMAN**: Hanging Man - bearish version
- **CDLDOJI**: Doji - indecision pattern

## References

- **Book**: *Japanese Candlestick Charting Techniques* by Steve Nison
- [TA-Lib Source Code: ta_CDLHAMMER.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_CDLHAMMER.c)
- [Investopedia: Hammer](https://www.investopedia.com/terms/h/hammer.asp)
- [StockCharts: Hammer](https://school.stockcharts.com/doku.php?id=chart_analysis:candlesticks)

## Additional Notes

The Hammer is one of the most reliable bullish reversal patterns. It's particularly significant when it appears after a strong downtrend, as it often signals that selling pressure has been exhausted and buyers are stepping in.

### Key Insights

1. **Reversal Signal**:
   - Strong bullish reversal pattern
   - Sellers exhausted, buyers stepping in
   - Potential bottom formation
   - Requires confirmation

2. **Support Confirmation**:
   - Hammer at support = strong signal
   - Multiple Hammers = very strong support
   - Volume confirmation important
   - Next candle direction crucial

3. **Risk Management**:
   - Clear stop level (below Hammer low)
   - Risk/reward ratio favorable
   - Position sizing important
   - Multiple timeframe analysis

4. **Best Applications**:
   - Downtrend bottoms
   - Support level trading
   - Reversal strategies
   - High conviction setups

5. **Confirmation Required**:
   - Never trade Hammer alone
   - Wait for next candle
   - Use volume analysis
   - Combine with support/resistance

### Practical Tips

**For Reversal Trading**:
- Wait for Hammer after downtrend
- Confirm with next candle up
- Use volume for validation
- Set stops below Hammer low

**For Support Trading**:
- Hammer at support = strong signal
- Wait for bounce confirmation
- Use volume for validation
- Set stops below support

**For Risk Management**:
- Clear stop level below Hammer
- Favorable risk/reward ratio
- Position sizing based on risk
- Multiple timeframe confirmation

**For Entry Timing**:
- Wait for next candle up
- Use volume confirmation
- Combine with other indicators
- Avoid in ranging markets

The Hammer is particularly valuable for identifying potential reversal points and strong support levels. It's one of the most reliable candlestick patterns when properly confirmed and used in the right context.

