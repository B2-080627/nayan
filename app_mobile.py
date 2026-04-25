import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(layout="wide")
st.title("📊 Stock Analysis Dashboard (India Pro)")

# -------- SIDEBAR CONTROLS (MOBILE FRIENDLY) --------
st.sidebar.title("⚙️ Controls")

search = st.sidebar.text_input("🔍 Search Stock")

timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    ["5m", "15m", "1h", "1d", "1wk", "1mo"]
)

# -------- LOAD NSE STOCK LIST --------
@st.cache_data
def load_stocks():
    url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
    df = pd.read_csv(url)
    return df[['SYMBOL', 'NAME OF COMPANY']]

stocks_df = load_stocks()

# -------- AUTOCOMPLETE --------
filtered_df = stocks_df[
    stocks_df['SYMBOL'].str.contains(search.upper(), na=False) |
    stocks_df['NAME OF COMPANY'].str.contains(search, case=False, na=False)
].head(20)

if filtered_df.empty:
    st.warning("No matching stocks found")
    st.stop()

options = [
    f"{row['SYMBOL']} - {row['NAME OF COMPANY']}"
    for _, row in filtered_df.iterrows()
]

selected = st.selectbox("📌 Select Stock", options, key="stock_select")

ticker_symbol = selected.split(" - ")[0]
ticker = ticker_symbol + ".NS"

# -------- TIMEFRAME LOGIC --------
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

# -------- DATA --------
df = yf.download(ticker, period=period, interval=timeframe)

if df.empty:
    st.error("❌ No data found")
    st.stop()

if isinstance(df.columns, pd.MultiIndex):
    df.columns = [col[0] for col in df.columns]

df = df.reset_index()

# -------- COMPANY INFO --------
stock = yf.Ticker(ticker)
info = stock.info

st.subheader("🏢 Company Info")
st.write("**Industry:**", info.get("industry", "N/A"))
st.write("**Sector:**", info.get("sector", "N/A"))

# -------- PRICE CHART --------
st.subheader("📈 Price Chart")

fig = px.line(df, x=df.columns[0], y="Close")

fig.update_layout(
    height=400,
    margin=dict(l=10, r=10, t=30, b=10)
)

st.plotly_chart(fig, use_container_width=True)

# -------- TECHNICAL --------
with st.expander("📊 Technical Analysis"):

    df['Return'] = df['Close'].pct_change()
    df['Volatility'] = df['Return'].rolling(10).std()
    df['Momentum'] = df['Close'] / df['Close'].shift(10)

    latest = df.iloc[-1]

    trend = "Bullish" if latest['Momentum'] > 1 else "Bearish"
    volatility = "High" if latest['Volatility'] > df['Volatility'].mean() else "Low"

    st.metric("Trend", trend)
    st.metric("Volatility", volatility)
    st.metric("Price (₹)", f"{latest['Close']:.2f}")

# -------- AI --------
with st.expander("🤖 AI Prediction"):

    df['Target'] = df['Return'].shift(-1)
    df.dropna(inplace=True)

    if len(df) > 50:
        X = df[['Momentum', 'Volatility']]
        y = df['Target']

        model = RandomForestRegressor(n_estimators=100)
        model.fit(X, y)

        pred = model.predict(X.tail(1))[0]

        if pred > 0:
            st.success(f"📈 Bullish ({pred:.4f})")
        else:
            st.error(f"📉 Bearish ({pred:.4f})")

# -------- FUNDAMENTALS --------
with st.expander("📑 Fundamental Analysis"):

    def to_thousand_crore(value):
        if value is None:
            return "N/A"
        return f"₹{value / 1e10:.2f}K Cr"

    st.write("Market Cap:", to_thousand_crore(info.get("marketCap")))
    st.write("Revenue:", to_thousand_crore(info.get("totalRevenue")))
    st.write("Net Profit:", to_thousand_crore(info.get("netIncomeToCommon")))
    st.write("P/E:", info.get("trailingPE", "N/A"))

# -------- STOCK SCANNER --------
st.subheader("🏆 Best Stock Finder")

multi_input = st.text_input(
    "Enter stocks (comma separated)",
    "RELIANCE, TCS, INFY"
)

if st.button("🚀 Scan Stocks", use_container_width=True):

    results = []

    for stock in multi_input.split(","):
        stock = stock.strip().upper() + ".NS"

        temp = yf.download(stock, period="6mo")

        if temp.empty:
            continue

        temp['Return'] = temp['Close'].pct_change()
        temp['Momentum'] = temp['Close'] / temp['Close'].shift(10)

        temp.dropna(inplace=True)

        if len(temp) < 50:
            continue

        model = RandomForestRegressor()
        model.fit(temp[['Momentum']], temp['Return'])

        pred = model.predict(temp[['Momentum']].tail(1))[0]

        results.append((stock, pred))

    if results:
        ranked = sorted(results, key=lambda x: x[1], reverse=True)
        st.dataframe(pd.DataFrame(ranked, columns=["Stock", "Prediction"]))
        st.success(f"🏆 Top Pick: {ranked[0][0]}")