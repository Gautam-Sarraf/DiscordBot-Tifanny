import logging
import sys
from services.config import Config

class CustomFormatter(logging.Formatter):
    """Custom formatter to add ANSI colors for terminal logging."""
    
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    cyan = "\x1b[36;20m"
    reset = "\x1b[0m"
    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: cyan + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: red + fmt + reset,
        logging.CRITICAL: bold_red + fmt + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno, self.grey + self.fmt + self.reset)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger() -> logging.Logger:
    """Configures and returns the main bot logger."""
    logger = logging.getLogger("TiffanyBot")
    
    # Avoid duplicate handlers if setup is run multiple times
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(getattr(logging, Config.LOG_LEVEL, logging.INFO))

    # Console Handler with color
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    # File Handler for production logs
    try:
        # Ensure the directories for the log file are created first
        Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(Config.LOG_FILE, encoding="utf-8")
        file_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
        file_formatter = logging.Formatter(file_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Failed to initialize file logger: {e}. Logging to console only.")

    return logger

# Singleton instance of the logger
log = setup_logger()
