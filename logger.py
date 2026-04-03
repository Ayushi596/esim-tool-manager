"""
logger.py
---------
Centralized logging system for eSim Tool Manager.
All actions (installs, updates, errors, config changes) are logged here.
"""

import logging
import os
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "esim_tool_manager.log")


def setup_logger():
    """
    Sets up and returns the eSim Tool Manager logger.
    Logs to both the console and a log file simultaneously.
    """
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("eSim_Tool_Manager")
    logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers if called multiple times
    if logger.handlers:
        return logger

    # --- File Handler: writes everything (DEBUG and above) to log file ---
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    # --- Console Handler: shows INFO and above to terminal ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger():
    """Returns the existing logger (or creates it if not set up yet)."""
    return setup_logger()