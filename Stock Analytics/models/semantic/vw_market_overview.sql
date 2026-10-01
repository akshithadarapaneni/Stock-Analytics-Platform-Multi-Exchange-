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
    f.VOLUME,
    f.VWAP,
    f.DAILY_RETURN_PCT,
    f.VOLATILITY_20D,
    CASE 
        WHEN f.DAILY_RETURN_PCT > 0 THEN 'GAINER'
        WHEN f.DAILY_RETURN_PCT < 0 THEN 'LOSER'
        ELSE 'FLAT'
    END AS MOVER_TYPE
FROM {{ ref('fact_daily_price') }} f
