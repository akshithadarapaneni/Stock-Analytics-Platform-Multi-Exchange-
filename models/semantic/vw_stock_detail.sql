{{ config(materialized='view') }}

SELECT
    f.PRICE_FACT_SK,
    f.TRADE_DATE,
    f.COMPANY_ID,
    f.TICKER,
    f.COMPANY_NAME,
    f.SECTOR,
    f.EXCHANGE_CODE,
    f.OPEN_PRICE,
    f.HIGH_PRICE,
    f.LOW_PRICE,
    f.CLOSE_PRICE,
    f.ADJ_CLOSE_PRICE,
    f.VOLUME,
    f.VWAP,
    f.DAILY_RETURN_PCT,
    f.VOLATILITY_20D,
    ca.ACTION_TYPE AS CORPORATE_ACTION_TYPE,
    ca.ACTION_VALUE AS CORPORATE_ACTION_VALUE,
    ca.RATIO AS CORPORATE_ACTION_RATIO
FROM {{ ref('fact_daily_price') }} f
LEFT JOIN {{ ref('fct_corporate_actions') }} ca
    ON f.COMPANY_ID = ca.COMPANY_ID 
    AND f.TRADE_DATE = ca.EX_DATE
