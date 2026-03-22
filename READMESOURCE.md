Theoretical Framework: The Fixed Threshold Anomaly


This repository is built upon counter-intuitive quantitative research regarding intraday momentum in precious metals.

📄 The Source Material
Paper Title: Assessing the profitability of intraday opening range breakout strategies

Authors: Holmberg, Lönnbark, Lundström (2013) / Sönnert (2014)

Target Asset: XAU/USD (Gold)

🧠 The Quantitative Thesis
The Opening Range Breakout (ORB) strategy fundamentally challenges the Efficient Market Hypothesis by asserting that asset prices systematically deviate from a random walk during specific, highly concentrated intraday windows. In the XAU/USD market, the overlap between the London and New York trading sessions represents periods of extreme liquidity, volume, and macroeconomic data dissemination.

When gold prices break out of a tightly defined consolidation range established early in the session, it frequently signals a structural transition from a low-volatility mean-reverting regime to an aggressive, directional momentum regime.

🧮 The Mathematical Edge
The mathematical edge of this ORB strategy relies heavily on the principles of asymmetric payoff distributions. Its profitability depends not on a high win rate, but on the magnitude of the winning trades vastly outperforming the frequency and size of losing trades.

The researchers tested whether dynamic thresholds based on an advanced GARCH(1,1) volatility forecasting model would improve performance. Surprisingly, the rigorous empirical data proved that a fixed, narrow threshold (specifically exactly 10 basis points from the daily opening price) vastly outperformed the dynamic GARCH adjustments.

The quantitative edge lies purely in the extreme asymmetry of the payout matrix: while approximately 78% of trading days result in minor, strictly capped losses due to false breakouts, the remaining 22% of days capture massive, unhindered intraday trends. These fat-tailed winning days generate remarkably high mean profits, resulting in a statistically significant positive expectancy.
