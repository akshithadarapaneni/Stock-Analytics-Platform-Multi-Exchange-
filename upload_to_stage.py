import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database="STOCK_ANALYTICS_DB",
    schema="BRONZE",
    role=os.getenv("SNOWFLAKE_ROLE")
)
cur = conn.cursor()

# File mapping: local CSV -> stage subfolder
files_to_upload = [
    ("stock_exchanges.csv", "exchanges"),
    ("stock_companies.csv", "companies"),
    ("stock_prices_daily.csv", "prices_daily"),
    ("stock_corporate_actions.csv", "corporate_actions")
]

base_dir = os.path.abspath(os.path.dirname(__file__)).replace("\\", "/")

print("Uploading files to Snowflake Internal Stage @BRONZE.STOCK_STAGE...\n")

for filename, subfolder in files_to_upload:
    local_path = f"{base_dir}/data/{filename}"
    stage_path = f"@STOCK_ANALYTICS_DB.BRONZE.STOCK_STAGE/{subfolder}/"
    
    put_cmd = f"PUT 'file://{local_path}' {stage_path} AUTO_COMPRESS=FALSE OVERWRITE=TRUE;"
    print(f"Executing: PUT {filename} -> {stage_path}")
    cur.execute(put_cmd)
    res = cur.fetchall()
    print(f"  Result: {res[0][0]} -> status: {res[0][6]}")

# List files currently in stage
print("\n--- Current files in @BRONZE.STOCK_STAGE ---")
cur.execute("LIST @STOCK_ANALYTICS_DB.BRONZE.STOCK_STAGE;")
for row in cur.fetchall():
    print(f"File: {row[0]} | Size: {row[1]} bytes")

cur.close()
conn.close()
print("\nAll files successfully uploaded to stage!")
