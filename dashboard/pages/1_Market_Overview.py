# dashboard/pages/1_Market_Overview.py
import streamlit as st
import plotly.graph_objects as go
from utils import get_ohlcv, SYMBOLS

st.set_page_config(page_title="Market Overview", layout="wide")
st.title("📊 Market Overview")

symbol = st.sidebar.selectbox("Symbol", SYMBOLS)
limit = st.sidebar.slider("Candles", 50, 500, 200)

df = get_ohlcv(symbol, limit)

if df.empty:
    st.warning("No data found. Run the data collector first.")
else:
    fig = go.Figure(data=[go.Candlestick(
        x=df["open_time"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"]
    )])
    fig.update_layout(
        title=f"{symbol} Price Chart",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        xaxis_rangeslider_visible=False,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Volume")
    st.bar_chart(df.set_index("open_time")["volume"])

    st.subheader("Raw Data")
    st.dataframe(df.tail(50), use_container_width=True)
