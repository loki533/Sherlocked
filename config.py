from pathlib import Path

# Root directory 
BASE_DIR = Path(__file__).resolve().parent

# Project folders
CASES_DIR = BASE_DIR / "cases"
EVIDENCE_DIR = BASE_DIR / "evidence"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Hash algorithms used 
HASH_ALGORITHMS = ["md5", "sha1", "sha256"]