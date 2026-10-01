import streamlit as st
import pandas as pd
from snowflake_db import query_data

st.set_page_config(
    page_title="Stock Analytics Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Multi-Exchange Stock Analytics Platform")
st.markdown("### Production-Grade Medallion Data Engineering & Analytics Pipeline")

st.markdown("""
Welcome to the **Multi-Exchange Stock Analytics Platform**.
This platform ingests daily price feeds, reference masters, and corporate action events 
across global exchanges using Snowflake, dbt, and Streamlit.
""")

# High-level pipeline metrics
col1, col2, col3, col4 = st.columns(4)

try:
    overview_df = query_data("SELECT * FROM SEMANTIC.VW_MARKET_OVERVIEW")
    screener_df = query_data("SELECT * FROM SEMANTIC.VW_SCREENER")
    
    total_companies = screener_df["COMPANY_ID"].nunique() if not screener_df.empty else 0
    total_exchanges = overview_df["EXCHANGE_CODE"].nunique() if not overview_df.empty else 0
    total_records = len(overview_df)
    total_volume = overview_df["VOLUME"].sum() if not overview_df.empty else 0

    col1.metric("Tracked Companies", f"{total_companies}")
    col2.metric("Supported Exchanges", f"{total_exchanges}")
    col3.metric("Price Feed Records", f"{total_records}")
    col4.metric("Total Volume Traded", f"{total_volume:,.0f}")
except Exception as e:
    st.error(f"Error connecting to Snowflake Semantic layer: {e}")

st.divider()

col_left, col_right = st.columns([1.2, 0.8])

with col_left:
    st.subheader("Architecture Overview")
    st.markdown("""
    * **Bronze Layer (RAW)**: Automated ingestion via **Snowpipe** into `RAW_EXCHANGES`, `RAW_COMPANIES`, `RAW_PRICES_DAILY`, and `RAW_CORPORATE_ACTIONS` with file metadata tracking.
    * **Silver Layer (Staging)**: Cleaned, standardized, and typed views transformed by **dbt** (`stg_*`) with returns and 20D volatility calculation.
    * **Gold Layer (Star Schema)**: Business-ready facts and dimensions:
        * `DIM_COMPANY` with **SCD Type 2** historical tracking using MD5 `HASH_DIFF`.
        * `DIM_EXCHANGE` (Type 1) & `DIM_DATE` (Calendar spine).
        * `FACT_DAILY_PRICE` with dimensional surrogate keys.
        * `FCT_CORPORATE_ACTIONS` for splits, bonuses, dividends, and buybacks.
    * **Semantic Layer**: Secure analytical views (`SEMANTIC.VW_*`) consumed directly by this Streamlit application.
    """)

with col_right:
    st.subheader("Explore Dashboard Pages")
    st.info("""
    Use the left sidebar navigation to explore:
    
    1. **Market Overview**: Top movers, volume leaders, and sector aggregates.
    2. **Stock Detail**: Interactive price history, returns, volume, volatility, and corporate actions.
    3. **Sector / Exchange Analysis**: Performance and volume breakdown by market sector and exchange.
    4. **Stock Screener**: Interactive stock filtering by sector, market cap, and volatility bands with CSV export.
    """)
