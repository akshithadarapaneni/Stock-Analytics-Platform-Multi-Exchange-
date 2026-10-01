{{ config(materialized='view') }}

WITH latest_prices AS (
    SELECT
        COMPANY_ID,
        TICKER,
        COMPANY_NAME,
        SECTOR,
        EXCHANGE_CODE,
        TRADE_DATE,
        CLOSE_PRICE,
        VOLUME,
        DAILY_RETURN_PCT,
        VOLATILITY_20D,
        ROW_NUMBER() OVER (PARTITION BY COMPANY_ID ORDER BY TRADE_DATE DESC) AS rn
    FROM {{ ref('fact_daily_price') }}
)

SELECT
    lp.COMPANY_ID,
    lp.TICKER,
    lp.COMPANY_NAME,
    c.MARKET_CAP_BAND,
    lp.SECTOR,
    c.INDUSTRY,
    c.COUNTRY,
    lp.EXCHANGE_CODE,
    lp.TRADE_DATE AS LATEST_TRADE_DATE,
    lp.CLOSE_PRICE AS LATEST_CLOSE_PRICE,
    lp.DAILY_RETURN_PCT,
    lp.VOLATILITY_20D,
    lp.VOLUME AS LATEST_VOLUME,
    CASE
        WHEN lp.VOLATILITY_20D < 10 THEN 'LOW'
        WHEN lp.VOLATILITY_20D BETWEEN 10 AND 50 THEN 'MEDIUM'
        ELSE 'HIGH'
    END AS VOLATILITY_BAND
FROM latest_prices lp
INNER JOIN {{ ref('dim_company') }} c
    ON lp.COMPANY_ID = c.COMPANY_ID AND c.IS_CURRENT = TRUE
WHERE lp.rn = 1
