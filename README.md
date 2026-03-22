# Gold 10-BPS ATR Breakout Trap

A highly aggressive, structurally constrained Opening Range Breakout (ORB) algorithm engineered for the XAU/USD (Gold) market. It utilizes fixed basis-point thresholds and a volatility gatekeeper to capture massive asymmetric intraday trends.

## 📌 Overview
Standard breakout strategies often fail in retail environments due to micro-whipsaws, overtrading, and spread drag. This algorithm counters those frictions by abandoning dynamic indicators in favor of rigid mathematical thresholds. 

It anchors to the New York pre-market open and sets a strict 10-basis-point trap. To prevent the algorithm from bleeding out during low-volatility summer months or sideways macro regimes, it features a 14-Day Average True Range (ATR) gatekeeper. If the daily gold volatility drops below a defined threshold, the bot refuses to arm the trap and stays safely in cash.

## ⚙️ Core Mechanics
* **Target Asset:** XAU/USD (Gold)
* **Execution Timeframe:** M5 (5-minute) precise triggering
* **The Trap:** Fixed +/- 0.10% (10 BPS) from the 08:30 AM EST Open
* **The Filter:** 14-Day ATR must exceed $18.00/day
* **Friction Control:** Hardcoded limit of exactly 1 Long and 1 Short execution per day to completely neutralize broker commission drag.

## 📊 Backtest Performance (2022 - 2026 Stress Test)
The strategy relies heavily on asymmetric payoffs rather than high win rates. The mathematical expectation is that the majority of trading days will result in minor, strictly capped losses, while the winning days capture massive, unhindered macro trends.
* **Win Rate:** ~42-43%
* **Payoff Profile:** Extreme Asymmetry (Fat-tailed wins)
* **Capital Preservation:** ATR filter bypasses hundreds of low-volatility days, drastically reducing maximum drawdown.

## 🚀 Installation & Usage
1. Ensure you have [MetaTrader 5](https://www.metatrader5.com/) installed and connected to a broker providing `XAUUSD` data.
2. Install the required Python libraries:
   ```bash
   pip install MetaTrader5 pandas pandas-ta numpy plotly
