import streamlit as st
import pandas as pd
import plotly.express as px
from snowflake_db import query_data

st.set_page_config(page_title="Market Overview", layout="wide")

st.title("Market Overview")
st.markdown("Daily market movements, top gainers, losers, volume leaders, and sector aggregates.")

try:
    df = query_data("SELECT * FROM SEMANTIC.VW_MARKET_OVERVIEW")
    
    if df.empty:
        st.warning("No market data available.")
        st.stop()

    # Convert numeric columns explicitly
    df["CLOSE_PRICE"] = pd.to_numeric(df["CLOSE_PRICE"])
    df["DAILY_RETURN_PCT"] = pd.to_numeric(df["DAILY_RETURN_PCT"])
    df["VOLUME"] = pd.to_numeric(df["VOLUME"])

    col1, col2 = st.columns(2)

    # Top Gainers & Losers
    with col1:
        st.subheader("Top Gainers (% Return)")
        gainers = df[df["DAILY_RETURN_PCT"] > 0].sort_values(by="DAILY_RETURN_PCT", ascending=False).head(5)
        if not gainers.empty:
            fig_g = px.bar(
                gainers,
                x="DAILY_RETURN_PCT",
                y="TICKER",
                orientation="h",
                color="DAILY_RETURN_PCT",
                color_continuous_scale="Greens",
                text="DAILY_RETURN_PCT",
                labels={"DAILY_RETURN_PCT": "Return %", "TICKER": "Company"},
                title="Top 5 Gainers"
            )
            fig_g.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            fig_g.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            st.plotly_chart(fig_g)
        else:
            st.info("No positive movers in this feed.")

    with col2:
        st.subheader("Top Losers (% Return)")
        losers = df[df["DAILY_RETURN_PCT"] < 0].sort_values(by="DAILY_RETURN_PCT", ascending=True).head(5)
        if not losers.empty:
            fig_l = px.bar(
                losers,
                x="DAILY_RETURN_PCT",
                y="TICKER",
                orientation="h",
                color="DAILY_RETURN_PCT",
                color_continuous_scale="Reds_r",
                text="DAILY_RETURN_PCT",
                labels={"DAILY_RETURN_PCT": "Return %", "TICKER": "Company"},
                title="Top 5 Losers"
            )
            fig_l.update_layout(yaxis={'categoryorder':'total descending'}, showlegend=False)
            fig_l.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            st.plotly_chart(fig_l)
        else:
            st.info("No negative movers in this feed.")

    st.divider()

    col3, col4 = st.columns(2)

    # Volume Leaders
    with col3:
        st.subheader("Volume Leaders")
        vol_leaders = df.groupby(["TICKER", "COMPANY_NAME"])["VOLUME"].sum().reset_index()
        vol_leaders = vol_leaders.sort_values(by="VOLUME", ascending=False).head(7)
        fig_v = px.bar(
            vol_leaders,
            x="TICKER",
            y="VOLUME",
            color="VOLUME",
            color_continuous_scale="Viridis",
            labels={"VOLUME": "Total Volume Traded", "TICKER": "Stock"},
            title="Most Active Stocks by Trading Volume"
        )
        st.plotly_chart(fig_v)

    # Sector Breakdown
    with col4:
        st.subheader("Sector Distribution")
        sector_counts = df.groupby("SECTOR")["PRICE_FACT_SK"].count().reset_index()
        sector_counts.columns = ["Sector", "Feed Count"]
        fig_s = px.pie(
            sector_counts,
            names="Sector",
            values="Feed Count",
            hole=0.4,
            title="Trading Feeds by Sector"
        )
        st.plotly_chart(fig_s)

    # Detailed table
    st.subheader("Market Feeds Snapshot")
    st.dataframe(
        df[["TRADE_DATE", "TICKER", "COMPANY_NAME", "SECTOR", "EXCHANGE_CODE", "CLOSE_PRICE", "DAILY_RETURN_PCT", "VOLUME"]].rename(
            columns={
                "TRADE_DATE": "Date",
                "TICKER": "Ticker",
                "COMPANY_NAME": "Company",
                "SECTOR": "Sector",
                "EXCHANGE_CODE": "Exchange",
                "CLOSE_PRICE": "Close ($/₹)",
                "DAILY_RETURN_PCT": "Return (%)",
                "VOLUME": "Volume"
            }
        ),
        width=1200
    )

except Exception as e:
    st.error(f"Error loading Market Overview: {e}")
