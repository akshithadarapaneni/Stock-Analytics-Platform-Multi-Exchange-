{{ config(materialized='table') }}

SELECT
    MD5(CONCAT_WS('||', p.PRICE_ID, p.TRADE_DATE, p.COMPANY_ID, p.EXCHANGE_ID)) AS PRICE_FACT_SK,
    d.DATE_SK,
    c.COMPANY_SK,
    e.EXCHANGE_SK,
    p.PRICE_ID,
    p.TRADE_DATE,
    p.COMPANY_ID,
    c.TICKER,
    c.COMPANY_NAME,
    c.SECTOR,
    p.EXCHANGE_ID,
    e.EXCHANGE_CODE,
    p.OPEN_PRICE,
    p.HIGH_PRICE,
    p.LOW_PRICE,
    p.CLOSE_PRICE,
    p.ADJ_CLOSE_PRICE,
    p.VOLUME,
    p.VWAP,
    p.DAILY_RETURN_PCT,
    p.VOLATILITY_20D,
    CURRENT_TIMESTAMP() AS DW_INSERT_TS
FROM {{ ref('stg_prices_daily') }} p
INNER JOIN {{ ref('dim_date') }} d
    ON p.TRADE_DATE = d.CALENDAR_DATE
INNER JOIN {{ ref('dim_company') }} c
    ON p.COMPANY_ID = c.COMPANY_ID AND c.IS_CURRENT = TRUE
INNER JOIN {{ ref('dim_exchange') }} e
    ON p.EXCHANGE_ID = e.EXCHANGE_ID
