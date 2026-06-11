# dashboard/pages/2_Signals.py
import streamlit as st
from utils import get_signals, SYMBOLS

st.set_page_config(page_title="Signals", layout="wide")
st.title("🚦 Trading Signals")

symbol = st.sidebar.selectbox("Symbol", SYMBOLS)
limit = st.sidebar.slider("Recent Signals", 10, 200, 50)

df = get_signals(symbol, limit)

if df.empty:
    st.warning("No signals found. Run the signal generator first.")
else:
    buys = df[df["signal"] == "BUY"]
    sells = df[df["signal"] == "SELL"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Signals", len(df))
    col2.metric("BUY Signals", len(buys))
    col3.metric("SELL Signals", len(sells))

    st.markdown("---")
    st.subheader("Signal Table")

    def color_signal(val):
        color = "green" if val == "BUY" else "red"
        return f"color: {color}; font-weight: bold"

    styled = df.style.applymap(color_signal, subset=["signal"])
    st.dataframe(styled, use_container_width=True)
