{{ config(materialized='table') }}

SELECT
    MD5(EXCHANGE_ID) AS EXCHANGE_SK,
    EXCHANGE_ID,
    EXCHANGE_CODE,
    COUNTRY,
    CURRENCY,
    TIMEZONE,
    MARKET_TYPE,
    STATUS,
    ESTABLISHED_DATE,
    UPDATED_AT,
    CURRENT_TIMESTAMP() AS DW_INSERT_TS
FROM {{ ref('stg_exchanges') }}
