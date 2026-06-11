# dashboard/pages/3_Backtest.py
import streamlit as st
from utils import get_backtest_results, SYMBOLS

st.set_page_config(page_title="Backtest", layout="wide")
st.title("🔬 Backtest Results")

symbol = st.sidebar.selectbox("Symbol", SYMBOLS)

df = get_backtest_results(symbol)

if df.empty:
    st.warning("No backtest results found. Run the backtester first.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trades", len(df))
    col2.metric("Win Rate", f"{(df['pnl'] > 0).mean() * 100:.1f}%")
    col3.metric("Total PnL", f"{df['pnl'].sum():.2f} USDT")
    col4.metric("Avg PnL", f"{df['pnl'].mean():.2f} USDT")

    st.markdown("---")

    st.subheader("Cumulative PnL")
    st.line_chart(df.set_index("exit_time")["pnl"].cumsum())

    st.subheader("Trade History")

    def color_pnl(val):
        color = "green" if val > 0 else "red"
        return f"color: {color}; font-weight: bold"

    styled = df.style.applymap(color_pnl, subset=["pnl"])
    st.dataframe(styled, use_container_width=True)

