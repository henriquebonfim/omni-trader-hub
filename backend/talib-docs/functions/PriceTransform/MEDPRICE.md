# MEDPRICE - Median Price

## Description

The Median Price is a simple price indicator that calculates the midpoint between the high and low prices for a given period. It represents the center of the price range and is useful for smoothing price action and as input to other technical indicators.

## Category
Price Transform / Math Operators

## Calculation

Median Price is the average of high and low:

### Formula
```
Median Price = (High + Low) / 2
```

## Parameters

None

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`

## Outputs
- Median Price values: `double[]`

## Interpretation

### Purpose
- **Range Midpoint**: Center of the high-low range
- **Simplified Price**: Single value for the bar's range
- **Support/Resistance**: Can act as pivot point
- **Smoothing**: Reduces noise from extreme highs/lows

### Usage
Median Price is commonly used:
1. **As input to indicators**: Instead of close price
2. **Pivot calculations**: Reference point for the bar
3. **Support/Resistance**: Midpoint often significant
4. **Smoothing**: Moving averages of median price

## Usage Example

```c
// C/C++ Example
double high[100], low[100];
double medprice[100];
int outBegIdx, outNBElement;

// Calculate Median Price
TA_RetCode retCode = TA_MEDPRICE(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    medprice              // output: median price values
);
```

## Comparison with Other Price Transforms

| Price Type | Formula | Characteristics |
|------------|---------|-----------------|
| Close | Close | Most common, final price |
| Median | (H+L)/2 | Range midpoint, ignores close |
| Typical | (H+L+C)/3 | Includes close, balanced |
| Weighted Close | (H+L+C+C)/4 | Emphasizes close |

## Advantages

1. **Simple**: Very easy to calculate
2. **Range Focus**: Emphasizes trading range
3. **Smoothing**: Reduces impact of closing anomalies
4. **Neutral**: Not biased by close direction

## Limitations

1. **Ignores Close**: Doesn't consider where price settled
2. **Ignores Volume**: No volume consideration
3. **Simple**: Less comprehensive than typical or weighted prices

## Related Functions

- **TYPPRICE**: Typical Price (H+L+C)/3
- **WCLPRICE**: Weighted Close Price (H+L+C+C)/4
- **AVGPRICE**: Average Price (O+H+L+C)/4
- **MIDPOINT**: MidPoint over period - different concept
- **MIDPRICE**: Midpoint Price over period - uses period parameter

## References

- [TA-Lib Source Code: ta_MEDPRICE.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_MEDPRICE.c)
- [Investopedia: Median Price](https://www.investopedia.com/terms/m/median.asp)

## Additional Notes

Median Price is particularly useful in range-bound markets where the midpoint of each bar's range provides a clearer picture of price equilibrium than the closing price alone. It's often used in indicators that focus on price ranges and volatility rather than directional closes.

