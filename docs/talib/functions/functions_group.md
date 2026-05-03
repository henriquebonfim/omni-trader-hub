# TA-Lib Function Groups

This document provides a comprehensive overview of all TA-Lib function groups and their organization.

## Function Groups Overview

TA-Lib functions are organized into the following categories:

### 1. Overlap Studies (重叠研究)
Moving averages and trend-following indicators that overlay on price charts.

**Functions:** 31 functions  
**Directory:** [OverlapStudies/](OverlapStudies/)

#### Function List

| Function Name | English Documentation | Chinese Documentation |
|---------------|-----------------------|-----------------------|
| BBANDS | [BBANDS.md](OverlapStudies/BBANDS.md) | [BBANDS_cn.md](OverlapStudies/BBANDS_cn.md) |
| DEMA | [DEMA.md](OverlapStudies/DEMA.md) | [DEMA_cn.md](OverlapStudies/DEMA_cn.md) |
| EMA | [EMA.md](OverlapStudies/EMA.md) | [EMA_cn.md](OverlapStudies/EMA_cn.md) |
| HT_TRENDLINE | [HT_TRENDLINE.md](OverlapStudies/HT_TRENDLINE.md) | [HT_TRENDLINE_cn.md](OverlapStudies/HT_TRENDLINE_cn.md) |
| KAMA | [KAMA.md](OverlapStudies/KAMA.md) | [KAMA_cn.md](OverlapStudies/KAMA_cn.md) |
| MA | [MA.md](OverlapStudies/MA.md) | [MA_cn.md](OverlapStudies/MA_cn.md) |
| MAMA | [MAMA.md](OverlapStudies/MAMA.md) | [MAMA_cn.md](OverlapStudies/MAMA_cn.md) |
| MAVP | [MAVP.md](OverlapStudies/MAVP.md) | [MAVP_cn.md](OverlapStudies/MAVP_cn.md) |
| MIDPOINT | [MIDPOINT.md](OverlapStudies/MIDPOINT.md) | [MIDPOINT_cn.md](OverlapStudies/MIDPOINT_cn.md) |
| MIDPRICE | [MIDPRICE.md](OverlapStudies/MIDPRICE.md) | [MIDPRICE_cn.md](OverlapStudies/MIDPRICE_cn.md) |
| SAR | [SAR.md](OverlapStudies/SAR.md) | [SAR_cn.md](OverlapStudies/SAR_cn.md) |
| SAREXT | [SAREXT.md](OverlapStudies/SAREXT.md) | [SAREXT_cn.md](OverlapStudies/SAREXT_cn.md) |
| SMA | [SMA.md](OverlapStudies/SMA.md) | [SMA_cn.md](OverlapStudies/SMA_cn.md) |
| T3 | [T3.md](OverlapStudies/T3.md) | [T3_cn.md](OverlapStudies/T3_cn.md) |
| TEMA | [TEMA.md](OverlapStudies/TEMA.md) | [TEMA_cn.md](OverlapStudies/TEMA_cn.md) |
| TRIMA | [TRIMA.md](OverlapStudies/TRIMA.md) | [TRIMA_cn.md](OverlapStudies/TRIMA_cn.md) |
| WMA | [WMA.md](OverlapStudies/WMA.md) | [WMA_cn.md](OverlapStudies/WMA_cn.md) |

#### Description
Overlap Studies include various types of moving averages and trend-following indicators that are typically plotted on top of price charts. These indicators help identify trend direction, support and resistance levels, and potential entry/exit points.

**Key Categories:**
- **Simple Moving Averages**: SMA, EMA, DEMA, TEMA
- **Weighted Moving Averages**: WMA, T3
- **Adaptive Moving Averages**: KAMA, MAMA
- **Bollinger Bands**: BBANDS
- **Parabolic SAR**: SAR, SAREXT
- **Price-based Indicators**: MIDPOINT, MIDPRICE

---

### 2. Momentum Indicators (动量指标)
Oscillators and momentum indicators that help identify trend strength and potential reversals.

**Functions:** 32 functions  
**Directory:** [MomentumIndicators/](MomentumIndicators/)

#### Function List

| Function Name | English Documentation | Chinese Documentation |
|---------------|-----------------------|-----------------------|
| ADX | [ADX.md](MomentumIndicators/ADX.md) | [ADX_cn.md](MomentumIndicators/ADX_cn.md) |
| ADXR | [ADXR.md](MomentumIndicators/ADXR.md) | [ADXR_cn.md](MomentumIndicators/ADXR_cn.md) |
| APO | [APO.md](MomentumIndicators/APO.md) | [APO_cn.md](MomentumIndicators/APO_cn.md) |
| AROON | [AROON.md](MomentumIndicators/AROON.md) | [AROON_cn.md](MomentumIndicators/AROON_cn.md) |
| AROONOSC | [AROONOSC.md](MomentumIndicators/AROONOSC.md) | [AROONOSC_cn.md](MomentumIndicators/AROONOSC_cn.md) |
| BOP | [BOP.md](MomentumIndicators/BOP.md) | [BOP_cn.md](MomentumIndicators/BOP_cn.md) |
| CCI | [CCI.md](MomentumIndicators/CCI.md) | [CCI_cn.md](MomentumIndicators/CCI_cn.md) |
| CMO | [CMO.md](MomentumIndicators/CMO.md) | [CMO_cn.md](MomentumIndicators/CMO_cn.md) |
| DX | [DX.md](MomentumIndicators/DX.md) | [DX_cn.md](MomentumIndicators/DX_cn.md) |
| MACD | [MACD.md](MomentumIndicators/MACD.md) | [MACD_cn.md](MomentumIndicators/MACD_cn.md) |
| MACDEXT | [MACDEXT.md](MomentumIndicators/MACDEXT.md) | [MACDEXT_cn.md](MomentumIndicators/MACDEXT_cn.md) |
| MACDFIX | [MACDFIX.md](MomentumIndicators/MACDFIX.md) | [MACDFIX_cn.md](MomentumIndicators/MACDFIX_cn.md) |
| MFI | [MFI.md](MomentumIndicators/MFI.md) | [MFI_cn.md](MomentumIndicators/MFI_cn.md) |
| MINUS_DI | [MINUS_DI.md](MomentumIndicators/MINUS_DI.md) | [MINUS_DI_cn.md](MomentumIndicators/MINUS_DI_cn.md) |
| MINUS_DM | [MINUS_DM.md](MomentumIndicators/MINUS_DM.md) | [MINUS_DM_cn.md](MomentumIndicators/MINUS_DM_cn.md) |
| MOM | [MOM.md](MomentumIndicators/MOM.md) | [MOM_cn.md](MomentumIndicators/MOM_cn.md) |
| PLUS_DI | [PLUS_DI.md](MomentumIndicators/PLUS_DI.md) | [PLUS_DI_cn.md](MomentumIndicators/PLUS_DI_cn.md) |
| PLUS_DM | [PLUS_DM.md](MomentumIndicators/PLUS_DM.md) | [PLUS_DM_cn.md](MomentumIndicators/PLUS_DM_cn.md) |
| PPO | [PPO.md](MomentumIndicators/PPO.md) | [PPO_cn.md](MomentumIndicators/PPO_cn.md) |
| ROC | [ROC.md](MomentumIndicators/ROC.md) | [ROC_cn.md](MomentumIndicators/ROC_cn.md) |
| ROCP | [ROCP.md](MomentumIndicators/ROCP.md) | [ROCP_cn.md](MomentumIndicators/ROCP_cn.md) |
| ROCR | [ROCR.md](MomentumIndicators/ROCR.md) | [ROCR_cn.md](MomentumIndicators/ROCR_cn.md) |
| ROCR100 | [ROCR100.md](MomentumIndicators/ROCR100.md) | [ROCR100_cn.md](MomentumIndicators/ROCR100_cn.md) |
| RSI | [RSI.md](MomentumIndicators/RSI.md) | [RSI_cn.md](MomentumIndicators/RSI_cn.md) |
| STOCH | [STOCH.md](MomentumIndicators/STOCH.md) | [STOCH_cn.md](MomentumIndicators/STOCH_cn.md) |
| STOCHF | [STOCHF.md](MomentumIndicators/STOCHF.md) | [STOCHF_cn.md](MomentumIndicators/STOCHF_cn.md) |
| STOCHRSI | [STOCHRSI.md](MomentumIndicators/STOCHRSI.md) | [STOCHRSI_cn.md](MomentumIndicators/STOCHRSI_cn.md) |
| TRIX | [TRIX.md](MomentumIndicators/TRIX.md) | [TRIX_cn.md](MomentumIndicators/TRIX_cn.md) |
| ULTOSC | [ULTOSC.md](MomentumIndicators/ULTOSC.md) | [ULTOSC_cn.md](MomentumIndicators/ULTOSC_cn.md) |
| WILLR | [WILLR.md](MomentumIndicators/WILLR.md) | [WILLR_cn.md](MomentumIndicators/WILLR_cn.md) |

#### Description
Momentum Indicators are oscillators that help identify trend strength, momentum shifts, and potential reversal points. These indicators typically oscillate between fixed ranges and provide signals when they reach extreme levels.

**Key Categories:**
- **Trend Strength**: ADX, ADXR, DX
- **Directional Movement**: PLUS_DI, MINUS_DI, PLUS_DM, MINUS_DM
- **MACD Family**: MACD, MACDEXT, MACDFIX, APO, PPO
- **Rate of Change**: ROC, ROCP, ROCR, ROCR100, MOM
- **Stochastic Oscillators**: STOCH, STOCHF, STOCHRSI, STOCHMI
- **Relative Strength**: RSI, CCI, WILLR, ULTOSC
- **Volume-based**: MFI, BOP
- **Trend Detection**: AROON, AROONOSC, TRIX, CMO

---

### 3. Volume Indicators (成交量指标)
Indicators that analyze trading volume patterns and relationships with price.

**Functions:** 4 functions  
**Directory:** [VolumeIndicators/](VolumeIndicators/)

#### Function List

| Function Name | English Documentation | Chinese Documentation |
|---------------|-----------------------|-----------------------|
| AD | [AD.md](VolumeIndicators/AD.md) | [AD_cn.md](VolumeIndicators/AD_cn.md) |
| ADOSC | [ADOSC.md](VolumeIndicators/ADOSC.md) | [ADOSC_cn.md](VolumeIndicators/ADOSC_cn.md) |
| OBV | [OBV.md](VolumeIndicators/OBV.md) | [OBV_cn.md](VolumeIndicators/OBV_cn.md) |

#### Description
Volume Indicators analyze trading volume patterns and their relationship with price movements. These indicators help confirm price trends and identify potential reversals based on volume analysis.

**Key Categories:**
- **Accumulation/Distribution**: AD (Accumulation/Distribution Line)
- **Volume Oscillators**: ADOSC (Accumulation/Distribution Oscillator)
- **Volume Trend**: OBV (On Balance Volume)

---

### 4. Volatility Indicators (波动率指标)
Indicators that measure price volatility and market uncertainty.

**Functions:** 5 functions  
**Directory:** [VolatilityIndicators/](VolatilityIndicators/)

#### Function List

| Function Name | English Documentation | Chinese Documentation |
|---------------|-----------------------|-----------------------|
| ATR | [ATR.md](VolatilityIndicators/ATR.md) | [ATR_cn.md](VolatilityIndicators/ATR_cn.md) |
| NATR | [NATR.md](VolatilityIndicators/NATR.md) | [NATR_cn.md](VolatilityIndicators/NATR_cn.md) |
| STDDEV | [STDDEV.md](VolatilityIndicators/STDDEV.md) | [STDDEV_cn.md](VolatilityIndicators/STDDEV_cn.md) |
| TRANGE | [TRANGE.md](VolatilityIndicators/TRANGE.md) | [TRANGE_cn.md](VolatilityIndicators/TRANGE_cn.md) |
| VAR | [VAR.md](VolatilityIndicators/VAR.md) | [VAR_cn.md](VolatilityIndicators/VAR_cn.md) |

#### Description
Volatility Indicators measure the degree of price variation over time. These indicators help assess market uncertainty, set stop-loss levels, and identify periods of high or low volatility.

**Key Categories:**
- **True Range**: ATR (Average True Range), NATR (Normalized ATR), TRANGE (True Range)
- **Volatility Measurement**: Used for position sizing, stop-loss placement, and market condition assessment

---

### 5. Price Transform (价格变换)
Functions that transform price data into different representations.

**Functions:** 4 functions  
**Directory:** [PriceTransform/](PriceTransform/)

#### Function List

| Function Name | English Documentation | Chinese Documentation |
|---------------|-----------------------|-----------------------|
| AVGPRICE | [AVGPRICE.md](PriceTransform/AVGPRICE.md) | [AVGPRICE_cn.md](PriceTransform/AVGPRICE_cn.md) |
| MEDPRICE | [MEDPRICE.md](PriceTransform/MEDPRICE.md) | [MEDPRICE_cn.md](PriceTransform/MEDPRICE_cn.md) |
| TYPPRICE | [TYPPRICE.md](PriceTransform/TYPPRICE.md) | [TYPPRICE_cn.md](PriceTransform/TYPPRICE_cn.md) |
| WCLPRICE | [WCLPRICE.md](PriceTransform/WCLPRICE.md) | [WCLPRICE_cn.md](PriceTransform/WCLPRICE_cn.md) |

#### Description
Price Transform functions convert OHLC (Open, High, Low, Close) price data into different price representations. These transformed prices are often used as inputs for other technical indicators.

**Key Categories:**
- **Average Price**: AVGPRICE (Average Price)
- **Median Price**: MEDPRICE (Median Price)
- **Typical Price**: TYPPRICE (Typical Price)
- **Weighted Close Price**: WCLPRICE (Weighted Close Price)

---

### 6. Cycle Indicators (周期指标)
Indicators that analyze cyclical patterns in price data.

**Functions:** 5 functions  
**Directory:** [CycleIndicators/](CycleIndicators/)

#### Function List

| Function Name | English Documentation | Chinese Documentation |
|---------------|-----------------------|-----------------------|
| HT_DCPERIOD | [HT_DCPERIOD.md](CycleIndicators/HT_DCPERIOD.md) | [HT_DCPERIOD_cn.md](CycleIndicators/HT_DCPERIOD_cn.md) |
| HT_DCPHASE | [HT_DCPHASE.md](CycleIndicators/HT_DCPHASE.md) | [HT_DCPHASE_cn.md](CycleIndicators/HT_DCPHASE_cn.md) |
| HT_PHASOR | [HT_PHASOR.md](CycleIndicators/HT_PHASOR.md) | [HT_PHASOR_cn.md](CycleIndicators/HT_PHASOR_cn.md) |
| HT_SINE | [HT_SINE.md](CycleIndicators/HT_SINE.md) | [HT_SINE_cn.md](CycleIndicators/HT_SINE_cn.md) |
| HT_TRENDMODE | [HT_TRENDMODE.md](CycleIndicators/HT_TRENDMODE.md) | [HT_TRENDMODE_cn.md](CycleIndicators/HT_TRENDMODE_cn.md) |

#### Description
Cycle Indicators analyze cyclical patterns in price data using Hilbert Transform techniques. These indicators help identify dominant cycles and phase relationships in market data.

**Key Categories:**
- **Cycle Analysis**: HT_DCPERIOD (Hilbert Transform - Dominant Cycle Period)
- **Phase Analysis**: HT_DCPHASE (Hilbert Transform - Dominant Cycle Phase)
- **Phasor Components**: HT_PHASOR (Hilbert Transform - Phasor Components)
- **Sine Wave**: HT_SINE (Hilbert Transform - SineWave)
- **Trend Mode**: HT_TRENDMODE (Hilbert Transform - Trend vs Cycle Mode)

---

### 7. Math Operators (数学运算符)
Basic mathematical operators for vector arithmetic operations.

**Functions:** 11 functions  
**Directory:** [MathOperators/](MathOperators/)

#### Function List

| Function Name | English Documentation | Chinese Documentation |
|---------------|-----------------------|-----------------------|
| ADD | [ADD.md](MathOperators/ADD.md) | [ADD_cn.md](MathOperators/ADD_cn.md) |
| DIV | [DIV.md](MathOperators/DIV.md) | [DIV_cn.md](MathOperators/DIV_cn.md) |
| MAX | [MAX.md](MathOperators/MAX.md) | [MAX_cn.md](MathOperators/MAX_cn.md) |
| MAXINDEX | [MAXINDEX.md](MathOperators/MAXINDEX.md) | [MAXINDEX_cn.md](MathOperators/MAXINDEX_cn.md) |
| MIN | [MIN.md](MathOperators/MIN.md) | [MIN_cn.md](MathOperators/MIN_cn.md) |
| MININDEX | [MININDEX.md](MathOperators/MININDEX.md) | [MININDEX_cn.md](MathOperators/MININDEX_cn.md) |
| MINMAX | [MINMAX.md](MathOperators/MINMAX.md) | [MINMAX_cn.md](MathOperators/MINMAX_cn.md) |
| MINMAXINDEX | [MINMAXINDEX.md](MathOperators/MINMAXINDEX.md) | [MINMAXINDEX_cn.md](MathOperators/MINMAXINDEX_cn.md) |
| MULT | [MULT.md](MathOperators/MULT.md) | [MULT_cn.md](MathOperators/MULT_cn.md) |
| SUB | [SUB.md](MathOperators/SUB.md) | [SUB_cn.md](MathOperators/SUB_cn.md) |
| SUM | [SUM.md](MathOperators/SUM.md) | [SUM_cn.md](MathOperators/SUM_cn.md) |

#### Description
Math Operators provide basic mathematical operations for vector arithmetic. These functions perform element-wise operations on input arrays and are fundamental building blocks for more complex technical indicators.

**Key Categories:**
- **Arithmetic Operations**: ADD, SUB, MULT, DIV
- **Statistical Operations**: SUM, MAX, MIN
- **Index Operations**: MAXINDEX, MININDEX, MINMAXINDEX
- **Range Operations**: MINMAX

---

### 8. Pattern Recognition (形态识别)
Candlestick pattern recognition functions for identifying specific price formations.

**Functions:** 63 functions  
**Directory:** [PatternRecognition/](PatternRecognition/)

#### Function List

| Function Name | English Documentation | Chinese Documentation |
|---------------|-----------------------|-----------------------|
| CDL2CROWS | [CDL2CROWS.md](PatternRecognition/CDL2CROWS.md) | [CDL2CROWS_cn.md](PatternRecognition/CDL2CROWS_cn.md) |
| CDL3BLACKCROWS | [CDL3BLACKCROWS.md](PatternRecognition/CDL3BLACKCROWS.md) | [CDL3BLACKCROWS_cn.md](PatternRecognition/CDL3BLACKCROWS_cn.md) |
| CDL3INSIDE | [CDL3INSIDE.md](PatternRecognition/CDL3INSIDE.md) | [CDL3INSIDE_cn.md](PatternRecognition/CDL3INSIDE_cn.md) |
| CDL3LINESTRIKE | [CDL3LINESTRIKE.md](PatternRecognition/CDL3LINESTRIKE.md) | [CDL3LINESTRIKE_cn.md](PatternRecognition/CDL3LINESTRIKE_cn.md) |
| CDL3OUTSIDE | [CDL3OUTSIDE.md](PatternRecognition/CDL3OUTSIDE.md) | [CDL3OUTSIDE_cn.md](PatternRecognition/CDL3OUTSIDE_cn.md) |
| CDL3STARSINSOUTH | [CDL3STARSINSOUTH.md](PatternRecognition/CDL3STARSINSOUTH.md) | [CDL3STARSINSOUTH_cn.md](PatternRecognition/CDL3STARSINSOUTH_cn.md) |
| CDL3WHITESOLDIERS | [CDL3WHITESOLDIERS.md](PatternRecognition/CDL3WHITESOLDIERS.md) | [CDL3WHITESOLDIERS_cn.md](PatternRecognition/CDL3WHITESOLDIERS_cn.md) |
| CDLABANDONEDBABY | [CDLABANDONEDBABY.md](PatternRecognition/CDLABANDONEDBABY.md) | [CDLABANDONEDBABY_cn.md](PatternRecognition/CDLABANDONEDBABY_cn.md) |
| CDLADVANCEBLOCK | [CDLADVANCEBLOCK.md](PatternRecognition/CDLADVANCEBLOCK.md) | [CDLADVANCEBLOCK_cn.md](PatternRecognition/CDLADVANCEBLOCK_cn.md) |
| CDLBELTHOLD | [CDLBELTHOLD.md](PatternRecognition/CDLBELTHOLD.md) | [CDLBELTHOLD_cn.md](PatternRecognition/CDLBELTHOLD_cn.md) |
| CDLBREAKAWAY | [CDLBREAKAWAY.md](PatternRecognition/CDLBREAKAWAY.md) | [CDLBREAKAWAY_cn.md](PatternRecognition/CDLBREAKAWAY_cn.md) |
| CDLCLOSINGMARUBOZU | [CDLCLOSINGMARUBOZU.md](PatternRecognition/CDLCLOSINGMARUBOZU.md) | [CDLCLOSINGMARUBOZU_cn.md](PatternRecognition/CDLCLOSINGMARUBOZU_cn.md) |
| CDLCONCEALBABYSWALL | [CDLCONCEALBABYSWALL.md](PatternRecognition/CDLCONCEALBABYSWALL.md) | [CDLCONCEALBABYSWALL_cn.md](PatternRecognition/CDLCONCEALBABYSWALL_cn.md) |
| CDLCOUNTERATTACK | [CDLCOUNTERATTACK.md](PatternRecognition/CDLCOUNTERATTACK.md) | [CDLCOUNTERATTACK_cn.md](PatternRecognition/CDLCOUNTERATTACK_cn.md) |
| CDLDARKCLOUDCOVER | [CDLDARKCLOUDCOVER.md](PatternRecognition/CDLDARKCLOUDCOVER.md) | [CDLDARKCLOUDCOVER_cn.md](PatternRecognition/CDLDARKCLOUDCOVER_cn.md) |
| CDLDOJI | [CDLDOJI.md](PatternRecognition/CDLDOJI.md) | [CDLDOJI_cn.md](PatternRecognition/CDLDOJI_cn.md) |
| CDLDOJISTAR | [CDLDOJISTAR.md](PatternRecognition/CDLDOJISTAR.md) | [CDLDOJISTAR_cn.md](PatternRecognition/CDLDOJISTAR_cn.md) |
| CDLDRAGONFLYDOJI | [CDLDRAGONFLYDOJI.md](PatternRecognition/CDLDRAGONFLYDOJI.md) | [CDLDRAGONFLYDOJI_cn.md](PatternRecognition/CDLDRAGONFLYDOJI_cn.md) |
| CDLENGULFING | [CDLENGULFING.md](PatternRecognition/CDLENGULFING.md) | [CDLENGULFING_cn.md](PatternRecognition/CDLENGULFING_cn.md) |
| CDLEVENINGDOJISTAR | [CDLEVENINGDOJISTAR.md](PatternRecognition/CDLEVENINGDOJISTAR.md) | [CDLEVENINGDOJISTAR_cn.md](PatternRecognition/CDLEVENINGDOJISTAR_cn.md) |
| CDLEVENINGSTAR | [CDLEVENINGSTAR.md](PatternRecognition/CDLEVENINGSTAR.md) | [CDLEVENINGSTAR_cn.md](PatternRecognition/CDLEVENINGSTAR_cn.md) |
| CDLGAPSIDESIDEWHITE | [CDLGAPSIDESIDEWHITE.md](PatternRecognition/CDLGAPSIDESIDEWHITE.md) | [CDLGAPSIDESIDEWHITE_cn.md](PatternRecognition/CDLGAPSIDESIDEWHITE_cn.md) |
| CDLGRAVESTONEDOJI | [CDLGRAVESTONEDOJI.md](PatternRecognition/CDLGRAVESTONEDOJI.md) | [CDLGRAVESTONEDOJI_cn.md](PatternRecognition/CDLGRAVESTONEDOJI_cn.md) |
| CDLHAMMER | [CDLHAMMER.md](PatternRecognition/CDLHAMMER.md) | [CDLHAMMER_cn.md](PatternRecognition/CDLHAMMER_cn.md) |
| CDLHANGINGMAN | [CDLHANGINGMAN.md](PatternRecognition/CDLHANGINGMAN.md) | [CDLHANGINGMAN_cn.md](PatternRecognition/CDLHANGINGMAN_cn.md) |
| CDLHARAMI | [CDLHARAMI.md](PatternRecognition/CDLHARAMI.md) | [CDLHARAMI_cn.md](PatternRecognition/CDLHARAMI_cn.md) |
| CDLHARAMICROSS | [CDLHARAMICROSS.md](PatternRecognition/CDLHARAMICROSS.md) | [CDLHARAMICROSS_cn.md](PatternRecognition/CDLHARAMICROSS_cn.md) |
| CDLHIGHWAVE | [CDLHIGHWAVE.md](PatternRecognition/CDLHIGHWAVE.md) | [CDLHIGHWAVE_cn.md](PatternRecognition/CDLHIGHWAVE_cn.md) |
| CDLHIKKAKE | [CDLHIKKAKE.md](PatternRecognition/CDLHIKKAKE.md) | [CDLHIKKAKE_cn.md](PatternRecognition/CDLHIKKAKE_cn.md) |
| CDLHIKKAKEMOD | [CDLHIKKAKEMOD.md](PatternRecognition/CDLHIKKAKEMOD.md) | [CDLHIKKAKEMOD_cn.md](PatternRecognition/CDLHIKKAKEMOD_cn.md) |
| CDLHOMINGPIGEON | [CDLHOMINGPIGEON.md](PatternRecognition/CDLHOMINGPIGEON.md) | [CDLHOMINGPIGEON_cn.md](PatternRecognition/CDLHOMINGPIGEON_cn.md) |
| CDLIDENTICAL3CROWS | [CDLIDENTICAL3CROWS.md](PatternRecognition/CDLIDENTICAL3CROWS.md) | [CDLIDENTICAL3CROWS_cn.md](PatternRecognition/CDLIDENTICAL3CROWS_cn.md) |
| CDLINNECK | [CDLINNECK.md](PatternRecognition/CDLINNECK.md) | [CDLINNECK_cn.md](PatternRecognition/CDLINNECK_cn.md) |
| CDLINVERTEDHAMMER | [CDLINVERTEDHAMMER.md](PatternRecognition/CDLINVERTEDHAMMER.md) | [CDLINVERTEDHAMMER_cn.md](PatternRecognition/CDLINVERTEDHAMMER_cn.md) |
| CDLKICKING | [CDLKICKING.md](PatternRecognition/CDLKICKING.md) | [CDLKICKING_cn.md](PatternRecognition/CDLKICKING_cn.md) |
| CDLKICKINGBYLENGTH | [CDLKICKINGBYLENGTH.md](PatternRecognition/CDLKICKINGBYLENGTH.md) | [CDLKICKINGBYLENGTH_cn.md](PatternRecognition/CDLKICKINGBYLENGTH_cn.md) |
| CDLLADDERBOTTOM | [CDLLADDERBOTTOM.md](PatternRecognition/CDLLADDERBOTTOM.md) | [CDLLADDERBOTTOM_cn.md](PatternRecognition/CDLLADDERBOTTOM_cn.md) |
| CDLLONGLEGGEDDOJI | [CDLLONGLEGGEDDOJI.md](PatternRecognition/CDLLONGLEGGEDDOJI.md) | [CDLLONGLEGGEDDOJI_cn.md](PatternRecognition/CDLLONGLEGGEDDOJI_cn.md) |
| CDLLONGLINE | [CDLLONGLINE.md](PatternRecognition/CDLLONGLINE.md) | [CDLLONGLINE_cn.md](PatternRecognition/CDLLONGLINE_cn.md) |
| CDLMARUBOZU | [CDLMARUBOZU.md](PatternRecognition/CDLMARUBOZU.md) | [CDLMARUBOZU_cn.md](PatternRecognition/CDLMARUBOZU_cn.md) |
| CDLMATCHINGLOW | [CDLMATCHINGLOW.md](PatternRecognition/CDLMATCHINGLOW.md) | [CDLMATCHINGLOW_cn.md](PatternRecognition/CDLMATCHINGLOW_cn.md) |
| CDLMATHOLD | [CDLMATHOLD.md](PatternRecognition/CDLMATHOLD.md) | [CDLMATHOLD_cn.md](PatternRecognition/CDLMATHOLD_cn.md) |
| CDLMORNINGDOJISTAR | [CDLMORNINGDOJISTAR.md](PatternRecognition/CDLMORNINGDOJISTAR.md) | [CDLMORNINGDOJISTAR_cn.md](PatternRecognition/CDLMORNINGDOJISTAR_cn.md) |
| CDLMORNINGSTAR | [CDLMORNINGSTAR.md](PatternRecognition/CDLMORNINGSTAR.md) | [CDLMORNINGSTAR_cn.md](PatternRecognition/CDLMORNINGSTAR_cn.md) |
| CDLONNECK | [CDLONNECK.md](PatternRecognition/CDLONNECK.md) | [CDLONNECK_cn.md](PatternRecognition/CDLONNECK_cn.md) |
| CDLPIERCING | [CDLPIERCING.md](PatternRecognition/CDLPIERCING.md) | [CDLPIERCING_cn.md](PatternRecognition/CDLPIERCING_cn.md) |
| CDLRICKSHAWMAN | [CDLRICKSHAWMAN.md](PatternRecognition/CDLRICKSHAWMAN.md) | [CDLRICKSHAWMAN_cn.md](PatternRecognition/CDLRICKSHAWMAN_cn.md) |
| CDLRISEFALL3METHODS | [CDLRISEFALL3METHODS.md](PatternRecognition/CDLRISEFALL3METHODS.md) | [CDLRISEFALL3METHODS_cn.md](PatternRecognition/CDLRISEFALL3METHODS_cn.md) |
| CDLSEPARATINGLINES | [CDLSEPARATINGLINES.md](PatternRecognition/CDLSEPARATINGLINES.md) | [CDLSEPARATINGLINES_cn.md](PatternRecognition/CDLSEPARATINGLINES_cn.md) |
| CDLSHOOTINGSTAR | [CDLSHOOTINGSTAR.md](PatternRecognition/CDLSHOOTINGSTAR.md) | [CDLSHOOTINGSTAR_cn.md](PatternRecognition/CDLSHOOTINGSTAR_cn.md) |
| CDLSHORTLINE | [CDLSHORTLINE.md](PatternRecognition/CDLSHORTLINE.md) | [CDLSHORTLINE_cn.md](PatternRecognition/CDLSHORTLINE_cn.md) |
| CDLSPINNINGTOP | [CDLSPINNINGTOP.md](PatternRecognition/CDLSPINNINGTOP.md) | [CDLSPINNINGTOP_cn.md](PatternRecognition/CDLSPINNINGTOP_cn.md) |
| CDLSTALLEDPATTERN | [CDLSTALLEDPATTERN.md](PatternRecognition/CDLSTALLEDPATTERN.md) | [CDLSTALLEDPATTERN_cn.md](PatternRecognition/CDLSTALLEDPATTERN_cn.md) |
| CDLSTICKSANDWICH | [CDLSTICKSANDWICH.md](PatternRecognition/CDLSTICKSANDWICH.md) | [CDLSTICKSANDWICH_cn.md](PatternRecognition/CDLSTICKSANDWICH_cn.md) |
| CDLTAKURI | [CDLTAKURI.md](PatternRecognition/CDLTAKURI.md) | [CDLTAKURI_cn.md](PatternRecognition/CDLTAKURI_cn.md) |
| CDLTASUKIGAP | [CDLTASUKIGAP.md](PatternRecognition/CDLTASUKIGAP.md) | [CDLTASUKIGAP_cn.md](PatternRecognition/CDLTASUKIGAP_cn.md) |
| CDLTHRUSTING | [CDLTHRUSTING.md](PatternRecognition/CDLTHRUSTING.md) | [CDLTHRUSTING_cn.md](PatternRecognition/CDLTHRUSTING_cn.md) |
| CDLTRISTAR | [CDLTRISTAR.md](PatternRecognition/CDLTRISTAR.md) | [CDLTRISTAR_cn.md](PatternRecognition/CDLTRISTAR_cn.md) |
| CDLUNIQUE3RIVER | [CDLUNIQUE3RIVER.md](PatternRecognition/CDLUNIQUE3RIVER.md) | [CDLUNIQUE3RIVER_cn.md](PatternRecognition/CDLUNIQUE3RIVER_cn.md) |
| CDLUPSIDEGAP2CROWS | [CDLUPSIDEGAP2CROWS.md](PatternRecognition/CDLUPSIDEGAP2CROWS.md) | [CDLUPSIDEGAP2CROWS_cn.md](PatternRecognition/CDLUPSIDEGAP2CROWS_cn.md) |
| CDLXSIDEGAP3METHODS | [CDLXSIDEGAP3METHODS.md](PatternRecognition/CDLXSIDEGAP3METHODS.md) | [CDLXSIDEGAP3METHODS_cn.md](PatternRecognition/CDLXSIDEGAP3METHODS_cn.md) |

#### Description
Pattern Recognition functions identify specific candlestick patterns that can signal potential price reversals, continuations, or market indecision. These patterns are based on Japanese candlestick charting techniques.

**Key Categories:**
- **Single Candle Patterns**: DOJI, HAMMER, HANGINGMAN, SHOOTINGSTAR, MARUBOZU, SPINNINGTOP
- **Two Candle Patterns**: ENGULFING, HARAMI, PIERCING, DARKCLOUDCOVER, COUNTERATTACK
- **Three Candle Patterns**: MORNINGSTAR, EVENINGSTAR, THREE WHITE SOLDIERS, THREE BLACK CROWS
- **Complex Patterns**: ABANDONEDBABY, BREAKAWAY, KICKING, TASUKIGAP, UNIQUE3RIVER
- **Doji Variations**: DRAGONFLYDOJI, GRAVESTONEDOJI, LONGLEGGEDDOJI, RICKSHAWMAN
- **Star Patterns**: DOJISTAR, MORNINGDOJISTAR, EVENINGDOJISTAR, TRISTAR

---

## Documentation Structure

Each function group contains:
- English documentation files (`.md`)
- Chinese documentation files (`_cn.md`)
- Group-specific overview table
- Detailed function descriptions and usage information

## Usage

Navigate to the specific function group directory to find:
- Individual function documentation
- Both English and Chinese versions
- Function-specific examples and usage instructions

## Total Functions

**Total TA-Lib Functions:** 153 functions across 8 categories

---

*This documentation is organized according to the official TA-Lib Python library structure.*