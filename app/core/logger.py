import os
from loguru import logger
import sys


def set_logger(name: str):
    # Clear any existing handlers
    logger.remove()
    
    # Configure logger format
    log_format = "<level>{level: <8}</level> <green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> - <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    # Add console handler (this will go to CloudWatch in Lambda)
    logger.add(
        sys.stdout,
        format=log_format,
        level="INFO",
        serialize=True  # This helps with CloudWatch formatting
    )
    
    # Set up file logging in Lambda's writable /tmp directory
    log_path = os.path.join('/tmp', f'{name}.log')
    logger.add(
        log_path,
        format=log_format,
        level="DEBUG",
        rotation="10 MB"
    )
    
    return logger

# Create a global logger instance
logger = set_logger("app")