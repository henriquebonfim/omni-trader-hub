# CDLDOJI - Doji

## Description

The Doji is a candlestick pattern that occurs when the opening and closing prices are very close or equal, creating a cross-like appearance. The Doji represents market indecision and can signal potential trend reversals, especially when it appears after a strong trend. It's one of the most important single-candlestick patterns in technical analysis.

## Category
Pattern Recognition / Candlestick Patterns

## Author
Traditional Japanese Candlestick Analysis

## Calculation

A Doji is identified when the opening and closing prices are very close:

### Criteria
A Doji is detected when the real body (difference between open and close) is very small relative to the total range. The exact threshold is adaptive and adjusts to recent market behavior.

**Conceptually**: |Close - Open| is very small compared to (High - Low)

### Visual Characteristics
- **Small Body**: Very small or no real body
- **Long Shadows**: Upper and lower shadows can be long
- **Cross Shape**: Resembles a cross or plus sign
- **Indecision**: Represents market uncertainty

## Implementation Note

**This pattern uses TA-Lib's adaptive threshold system** for determining candle characteristics like "long body", "short body", "doji", etc. These thresholds automatically adjust based on recent market behavior rather than using fixed percentages.

For detailed information about:
- How adaptive thresholds work
- Configuring pattern detection sensitivity  
- Understanding output values
- Technical implementation details

See: [Candlestick Pattern Recognition Overview](CANDLESTICK_PATTERNS_OVERVIEW.md)


## Parameters

None - CDLDOJI is a pattern recognition function

## Inputs
- **Open** prices: `double[]`
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- Pattern values: `int[]` (100 = Doji, 0 = No Doji)

## Interpretation

### Doji Types

1. **Standard Doji**:
   - Open ≈ Close
   - Upper and lower shadows
   - Most common type

2. **Long-Legged Doji**:
   - Open ≈ Close
   - Very long upper and lower shadows
   - High volatility, strong indecision

3. **Dragonfly Doji**:
   - Open ≈ Close
   - Long lower shadow, no upper shadow
   - Bullish reversal signal

4. **Gravestone Doji**:
   - Open ≈ Close
   - Long upper shadow, no lower shadow
   - Bearish reversal signal

### Trading Signals

1. **Reversal Signal**:
   - **Bullish**: Doji after downtrend
   - **Bearish**: Doji after uptrend
   - **Confirmation**: Next candle confirms direction

2. **Indecision Signal**:
   - Market uncertainty
   - Potential trend change
   - Wait for confirmation
   - Volume analysis important

3. **Support/Resistance**:
   - Doji at key levels
   - Strong reversal potential
   - Multiple timeframe analysis
   - Price action confirmation

## Usage Example

```c
// C/C++ Example
double open[100], high[100], low[100], close[100];
int dojiPattern[100];
int outBegIdx, outNBElement;

// Detect Doji patterns
TA_RetCode retCode = TA_CDLDOJI(
    0,                    // start index
    99,                   // end index
    open,                 // open prices
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    dojiPattern           // output: Doji patterns
);
```

## Implementation Details

The TA-Lib CDLDOJI implementation:

1. **Body Calculation**: Determines if body is small enough
2. **Threshold Check**: Applies 10% threshold rule
3. **Pattern Recognition**: Returns 100 for Doji, 0 otherwise
4. **No Lookback**: Analyzes each candle independently

## Trading Strategies

### 1. Doji Reversal Strategy
- **Setup**: Doji after strong trend
- **Entry**: Wait for confirmation candle
- **Direction**: Opposite to previous trend
- **Stop**: Beyond Doji range
- **Best in**: Trend exhaustion

### 2. Doji + Support/Resistance
- **Setup**: Doji at key levels
- **Entry**: On breakout from Doji
- **Confirmation**: Volume and price action
- **Best in**: Key technical levels

### 3. Doji + Volume Analysis
- **Setup**: Doji with high volume
- **Entry**: On volume confirmation
- **Direction**: Volume direction
- **Best in**: High conviction setups

### 4. Multiple Doji Strategy
- **Setup**: Multiple Doji in sequence
- **Entry**: On clear direction
- **Confirmation**: Strong price action
- **Best in**: Consolidation periods

## Doji Variations

### 1. Long-Legged Doji
- **Characteristics**: Very long shadows
- **Meaning**: High volatility, strong indecision
- **Signal**: Strong reversal potential
- **Best in**: High volatility markets

### 2. Dragonfly Doji
- **Characteristics**: Long lower shadow, no upper shadow
- **Meaning**: Sellers rejected, buyers stepped in
- **Signal**: Bullish reversal
- **Best in**: Downtrend bottoms

### 3. Gravestone Doji
- **Characteristics**: Long upper shadow, no lower shadow
- **Meaning**: Buyers rejected, sellers stepped in
- **Signal**: Bearish reversal
- **Best in**: Uptrend tops

## Advantages

1. **Clear Signal**: Obvious indecision pattern
2. **Reversal Potential**: Strong reversal signal
3. **Universal**: Works across all markets
4. **Simple**: Easy to identify
5. **Reliable**: High success rate with confirmation

## Limitations

1. **Requires Confirmation**: Not a standalone signal
2. **False Signals**: Can occur without reversal
3. **Context Dependent**: Needs trend context
4. **Volume Important**: Volume confirmation needed
5. **Timing**: Entry timing can be difficult

## Related Functions

- **CDLDRAGONFLYDOJI**: Dragonfly Doji - specific type
- **CDLGRAVESTONEDOJI**: Gravestone Doji - specific type
- **CDLLONGLEGGEDDOJI**: Long Legged Doji - specific type
- **CDLHAMMER**: Hammer - similar reversal pattern

## References

- **Book**: *Japanese Candlestick Charting Techniques* by Steve Nison
- [TA-Lib Source Code: ta_CDLDOJI.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_CDLDOJI.c)
- [Investopedia: Doji](https://www.investopedia.com/terms/d/doji.asp)
- [StockCharts: Doji](https://school.stockcharts.com/doku.php?id=chart_analysis:candlesticks)

## Additional Notes

The Doji is one of the most important candlestick patterns because it represents pure market indecision. It's particularly significant when it appears after a strong trend, as it often signals exhaustion and potential reversal.

### Key Insights

1. **Indecision Signal**:
   - Represents market uncertainty
   - Buyers and sellers in balance
   - Potential trend change
   - Requires confirmation

2. **Reversal Potential**:
   - Strong reversal signal
   - Especially after trends
   - Volume confirmation important
   - Next candle direction crucial

3. **Context Matters**:
   - Doji after uptrend = bearish
   - Doji after downtrend = bullish
   - Doji in range = indecision
   - Doji at extremes = reversal

4. **Confirmation Required**:
   - Never trade Doji alone
   - Wait for next candle
   - Use volume analysis
   - Combine with support/resistance

5. **Best Applications**:
   - Trend exhaustion points
   - Key support/resistance levels
   - High volatility periods
   - Multiple timeframe analysis

### Practical Tips

**For Reversal Trading**:
- Wait for Doji after strong trend
- Confirm with next candle
- Use volume for validation
- Set stops beyond Doji range

**For Support/Resistance**:
- Doji at key levels = strong signal
- Wait for breakout direction
- Use volume for confirmation
- Set stops beyond Doji

**For Indecision Analysis**:
- Doji = market uncertainty
- Wait for clear direction
- Use other indicators
- Avoid trading until resolved

**For Risk Management**:
- Doji = high uncertainty
- Reduce position size
- Use wider stops
- Wait for confirmation

The Doji is particularly valuable for identifying potential reversal points and market indecision. It's one of the most reliable candlestick patterns when properly confirmed and used in the right context.

