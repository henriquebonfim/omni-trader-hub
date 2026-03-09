# MFI - Money Flow Index

## Description

The Money Flow Index (MFI) is a momentum oscillator that uses both price and volume to measure the strength of money flowing in and out of a security. It's similar to RSI but incorporates volume, making it a more comprehensive indicator for identifying overbought/oversold conditions and potential trend reversals.

## Category
Volume Indicators

## Author
Gene Quong and Avrum Soudack

## Calculation

MFI is calculated using both price and volume:

### Step 1: Calculate Typical Price
```
TP = (High + Low + Close) / 3
```

### Step 2: Calculate Raw Money Flow
```
RMF = TP × Volume
```

### Step 3: Calculate Positive Money Flow
```
PMF = Sum of RMF when TP > Previous TP
```

### Step 4: Calculate Negative Money Flow
```
NMF = Sum of RMF when TP < Previous TP
```

### Step 5: Calculate Money Flow Ratio
```
MFR = PMF / NMF
```

### Step 6: Calculate MFI
```
MFI = 100 - (100 / (1 + MFR))
```

## Parameters

- **optInTimePeriod** (default: 14): Period for calculation
  - Valid range: 2 to 100000
  - Common values: 14 (standard), 21, 30

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`
- **Volume** data: `double[]`

## Outputs
- MFI values: `double[]` (range: 0 to 100)

## Interpretation

### MFI Values
- **0-20**: Oversold territory
- **20-80**: Neutral territory
- **80-100**: Overbought territory
- **50**: Neutral center line

### Trading Signals

1. **Overbought/Oversold**:
   - **Oversold**: MFI < 20 (potential buy)
   - **Overbought**: MFI > 80 (potential sell)
   - **Neutral**: MFI 20-80 (no clear signal)

2. **Divergence**:
   - **Bullish**: Price lower lows, MFI higher lows
   - **Bearish**: Price higher highs, MFI lower highs
   - **Best in**: Trend exhaustion points

3. **Center Line Crossovers**:
   - **Buy**: MFI crosses above 50
   - **Sell**: MFI crosses below 50
   - **Best in**: Momentum change detection

4. **Volume Analysis**:
   - **High MFI**: Strong buying pressure
   - **Low MFI**: Strong selling pressure
   - **Neutral MFI**: Balanced buying/selling

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100], volume[100];
double mfiOutput[100];
int outBegIdx, outNBElement;

// Calculate 14-period MFI
TA_RetCode retCode = TA_MFI(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    volume,               // volume data
    14,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    mfiOutput             // output: MFI values
);
```

## Implementation Details

The TA-Lib MFI implementation:

1. **Typical Price**: Calculates typical price for each bar
2. **Money Flow**: Calculates raw money flow
3. **Positive/Negative Flow**: Separates positive and negative flows
4. **Money Flow Ratio**: Calculates ratio of flows
5. **MFI**: Applies RSI formula to money flows
6. **Lookback**: Requires n periods for first output

## Trading Strategies

### 1. Overbought/Oversold Strategy
- **Buy**: MFI < 20, then crosses above 20
- **Sell**: MFI > 80, then crosses below 80
- **Confirmation**: Wait for price confirmation
- **Best in**: Range-bound markets

### 2. Divergence Strategy
- **Setup**: Identify divergence between price and MFI
- **Confirmation**: Wait for price pattern
- **Entry**: On confirmation
- **Best in**: Trend exhaustion points

### 3. Center Line Strategy
- **Buy**: MFI crosses above 50
- **Sell**: MFI crosses below 50
- **Filter**: Only trade when |MFI - 50| > 10
- **Best in**: Momentum change detection

### 4. MFI + Volume Strategy
- **Setup**: Use MFI for volume analysis
- **Entry**: Price direction with MFI confirmation
- **Exit**: MFI reversal or price change
- **Best in**: Volume-confirmed trading

## MFI vs. RSI

| Aspect | MFI | RSI |
|--------|-----|-----|
| Volume | Includes volume | No volume |
| Signals | More reliable | Less reliable |
| Calculation | More complex | Simpler |
| Best For | Volume analysis | Price analysis |
| Accuracy | Higher | Lower |

## Advantages

1. **Volume-Based**: Incorporates volume information
2. **More Reliable**: More accurate than RSI
3. **Universal**: Works across all markets
4. **Clear**: Easy to interpret
5. **Comprehensive**: Combines price and volume

## Limitations

1. **Complex**: More complex than RSI
2. **Volume Dependent**: Requires volume data
3. **Still Lags**: Based on historical data
4. **Whipsaws**: Possible in choppy markets
5. **Period Sensitivity**: Results vary with period

## Period Selection

### Short Periods (9-14)
- **Characteristics**: More responsive
- **Use**: Short-term trading
- **Trade-off**: More signals, more noise
- **Best for**: Active trading

### Standard Periods (14-21)
- **Characteristics**: Balanced approach
- **Use**: General analysis
- **Trade-off**: Good balance
- **Best for**: Most applications

### Long Periods (21-30)
- **Characteristics**: Smoother, less responsive
- **Use**: Long-term analysis
- **Trade-off**: Fewer signals, more reliable
- **Best for**: Position trading

## Related Functions

- **RSI**: Relative Strength Index - similar concept
- **OBV**: On Balance Volume - volume-based
- **AD**: Accumulation/Distribution Line - volume-based
- **VWMA**: Volume Weighted Moving Average - volume-based

## References

- **Book**: *Technical Analysis of Stock Trends* by Gene Quong and Avrum Soudack
- [TA-Lib Source Code: ta_MFI.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_MFI.c)
- [Investopedia: Money Flow Index](https://www.investopedia.com/terms/m/mfi.asp)
- [StockCharts: MFI](https://school.stockcharts.com/doku.php?id=technical_indicators:money_flow_index_mfi)

## Additional Notes

Gene Quong and Avrum Soudack developed MFI as an improvement over RSI, incorporating volume to provide more accurate overbought/oversold signals. The key insight is that volume confirms price movements and provides more reliable signals.

### Key Insights

1. **Volume Confirmation**:
   - Volume confirms price movements
   - High volume = stronger signals
   - Low volume = weaker signals
   - Volume divergence = potential reversal

2. **Money Flow Analysis**:
   - Positive money flow = buying pressure
   - Negative money flow = selling pressure
   - Money flow ratio = strength of flows
   - MFI = normalized money flow

3. **Best Applications**:
   - Volume-confirmed trading
   - Overbought/oversold analysis
   - Trend reversal detection
   - Money flow analysis

4. **Signal Interpretation**:
   - < 20 = oversold
   - > 80 = overbought
   - 20-80 = neutral
   - 50 = center line

5. **Combination Strategies**:
   - Use with price indicators
   - Combine with trend analysis
   - Use for volume confirmation
   - Multiple timeframe analysis

### Practical Tips

**For Volume Confirmation**:
- Use MFI to confirm price signals
- High MFI = strong buying pressure
- Low MFI = strong selling pressure
- Wait for MFI confirmation

**For Overbought/Oversold**:
- Use 20/80 levels as thresholds
- Wait for confirmation from price
- Use volume for validation
- Avoid in strong trends

**For Divergence Trading**:
- Identify price vs. MFI divergence
- Confirm with price action
- Use volume for validation
- Set stops beyond extremes

**For Risk Management**:
- Use MFI for position sizing
- Reduce size during extreme readings
- Use for stop placement
- Monitor MFI trends

MFI is particularly valuable for traders who want to incorporate volume analysis into their overbought/oversold assessment. It's excellent for volume-confirmed trading and provides more reliable signals than RSI.

