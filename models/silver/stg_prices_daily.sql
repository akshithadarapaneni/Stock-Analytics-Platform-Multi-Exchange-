{{ config(materialized='view') }}

WITH base_prices AS (
    SELECT
        TRIM(PRICE_ID) AS PRICE_ID,
        TRY_TO_DATE(TRADE_DATE) AS TRADE_DATE,
        TRIM(COMPANY_ID) AS COMPANY_ID,
        TRIM(EXCHANGE_ID) AS EXCHANGE_ID,
        TRY_TO_DECIMAL(OPEN, 12, 2) AS OPEN_PRICE,
        TRY_TO_DECIMAL(HIGH, 12, 2) AS HIGH_PRICE,
        TRY_TO_DECIMAL(LOW, 12, 2) AS LOW_PRICE,
        TRY_TO_DECIMAL(CLOSE, 12, 2) AS CLOSE_PRICE,
        TRY_TO_DECIMAL(ADJ_CLOSE, 12, 2) AS ADJ_CLOSE_PRICE,
        TRY_TO_NUMBER(VOLUME) AS VOLUME,
        TRY_TO_DECIMAL(VWAP, 12, 2) AS VWAP,
        TRY_TO_TIMESTAMP_NTZ(UPDATED_AT) AS UPDATED_AT,
        METADATA_LOAD_TS,
        METADATA_FILE_NAME
    FROM {{ source('bronze', 'raw_prices_daily') }}
),

with_returns AS (
    SELECT
        *,
        LAG(CLOSE_PRICE) OVER (
            PARTITION BY COMPANY_ID 
            ORDER BY TRADE_DATE
        ) AS PREV_CLOSE_PRICE
    FROM base_prices
),

with_metrics AS (
    SELECT
        *,
        ROUND(
            ((CLOSE_PRICE - PREV_CLOSE_PRICE) / NULLIF(PREV_CLOSE_PRICE, 0)) * 100, 
            4
        ) AS DAILY_RETURN_PCT
    FROM with_returns
)

SELECT
    PRICE_ID,
    TRADE_DATE,
    COMPANY_ID,
    EXCHANGE_ID,
    OPEN_PRICE,
    HIGH_PRICE,
    LOW_PRICE,
    CLOSE_PRICE,
    ADJ_CLOSE_PRICE,
    VOLUME,
    VWAP,
    PREV_CLOSE_PRICE,
    COALESCE(DAILY_RETURN_PCT, 0.0) AS DAILY_RETURN_PCT,
    ROUND(
        COALESCE(
            STDDEV(DAILY_RETURN_PCT) OVER (
                PARTITION BY COMPANY_ID 
                ORDER BY TRADE_DATE 
                ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
            ),
            0.0
        ),
        4
    ) AS VOLATILITY_20D,
    UPDATED_AT,
    METADATA_LOAD_TS,
    METADATA_FILE_NAME
FROM with_metrics
