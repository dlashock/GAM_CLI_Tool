"""
Logging module for GAM Admin Tool.

Provides centralized error logging to both file and console
with timestamp and operation tracking.
"""

import logging
import os
from datetime import datetime


# Module-level logger instance
_logger = None
_log_file = 'gam_tool_errors.log'


def setup_logger(log_file=None):
    """
    Initialize the logger for the application.

    Args:
        log_file (str, optional): Path to log file. Defaults to 'gam_tool_errors.log'
            in the current directory.

    Returns:
        logging.Logger: Configured logger instance
    """
    global _logger, _log_file

    if log_file:
        _log_file = log_file

    # Create logger
    _logger = logging.getLogger('GAMAdminTool')
    _logger.setLevel(logging.ERROR)

    # Prevent duplicate handlers if setup_logger is called multiple times
    if _logger.handlers:
        return _logger

    # Create formatters
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(operation)s] ERROR: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_formatter = logging.Formatter(
        '[%(operation)s] ERROR: %(message)s'
    )

    # Create file handler (mode='w' to create new log file each run)
    try:
        file_handler = logging.FileHandler(_log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(file_formatter)
        _logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file '{_log_file}': {e}")

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(console_formatter)
    _logger.addHandler(console_handler)

    return _logger


def get_logger():
    """
    Get the logger instance, creating it if it doesn't exist.

    Returns:
        logging.Logger: Logger instance
    """
    global _logger
    if _logger is None:
        setup_logger()
    return _logger


def log_error(operation, message):
    """
    Log an error message with operation context.

    Args:
        operation (str): The operation being performed when the error occurred
            (e.g., "Delete Messages", "Fetch Users", "Add Delegate")
        message (str): The error message to log

    Example:
        log_error("Delete Messages", "Failed to delete messages for user@domain.com: Invalid query")
    """
    logger = get_logger()

    # Use LoggerAdapter to add operation context
    adapter = logging.LoggerAdapter(logger, {'operation': operation})
    adapter.error(message)


def log_info(operation, message):
    """
    Log an informational message with operation context.

    Note: Currently the logger is configured for ERROR level only.
    This function is provided for future extensibility if INFO logging is needed.

    Args:
        operation (str): The operation being performed
        message (str): The info message to log
    """
    logger = get_logger()

    # Temporarily set to INFO level if needed
    old_level = logger.level
    logger.setLevel(logging.INFO)

    adapter = logging.LoggerAdapter(logger, {'operation': operation})
    adapter.info(message)

    # Restore previous level
    logger.setLevel(old_level)


def get_log_file_path():
    """
    Get the absolute path to the log file.

    Returns:
        str: Absolute path to the log file
    """
    return os.path.abspath(_log_file)


def log_file_exists():
    """
    Check if the log file exists.

    Returns:
        bool: True if log file exists, False otherwise
    """
    return os.path.exists(_log_file)


def read_log_file(max_lines=None):
    """
    Read and return contents of the log file.

    Args:
        max_lines (int, optional): Maximum number of lines to read from end of file.
            If None, reads entire file.

    Returns:
        str: Contents of the log file, or empty string if file doesn't exist
    """
    if not log_file_exists():
        return ""

    try:
        with open(_log_file, 'r', encoding='utf-8') as f:
            if max_lines is None:
                return f.read()
            else:
                # Read last N lines
                lines = f.readlines()
                return ''.join(lines[-max_lines:])
    except Exception as e:
        return f"Error reading log file: {e}"
