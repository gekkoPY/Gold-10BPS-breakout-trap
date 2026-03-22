import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ==========================================
# 1. STRATEGY PARAMETERS (XAU/USD)
# ==========================================
SYMBOL = "GOLD.pro" 
TIMEFRAME = mt5.TIMEFRAME_M5 
SPREAD = 0.30 
BPS_THRESHOLD = 0.0010 # 10 Basis Points

# --- THE VOLATILITY GATEKEEPER ---
MIN_ATR_THRESHOLD = 18.0 # Gold must be averaging an $18/day range

# --- MT5 SERVER TIME ALIGNMENT (Assuming GMT+2/EET) ---
ANCHOR_HOUR = 15
ANCHOR_MIN = 30
CLOSE_HOUR = 22
CLOSE_MIN = 55

print("\n" + "="*60)
print(f"📡 DOWNLOADING MULTI-YEAR M5 DATA (2022-2026) FOR {SYMBOL}")
print("="*60)

if not mt5.initialize():
    print("❌ MT5 Initialization failed.")
    quit()

start_date = datetime(2022, 1, 1)
end_date = datetime.now()
rates = mt5.copy_rates_range(SYMBOL, TIMEFRAME, start_date, end_date)
mt5.shutdown()

if rates is None or len(rates) == 0:
    print(f"❌ MT5 returned no data! Scroll your M5 chart back to 2022 to download history.")
    quit()

df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
df.set_index('time', inplace=True)

# ==========================================
# 2. VOLATILITY FILTER PRE-PROCESSING (ATR)
# ==========================================
print("🧮 Calculating 14-Day Average True Range (ATR)...")
# Resample M5 data into Daily data to calculate daily volatility accurately
daily_df = df.resample('D').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last'
}).dropna()

# Calculate 14-Day ATR
daily_df.ta.atr(length=14, append=True)
atr_col = [c for c in daily_df.columns if c.startswith('ATRr_')][0]

# Map the Date column back to the main dataframe
df['Date'] = df.index.date
daily_df['Date'] = daily_df.index.date

print(f"✅ Loaded {len(df)} M5 Candles. Initiating ATR-Filtered Stress Test...")

# ==========================================
# 3. THE 10-BPS GOLD TRAP ENGINE
# ==========================================
unique_days = df['Date'].unique()
results = []
equity = 0.0
equity_curve = [0.0]
total_spread_paid = 0.0
days_skipped_by_filter = 0

for i in range(1, len(unique_days)):
    day = unique_days[i]
    prev_day = unique_days[i-1]
    
    # 1. VOLATILITY GATEKEEPER CHECK
    try:
        # Check the ATR from yesterday's close
        yesterday_atr = daily_df.loc[daily_df['Date'] == prev_day, atr_col].values[0]
        if pd.isna(yesterday_atr) or yesterday_atr < MIN_ATR_THRESHOLD:
            days_skipped_by_filter += 1
            continue # Market is dead. Stay in cash.
    except IndexError:
        continue # Skip if ATR data is missing for the day
        
    day_data = df[df['Date'] == day]
    
    anchor_time = datetime.combine(day, datetime.min.time()).replace(hour=ANCHOR_HOUR, minute=ANCHOR_MIN)
    session_end_time = datetime.combine(day, datetime.min.time()).replace(hour=CLOSE_HOUR, minute=CLOSE_MIN)
    
    session_data = day_data[(day_data.index >= anchor_time) & (day_data.index <= session_end_time)]
    
    if session_data.empty or anchor_time not in session_data.index:
        continue 
        
    anchor_price = session_data.loc[anchor_time]['open']
    trap_high = anchor_price * (1 + BPS_THRESHOLD)
    trap_low = anchor_price * (1 - BPS_THRESHOLD)
    
    position = 0
    entry_price = 0.0
    daily_pnl = 0.0
    
    long_taken = False
    short_taken = False
    
    for index, row in session_data.iterrows():
        if position == 0:
            if row['high'] >= trap_high and not long_taken:
                position = 1
                entry_price = trap_high + SPREAD
                long_taken = True
                total_spread_paid += SPREAD
            elif row['low'] <= trap_low and not short_taken:
                position = -1
                entry_price = trap_low - SPREAD
                short_taken = True
                total_spread_paid += SPREAD
                
        elif position == 1:
            if row['low'] <= trap_low:
                daily_pnl += (trap_low - entry_price) 
                position = 0
                if not short_taken:
                    position = -1
                    entry_price = trap_low - SPREAD
                    short_taken = True
                    total_spread_paid += SPREAD
                    
        elif position == -1:
            if row['high'] >= trap_high:
                daily_pnl += (entry_price - trap_high) 
                position = 0
                if not long_taken:
                    position = 1
                    entry_price = trap_high + SPREAD
                    long_taken = True
                    total_spread_paid += SPREAD
                    
    if position != 0:
        try:
            exit_candle = session_data.iloc[-1] 
            exit_price = exit_candle['close']
            if position == 1: daily_pnl += (exit_price - entry_price)
            elif position == -1: daily_pnl += (entry_price - exit_price)
        except Exception:
            pass
            
    if long_taken or short_taken:
        equity += daily_pnl
        equity_curve.append(equity)
        results.append({'Date': day, 'PnL': daily_pnl})

# ==========================================
# 4. STATS, DRAWDOWN & VISUALIZATION
# ==========================================
total_days_traded = len(results)
winning_days = len([r for r in results if r['PnL'] > 0])
win_rate = (winning_days / total_days_traded * 100) if total_days_traded > 0 else 0

running_max = np.maximum.accumulate(equity_curve)
drawdowns = running_max - equity_curve
max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0

print("\n" + "="*60)
print("🏆 ATR-FILTERED MACRO STRESS TEST: 10-BPS GOLD TRAP")
print("="*60)
print(f"➤ Total Days Skipped     : {days_skipped_by_filter} (Low Volatility)")
print(f"➤ Total Days Traded      : {total_days_traded}")
print(f"➤ Daily Win Rate         : {win_rate:.2f}%")
print(f"➤ Total Spread Paid      : ${total_spread_paid:.2f} per ounce")
print(f"➤ Maximum Drawdown       : -${max_drawdown:.2f} per ounce")
print(f"➤ Final Net Profit       : ${equity:.2f} per ounce")
print("="*60)

fig = go.Figure()
fig.add_trace(go.Scatter(
    y=equity_curve,
    mode='lines', name='Filtered 10-BPS Net Equity',
    fill='tozeroy', line=dict(color='#00FF7F', width=2)
))

fig.update_layout(
    title=f"ATR-Filtered Stress Test: 10-BPS Breakout (Gold, 2022-2026)",
    xaxis_title="Trading Days",
    yaxis_title="Net Profit ($ per oz)",
    template="plotly_dark",
    hovermode="x unified"
)
fig.write_html("gold_atr_filtered.html", auto_open=True)
print("✅ Backtest Complete. Check your browser.")
