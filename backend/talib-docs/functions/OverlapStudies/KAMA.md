# KAMA - Kaufman Adaptive Moving Average

## Description

The Kaufman Adaptive Moving Average (KAMA) is an adaptive moving average that automatically adjusts its smoothing based on market volatility. Developed by Perry Kaufman, it uses the Efficiency Ratio to determine how much smoothing to apply, making it more responsive in trending markets and smoother in ranging markets.

## Category
Overlap Studies

## Author
Perry Kaufman

## Calculation

KAMA uses an adaptive smoothing factor based on market efficiency:

### Step 1: Calculate Efficiency Ratio (ER)
```
ER = |Change| / Volatility
```

Where:
- Change = |Close - Close(n periods ago)|
- Volatility = Sum of |Close - Close(previous)| over n periods

### Step 2: Calculate Smoothing Constant (SC)
```
SC = [ER × (fastSC - slowSC) + slowSC]²
```

Where:
- fastSC = 2/(fast period + 1) = 2/3 = 0.67
- slowSC = 2/(slow period + 1) = 2/31 = 0.0645
- Default periods: fast = 2, slow = 30

### Step 3: Calculate KAMA
```
KAMA = KAMA(previous) + SC × [Price - KAMA(previous)]
```

## Parameters

- **optInTimePeriod** (default: 30): Period for efficiency ratio calculation
  - Valid range: 2 to 100000
  - Common values: 10, 14, 30

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- KAMA values: `double[]`

## Interpretation

### Adaptive Behavior
- **Trending Markets**: High efficiency → More responsive (like fast EMA)
- **Ranging Markets**: Low efficiency → More smoothing (like slow EMA)
- **Automatic Adjustment**: No manual parameter changes needed

### Efficiency Ratio
- **ER = 1.0**: Perfect trend (maximum responsiveness)
- **ER = 0.0**: No trend (maximum smoothing)
- **ER = 0.5**: Mixed conditions (balanced smoothing)

### Trading Signals
1. **Trend Following**:
   - Price above KAMA = Uptrend
   - Price below KAMA = Downtrend
   - KAMA slope indicates trend strength

2. **Crossovers**:
   - Price crossing KAMA = Trend change signal
   - More reliable than fixed-period MAs

3. **Adaptive Nature**:
   - Responds quickly to new trends
   - Smooths out noise in ranges
   - Self-adjusting to market conditions

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double kamaOutput[100];
int outBegIdx, outNBElement;

// Calculate 30-period KAMA
TA_RetCode retCode = TA_KAMA(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    30,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    kamaOutput            // output: KAMA values
);
```

## Implementation Details

The TA-Lib KAMA implementation:

1. **Efficiency Ratio**: Calculates market efficiency over period
2. **Smoothing Constant**: Derives adaptive smoothing factor
3. **KAMA Calculation**: Applies adaptive smoothing
4. **Initialization**: Uses SMA for first value
5. **Lookback**: Requires period + 1 bars for first output

## Trading Strategies

### 1. Pure KAMA Strategy
- **Buy**: Price crosses above KAMA
- **Sell**: Price crosses below KAMA
- **Stop**: Below/above KAMA
- **Best in**: All market conditions (adaptive)

### 2. KAMA + Trend Filter
- **Filter**: Use ADX for trend strength
- **Entry**: KAMA signal only if ADX > 25
- **Exit**: KAMA reversal or ADX < 20
- **Best in**: Avoiding ranging markets

### 3. Multiple KAMA System
- **Setup**: Two KAMAs (e.g., 10 and 30 period)
- **Buy**: Fast KAMA crosses above slow KAMA
- **Sell**: Fast KAMA crosses below slow KAMA
- **Best in**: Trend change detection

### 4. KAMA + Volatility
- **Context**: Use ATR for volatility
- **Entry**: KAMA signal with expanding ATR
- **Exit**: KAMA reversal or contracting ATR
- **Best in**: Volatility-based entries

## Advantages

1. **Adaptive**: Automatically adjusts to market conditions
2. **Trend Responsive**: Fast in trending markets
3. **Noise Reduction**: Smooth in ranging markets
4. **Self-Optimizing**: No manual parameter adjustment
5. **Universal**: Works across all markets and timeframes
6. **Efficient**: Combines benefits of fast and slow MAs

## Limitations

1. **Complex Calculation**: More complex than simple MAs
2. **Still Lags**: Adaptive but still has some lag
3. **Parameter Sensitivity**: Period choice affects results
4. **Whipsaws**: Possible in very choppy conditions
5. **Learning Curve**: Requires understanding of efficiency concept

## Efficiency Ratio Interpretation

### High Efficiency (ER > 0.5)
- **Market**: Strong trending
- **KAMA Behavior**: More responsive (like fast EMA)
- **Trading**: Good for trend following
- **Signals**: More frequent, earlier

### Low Efficiency (ER < 0.5)
- **Market**: Ranging/choppy
- **KAMA Behavior**: More smoothing (like slow EMA)
- **Trading**: Avoid or use other strategies
- **Signals**: Less frequent, more reliable

### Medium Efficiency (ER ≈ 0.5)
- **Market**: Mixed conditions
- **KAMA Behavior**: Balanced responsiveness
- **Trading**: Moderate trend following
- **Signals**: Balanced frequency and reliability

## Related Functions

- **EMA**: Exponential Moving Average - fixed smoothing
- **MAMA**: MESA Adaptive Moving Average - cycle-based adaptive
- **T3**: T3 Moving Average - smooth with low lag
- **DEMA**: Double Exponential Moving Average - fixed fast response

## References

- **Book**: *Trading Systems and Methods* by Perry Kaufman (ISBN: 978-1118431981)
- [TA-Lib Source Code: ta_KAMA.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_KAMA.c)
- [Investopedia: Kaufman Adaptive Moving Average](https://www.investopedia.com/terms/k/kaufman-adaptive-moving-average.asp)
- [StockCharts: KAMA](https://school.stockcharts.com/doku.php?id=technical_indicators:kaufman_adaptive_moving_average_kama)

## Additional Notes

Perry Kaufman developed KAMA as part of his work on adaptive trading systems. The key insight is that market efficiency (trending vs. ranging) should determine how much smoothing to apply.

### Key Insights

1. **Efficiency Ratio Concept**:
   - Measures how efficiently price moves in one direction
   - High efficiency = strong trend = less smoothing needed
   - Low efficiency = ranging market = more smoothing needed
   - Automatically adapts to market conditions

2. **Adaptive Smoothing**:
   - Fast smoothing in trends (responsive)
   - Slow smoothing in ranges (stable)
   - No manual adjustment required
   - Self-optimizing for current conditions

3. **Best Applications**:
   - Markets with changing volatility
   - Multiple timeframe analysis
   - Trend following systems
   - Volatile instruments

4. **Period Selection**:
   - Shorter periods (10-14): More responsive
   - Longer periods (30-50): More stable
   - Balance based on instrument and timeframe
   - Test different periods for your market

5. **Combination Strategies**:
   - Use KAMA for trend direction
   - Use oscillators for overbought/oversold
   - Use volume for confirmation
   - Use multiple timeframes for context

### Practical Tips

**For Trending Markets**:
- KAMA will be more responsive
- Good for trend following
- Use for entry timing
- Combine with momentum indicators

**For Ranging Markets**:
- KAMA will be more smoothing
- Avoid trend-following strategies
- Use oscillators instead
- Wait for breakout with KAMA expansion

**For Volatile Markets**:
- KAMA adapts to volatility changes
- More responsive during high volatility
- Smoother during low volatility
- Excellent for crypto and commodities

KAMA is particularly valuable for traders who want the benefits of both fast and slow moving averages without having to manually switch between them or constantly adjust parameters. It's one of the most sophisticated moving averages available and works well across different market conditions.