# MULT - Vector Arithmetic Multiplication

The Vector Arithmetic Multiplication (MULT) function performs element-wise multiplication of two input arrays. It's a basic mathematical operation that multiplies corresponding elements from two input vectors and returns the result.

## Function Signature

```c
TA_RetCode TA_MULT(
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
- **inReal0[]**: First input array
- **inReal1[]**: Second input array
- **outBegIdx**: Pointer to the beginning index of the output
- **outNBElement**: Pointer to the number of elements in the output
- **outReal[]**: Output array containing the multiplication results

## Calculation

For each element i in the range [startIdx, endIdx]:

```
outReal[i] = inReal0[i] * inReal1[i]
```

## Usage

MULT is commonly used for:
- **Price Calculations**: Multiplying price by volume for volume-weighted calculations
- **Indicator Combinations**: Combining multiple indicators through multiplication
- **Mathematical Operations**: Basic vector arithmetic operations
- **Custom Indicators**: Building custom technical indicators

## Example

```python
import talib
import numpy as np

# Example data
price = np.array([10.0, 11.0, 12.0, 13.0, 14.0])
volume = np.array([1000, 1100, 1200, 1300, 1400])

# Calculate price * volume
result = talib.MULT(price, volume)
print(result)  # [10000.0, 12100.0, 14400.0, 16900.0, 19600.0]
```

## Characteristics

### Advantages
1. **Simple Operation**: Basic mathematical multiplication
2. **Element-wise**: Operates on corresponding elements
3. **Efficient**: Fast computation
4. **Versatile**: Can be used in various contexts

### Limitations
1. **No Validation**: Doesn't check for division by zero or invalid inputs
2. **Basic Function**: Limited to simple multiplication
3. **No Smoothing**: No built-in smoothing or filtering

## Mathematical Properties

- **Commutative**: `MULT(A, B) = MULT(B, A)`
- **Associative**: `MULT(A, MULT(B, C)) = MULT(MULT(A, B), C)`
- **Distributive**: `MULT(A, ADD(B, C)) = ADD(MULT(A, B), MULT(A, C))`

## Related Functions

- **ADD**: Vector Arithmetic Addition
- **SUB**: Vector Arithmetic Subtraction
- **DIV**: Vector Arithmetic Division
- **MAX**: Maximum value between two arrays
- **MIN**: Minimum value between two arrays

## References

- [TA-Lib Source Code: ta_MULT.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_MULT.c)
- [Mathematical Operations in Technical Analysis](https://en.wikipedia.org/wiki/Technical_analysis)
- [Vector Arithmetic Operations](https://en.wikipedia.org/wiki/Vector_space)

---

*This function is part of the Math Operators group in TA-Lib.*
