import logging

from sherlocked.utils.paths import LOGS_DIR


LOGS_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("Sherlocked")
logger.setLevel(logging.INFO)


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