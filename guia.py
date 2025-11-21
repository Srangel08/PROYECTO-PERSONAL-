# ============================================================
# Binance Interactive Dashboard Example
# Author: Copilot & Santiago
# ============================================================
# This script demonstrates how to:
# 1. Connect to Binance API using python-binance
# 2. Fetch live BTC/USDT price data
# 3. Display historical candlestick data
# 4. Build an interactive dashboard with Streamlit
#
# Paste this into VS Code, install dependencies, and run:
#   streamlit run dashboard.py
# ============================================================

# -----------------------------
# Step 1: Import libraries
# -----------------------------
from binance.client import Client
from binance import ThreadedWebsocketManager
import pandas as pd
import streamlit as st
import time

# -----------------------------
# Step 2: API Keys
# -----------------------------
# IMPORTANT: Replace with your own Binance API key/secret.
# For safety, use environment variables or a config file.
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_API_SECRET"

# Initialize the Binance client
client = Client(API_KEY, API_SECRET)

# -----------------------------
# Step 3: Streamlit Dashboard Setup
# -----------------------------
st.set_page_config(page_title="Binance Dashboard", layout="wide")
st.title("📊 Binance Interactive Dashboard")
st.markdown("Live BTC/USDT data with charts and balances")

# -----------------------------
# Step 4: Fetch Account Balances
# -----------------------------
# This shows your wallet balances (only works if API key has 'read' permission)
account_info = client.get_account()
balances = account_info["balances"]

# Convert balances to DataFrame for display
df_balances = pd.DataFrame(balances)
df_balances = df_balances[df_balances["free"].astype(float) > 0]  # show only non-zero balances
st.subheader("💰 Account Balances")
st.dataframe(df_balances)

# -----------------------------
# Step 5: Historical Price Data
# -----------------------------
# Fetch last 100 candlesticks for BTC/USDT (1 minute interval)
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1MINUTE, "2 hour ago UTC")

# Convert to DataFrame
df = pd.DataFrame(klines, columns=[
    "timestamp", "open", "high", "low", "close", "volume",
    "close_time", "quote_asset_volume", "number_of_trades",
    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
])

# Keep only useful columns
df = df[["timestamp", "open", "high", "low", "close", "volume"]]
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
df["close"] = df["close"].astype(float)

st.subheader("📈 BTC/USDT Price Chart (last 2 hours)")
st.line_chart(df.set_index("timestamp")["close"])

# -----------------------------
# Step 6: Live Price Updates
# -----------------------------
st.subheader("⚡ Live BTC/USDT Price")

# Create a placeholder for live updates
price_placeholder = st.empty()

# Start WebSocket Manager
twm = ThreadedWebsocketManager(api_key=API_KEY, api_secret=API_SECRET)
twm.start()

# Define callback for live ticker
def handle_message(msg):
    # Extract price from WebSocket message
    live_price = msg["c"]  # 'c' = current close price
    # Update Streamlit placeholder
    price_placeholder.metric(label="BTC/USDT", value=live_price)

# Start ticker socket
twm.start_symbol_ticker_socket(callback=handle_message, symbol="BTCUSDT")

# Keep Streamlit running
while True:
    time.sleep(1)