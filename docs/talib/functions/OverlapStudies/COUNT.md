# COUNT - Count of Values Over Period

## Description

The COUNT function counts the number of non-zero values over a specified period. It's a simple but useful mathematical operator that can be used for various calculations, including counting valid data points, identifying data quality, and as a building block for more complex indicators. COUNT is often used in combination with other functions to create custom indicators.

## Category
Math Operators

## Calculation

COUNT counts the number of non-zero values over a rolling window:

### Formula
```
COUNT = Σ(1 if value ≠ 0, 0 if value = 0)
```

Where:
- Σ = summation over the period
- 1 = count if value is non-zero
- 0 = don't count if value is zero

### Example
For a 5-period COUNT with values [10, 0, 12, 0, 9]:
```
COUNT = 1 + 0 + 1 + 0 + 1 = 3
```

## Parameters

- **optInTimePeriod** (default: 30): Number of periods to count
  - Valid range: 2 to 100000
  - Common values: 10, 20, 50

## Inputs
- Price data: `double[]` (any data)

## Outputs
- COUNT values: `double[]` (count over period)

## Interpretation

### Usage
1. **Data Quality**: Count of valid data points
2. **Custom Indicators**: Building block for other indicators
3. **Data Analysis**: Analyze data completeness
4. **Quality Control**: Monitor data quality

### Trading Applications

1. **Data Quality Analysis**:
   - **High COUNT**: Good data quality
   - **Low COUNT**: Poor data quality
   - **COUNT Trends**: Data quality trends
   - **Best in**: Data validation

2. **Custom Indicators**:
   - **Building Block**: For other indicators
   - **Custom Calculations**: User-defined indicators
   - **Combination**: With other functions
   - **Best in**: Custom analysis

3. **Data Analysis**:
   - **Data Completeness**: Measure data completeness
   - **Data Patterns**: Identify data patterns
   - **Data Trends**: Track data trends
   - **Best in**: Data analysis

## Usage Example

```c
// C/C++ Example
double closePrices[100];
double countOutput[100];
int outBegIdx, outNBElement;

// Calculate 20-period COUNT
TA_RetCode retCode = TA_COUNT(
    0,                    // start index
    99,                   // end index
    closePrices,          // input price data
    20,                   // time period
    &outBegIdx,           // output: beginning index
    &outNBElement,        // output: number of elements
    countOutput           // output: COUNT values
);
```

## Implementation Details

The TA-Lib COUNT implementation:

1. **Rolling Window**: Maintains window of n values
2. **Counting**: Counts non-zero values in window
3. **Efficient Update**: Updates efficiently for each new bar
4. **Lookback**: Requires n-1 periods for first output

## Trading Strategies

### 1. Data Quality Strategy
- **Setup**: Track COUNT over time
- **Entry**: When COUNT is high (good data)
- **Exit**: When COUNT is low (poor data)
- **Best in**: Data validation

### 2. Custom Indicator Strategy
- **Setup**: Use COUNT for custom calculations
- **Entry**: Based on custom indicator
- **Exit**: Based on custom indicator
- **Best in**: Custom analysis

### 3. Data Analysis Strategy
- **Setup**: Analyze data completeness
- **Entry**: On data quality improvements
- **Exit**: On data quality degradation
- **Best in**: Data analysis

### 4. Quality Control Strategy
- **Setup**: Monitor data quality
- **Entry**: When quality is good
- **Exit**: When quality is poor
- **Best in**: Quality control

## COUNT Applications

### 1. Data Quality Analysis
- **Data Completeness**: Measure data completeness
- **Data Patterns**: Identify data patterns
- **Data Trends**: Track data trends
- **Best in**: Data validation

### 2. Custom Indicators
- **Building Block**: For other indicators
- **Custom Calculations**: User-defined indicators
- **Combination**: With other functions
- **Best in**: Custom analysis

### 3. Data Analysis
- **Data Completeness**: Measure data completeness
- **Data Patterns**: Identify data patterns
- **Data Trends**: Track data trends
- **Best in**: Data analysis

### 4. Quality Control
- **Data Quality**: Monitor data quality
- **Data Patterns**: Identify data patterns
- **Data Trends**: Track data trends
- **Best in**: Quality control

## Advantages

1. **Simple**: Easy to understand and calculate
2. **Versatile**: Works with any data
3. **Fast**: Very efficient calculation
4. **Universal**: Works across all markets
5. **Building Block**: For other indicators

## Limitations

1. **No Magnitude**: Doesn't measure value magnitude
2. **Period Dependent**: Results vary with period
3. **No Direction**: Doesn't indicate direction
4. **Context Dependent**: Needs interpretation
5. **No Bounds**: Unbounded values

## Related Functions

- **SUM**: Sum of values over period
- **MAX**: Highest value over period
- **MIN**: Lowest value over period
- **SMA**: Simple Moving Average - average of values

## References

- [TA-Lib Source Code: ta_COUNT.c](https://github.com/TA-Lib/ta-lib/blob/main/src/ta_func/ta_COUNT.c)
- [Investopedia: Technical Analysis](https://www.investopedia.com/terms/t/technicalanalysis.asp)

## Additional Notes

COUNT is a fundamental mathematical operator that serves as a building block for many other indicators. It's particularly useful for:

- **Data Quality Analysis**: Count of valid data points
- **Custom Indicators**: Building block for other indicators
- **Data Analysis**: Analyze data completeness
- **Quality Control**: Monitor data quality

### Key Insights

1. **Mathematical Foundation**:
   - Basic counting operation
   - Building block for other indicators
   - Works with any data series
   - Efficient calculation

2. **Data Quality Applications**:
   - Count of valid data points
   - Data quality assessment
   - Data completeness analysis
   - Quality control

3. **Custom Indicators**:
   - Building block for other indicators
   - User-defined calculations
   - Combination with other functions
   - Custom analysis

4. **Data Analysis**:
   - Data completeness measurement
   - Data pattern identification
   - Data trend analysis
   - Quality monitoring

5. **Trading Applications**:
   - Data quality validation
   - Custom indicator development
   - Data analysis
   - Quality control

### Practical Tips

**For Data Quality Analysis**:
- Track COUNT over time
- Identify data quality trends
- Use for data validation
- Monitor data completeness

**For Custom Indicators**:
- Use COUNT as building block
- Combine with other functions
- Create custom calculations
- Develop user-defined indicators

**For Data Analysis**:
- Analyze data completeness
- Identify data patterns
- Track data trends
- Monitor data quality

**For Quality Control**:
- Monitor data quality
- Set quality thresholds
- Track quality trends
- Use for data validation

COUNT is particularly valuable as a building block for other indicators and for data quality analysis. It's a simple but essential tool for technical analysis and custom indicator development.

