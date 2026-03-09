# MIN - Lowest Value Over Period

## Description

The MIN function returns the lowest value over a specified period. It's a simple but useful indicator that identifies the lowest price (or any value) within a rolling window, making it valuable for identifying recent lows, support levels, and trend analysis.

## Category
Math Operators / Statistical Functions

## Calculation

MIN finds the lowest value in a rolling window:

### Formula
```
MIN = min(Price[i], Price[i-1], ..., Price[i-n+1])
```

Where:
- n = lookback period
- min() = mathematical minimum function

### Example
For a 5-period MIN with prices [10, 12, 11, 13, 9]:
```
MIN = min(10, 12, 11, 13, 9) = 9
```

## Parameters

- **optInTimePeriod** (default: 30): Number of periods to look back
  - Valid range: 2 to 100000
  - Common values: 10, 20, 50

## Inputs
- Price data: `double[]` (typically low prices)

## Outputs
- MIN values: `double[]` (lowest values over period)

## Interpretation

### Usage
1. **Support Levels**: MIN shows recent support
2. **Trend Analysis**: Rising MIN = uptrend, falling MIN = downtrend
3. **Breakdown Confirmation**: Price breaking below MIN
4. **Resistance Levels**: Previous MIN can become resistance

### Trading Applications

1. **Support Identification**:
   - MIN shows recent low points
   - Price approaching MIN = potential support
   - Price breaking below MIN = breakdown signal

2. **Trend Following**:
   - Rising MIN = uptrend continuing
   - Falling MIN = downtrend continuing
   - MIN slope indicates trend strength

3. **Breakdown Trading**:
   - Price below MIN = bearish
   - Price above MIN = bullish
   - MIN breakdowns = strong signals

## Usage Example

```c
// C/C++ Example
double lowPrices[100];
double minOutput[100];
int outBegIdx, outNBElement;

// Calculate 20-period MIN
TA_RetCode retCode = TA_MIN(
    0,                    // start index
    99,                   // end index
    lowPrices,            // input price data
    20,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    minOutput             // output: MIN values
);
```

## Implementation Details

The TA-Lib MIN implementation:

1. **Rolling Window**: Maintains window of n values
2. **Minimum Search**: Finds lowest value in window
3. **Efficient Update**: Updates efficiently for each new bar
4. **Lookback**: Requires n-1 periods for first output

## Trading Strategies

### 1. Support Strategy
- **Setup**: Identify MIN as support
- **Entry**: Wait for price to approach MIN
- **Signal**: Price bounce at MIN
- **Best in**: Range-bound markets

### 2. Breakdown Strategy
- **Setup**: Price consolidating above MIN
- **Entry**: Price breaks below MIN
- **Confirmation**: Volume increase
- **Best in**: Trending markets

### 3. Trend Following Strategy
- **Uptrend**: Price consistently above MIN
- **Downtrend**: Price consistently below MIN
- **Exit**: Price rises above MIN (downtrend)
- **Best in**: Strong trends

### 4. MIN + MAX Strategy
- **Range**: Use MIN and MAX together
- **Entry**: Buy near MIN, sell near MAX
- **Exit**: Opposite extreme
- **Best in**: Ranging markets

## Advantages

1. **Simple**: Easy to understand and calculate
2. **Objective**: Clear, unambiguous values
3. **Versatile**: Works on any price data
4. **Fast**: Very efficient calculation
5. **Universal**: Works across all markets

## Limitations

1. **Lagging**: Based on historical data
2. **No Prediction**: Doesn't predict future lows
3. **Period Dependent**: Results vary with period
4. **Whipsaws**: Can generate false signals
5. **No Direction**: Doesn't indicate trend direction

## Related Functions

- **MAX**: Highest value over period
- **MINMAX**: Both highest and lowest values
- **MININDEX**: Index of lowest value
- **MINMAXINDEX**: Indexes of highest and lowest

## References

- [TA-Lib Source Code: ta_MIN.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_MIN.c)
- [Investopedia: Technical Analysis](https://www.investopedia.com/terms/t/technicalanalysis.asp)

## Additional Notes

MIN is a fundamental building block for many technical analysis concepts. It's used in:

- **Donchian Channels**: MIN and MAX together
- **Parabolic SAR**: Uses MIN for stop calculation
- **Support Levels**: Recent lows
- **Trend Analysis**: Rising/falling lows
- **Breakdown Confirmation**: Price vs. recent low

### Key Insights

1. **Support Concept**:
   - MIN shows recent support levels
   - Price approaching MIN = potential support
   - Price breaking MIN = breakdown signal
   - Previous MIN can become resistance

2. **Trend Analysis**:
   - Rising MIN = uptrend
   - Falling MIN = downtrend
   - MIN slope = trend strength
   - MIN divergence = trend weakness

3. **Breakdown Trading**:
   - Price below MIN = bearish
   - Price above MIN = bullish
   - MIN breakdowns = strong signals
   - Use volume for confirmation

4. **Period Selection**:
   - Shorter periods = more responsive
   - Longer periods = more stable
   - Balance based on trading style
   - Test different periods

5. **Combination Strategies**:
   - Use MIN with MAX for ranges
   - Combine with trend indicators
   - Use volume for confirmation
   - Multiple timeframes for context

### Practical Tips

**For Support Trading**:
- Identify MIN as support
- Wait for price approach
- Look for bounce signals
- Set stops below MIN

**For Breakdown Trading**:
- Wait for price consolidation above MIN
- Enter on breakdown below MIN
- Use volume for confirmation
- Set stops above MIN

**For Trend Analysis**:
- Rising MIN = uptrend
- Falling MIN = downtrend
- MIN slope = trend strength
- Watch for MIN divergence

**For Range Trading**:
- Use MIN and MAX together
- Buy near MIN, sell near MAX
- Exit at opposite extreme
- Avoid in trending markets

MIN is particularly valuable for identifying support levels and confirming breakdowns. It's a simple but essential tool for technical analysis.

