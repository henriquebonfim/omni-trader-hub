# TYPPRICE - Typical Price

## Description

The Typical Price is a simple price indicator that represents the average of the high, low, and closing prices for a given period. It provides a more comprehensive view of price action than using the close alone, as it incorporates the full price range of the period.

## Category
Price Transform / Math Operators

## Calculation

Typical Price is the arithmetic mean of high, low, and close:

### Formula
```
Typical Price = (High + Low + Close) / 3
```

## Parameters

None

## Inputs
- **High** prices: `double[]`
- **Low** prices: `double[]`
- **Close** prices: `double[]`

## Outputs
- Typical Price values: `double[]`

## Interpretation

### Purpose
- **Representative Price**: Single value representing the bar's price action
- **Volume Analysis**: Often used with volume indicators
- **Fair Value**: Approximates the "fair" or "average" price of the period

### Usage
Typical Price is commonly used as input for:
1. **Volume Indicators**: Money Flow Index (MFI), Volume-weighted indicators
2. **Oscillators**: Can be used instead of close in calculations
3. **Moving Averages**: Smoothing typical price instead of close
4. **Accumulation/Distribution**: Component of A/D calculation

## Usage Example

```c
// C/C++ Example
double high[100], low[100], close[100];
double typprice[100];
int outBegIdx, outNBElement;

// Calculate Typical Price
TA_RetCode retCode = TA_TYPPRICE(
    0,                    // start index
    99,                   // end index
    high,                 // high prices
    low,                  // low prices
    close,                // close prices
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    typprice              // output: typical price values
);
```

## Comparison with Other Price Transforms

| Price Type | Formula | Use Case |
|------------|---------|----------|
| Close | Close | Most common, end of period |
| Typical | (H+L+C)/3 | Balanced, volume indicators |
| Median | (H+L)/2 | Range midpoint |
| Weighted Close | (H+L+C+C)/4 | Emphasizes close |
| Average | (O+H+L+C)/4 | Complete OHLC average |

## Advantages

1. **Comprehensive**: Includes full price range
2. **Simple**: Easy to calculate and understand
3. **Balanced**: Equal weight to H, L, C
4. **Standard**: Widely used in indicators

## Limitations

1. **Equal Weighting**: Doesn't emphasize close
2. **No Volume**: Doesn't incorporate volume data
3. **Simple Average**: May not reflect true "typical" price

## Related Functions

- **MEDPRICE**: Median Price (H+L)/2
- **WCLPRICE**: Weighted Close Price (H+L+C+C)/4
- **AVGPRICE**: Average Price (O+H+L+C)/4
- **CCI**: Commodity Channel Index - uses typical price
- **MFI**: Money Flow Index - uses typical price

## References

- [TA-Lib Source Code: ta_TYPPRICE.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_TYPPRICE.c)
- [Investopedia: Typical Price](https://www.investopedia.com/terms/t/typical-price.asp)

## Additional Notes

Typical Price is primarily a building block for other indicators rather than a standalone trading tool. Its main value is in providing a single representative price that captures the high, low, and close of each period, making it useful for volume-weighted calculations and indicators that benefit from considering the full price range rather than just the closing price.

