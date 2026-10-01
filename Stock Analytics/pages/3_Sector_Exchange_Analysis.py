import streamlit as st
import pandas as pd
import plotly.express as px
from snowflake_db import query_data

st.set_page_config(page_title="Sector & Exchange Analysis", layout="wide")

st.title("Sector & Exchange Performance Analysis")
st.markdown("Macro-level cross-sectional analytics across market sectors and global stock exchanges.")

try:
    df = query_data("SELECT * FROM SEMANTIC.VW_SECTOR_ANALYSIS")
    
    if df.empty:
        st.warning("No sector/exchange data available.")
        st.stop()

    num_cols = ["TOTAL_COMPANIES", "TOTAL_TRADING_RECORDS", "AVG_CLOSE_PRICE", "AVG_DAILY_RETURN_PCT", "AVG_VOLATILITY_20D", "TOTAL_VOLUME", "SECTOR_VWAP"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col])

    col1, col2 = st.columns(2)

    # Sector Total Volume
    with col1:
        st.subheader("Trading Volume by Sector")
        sector_vol = df.groupby("SECTOR")["TOTAL_VOLUME"].sum().reset_index()
        fig_sv = px.bar(
            sector_vol,
            x="SECTOR",
            y="TOTAL_VOLUME",
            color="SECTOR",
            title="Total Shares Traded per Sector",
            labels={"TOTAL_VOLUME": "Total Volume", "SECTOR": "Sector"}
        )
        st.plotly_chart(fig_sv)

    # Sector Volatility
    with col2:
        st.subheader("Average Volatility by Sector")
        sector_volat = df.groupby("SECTOR")["AVG_VOLATILITY_20D"].mean().reset_index()
        fig_svol = px.bar(
            sector_volat,
            x="SECTOR",
            y="AVG_VOLATILITY_20D",
            color="AVG_VOLATILITY_20D",
            color_continuous_scale="Oranges",
            title="Average 20D Volatility (%) per Sector",
            labels={"AVG_VOLATILITY_20D": "Avg Volatility (%)", "SECTOR": "Sector"}
        )
        st.plotly_chart(fig_svol)

    st.divider()

    col3, col4 = st.columns(2)

    # Exchange comparison
    with col3:
        st.subheader("Exchange Activity")
        exch_df = df.groupby("EXCHANGE_CODE").agg({
            "TOTAL_VOLUME": "sum",
            "TOTAL_COMPANIES": "sum"
        }).reset_index()
        fig_exch = px.pie(
            exch_df,
            names="EXCHANGE_CODE",
            values="TOTAL_VOLUME",
            hole=0.35,
            title="Volume Share by Exchange"
        )
        st.plotly_chart(fig_exch)

    with col4:
        st.subheader("Sector VWAP Comparison")
        fig_vwap = px.bar(
            df,
            x="SECTOR",
            y="SECTOR_VWAP",
            color="EXCHANGE_CODE",
            barmode="group",
            title="Sector Benchmark VWAP by Exchange",
            labels={"SECTOR_VWAP": "VWAP Price", "SECTOR": "Sector", "EXCHANGE_CODE": "Exchange"}
        )
        st.plotly_chart(fig_vwap)

    st.subheader("Sector & Exchange Aggregated Metrics")
    st.dataframe(df, width=1200)

except Exception as e:
    st.error(f"Error loading Sector/Exchange analysis: {e}")
