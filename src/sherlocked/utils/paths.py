from pathlib import Path


# Sherlocked/
# ├── src/
# │   └── sherlocked/
# │       └── utils/
#
# parents[3] -> Sherlocked/

PROJECT_ROOT = Path(__file__).resolve().parents[3]

CASES_DIR = PROJECT_ROOT / "cases"
LOGS_DIR = PROJECT_ROOT / "logs"
REPORTS_DIR = PROJECT_ROOT / "reports"
SAMPLE_DATA_DIR = PROJECT_ROOT / "sample_data"


# Create runtime directories if they don't exist
CASES_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)