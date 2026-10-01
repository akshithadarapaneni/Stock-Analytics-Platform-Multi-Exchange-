# Stock Analytics Platform (Multi-Exchange)

A production-grade, beginner-to-intermediate Data Engineering and Analytics platform demonstrating a **Medallion Architecture** using **Snowflake**, **Snowpipe**, **dbt**, and **Streamlit**.

---

## Architecture Overview

```text
       CSV Files (4 Feeds)
               │
               ▼  (Snowflake PUT via upload_to_stage.py)
     Internal Stage (@BRONZE.STOCK_STAGE)
               │
               ▼  (Snowpipe auto-ingestion / refresh)
         BRONZE LAYER
    RAW_* Tables with metadata (Load TS, File Name, Row Number)
               │
               ▼  (dbt run --select silver)
         SILVER LAYER
    Cleaned Views (`stg_*`), Daily Returns, 20D Volatility, SCD2 HASH_DIFF
               │
               ▼  (dbt run --select gold)
         GOLD LAYER
    Star Schema (`DIM_DATE`, `DIM_EXCHANGE`, `DIM_COMPANY` [SCD2], `FACT_DAILY_PRICE`, `FCT_CORPORATE_ACTIONS`)
               │
               ▼  (dbt test)
      23 Data Quality Tests Passed
               │
               ▼  (dbt run --select semantic)
      SEMANTIC LAYER (`VW_*`)
               │
               ▼
     STREAMLIT DASHBOARD (http://localhost:8501)
```

---

## Repository Structure

```text
.
├── .env                              # Secure Snowflake credentials (never committed)
├── .gitignore                        # Prevents secrets & build logs from being tracked
├── README.md                         # Project documentation
├── Stock_Analytics_HLD.docx          # High-Level Design document
├── stock_star_schema_diagram.png     # Star Schema architecture diagram
├── data/
│   ├── stock_exchanges.csv               # Exchange master source file
│   ├── stock_companies.csv               # Company master source file
│   ├── stock_prices_daily.csv            # Daily OHLC price feeds source file
│   └── stock_corporate_actions.csv       # Corporate actions source file
│
├── setup_snowflake.sql               # DDL for Warehouse, DB, Schemas, Stage, RAW tables, Snowpipes, RBAC
├── upload_to_stage.py                # Ingestion helper to upload CSVs into internal stage folders
│
├── dbt_project.yml                   # dbt project definition
├── profiles.yml                      # dbt Snowflake connection profile
├── run_dbt.py                        # Reusable helper to execute dbt commands with .env
│
├── macros/
│   └── generate_schema_name.sql      # Schema naming override (BRONZE, SILVER, GOLD, SEMANTIC)
│
├── models/
│   ├── sources.yml                   # Bronze source definitions
│   ├── schema.yml                    # dbt Data Quality test assertions (23 tests)
│   ├── silver/                       # Cleaned staging views
│   │   ├── stg_exchanges.sql
│   │   ├── stg_companies.sql
│   │   ├── stg_prices_daily.sql
│   │   └── stg_corporate_actions.sql
│   ├── gold/                         # Star Schema (Facts & Dimensions)
│   │   ├── dim_date.sql
│   │   ├── dim_exchange.sql
│   │   ├── dim_company.sql           # SCD Type 2 tracking with HASH_DIFF
│   │   ├── fact_daily_price.sql      # Fact grain: 1 row / company / date / exchange
│   │   └── fct_corporate_actions.sql
│   └── semantic/                     # Analytical views consumed by Streamlit
│       ├── vw_market_overview.sql
│       ├── vw_stock_detail.sql
│       ├── vw_sector_analysis.sql
│       └── vw_screener.sql
│
├── tests/
│   └── assert_fact_daily_price_valid_ranges.sql   # Custom financial validation test
│
├── app.py                            # Streamlit main entry page
├── snowflake_db.py                   # Cached Snowflake connection helper
└── pages/                            # Interactive Streamlit dashboard pages
    ├── 1_Market_Overview.py
    ├── 2_Stock_Detail.py
    ├── 3_Sector_Exchange_Analysis.py
    └── 4_Stock_Screener.py
```

---

## How to Run the Pipeline

### 1. Ingest Data into Snowflake Internal Stage
```bash
python upload_to_stage.py
```

### 2. Run dbt Transformations
```bash
# Run Silver Staging Models
python run_dbt.py run --select silver

# Run Gold Star Schema Models (Dimensions, SCD2, Facts)
python run_dbt.py run --select gold

# Run Data Quality Tests (23 tests)
python run_dbt.py test

# Run Semantic Views
python run_dbt.py run --select semantic
```

### 3. Launch Streamlit Dashboard
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your web browser.
