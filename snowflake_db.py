import os
import streamlit as st
import pandas as pd
import snowflake.connector
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

@st.cache_resource
def get_connection():
    """Establishes and caches the Snowflake connection using environment variables."""
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "STOCK_ANALYTICS_WH"),
        database=os.getenv("SNOWFLAKE_DATABASE", "STOCK_ANALYTICS_DB"),
        schema="SEMANTIC",
        role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
    )

@st.cache_data(ttl=120)
def query_data(sql_query: str) -> pd.DataFrame:
    """Executes a SELECT query on Snowflake SEMANTIC views and returns a Pandas DataFrame."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql_query)
        df = cur.fetch_pandas_all()
    return df
