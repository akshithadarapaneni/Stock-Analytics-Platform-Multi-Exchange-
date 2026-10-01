{{ config(materialized='table') }}

SELECT
    MD5(CONCAT(ca.ACTION_ID, '||', COALESCE(ca.EX_DATE::VARCHAR, ''))) AS ACTION_FACT_SK,
    c.COMPANY_SK,
    ca.ACTION_ID,
    ca.COMPANY_ID,
    ca.TICKER,
    c.COMPANY_NAME,
    c.SECTOR,
    ca.ACTION_TYPE,
    ca.EX_DATE,
    ca.RECORD_DATE,
    ca.PAY_DATE,
    ca.ACTION_VALUE,
    ca.RATIO,
    ca.CURRENCY,
    ca.STATUS,
    CURRENT_TIMESTAMP() AS DW_INSERT_TS
FROM {{ ref('stg_corporate_actions') }} ca
LEFT JOIN {{ ref('dim_company') }} c
    ON ca.COMPANY_ID = c.COMPANY_ID AND c.IS_CURRENT = TRUE
