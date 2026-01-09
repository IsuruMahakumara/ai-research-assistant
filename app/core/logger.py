import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Log file path
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"


class ISTFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=IST)
        if datefmt:
            return dt.strftime(datefmt)
        return dt.strftime("%Y-%m-%d %H:%M:%S IST")


def setup_logging() -> None:
    """Configure logging with IST timestamps and file output."""
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    formatter = ISTFormatter(log_format)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)

    # Root logger config
    logging.basicConfig(level=logging.INFO, handlers=[console_handler, file_handler])


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)

