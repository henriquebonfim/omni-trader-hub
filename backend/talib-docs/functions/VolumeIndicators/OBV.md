# OBV - On Balance Volume

## Description

On Balance Volume (OBV) is a momentum indicator that uses volume flow to predict changes in stock price. It relates volume to price change by adding volume on up days and subtracting volume on down days, creating a cumulative total. OBV is based on the premise that volume precedes price movement.

## Category
Volume Indicators

## Author
Joseph Granville

## Calculation

OBV is calculated using a simple cumulative formula:

```
If Close > Previous Close:
    OBV = Previous OBV + Volume

If Close < Previous Close:
    OBV = Previous OBV - Volume

If Close = Previous Close:
    OBV = Previous OBV
```

The calculation starts with an arbitrary value (often zero or the first day's volume) and builds from there.

### Formula
```
OBV(t) = OBV(t-1) + sign(Close(t) - Close(t-1)) × Volume(t)
```

Where:
- sign = +1 if close is higher, -1 if lower, 0 if unchanged

## Parameters

None - OBV uses only price and volume data

## Inputs
- **Close** prices: `double[]`
- **Volume**: `double[]`

## Outputs
- OBV values: `double[]` (cumulative, unbounded)

## Interpretation

### Basic Principle
- **Volume leads price**: Changes in OBV often precede price changes
- **Rising OBV**: Accumulation, buying pressure
- **Falling OBV**: Distribution, selling pressure

### Trading Signals

1. **Trend Confirmation**:
   - **Bullish**: Price rising + OBV rising (healthy uptrend)
   - **Bearish**: Price falling + OBV falling (healthy downtrend)
   - Both trending together confirms trend strength

2. **Divergence** (Most Important):
   - **Bullish Divergence**:
     * Price makes lower lows
     * OBV makes higher lows
     * Suggests accumulation, potential reversal up
     * More reliable than price alone

   - **Bearish Divergence**:
     * Price makes higher highs
     * OBV makes lower highs
     * Suggests distribution, potential reversal down
     * Warning sign for long positions

3. **Breakouts**:
   - **Confirmed Breakout**: OBV breaks resistance with price
   - **False Breakout**: OBV doesn't confirm price breakout
   - OBV confirmation adds significantly to reliability

4. **OBV Trendlines**:
   - Draw trendlines on OBV just like on price
   - OBV trendline breaks often precede price breaks
   - Can provide early warning signals

## Usage Example

```c
// C/C++ Example
double close[100], volume[100];
double obvOutput[100];
int outBegIdx, outNBElement;

// Calculate OBV
TA_RetCode retCode = TA_OBV(
    0,                    // start index
    99,                   // end index
    close,                // close prices
    volume,               // volume
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    obvOutput             // output: OBV values
);
```

## Implementation Details

The TA-Lib OBV implementation:

1. **Simple Cumulative**: Adds or subtracts volume based on price direction
2. **Initial Value**: Starts from zero or first volume value
3. **Unchanged Prices**: No volume added/subtracted when price unchanged
4. **No Smoothing**: Raw cumulative value, no averaging
5. **Fast Calculation**: Very efficient, O(n) complexity

### Calculation Steps
```
Step 1: Compare today's close to yesterday's close
Step 2: If higher, add today's volume to OBV
        If lower, subtract today's volume from OBV
        If equal, OBV remains unchanged
Step 3: Repeat for all bars
```

## Trading Strategies

### 1. Divergence Strategy
- **Setup**: Identify divergence between price and OBV
- **Entry**: Wait for price confirmation (reversal pattern)
- **Stop**: Beyond recent swing high/low
- **Target**: Previous swing or measured move
- **Best in**: Identifying trend reversals

### 2. Breakout Confirmation
- **Setup**: Price approaching resistance/support
- **Confirmation**: OBV also approaching breakout level
- **Entry**: When both break simultaneously
- **Stop**: Below/above breakout level
- **Target**: Measured move from pattern
- **Best in**: Range breakouts

### 3. Trend Following
- **Trend**: Establish trend with MA or ADX
- **Entry**: Pullbacks when OBV confirms trend
- **Filter**: Only trade when OBV trending with price
- **Exit**: When OBV breaks trend
- **Best in**: Strong trending markets

### 4. Relative Strength
- **Method**: Compare OBV of stock vs. OBV of index
- **Strong Stock**: Stock OBV rising faster than index
- **Weak Stock**: Stock OBV rising slower or falling
- **Use**: For stock selection in long portfolios

## OBV Analysis Techniques

### 1. OBV Moving Averages
Apply moving average to OBV:
```
OBV MA = SMA(OBV, period)
```

Signals:
- **Buy**: OBV crosses above its MA
- **Sell**: OBV crosses below its MA
- Smooth out OBV noise

### 2. OBV Rate of Change
```
OBV ROC = (OBV - OBV n periods ago) / OBV n periods ago × 100
```

- Shows momentum of volume accumulation
- Helps identify acceleration/deceleration

### 3. OBV Oscillator
```
OBV Oscillator = ((OBV - OBV MA) / OBV MA) × 100
```

- Normalized OBV for comparison
- Oscillates around zero
- Easier to identify extremes

### 4. OBV Trendlines
- Draw trendlines on OBV chart
- Breaks often lead price trendline breaks
- Use for early warning system

## Advantages

1. **Simple**: Easy to understand and calculate
2. **Leading Indicator**: Can precede price changes
3. **Volume Integration**: Incorporates important volume data
4. **Trend Confirmation**: Validates price movements
5. **Divergence Detection**: Effective at spotting divergences
6. **Universal**: Works across all markets and timeframes

## Limitations and Considerations

1. **Absolute Values Meaningless**: Only direction and divergences matter
2. **No Normalization**: Can't compare OBV across different stocks
3. **Binary Logic**: All-or-nothing volume assignment (less nuanced than A/D Line)
4. **Gap Handling**: Doesn't distinguish between small and large price changes
5. **No Overbought/Oversold**: No defined extreme levels
6. **Requires Confirmation**: Should not be used as standalone indicator

## OBV vs. A/D Line

| Characteristic | OBV | A/D Line |
|---------------|-----|----------|
| Volume Assignment | Binary (all in/out) | Proportional (based on close location) |
| Complexity | Simpler | More complex |
| Price Sensitivity | Close vs. previous close | Close vs. high/low range |
| Developed By | Joseph Granville | Marc Chaikin |
| Best For | Trend confirmation | Fine-tuned analysis |

Both are useful; many traders use both together.

## Market Application

### Different Market Conditions

**Trending Markets**:
- OBV most effective
- Strong trends show persistent OBV direction
- Divergences more meaningful
- Use for trend confirmation

**Ranging Markets**:
- Less effective
- Can generate false signals
- Better to use oscillators
- Wait for breakout

**Volatile Markets**:
- Watch for divergences
- Can signal turning points
- Combine with price patterns
- Higher false signal rate

**Low Volume Markets**:
- Less reliable
- Volume data less meaningful
- Consider other indicators
- Be cautious with signals

## Volume Patterns

### 1. Steady Accumulation
- **Pattern**: Consistently rising OBV
- **Meaning**: Persistent buying pressure
- **Action**: Look for buy opportunities
- **Caution**: Verify with price confirmation

### 2. Steady Distribution
- **Pattern**: Consistently falling OBV
- **Meaning**: Persistent selling pressure
- **Action**: Avoid buying, consider shorts
- **Caution**: Verify with price confirmation

### 3. OBV Surge
- **Pattern**: Sharp rise in OBV
- **Meaning**: Heavy accumulation
- **Action**: Potential breakout coming
- **Caution**: Could be climax, watch for reversal

### 4. OBV Plunge
- **Pattern**: Sharp fall in OBV
- **Meaning**: Heavy distribution
- **Action**: Potential breakdown coming
- **Caution**: Could be capitulation, watch for bottom

## Related Functions

- **AD**: Accumulation/Distribution Line - more sophisticated volume indicator
- **ADOSC**: Chaikin A/D Oscillator - derivative of A/D Line
- **MFI**: Money Flow Index - combines volume with RSI concept
- **CMF**: Chaikin Money Flow - shorter-term volume indicator

## References

- **Book**: *Granville's New Key to Stock Market Profits* by Joseph Granville
- [TA-Lib Source Code: ta_OBV.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_OBV.c)
- [Investopedia: On Balance Volume](https://www.investopedia.com/terms/o/onbalancevolume.asp)
- [StockCharts: On Balance Volume](https://school.stockcharts.com/doku.php?id=technical_indicators:on_balance_volume_obv)
- [Original TA-Doc: OBV](http://tadoc.org/indicator/OBV.htm)

## Additional Notes

Joseph Granville introduced On Balance Volume in his 1963 book *Granville's New Key to Stock Market Profits*. It was one of the first indicators to relate volume to price changes systematically.

### Key Insights

1. **Granville's Theory**:
   - "Volume precedes price"
   - Smart money accumulates/distributes before public
   - Volume reveals smart money activity
   - OBV captures this flow

2. **Early Warning System**:
   - OBV changes often happen before price changes
   - Divergences can signal days or weeks in advance
   - Not a timing tool but a warning indicator
   - Still need price action for entry timing

3. **Divergence Reliability**:
   - More reliable in trending markets
   - Less reliable in ranging markets
   - Stronger when confirmed by other indicators
   - Best when accompanied by price patterns

4. **Multiple Timeframe Use**:
   - Higher timeframe for overall volume trend
   - Lower timeframe for entry timing
   - Both should align for strongest signals
   - Divergence on higher TF more significant

5. **Sector Analysis**:
   - Compare OBV across sector stocks
   - Identify leadership (strongest OBV)
   - Identify laggards (weakest OBV)
   - Rotate to strongest OBV stocks

### Practical Tips

**For Long Positions**:
- Want to see rising OBV confirming rising price
- Enter on pullbacks when OBV stays strong
- Exit when OBV starts falling

**For Short Positions**:
- Want to see falling OBV confirming falling price
- Enter on rallies when OBV stays weak
- Exit when OBV starts rising

**For Breakouts**:
- Rising OBV before breakout = strong signal
- Falling OBV before breakout = weak signal
- OBV at new highs with price = very bullish
- OBV lagging price = caution

OBV is most effective when used as a confirmation tool rather than a standalone signal generator. Its simplicity is both its strength (easy to understand) and weakness (less nuanced than other volume indicators).

