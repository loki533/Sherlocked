import logging
from config import LOGS_DIR

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Create logger
logger = logging.getLogger("Sherlocked")
logger.setLevel(logging.INFO)

# Prevent duplicate logs
if not logger.handlers:

    file_handler = logging.FileHandler(
        LOGS_DIR / "sherlocked.log",
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)