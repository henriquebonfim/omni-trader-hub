# TEMA - Triple Exponential Moving Average

## Description

The Triple Exponential Moving Average (TEMA) is an advanced moving average developed by Patrick Mulloy that further reduces lag compared to DEMA. It uses three exponential moving averages combined in a way that significantly improves responsiveness while maintaining reasonable smoothness.

## Category
Overlap Studies

## Author
Patrick Mulloy

## Calculation

TEMA extends the DEMA concept to three levels of exponential smoothing:

### Formula
```
TEMA = (3 × EMA1) - (3 × EMA2) + EMA3
```

Where:
- EMA1 = EMA(Price, n)
- EMA2 = EMA(EMA1, n)
- EMA3 = EMA(EMA2, n)

### Detailed Steps
```
Step 1: Calculate first EMA
        EMA1 = EMA(Price, period)

Step 2: Calculate EMA of EMA1
        EMA2 = EMA(EMA1, period)

Step 3: Calculate EMA of EMA2
        EMA3 = EMA(EMA2, period)

Step 4: Calculate TEMA
        TEMA = (3 × EMA1) - (3 × EMA2) + EMA3
```

## Parameters

- **optInTimePeriod** (default: 30): Period for the exponential moving averages
  - Valid range: 2 to 100000
  - Common values: 9, 20, 30

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- TEMA values: `double[]`

## Interpretation

### Characteristics
- **Minimum Lag**: Among the lowest lag of traditional moving averages
- **Maximum Responsiveness**: Reacts very quickly to price changes
- **Reasonable Smoothness**: Despite responsiveness, maintains smoothness
- **Tracks Price Closely**: Hugs price action more than SMA, EMA, or DEMA

### Usage
1. **Trend Identification**:
   - Price above TEMA = Strong uptrend signal
   - Price below TEMA = Strong downtrend signal
   - TEMA slope shows trend strength

2. **Entry/Exit Signals**:
   - Price crossing TEMA generates signals
   - Earlier signals than traditional MAs
   - May require confirmation

3. **Dynamic Support/Resistance**:
   - TEMA acts as very responsive support/resistance
   - Useful for placing stops
   - Good for trailing stops

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double temaOutput[100];
int outBegIdx, outNBElement;

// Calculate 20-period TEMA
TA_RetCode retCode = TA_TEMA(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    20,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    temaOutput            // output: TEMA values
);
```

## Implementation Details

The TA-Lib TEMA implementation:

1. **Triple Smoothing**: Applies EMA three times
2. **Weighted Combination**: Uses 3×EMA1 - 3×EMA2 + EMA3 formula
3. **Lag Reduction**: Each level of combination reduces more lag
4. **Lookback**: Longer than DEMA due to triple smoothing

### Calculation Efficiency
Despite three levels of smoothing, TEMA is computed efficiently:
- Single pass through data
- Maintains running EMAs
- O(n) time complexity

## Trading Strategies

### 1. TEMA Trend Following
- **Buy**: Price crosses above TEMA, TEMA rising
- **Hold**: Price stays above TEMA
- **Sell**: Price crosses below TEMA
- **Stop**: Below recent TEMA touch
- **Best in**: Strong trending markets

### 2. Multiple TEMA System
- **Setup**: Two TEMAs (e.g., 9 and 21 period)
- **Buy**: Fast TEMA crosses above slow TEMA
- **Sell**: Fast TEMA crosses below slow TEMA
- **Advantage**: Very early trend change detection
- **Best in**: Capturing new trends early

### 3. TEMA + Price Action
- **Context**: Use TEMA for overall trend
- **Entry**: Price patterns at TEMA touches
- **Example**: Bull flag pullback to TEMA in uptrend
- **Confirmation**: Candlestick patterns
- **Best in**: Combining technical analysis methods

### 4. TEMA + Oscillator
- **Trend**: TEMA determines trend direction
- **Timing**: Oscillator (RSI, Stochastic) for entry
- **Buy**: TEMA uptrend + oscillator oversold
- **Sell**: TEMA downtrend + oscillator overbought
- **Best in**: Timing entries in established trends

## Advantages

1. **Minimal Lag**: Closest to price among traditional MAs
2. **Early Signals**: Generates signals before other MAs
3. **Smooth**: Maintains smoothness despite responsiveness
4. **Trend Tracking**: Excellent at following price trends
5. **Versatile**: Works on all timeframes

## Limitations and Considerations

1. **Increased Whipsaws**: Very responsive = more false signals
2. **Choppy Markets**: Difficult in ranging conditions
3. **Overshoot**: Can overshoot during sharp reversals
4. **Confirmation Needed**: Often requires additional confirmation
5. **Complexity**: More complex than simpler alternatives
6. **Not for Beginners**: Requires experience to use effectively

## Moving Average Comparison

| MA | Lag Level | Response Speed | Whipsaw Risk | Best Use |
|----|-----------|----------------|--------------|----------|
| SMA | Highest | Slowest | Lowest | Long-term trends |
| WMA | High | Slow | Low | Balanced approach |
| EMA | Medium | Medium | Medium | General purpose |
| DEMA | Low | Fast | Medium-High | Swing trading |
| TEMA | Lowest | Fastest | Highest | Day trading |

TEMA is at the extreme end of responsiveness vs. smoothness trade-off.

## Risk Management with TEMA

### Stop Loss Placement
Due to TEMA's responsiveness:
- **Wider Stops**: Use slightly wider stops than with slower MAs
- **ATR-Based**: Combine with ATR for volatility-adjusted stops
- **Trailing**: TEMA excellent for trailing stops

### Position Sizing
- **Smaller Positions**: With aggressive entry timing
- **Larger Positions**: When confirmed by other indicators
- **Scale In**: Add to position as trend confirms

## Related Functions

- **EMA**: Exponential Moving Average - building block
- **DEMA**: Double Exponential Moving Average - middle ground
- **KAMA**: Kaufman Adaptive Moving Average - adaptive alternative
- **T3**: T3 Moving Average - smooth low-lag alternative
- **SMA**: Simple Moving Average - baseline comparison

## References

- **Article**: "Smoothing Data with Faster Moving Averages" by Patrick G. Mulloy (Technical Analysis of Stocks & Commodities, January 1994)
- [TA-Lib Source Code: ta_TEMA.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_TEMA.c)
- [Investopedia: TEMA](https://www.investopedia.com/terms/t/triple-exponential-moving-average.asp)
- [Original TA-Doc: TEMA](http://tadoc.org/indicator/TEMA.htm)

## Additional Notes

Patrick Mulloy developed TEMA as an extension of his DEMA work, pushing lag reduction even further. TEMA represents close to the practical limit of lag reduction while maintaining moving average characteristics.

### Key Insights

1. **Lag Reduction Mechanism**:
   - Each EMA level adds lag
   - Weighted combination subtracts out the added lag
   - Result: Net lag reduction
   - TEMA achieves ~95% lag reduction vs. single EMA

2. **Trade-offs**:
   - Maximum responsiveness
   - Minimum lag
   - Cost: More false signals
   - Requires skilled interpretation

3. **Best Applications**:
   - Day trading: Fast reactions needed
   - Scalping: Very quick entries/exits
   - Strong trends: When speed matters
   - Volatile markets: Keeping up with price

4. **Not Ideal For**:
   - Ranging markets: Too many whipsaws
   - Choppy conditions: False signals
   - Long-term investing: Unnecessary responsiveness
   - Beginners: Requires experience

5. **Combining with Indicators**:
   - Use ADX to confirm trend strength
   - Use volume for confirmation
   - Use support/resistance for context
   - Use multiple timeframes for confirmation

6. **Period Selection**:
   - Very short (5-9): Scalping, extremely fast
   - Short (10-20): Day trading, very responsive
   - Medium (21-50): Swing trading, balanced
   - Long (50+): Position trading (rarely used with TEMA)

### Practical Tips

**For Entries**:
- Wait for price to clearly cross TEMA
- Confirm with volume surge
- Check higher timeframe alignment
- Use candlestick patterns for timing

**For Exits**:
- Use TEMA as trailing stop
- Exit on opposite TEMA cross
- Or use fixed risk/reward targets
- Monitor for divergences

**For False Signals**:
- More common in choppy markets
- Use ADX < 25 to avoid non-trending periods
- Require confirmation from second indicator
- Consider wider timeframe for context

TEMA is a powerful tool for experienced traders who need fast, responsive trend identification. However, its speed comes with the cost of more frequent false signals, requiring skill and experience to use effectively.

