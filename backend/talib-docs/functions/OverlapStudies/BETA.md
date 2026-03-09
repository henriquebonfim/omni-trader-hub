# BETA - Beta

## Overview
Beta measures the volatility or systematic risk of a security compared to the market as a whole. It's a key metric in portfolio management and risk assessment.

## Category
Statistic Functions

## Calculation
Beta is calculated using linear regression between the security's returns and the market's returns:

### Formula
```
Beta = Covariance(Security Returns, Market Returns) / Variance(Market Returns)
     = Correlation(Security, Market) × (StdDev(Security) / StdDev(Market))
```

## Parameters
- **optInTimePeriod** (default: 5): Number of periods for calculation
  - Valid range: 1 to 100000

## Inputs
- Two price series (typically security and market/benchmark): `double[]`, `double[]`

## Outputs
- Beta coefficient values: `double[]`

## What It Means
Beta values interpret as follows:
- **Beta = 1.0**: Security moves in line with the market
- **Beta > 1.0**: Security is more volatile than the market (amplifies market moves)
- **Beta < 1.0**: Security is less volatile than the market (dampens market moves)
- **Beta = 0**: Security moves independently of the market
- **Beta < 0**: Security moves inversely to the market

## How to Use
1. **Risk Assessment**: Measure systematic risk of a security
2. **Portfolio Construction**: Balance portfolio beta to match risk tolerance
3. **Performance Attribution**: Understand sources of returns
4. **Hedging**: Use beta to determine hedge ratios

## Usage Example
```c
#include "ta_libc.h"

int main() {
    // Calculate BETA
    TA_RetCode ret = TA_BETA(
        0,                    // startIdx
        99,                   // endIdx
        security_prices,      // inReal0 (security)
        market_prices,        // inReal1 (market/benchmark)
        5,                    // timePeriod
        &outBegIdx,          // outBegIdx
        &outNBElement,       // outNBElement
        beta                 // outReal
    );
    
    if (ret == TA_SUCCESS) {
        // Use beta array for analysis
        for (int i = 0; i < outNBElement; i++) {
            if (beta[i] > 1.5) {
                // High beta stock - more volatile than market
            } else if (beta[i] < 0.5) {
                // Low beta stock - less volatile than market
            }
        }
    }
}
```

## Trading Strategies
1. **High Beta Stocks**: Trade in trending markets (amplify gains/losses)
2. **Low Beta Stocks**: Hold in uncertain markets (reduce volatility)
3. **Market Timing**: Adjust portfolio beta based on market outlook
4. **Hedging**: Use beta to calculate hedge ratios for risk management

## Advantages
- Widely used and understood measure
- Useful for portfolio management
- Helps assess systematic risk
- Important for CAPM calculations

## Limitations
- Assumes linear relationship with market
- Historical beta may not predict future beta
- Single-factor model (ignores other risk factors)
- Can change over time and market conditions

## Related Functions
- `CORREL` - Pearson's Correlation Coefficient
- `VAR` - Variance
- `STDDEV` - Standard Deviation
- `LINEARREG` - Linear Regression

## References
- Sharpe, W. F. (1964). "Capital Asset Prices: A Theory of Market Equilibrium"
- Technical Analysis Explained by Martin Pring
- TA-Lib Documentation: https://ta-lib.github.io/ta-lib-python/
- DeepWiki TA-Lib: https://deepwiki.com/TA-Lib/ta-lib
