# ATR - Average True Range

## Description

The Average True Range (ATR) is a volatility indicator that measures the degree of price volatility by calculating the average of true ranges over a specified period. Unlike many indicators, ATR does not provide an indication of price direction or trend; instead, it measures the market's volatility level.

## Category
Volatility Indicators

## Author
J. Welles Wilder

## Calculation

The ATR is calculated in three steps:

### Step 1: Calculate True Range (TR)
True Range is the greatest of:
1. Current High - Current Low
2. |Current High - Previous Close|
3. |Current Low - Previous Close|

```
TR = max[(H - L), |H - Cp|, |L - Cp|]
```

Where:
- H = Current High
- L = Current Low
- Cp = Previous Close
- | | = Absolute value

### Step 2: Calculate Initial ATR
```
Initial ATR = Average of first n True Ranges
```

### Step 3: Calculate Subsequent ATR (Wilder's Smoothing)
```
ATR = ((Previous ATR × (n-1)) + Current TR) / n
```

This is Wilder's smoothing method (similar to exponential moving average but different).

## Parameters

- **optInTimePeriod** (default: 14): The number of periods for ATR calculation
  - Valid range: 1 to 100000
  - Common values: 7, 14, 21

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- ATR values: `double[]` (in same units as price)

## Interpretation

### Volatility Assessment
- **High ATR**: High volatility, large price swings
- **Low ATR**: Low volatility, small price swings
- **Rising ATR**: Increasing volatility
- **Falling ATR**: Decreasing volatility

### Key Concepts

1. **Absolute Measure**: ATR is expressed in price units, not percentages
   - $50 stock with ATR of $3 = 6% volatility
   - $100 stock with ATR of $3 = 3% volatility
   - Cannot directly compare ATR values across different priced securities

2. **Non-Directional**: ATR doesn't indicate trend direction
   - High ATR in uptrend = strong buying
   - High ATR in downtrend = strong selling
   - Low ATR = consolidation or weak trend

3. **Market Character**:
   - Trending markets usually have higher ATR
   - Ranging markets usually have lower ATR
   - Breakouts often accompanied by rising ATR

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double atrOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period ATR
TA_RetCode retCode = TA_ATR(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    atrOutput             // output: ATR values
);
```

## Implementation Details

The TA-Lib ATR implementation:

1. **True Range Calculation**: Handles first bar specially (no previous close)
2. **Initial Average**: Uses simple average for first ATR value
3. **Wilder's Smoothing**: Applies exponential-like smoothing for subsequent values
4. **Gap Handling**: True Range captures gaps between sessions
5. **Lookback Period**: Requires `timePeriod` bars before first output

### Calculation Steps
```
Step 1: For each bar, calculate TR = max(H-L, |H-Cp|, |L-Cp|)
Step 2: Initial ATR = Average of first n TRs
Step 3: Subsequent ATR = ((Prev ATR × (n-1)) + Current TR) / n
```

## Trading Applications

### 1. Stop Loss Placement
Most common use of ATR:

```
Stop Distance = ATR × Multiplier

For Long Positions:
Stop Loss = Entry Price - (ATR × 2)

For Short Positions:
Stop Loss = Entry Price + (ATR × 2)
```

Common multipliers: 1.5, 2, 2.5, 3

**Advantages**:
- Adapts to market volatility
- Wider stops in volatile markets (avoid premature stops)
- Tighter stops in quiet markets (preserve capital)

### 2. Position Sizing
Use ATR for risk-based position sizing:

```
Position Size = (Account Risk $) / (ATR × Multiplier)
```

Example:
- Account: $100,000
- Risk per trade: 1% = $1,000
- ATR: $2.50
- Multiplier: 2

Position Size = $1,000 / ($2.50 × 2) = 200 shares

### 3. Profit Targets
Set profit targets based on ATR:

```
Target = Entry + (ATR × Multiple)
```

Common multiples: 2, 3, 4 (aim for 2:1 or 3:1 reward:risk)

### 4. Breakout Validation
Confirm breakouts with ATR:

- **Valid Breakout**: ATR expands above recent average
- **False Breakout**: ATR remains low
- Rising ATR confirms genuine move

### 5. Chandelier Exit
Trailing stop based on ATR:

```
Long Chandelier Exit = Highest High - (ATR × Multiplier)
Short Chandelier Exit = Lowest Low + (ATR × Multiplier)
```

Follows price while giving room for normal volatility.

## Volatility Analysis

### ATR Patterns

1. **Volatility Contraction**:
   - ATR falling to multi-period lows
   - Indicates consolidation
   - Often precedes significant move
   - Direction unknown until breakout

2. **Volatility Expansion**:
   - ATR rising sharply
   - Indicates strong move in progress
   - Confirms breakouts and trends
   - Momentum building

3. **Volatility Cycles**:
   - Markets alternate between high and low volatility
   - After expansion comes contraction
   - After contraction comes expansion
   - Use for timing and expectation setting

### Historical ATR Analysis

Compare current ATR to historical levels:

```
ATR Percentile = Current ATR rank over past X periods
```

- **High Percentile (>80%)**: Extremely high volatility
- **Low Percentile (<20%)**: Extremely low volatility
- Use for context and mean reversion expectations

## Period Selection

### Different Periods
- **7-period**: Short-term, more responsive, for day traders
- **14-period**: Standard, recommended by Wilder, most common
- **21-period**: Longer-term, smoother, for position traders
- **50-period**: Very long-term, shows major volatility changes

### Timeframe Considerations
- **Intraday**: Shorter periods (7-10)
- **Daily**: Standard period (14)
- **Weekly**: Can use standard or slightly longer (14-21)

## Advantages

1. **Objective**: Clear, quantifiable volatility measure
2. **Adaptive**: Automatically adjusts to market conditions
3. **Universal**: Works across all markets and timeframes
4. **Risk Management**: Excellent for stops and position sizing
5. **Simple**: Easy to understand and calculate
6. **Practical**: Direct application to trading decisions

## Limitations and Considerations

1. **Non-Directional**: Doesn't indicate trend direction
2. **Absolute Values**: Can't compare across different priced securities
3. **Lagging**: Like all averages, lags current volatility
4. **No Price Levels**: Doesn't indicate support/resistance
5. **Smoothing**: Wilder's smoothing can delay response to volatility changes
6. **Period Sensitivity**: Different periods give different readings

## Related Functions

- **NATR**: Normalized Average True Range - percentage version of ATR
- **TRANGE**: True Range - single period, not averaged
- **STDDEV**: Standard Deviation - another volatility measure
- **BBANDS**: Bollinger Bands - uses standard deviation
- **KELTNER**: Keltner Channels - uses ATR for band width

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder (ISBN: 0894590278)
- [TA-Lib Source Code: ta_ATR.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_ATR.c)
- [Investopedia: Average True Range](https://www.investopedia.com/terms/a/atr.asp)
- [StockCharts: Average True Range](https://school.stockcharts.com/doku.php?id=technical_indicators:average_true_range_atr)
- [Original TA-Doc: ATR](http://tadoc.org/indicator/ATR.htm)

## Additional Notes

J. Welles Wilder introduced the Average True Range in his 1978 book *New Concepts in Technical Trading Systems*. It was originally developed for commodities trading but has proven effective across all markets.

### Key Insights

1. **True Range Innovation**: Wilder's True Range captures:
   - Normal within-day volatility (H - L)
   - Gap-up volatility (H - Cp)
   - Gap-down volatility (Cp - L)
   - Most comprehensive single-period volatility measure

2. **Wilder's Smoothing**: Different from SMA or EMA:
   - More weight to historical values
   - Smoother than equivalent-period EMA
   - Less prone to erratic moves
   - Better for trend-following applications

3. **Risk Management Gold Standard**:
   - Professional traders widely use ATR for:
     * Stop loss placement
     * Position sizing
     * Risk assessment
     * Portfolio volatility management

4. **Market Comparison**:
   - For comparing volatility across securities:
   - Use NATR (Normalized ATR)
   - Or calculate: ATR / Price × 100

5. **Volatility vs. Price Direction**:
   - High ATR can occur in any trend:
     * Strong uptrend = high ATR
     * Strong downtrend = high ATR
     * Volatile ranging = high ATR
   - Use with trend indicators for context

6. **Chandelier Exit**:
   - One of the most effective ATR-based systems
   - Created by Chuck LeBeau
   - Trailing stop at: Highest High - (3 × ATR)
   - Gives enough room while protecting profits

### Practical Tips

- **Multiple ATR Strategy**: Use 2× ATR for stop loss, 4× ATR for target
- **Volatility Filter**: Only trade when ATR is above average (high probability setups)
- **Entry Timing**: Wait for ATR expansion after contraction before entering
- **Avoid Low Volatility**: When ATR is at multi-month lows, reduce position size or wait

ATR is one of the most practical and widely used indicators in professional trading, primarily because it directly translates to risk management and position sizing decisions rather than just providing signals.

