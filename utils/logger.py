import logging
import os
from datetime import datetime
from config import LOGS_DIR, LOG_LEVEL

# Create logs directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)

# Configure logger
def setup_logger(name: str) -> logging.Logger:
    """Setup logger with file and console handler."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    
    # Format untuk log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler - Daily rotation
    date_str = datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOGS_DIR, f'bot_{date_str}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Global logger instances
bot_logger = setup_logger('CS_Bot')
db_logger = setup_logger('Database')
event_logger = setup_logger('Events')


def disable_console_logging():
    """Disable console output for all loggers."""
    # Remove console handlers from our loggers
    for logger in [bot_logger, db_logger, event_logger]:
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                logger.removeHandler(handler)
    
    # Also suppress root logger console output
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)
    
    # Suppress discord.py logging to console
    discord_logger = logging.getLogger('discord')
    for handler in discord_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            discord_logger.removeHandler(handler)


def enable_console_logging():
    """Re-enable console output for all loggers."""
    for logger in [bot_logger, db_logger, event_logger]:
        # Check if console handler already exists
        has_console = any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) 
                         for h in logger.handlers)
        if not has_console:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
