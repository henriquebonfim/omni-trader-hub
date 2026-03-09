# RSI - Relative Strength Index

## Description

The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and magnitude of price changes. It oscillates between 0 and 100 and is primarily used to identify overbought or oversold conditions in a market.

## Category
Momentum Indicators

## Author
J. Welles Wilder

## Calculation

The RSI is calculated using the following steps:

1. **Calculate Price Changes**: For each period, calculate the difference between consecutive closing prices
2. **Separate Gains and Losses**:
   - Gain = price change if positive, 0 otherwise
   - Loss = absolute value of price change if negative, 0 otherwise

3. **Calculate Average Gain and Average Loss**:
   - Initial Average Gain = Sum of Gains over period / period
   - Initial Average Loss = Sum of Losses over period / period

4. **Smooth the Averages** (Wilder's smoothing method):
   - Average Gain = [(Previous Average Gain) × (period-1) + Current Gain] / period
   - Average Loss = [(Previous Average Loss) × (period-1) + Current Loss] / period

5. **Calculate RS (Relative Strength)**:
   - RS = Average Gain / Average Loss

6. **Calculate RSI**:
   - RSI = 100 - (100 / (1 + RS))
   - Or equivalently: RSI = 100 × (Average Gain / (Average Gain + Average Loss))

### Formula
```
RSI = 100 × (Average Gain / (Average Gain + Average Loss))
```

## Parameters

- **optInTimePeriod** (default: 14): The number of periods used to calculate the RSI
  - Valid range: 2 to 100000
  - Common values: 9, 14, 25

## Inputs
- Price data (typically closing prices): `double[]`

## Outputs
- RSI values: `double[]` (range: 0 to 100)

## Interpretation

### Traditional Levels
- **Overbought**: RSI > 70 (prices may be too high and due for a correction)
- **Oversold**: RSI < 30 (prices may be too low and due for a bounce)
- **Neutral**: RSI around 50

### Trading Signals
1. **Overbought/Oversold**: 
   - Consider selling when RSI crosses above 70
   - Consider buying when RSI crosses below 30

2. **Divergence**:
   - **Bullish Divergence**: Price makes lower lows while RSI makes higher lows (potential reversal up)
   - **Bearish Divergence**: Price makes higher highs while RSI makes lower highs (potential reversal down)

3. **Centerline Crossover**:
   - RSI crossing above 50 may indicate bullish momentum
   - RSI crossing below 50 may indicate bearish momentum

4. **Failure Swings**:
   - Bullish: RSI drops below 30, bounces, pulls back but stays above 30, then breaks above its prior high
   - Bearish: RSI rises above 70, declines, rallies but stays below 70, then breaks below its prior low

### Period Selection
- **Shorter periods** (e.g., 9): More sensitive, generates more signals but more false signals
- **Longer periods** (e.g., 25): Less sensitive, fewer signals but more reliable
- **Standard period** (14): Balanced approach, most widely used

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double rsiOutput[100];
int outBegIdx, outNBElement;

// Calculate RSI with 14-period
TA_RetCode retCode = TA_RSI(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    rsiOutput             // output: RSI values
);
```

## Implementation Details

The TA-Lib implementation follows Wilder's original algorithm with the following characteristics:

1. **Smoothing Method**: Uses Wilder's exponential smoothing (different from standard EMA)
2. **Lookback Period**: Requires `timePeriod` bars before producing the first output
3. **Unstable Period**: Can be configured via `TA_SetUnstablePeriod` for RSI
4. **MetaStock Compatibility**: When compatibility mode is enabled, calculation starts one bar earlier
5. **Division by Zero Handling**: Returns 0 when both average gain and average loss are zero

## Limitations and Considerations

1. **Lagging Indicator**: RSI is based on historical prices and lags current price action
2. **False Signals in Trends**: During strong trends, RSI can remain in overbought or oversold territory for extended periods
3. **Time Frame Sensitivity**: Results vary significantly based on the chosen period
4. **Not a Standalone Indicator**: Should be used in conjunction with other technical analysis tools
5. **Whipsaws**: Can generate false signals during choppy, sideways markets

## Related Functions

- **STOCHRSI**: Stochastic RSI - applies Stochastic oscillator to RSI values
- **CMO**: Chande Momentum Oscillator - similar concept but different calculation
- **MFI**: Money Flow Index - volume-weighted version of RSI

## References

- **Book**: *New Concepts in Technical Trading Systems* by J. Welles Wilder (ISBN: 0894590278)
- [TA-Lib Source Code: ta_RSI.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_RSI.c)
- [Investopedia: RSI](https://www.investopedia.com/terms/r/rsi.asp)
- [StockCharts: RSI](https://school.stockcharts.com/doku.php?id=technical_indicators:relative_strength_index_rsi)
- [Original TA-Doc: RSI](http://tadoc.org/indicator/RSI.htm)

## Additional Notes

The RSI is one of the most popular technical indicators and is included in virtually all charting and technical analysis software. J. Welles Wilder introduced it in his 1978 book and recommended using a 14-day period. The indicator is particularly useful for:

- Identifying potential reversal points
- Confirming trend strength
- Spotting divergences that may precede trend changes
- Timing entry and exit points in range-bound markets

When using RSI, traders often adjust the overbought/oversold levels based on market conditions. In strong uptrends, the overbought level might be raised to 80, while in strong downtrends, the oversold level might be lowered to 20.

