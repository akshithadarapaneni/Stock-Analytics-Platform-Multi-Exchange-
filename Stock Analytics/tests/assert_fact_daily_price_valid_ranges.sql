-- Custom Data Quality Check:
-- Checks that HIGH price is at least MAX(OPEN, CLOSE),
-- LOW price is at most MIN(OPEN, CLOSE),
-- and VOLUME is non-negative.
-- Any returned rows represent a failure.

SELECT
    PRICE_FACT_SK,
    PRICE_ID,
    TRADE_DATE,
    OPEN_PRICE,
    HIGH_PRICE,
    LOW_PRICE,
    CLOSE_PRICE,
    VOLUME
FROM {{ ref('fact_daily_price') }}
WHERE HIGH_PRICE < OPEN_PRICE
   OR HIGH_PRICE < CLOSE_PRICE
   OR LOW_PRICE > OPEN_PRICE
   OR LOW_PRICE > CLOSE_PRICE
   OR VOLUME < 0
