import os
import sys
import subprocess
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv()

# Build dbt command
dbt_args = sys.argv[1:] if len(sys.argv) > 1 else ["run"]
cmd = ["dbt"] + dbt_args + ["--profiles-dir", "."]

print(f"Executing: {' '.join(cmd)}\n")
result = subprocess.run(cmd, env=os.environ)
sys.exit(result.returncode)
