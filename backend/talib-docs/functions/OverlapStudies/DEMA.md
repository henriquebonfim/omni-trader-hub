# DEMA - Double Exponential Moving Average

## Description

The Double Exponential Moving Average (DEMA) is a composite indicator developed by Patrick Mulloy that attempts to eliminate the lag inherent in traditional moving averages. Despite its name, DEMA is NOT simply an EMA of an EMA. Instead, it uses a combination of single and double EMAs to create a faster-responding moving average.

## Category
Overlap Studies

## Author
Patrick Mulloy

## Calculation

DEMA uses the difference between a single EMA and a double-smoothed EMA to reduce lag:

### Formula
```
DEMA = 2 × EMA(n) - EMA(EMA(n))
```

Where:
- EMA(n) = Exponential Moving Average of period n
- EMA(EMA(n)) = EMA applied to the first EMA

### Detailed Steps
```
Step 1: Calculate EMA of price
        EMA1 = EMA(Price, period)

Step 2: Calculate EMA of EMA1
        EMA2 = EMA(EMA1, period)

Step 3: Calculate DEMA
        DEMA = (2 × EMA1) - EMA2
```

The subtraction effectively compensates for the lag in the double EMA.

## Parameters

- **optInTimePeriod** (default: 30): Period for the exponential moving averages
  - Valid range: 2 to 100000
  - Common values: 9, 20, 50

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- DEMA values: `double[]`

## Interpretation

### Responsiveness
- **More Responsive than SMA/EMA**: Reacts faster to price changes
- **Less Lag**: Reduced lag compared to traditional moving averages
- **Trend Identification**: Better at tracking price more closely

### Usage
Use like any moving average:
1. **Trend Direction**:
   - Price above DEMA = Uptrend
   - Price below DEMA = Downtrend
   - DEMA slope indicates trend strength

2. **Crossovers**:
   - Price crossing above DEMA = Buy signal
   - Price crossing below DEMA = Sell signal

3. **Support/Resistance**:
   - DEMA acts as dynamic support in uptrends
   - DEMA acts as dynamic resistance in downtrends

4. **Multiple DEMA Systems**:
   - Use two DEMAs (e.g., 9 and 20 period)
   - Faster DEMA crossing slower = trend change signal

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double demaOutput[100];
int outBegIdx, outNBElement;

// Calculate 20-period DEMA
TA_RetCode retCode = TA_DEMA(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    20,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    demaOutput            // output: DEMA values
);
```

## Implementation Details

The TA-Lib DEMA implementation:

1. **First EMA**: Calculates EMA of prices
2. **Second EMA**: Calculates EMA of first EMA
3. **Combination**: Applies DEMA formula: 2×EMA1 - EMA2
4. **Lookback**: Longer than single EMA due to double smoothing

## Lag Reduction Explained

### Why DEMA Has Less Lag

The double application of EMA actually increases lag, but by subtracting it from 2 times the single EMA, the extra lag is removed and then some:

```
Single EMA:     Has lag = L
Double EMA:     Has lag ≈ 2L
DEMA Formula:   2×EMA - EMA(EMA) removes extra lag
Result:         Effective lag < L
```

This clever mathematical trick results in a moving average that hugs price more closely.

## Trading Strategies

### 1. DEMA Crossover Strategy
- **Buy**: Price crosses above DEMA
- **Sell**: Price crosses below DEMA
- **Advantage**: Earlier signals than SMA/EMA
- **Best in**: Trending markets

### 2. Dual DEMA Strategy
- **Setup**: Use two DEMAs (e.g., 9 and 21 period)
- **Buy**: Faster DEMA crosses above slower DEMA
- **Sell**: Faster DEMA crosses below slower DEMA
- **Best in**: Capturing trend changes early

### 3. DEMA + RSI Strategy
- **Trend**: Determined by DEMA
- **Entry**: RSI oversold in uptrend (DEMA rising)
- **Exit**: Price crosses below DEMA or RSI overbought
- **Best in**: Pullback entries in trends

### 4. DEMA Ribbon
- **Setup**: Multiple DEMAs (e.g., 5, 10, 15, 20, 25, 30)
- **Uptrend**: Ribbon expanding, price above all DEMAs
- **Downtrend**: Ribbon expanding, price below all DEMAs
- **Ranging**: Ribbon contracted
- **Best in**: Visual trend assessment

## Advantages

1. **Reduced Lag**: Significantly less lag than SMA or EMA
2. **More Responsive**: Faster reaction to price changes
3. **Smoother than Simple MA**: Better than just reducing period
4. **Trend Following**: Excellent for trend identification
5. **Universal**: Works on all markets and timeframes

## Limitations and Considerations

1. **More Whipsaws**: Increased responsiveness means more false signals
2. **Still Lags**: While reduced, lag isn't eliminated entirely
3. **Choppy Markets**: Can generate excessive signals in ranges
4. **Overshoot**: May overshoot during sharp reversals
5. **Complexity**: More complex than simple moving averages

## DEMA vs. Other Moving Averages

| MA Type | Lag | Responsiveness | Smoothness | Complexity |
|---------|-----|----------------|------------|------------|
| SMA | High | Low | High | Low |
| EMA | Medium | Medium | Medium | Low |
| WMA | Medium | Medium | Medium | Low |
| DEMA | Low | High | Low | Medium |
| TEMA | Very Low | Very High | Very Low | High |

DEMA sits between EMA and TEMA in terms of responsiveness and complexity.

## Related Functions

- **EMA**: Exponential Moving Average - basis for DEMA
- **TEMA**: Triple Exponential Moving Average - even less lag
- **KAMA**: Kaufman Adaptive Moving Average - adaptive approach
- **T3**: T3 Moving Average - smooth with low lag
- **SMA**: Simple Moving Average - baseline comparison

## References

- **Article**: "Smoothing Data with Faster Moving Averages" by Patrick G. Mulloy (Technical Analysis of Stocks & Commodities, January 1994)
- [TA-Lib Source Code: ta_DEMA.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_DEMA.c)
- [Investopedia: Double Exponential Moving Average](https://www.investopedia.com/terms/d/double-exponential-moving-average.asp)
- [Original TA-Doc: DEMA](http://tadoc.org/indicator/DEMA.htm)

## Additional Notes

Patrick Mulloy developed DEMA in the 1990s to address the lag problem inherent in all moving averages. His key insight was that by using the difference between a single and double EMA, he could create a composite indicator that responds faster than either component alone.

### Key Insights

1. **Not Just Smoothing Twice**:
   - DEMA ≠ EMA(EMA(price))
   - DEMA = 2×EMA(price) - EMA(EMA(price))
   - The subtraction is crucial for lag reduction

2. **Mathematical Elegance**:
   - Uses properties of exponential smoothing
   - Cleverly cancels out extra lag
   - Results in faster response without sacrificing too much smoothness

3. **Practical Application**:
   - Best used in trending markets
   - Generates earlier entry signals
   - May need wider stops due to more whipsaws
   - Consider using with volume confirmation

4. **Period Selection**:
   - Shorter periods (9-15): Day trading, very responsive
   - Medium periods (20-30): Swing trading, balanced
   - Longer periods (50-100): Position trading, smoother

5. **Comparison to TEMA**:
   - TEMA takes the concept further (triple smoothing)
   - DEMA offers good balance of speed vs. reliability
   - TEMA faster but more prone to whipsaws
   - Choose based on trading style and market conditions

DEMA is particularly popular among day traders and swing traders who need faster signals than traditional moving averages provide but want more reliability than simply using a shorter-period EMA.

