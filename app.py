# app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(layout="wide")
st.title("📊 Stock Analysis Dashboard (India Pro)")

st.info("💡 Search stocks like Reliance, TCS, Infosys")

# -------- LOAD NSE STOCK LIST --------
@st.cache_data
def load_stocks():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    return df[['SYMBOL', 'NAME OF COMPANY']]

stocks_df = load_stocks()

# -------- AUTOCOMPLETE SEARCH --------
search = st.text_input("🔍 Search Stock (Name or Symbol)")

filtered_df = stocks_df[
    stocks_df['SYMBOL'].str.contains(search.upper(), na=False) |
    stocks_df['NAME OF COMPANY'].str.contains(search, case=False, na=False)
]

filtered_df = filtered_df.head(20)

if not filtered_df.empty:

    options = [
        f"{row['SYMBOL']} - {row['NAME OF COMPANY']}"
        for _, row in filtered_df.iterrows()
    ]

    selected = st.selectbox("Select Stock", options)

    ticker_symbol = selected.split(" - ")[0]
    ticker = ticker_symbol + ".NS"

    st.success(f"Selected: {selected}")

    # -------- COMPANY INFO --------
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        industry = info.get("industry", "N/A")
        sector = info.get("sector", "N/A")

        col1, col2 = st.columns(2)
        col1.metric("🏭 Industry", industry)
        col2.metric("🏢 Sector", sector)

    except:
        st.warning("⚠️ Industry data not available")

else:
    st.warning("No matching stocks found")
    st.stop()

# -------- TIMEFRAME --------
timeframe = st.selectbox(
    "Select Timeframe",
    ["5m", "15m", "1h", "1d", "1wk", "1mo"]
)

if timeframe in ["5m", "15m"]:
    period = "5d"
elif timeframe == "1h":
    period = "1mo"
elif timeframe == "1d":
    period = "1y"
elif timeframe == "1wk":
    period = "5y"
else:
    period = "10y"

# -------- FETCH DATA --------
df = yf.download(ticker, period=period, interval=timeframe)

if df.empty:
    st.error("❌ No data found")
    st.stop()

# -------- FIX MULTIINDEX --------
if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[0] for col in df.columns]

df = df.reset_index()

# -------- PRICE CHART --------
st.subheader("📈 Price Chart")

fig = px.line(df, x=df.columns[0], y="Close", title="Price Trend")
st.plotly_chart(fig, use_container_width=True)

# -------- TECHNICAL ANALYSIS --------
st.subheader("📊 Technical Analysis")

df['Return'] = df['Close'].pct_change()
df['Volatility'] = df['Return'].rolling(10).std()
df['Momentum'] = df['Close'] / df['Close'].shift(10)

latest = df.iloc[-1]

trend = "Bullish" if latest['Momentum'] > 1 else "Bearish"
volatility = "High" if latest['Volatility'] > df['Volatility'].mean() else "Low"

col1, col2, col3 = st.columns(3)
col1.metric("Trend", trend)
col2.metric("Volatility", volatility)
col3.metric("Price (₹)", f"{latest['Close']:.2f}")

# -------- AI MODEL --------
df['Target'] = df['Return'].shift(-1)
df.dropna(inplace=True)

if len(df) > 50:
    X = df[['Momentum', 'Volatility']]
    y = df['Target']

    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)

    pred = model.predict(X.tail(1))[0]

    st.subheader("🤖 AI Prediction")

    if pred > 0:
        st.success(f"📈 Bullish ({pred:.4f})")
    else:
        st.error(f"📉 Bearish ({pred:.4f})")

# -------- FORMATTER --------
def to_thousand_crore(value):
    if value is None:
        return "N/A"
    return f"₹{value / 1e10:.2f}K Cr"

def safe_get(info, key):
    val = info.get(key, None)
    return val if val not in [None, "None"] else None

# -------- FUNDAMENTAL ANALYSIS --------
st.subheader("📑 Fundamental Analysis (₹ Thousand Crores)")

try:
    if not info or len(info) < 5:
        st.warning("⚠️ Fundamental data not available")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("Market Cap", to_thousand_crore(safe_get(info, "marketCap")))
        col2.metric("Revenue", to_thousand_crore(safe_get(info, "totalRevenue")))
        col3.metric("Net Profit", to_thousand_crore(safe_get(info, "netIncomeToCommon")))

        col1.metric("P/E Ratio", safe_get(info, "trailingPE") or "N/A")
        col2.metric("EPS (₹)", safe_get(info, "trailingEps") or "N/A")
        col3.metric("Debt/Equity", safe_get(info, "debtToEquity") or "N/A")

except:
    st.warning("⚠️ Could not fetch fundamental data")

# -------- MULTI STOCK SCANNER --------
st.subheader("🏆 Best Stock Finder")

multi_input = st.text_input(
    "Enter stocks (comma separated)",
    "RELIANCE, TCS, INFY"
)

stock_list = []
for s in multi_input.split(","):
    s = s.strip().upper()
    if not s.endswith(".NS"):
        s += ".NS"
    stock_list.append(s)

if st.button("Scan Stocks"):

    results = []

    for stock in stock_list:
        temp = yf.download(stock, period="6mo", interval="1d")

        if temp.empty:
            continue

        if isinstance(temp.columns, pd.MultiIndex):
            temp.columns = [col[0] for col in temp.columns]

        temp['Return'] = temp['Close'].pct_change()
        temp['Momentum'] = temp['Close'] / temp['Close'].shift(10)

        temp['Target'] = temp['Return'].shift(-1)
        temp.dropna(inplace=True)

        if len(temp) < 50:
            continue

        X_temp = temp[['Momentum']]
        y_temp = temp['Target']

        model.fit(X_temp, y_temp)

        pred = model.predict(X_temp.tail(1))[0]

        results.append((stock, pred))

    if results:
        ranked = sorted(results, key=lambda x: x[1], reverse=True)

        st.dataframe(pd.DataFrame(ranked, columns=["Stock", "Prediction"]))
        st.success(f"🏆 Top Pick: {ranked[0][0]}")
    else:
        st.error("No valid stocks found")