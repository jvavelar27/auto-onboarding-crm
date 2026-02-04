import logging
import sys
import os

def setup_logger(name="crm_automation", log_file="crm_automation.log", level=logging.INFO):
    """Configures and returns a logger instance."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File Handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        # Ignore file logging if filesystem is read-only (e.g. Vercel)
        pass
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Default logger instance
try:
    logger = setup_logger()
except Exception as e:
    # Fallback if even basic setup fails
    print(f"Failed to setup logger: {e}")
    logger = logging.getLogger("crm_automation")
    logger.addHandler(logging.StreamHandler(sys.stdout))
