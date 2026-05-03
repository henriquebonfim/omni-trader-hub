# SUB - Vector Arithmetic Subtraction

The Vector Arithmetic Subtraction (SUB) function performs element-wise subtraction of two input arrays. It's a basic mathematical operation that subtracts corresponding elements from two input vectors and returns the result.

## Function Signature

```c
TA_RetCode TA_SUB(
    int    startIdx,
    int    endIdx,
    const double inReal0[],
    const double inReal1[],
    int          *outBegIdx,
    int          *outNBElement,
    double       outReal[]
);
```

## Parameters

- **startIdx**: Starting index for the calculation
- **endIdx**: Ending index for the calculation
- **inReal0[]**: First input array (minuend)
- **inReal1[]**: Second input array (subtrahend)
- **outBegIdx**: Pointer to the beginning index of the output
- **outNBElement**: Pointer to the number of elements in the output
- **outReal[]**: Output array containing the subtraction results

## Calculation

For each element i in the range [startIdx, endIdx]:

```
outReal[i] = inReal0[i] - inReal1[i]
```

## Usage

SUB is commonly used for:
- **Price Differences**: Calculating price changes or spreads
- **Indicator Differences**: Finding differences between indicators
- **Mathematical Operations**: Basic vector arithmetic operations
- **Custom Indicators**: Building custom technical indicators
- **Rate of Change**: Calculating percentage changes

## Example

```python
import talib
import numpy as np

# Example data
current_price = np.array([10.0, 11.0, 12.0, 13.0, 14.0])
previous_price = np.array([9.5, 10.5, 11.5, 12.5, 13.5])

# Calculate price difference
result = talib.SUB(current_price, previous_price)
print(result)  # [0.5, 0.5, 0.5, 0.5, 0.5]
```

## Characteristics

### Advantages
1. **Simple Operation**: Basic mathematical subtraction
2. **Element-wise**: Operates on corresponding elements
3. **Efficient**: Fast computation
4. **Versatile**: Can be used in various contexts
5. **Directional**: Shows direction of change

### Limitations
1. **No Validation**: Doesn't check for invalid inputs
2. **Basic Function**: Limited to simple subtraction
3. **No Smoothing**: No built-in smoothing or filtering
4. **No Normalization**: Results depend on input scales

## Mathematical Properties

- **Non-commutative**: `SUB(A, B) ≠ SUB(B, A)`
- **Non-associative**: `SUB(A, SUB(B, C)) ≠ SUB(SUB(A, B), C)`
- **Identity Element**: `SUB(A, 0) = A`
- **Inverse**: `SUB(A, A) = 0`

## Common Applications

### Price Analysis
- **Price Changes**: Current price - previous price
- **Spread Analysis**: Bid price - ask price
- **Gap Analysis**: Open price - previous close

### Technical Indicators
- **MACD**: EMA(12) - EMA(26)
- **Price Oscillators**: Price - moving average
- **Volume Analysis**: Current volume - average volume

## Related Functions

- **ADD**: Vector Arithmetic Addition
- **MULT**: Vector Arithmetic Multiplication
- **DIV**: Vector Arithmetic Division
- **MAX**: Maximum value between two arrays
- **MIN**: Minimum value between two arrays
- **ROC**: Rate of Change (percentage)

## References

- [TA-Lib Source Code: ta_SUB.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_SUB.c)
- [Mathematical Operations in Technical Analysis](https://en.wikipedia.org/wiki/Technical_analysis)
- [Vector Arithmetic Operations](https://en.wikipedia.org/wiki/Vector_space)

---

*This function is part of the Math Operators group in TA-Lib.*
