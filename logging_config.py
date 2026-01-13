"""
Logging configuration for the AI Research Assistant
Provides centralized logging setup for both CLI and web app
"""

import logging
import os
from datetime import datetime


def setup_logging(app_name="research_assistant", log_level=logging.INFO):
    """
    Configure logging for the research assistant
    
    Args:
        app_name: Name of the application (used for log file naming)
        log_level: Logging level (default: INFO)
    
    Returns:
        logger: Configured logger instance
    """
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{app_name}_{timestamp}.log")
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler (detailed logging)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (simple logging)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name="research_assistant"):
    """
    Get an existing logger or create a new one
    
    Args:
        name: Name of the logger
    
    Returns:
        logger: Logger instance
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger = setup_logging(name)
    return logger


# Log rotation utility
def rotate_old_logs(log_dir="logs", days_to_keep=30):
    """
    Remove log files older than specified days
    
    Args:
        log_dir: Directory containing log files
        days_to_keep: Number of days to keep logs for
    """
    import os
    import time
    
    if not os.path.exists(log_dir):
        return
    
    current_time = time.time()
    cutoff_time = current_time - (days_to_keep * 86400)  # 86400 seconds in a day
    
    for filename in os.listdir(log_dir):
        filepath = os.path.join(log_dir, filename)
        if os.path.isfile(filepath):
            if os.stat(filepath).st_mtime < cutoff_time:
                try:
                    os.remove(filepath)
                    logger = logging.getLogger(__name__)
                    logger.info(f"Removed old log file: {filename}")
                except Exception as e:
                    logger.error(f"Failed to remove log file {filename}: {str(e)}")


if __name__ == "__main__":
    # Test the logging setup
    logger = setup_logging()
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    print("\nCheck the 'logs' directory for the generated log file")
