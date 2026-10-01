import streamlit as st
import pandas as pd
from snowflake_db import query_data

st.set_page_config(page_title="Stock Screener", layout="wide")

st.title("Stock Screener & Filter Engine")
st.markdown("Filter companies dynamically by Sector, Market Cap, Return range, and Volatility bands.")

try:
    df = query_data("SELECT * FROM SEMANTIC.VW_SCREENER")
    
    if df.empty:
        st.warning("No screener data available.")
        st.stop()

    df["LATEST_CLOSE_PRICE"] = pd.to_numeric(df["LATEST_CLOSE_PRICE"])
    df["DAILY_RETURN_PCT"] = pd.to_numeric(df["DAILY_RETURN_PCT"])
    df["VOLATILITY_20D"] = pd.to_numeric(df["VOLATILITY_20D"])
    df["LATEST_VOLUME"] = pd.to_numeric(df["LATEST_VOLUME"])

    # Sidebar / top filters
    with st.expander("Screener Filters", expanded=True):
        f_col1, f_col2, f_col3, f_col4 = st.columns(4)
        
        with f_col1:
            all_sectors = ["All"] + sorted(df["SECTOR"].dropna().unique().tolist())
            selected_sector = st.selectbox("Sector:", all_sectors)
            
        with f_col2:
            all_caps = ["All"] + sorted(df["MARKET_CAP_BAND"].dropna().unique().tolist())
            selected_cap = st.selectbox("Market Cap Band:", all_caps)

        with f_col3:
            all_bands = ["All"] + sorted(df["VOLATILITY_BAND"].dropna().unique().tolist())
            selected_band = st.selectbox("Volatility Band:", all_bands)

        with f_col4:
            min_ret = float(df["DAILY_RETURN_PCT"].min())
            max_ret = float(df["DAILY_RETURN_PCT"].max())
            ret_range = st.slider(
                "Return Range (%):",
                min_value=min_ret,
                max_value=max_ret,
                value=(min_ret, max_ret),
                step=1.0
            )

    # Apply filters
    filtered_df = df.copy()

    if selected_sector != "All":
        filtered_df = filtered_df[filtered_df["SECTOR"] == selected_sector]

    if selected_cap != "All":
        filtered_df = filtered_df[filtered_df["MARKET_CAP_BAND"] == selected_cap]

    if selected_band != "All":
        filtered_df = filtered_df[filtered_df["VOLATILITY_BAND"] == selected_band]

    filtered_df = filtered_df[
        (filtered_df["DAILY_RETURN_PCT"] >= ret_range[0]) & 
        (filtered_df["DAILY_RETURN_PCT"] <= ret_range[1])
    ]

    st.markdown(f"**Found {len(filtered_df)} matching companies**")

    # Display table
    display_df = filtered_df[[
        "TICKER", "COMPANY_NAME", "SECTOR", "INDUSTRY", "COUNTRY", 
        "EXCHANGE_CODE", "LATEST_CLOSE_PRICE", "DAILY_RETURN_PCT", 
        "VOLATILITY_20D", "VOLATILITY_BAND", "LATEST_VOLUME"
    ]].rename(columns={
        "TICKER": "Ticker",
        "COMPANY_NAME": "Company",
        "SECTOR": "Sector",
        "INDUSTRY": "Industry",
        "COUNTRY": "Country",
        "EXCHANGE_CODE": "Exchange",
        "LATEST_CLOSE_PRICE": "Latest Close",
        "DAILY_RETURN_PCT": "Return (%)",
        "VOLATILITY_20D": "20D Vol (%)",
        "VOLATILITY_BAND": "Volatility Band",
        "LATEST_VOLUME": "Volume"
    })

    st.dataframe(
        display_df.style.format({
            "Latest Close": "{:,.2f}",
            "Return (%)": "{:+.2f}%",
            "20D Vol (%)": "{:.2f}%",
            "Volume": "{:,.0f}"
        }),
        width=1200
    )

    # Export button
    csv_data = display_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Export Filtered Screener (CSV)",
        data=csv_data,
        file_name="screener_results.csv",
        mime="text/csv"
    )

except Exception as e:
    st.error(f"Error running Stock Screener: {e}")
