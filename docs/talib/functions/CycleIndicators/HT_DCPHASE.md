# HT_DCPHASE - Hilbert Transform - Dominant Cycle Phase

## Description

The Hilbert Transform Dominant Cycle Phase (HT_DCPHASE) is a cycle indicator that uses the Hilbert Transform to identify the current phase of the dominant cycle in price data. It's part of the MESA (MESA Adaptive Moving Average) suite of indicators developed by John Ehlers. The indicator helps identify where the market is in its current cycle, which can be used for cycle-based trading strategies and timing entries and exits.

## Category
Cycle Indicators

## Author
John Ehlers

## Calculation

HT_DCPHASE uses the Hilbert Transform to identify the current phase of the dominant cycle:

### Step 1: Hilbert Transform
```
Hilbert Transform = arctan(Imaginary / Real)
```

Where:
- Real and Imaginary are derived from price data using Hilbert Transform
- The transform identifies cyclical components

### Step 2: Phase Calculation
```
Phase = Hilbert Transform (in radians)
```

Where:
- Phase is the current position in the cycle
- 0 to 2π represents a full cycle
- 0 = cycle bottom, π = cycle top

### Step 3: Phase Interpretation
- **0 to π/2**: Rising phase (bottom to top)
- **π/2 to π**: Peak phase (top)
- **π to 3π/2**: Falling phase (top to bottom)
- **3π/2 to 2π**: Trough phase (bottom)

## Parameters

None - HT_DCPHASE is a cycle detection function

## Inputs
- Price data: `double[]` (typically closing prices)

## Outputs
- Cycle phase values: `double[]` (phase in radians, 0 to 2π)

## Interpretation

### Phase Values
- **0**: Cycle bottom (trough)
- **π/2**: Rising phase (quarter cycle)
- **π**: Cycle top (peak)
- **3π/2**: Falling phase (three-quarter cycle)
- **2π**: Cycle bottom (trough, next cycle)

### Trading Applications

1. **Cycle Timing**:
   - **0 to π/2**: Early uptrend phase
   - **π/2 to π**: Late uptrend phase
   - **π to 3π/2**: Early downtrend phase
   - **3π/2 to 2π**: Late downtrend phase

2. **Entry/Exit Signals**:
   - **Buy**: Near phase 0 (cycle bottom)
   - **Sell**: Near phase π (cycle top)
   - **Hold**: During rising/falling phases
   - **Exit**: At opposite phase

3. **Trend Analysis**:
   - **Rising Phase**: Uptrend in cycle
   - **Falling Phase**: Downtrend in cycle
   - **Peak Phase**: Cycle top
   - **Trough Phase**: Cycle bottom

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double cyclePhase[100];
int outBegIdx, outNBElement;

// Calculate dominant cycle phase
TA_RetCode retCode = TA_HT_DCPHASE(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    cyclePhase            // output: cycle phases
);
```

## Implementation Details

The TA-Lib HT_DCPHASE implementation:

1. **Hilbert Transform**: Applies Hilbert Transform to price data
2. **Phase Calculation**: Calculates current cycle phase
3. **Smoothing**: Smooths raw phase values
4. **Lookback**: Requires significant lookback for accurate calculation

## Trading Strategies

### 1. Cycle Phase Strategy
- **Setup**: Identify cycle phase
- **Entry**: Near phase 0 (bottom)
- **Exit**: Near phase π (top)
- **Best in**: Strong cyclical markets

### 2. Phase + Trend Strategy
- **Setup**: Use phase for timing
- **Entry**: Trend direction with phase timing
- **Exit**: Phase-based or trend-based
- **Best in**: Trending cyclical markets

### 3. Phase + Volume Strategy
- **Setup**: Use phase for timing
- **Entry**: Volume confirmation at phase
- **Exit**: Volume confirmation at opposite phase
- **Best in**: High conviction setups

### 4. Multiple Phase Strategy
- **Setup**: Identify multiple cycle phases
- **Entry**: When phases align
- **Exit**: When phases diverge
- **Best in**: Complex cyclical markets

## Phase Analysis

### 1. Trough Phase (0 to π/2)
- **Characteristics**: Cycle bottom, early uptrend
- **Trading**: Buy opportunities
- **Risk**: Early in cycle, some risk
- **Best in**: Cycle bottoms

### 2. Rising Phase (π/2 to π)
- **Characteristics**: Mid-cycle, strong uptrend
- **Trading**: Hold positions
- **Risk**: Mid-cycle, moderate risk
- **Best in**: Cycle uptrends

### 3. Peak Phase (π to 3π/2)
- **Characteristics**: Cycle top, early downtrend
- **Trading**: Sell opportunities
- **Risk**: Cycle top, high risk
- **Best in**: Cycle tops

### 4. Falling Phase (3π/2 to 2π)
- **Characteristics**: Mid-cycle, strong downtrend
- **Trading**: Hold short positions
- **Risk**: Mid-cycle, moderate risk
- **Best in**: Cycle downtrends

## Advantages

1. **Precise Timing**: Exact cycle phase identification
2. **Objective**: Mathematical phase calculation
3. **Universal**: Works across all markets
4. **Sophisticated**: Advanced cycle analysis
5. **MESA Integration**: Works with other MESA indicators

## Limitations

1. **Complex**: Requires understanding of cycles
2. **Lagging**: Based on historical data
3. **Noisy**: Raw phase can be noisy
4. **Context Dependent**: Needs market context
5. **Learning Curve**: Requires experience to use effectively

## Related Functions

- **HT_DCPERIOD**: Hilbert Transform - Dominant Cycle Period
- **HT_PHASOR**: Hilbert Transform - Phasor Components
- **HT_SINE**: Hilbert Transform - Sine Wave
- **MAMA**: MESA Adaptive Moving Average - uses cycle information

## References

- **Book**: *Rocket Science for Traders* by John Ehlers
- [TA-Lib Source Code: ta_HT_DCPHASE.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_HT_DCPHASE.c)
- [Investopedia: Hilbert Transform](https://www.investopedia.com/terms/h/hilbert-transform.asp)
- [MESA Software](http://www.mesasoftware.com/)

## Additional Notes

John Ehlers developed the Hilbert Transform cycle indicators as part of his work on adaptive trading systems. The key insight is that markets have cyclical components that can be identified and used for precise timing of entries and exits.

### Key Insights

1. **Cycle Phase Identification**:
   - Markets have cyclical components
   - Cycle phase can be identified mathematically
   - Phase indicates position in cycle
   - Adaptive systems can use phase information

2. **Precise Timing**:
   - Use phase for entry timing
   - Enter at cycle bottoms (phase 0)
   - Exit at cycle tops (phase π)
   - Hold during rising/falling phases

3. **Best Applications**:
   - Cyclical markets
   - Cycle-based trading
   - Precise entry/exit timing
   - Market phase identification

4. **Phase Analysis**:
   - Trough phase = buy opportunities
   - Rising phase = hold positions
   - Peak phase = sell opportunities
   - Falling phase = hold short positions

5. **Combination Strategies**:
   - Use with trend indicators
   - Combine with volume analysis
   - Use for cycle-based entries
   - Multiple timeframe confirmation

### Practical Tips

**For Cycle-Based Trading**:
- Identify current cycle phase
- Enter at cycle bottoms (phase 0)
- Exit at cycle tops (phase π)
- Hold during rising/falling phases

**For Precise Timing**:
- Use phase for entry timing
- Combine with price action
- Use volume for confirmation
- Set stops based on cycle

**For Market Analysis**:
- Trough phase = early uptrend
- Rising phase = strong uptrend
- Peak phase = early downtrend
- Falling phase = strong downtrend

**For Risk Management**:
- Cycle phase affects position sizing
- Trough phase = larger positions
- Peak phase = smaller positions
- Use phase for stop placement

HT_DCPHASE is particularly valuable for traders who want to understand the cyclical nature of markets and use this information for precise timing of entries and exits. It's an advanced tool that requires understanding of cycle analysis but can provide significant advantages in cyclical markets.

