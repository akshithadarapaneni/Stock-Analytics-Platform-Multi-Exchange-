import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from snowflake_db import query_data

st.set_page_config(page_title="Stock Detail", layout="wide")

st.title("Stock Detail & Technical Analytics")
st.markdown("Detailed price trends, daily returns, rolling 20D volatility, volume, and corporate action events.")

try:
    df = query_data("SELECT * FROM SEMANTIC.VW_STOCK_DETAIL ORDER BY TRADE_DATE ASC")
    
    if df.empty:
        st.warning("No stock detail data found.")
        st.stop()

    # Numeric conversion
    num_cols = ["OPEN_PRICE", "HIGH_PRICE", "LOW_PRICE", "CLOSE_PRICE", "VOLUME", "VWAP", "DAILY_RETURN_PCT", "VOLATILITY_20D"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col])

    # Stock selector
    stocks = sorted(df["TICKER"].unique())
    selected_stock = st.selectbox("Select a Ticker / Company:", stocks)

    stock_df = df[df["TICKER"] == selected_stock].sort_values(by="TRADE_DATE")
    
    if stock_df.empty:
        st.info(f"No records found for {selected_stock}.")
        st.stop()

    company_name = stock_df["COMPANY_NAME"].iloc[0]
    sector = stock_df["SECTOR"].iloc[0]
    exchange = stock_df["EXCHANGE_CODE"].iloc[0]

    st.subheader(f"{company_name} ({selected_stock}) — {exchange} | {sector}")

    # Top KPI row (latest available record)
    latest = stock_df.iloc[-1]
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Latest Close", f"{latest['CLOSE_PRICE']:,.2f}")
    kpi2.metric("Daily Return", f"{latest['DAILY_RETURN_PCT']:.2f}%")
    kpi3.metric("20D Volatility", f"{latest['VOLATILITY_20D']:.2f}%")
    kpi4.metric("Trading Volume", f"{latest['VOLUME']:,.0f}")
    kpi5.metric("VWAP", f"{latest['VWAP']:,.2f}")

    st.divider()

    # Candlestick / OHLC Chart or Line Chart
    tab1, tab2 = st.tabs(["Price Action & Volume", "Return & Volatility Trends"])

    with tab1:
        fig_candle = go.Figure()
        fig_candle.add_trace(go.Candlestick(
            x=stock_df["TRADE_DATE"],
            open=stock_df["OPEN_PRICE"],
            high=stock_df["HIGH_PRICE"],
            low=stock_df["LOW_PRICE"],
            close=stock_df["CLOSE_PRICE"],
            name="OHLC"
        ))
        fig_candle.update_layout(
            title=f"{selected_stock} Daily Price Action (OHLC)",
            xaxis_title="Trading Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False
        )
        st.plotly_chart(fig_candle)

        # Volume Sub-chart
        fig_vol = px.bar(
            stock_df,
            x="TRADE_DATE",
            y="VOLUME",
            title=f"{selected_stock} Daily Trading Volume",
            labels={"VOLUME": "Volume", "TRADE_DATE": "Date"}
        )
        st.plotly_chart(fig_vol)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            fig_ret = px.line(
                stock_df,
                x="TRADE_DATE",
                y="DAILY_RETURN_PCT",
                markers=True,
                title="Daily Return (%) Over Time",
                labels={"DAILY_RETURN_PCT": "Return %", "TRADE_DATE": "Date"}
            )
            fig_ret.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig_ret)

        with c2:
            fig_volat = px.line(
                stock_df,
                x="TRADE_DATE",
                y="VOLATILITY_20D",
                markers=True,
                line_shape="spline",
                title="Rolling 20-Day Volatility (%)",
                labels={"VOLATILITY_20D": "20D Volatility (%)", "TRADE_DATE": "Date"}
            )
            st.plotly_chart(fig_volat)

    st.divider()

    # Corporate actions for this company
    st.subheader(f"Corporate Actions & Events: {selected_stock}")
    ca_query = f"""
        SELECT ACTION_ID, ACTION_TYPE, EX_DATE, RECORD_DATE, PAY_DATE, ACTION_VALUE, RATIO, CURRENCY, STATUS
        FROM GOLD.FCT_CORPORATE_ACTIONS
        WHERE TICKER = '{selected_stock}'
        ORDER BY EX_DATE DESC
    """
    ca_df = query_data(ca_query)
    if not ca_df.empty:
        st.dataframe(ca_df, width=1200)
    else:
        st.info(f"No corporate action announcements recorded for {selected_stock}.")

except Exception as e:
    st.error(f"Error loading stock details: {e}")
