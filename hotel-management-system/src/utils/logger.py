# src/utils/logger.py

import logging
import os
import sys

def setup_logger():
    """
    Configures and returns a logger instance based on .env variables.
    
    Debug logs are only enabled if DEBUG_MODE is 'true' AND LOG_LEVEL is 'DEBUG'.
    Otherwise, the logger is set to the specified LOG_LEVEL (defaulting to INFO).
    """
    # Get environment variables with sensible defaults
    debug_mode = os.getenv("DEBUG_MODE", "false").lower()
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()

    # Determine the effective logging level
    effective_level = logging.INFO # Default level
    
    # Check the condition to enable DEBUG logs
    if debug_mode == 'true' and log_level_str == 'DEBUG':
        effective_level = logging.DEBUG
        print("✅ DEBUG mode is ON. Verbose logs will be shown.")
    else:
        # Get the level from the string (e.g., "INFO" -> logging.INFO)
        effective_level = getattr(logging, log_level_str, logging.INFO)

    # Configure the root logger
    # Using force=True to reconfigure if already set by another module
    logging.basicConfig(
        level=effective_level,
        format="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout, # Ensure logs go to standard output
        force=True
    )
    
    # Return the root logger for the main script to use
    return logging.getLogger()