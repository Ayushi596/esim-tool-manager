"""
utils.py
--------
Shared utility functions used across all modules of eSim Tool Manager.
"""

import subprocess
import shutil
import sys
import os
import platform
from logger import get_logger

logger = get_logger()


def get_os():
    """
    Returns the current operating system as a lowercase string.
    Possible values: 'windows', 'linux', 'darwin' (macOS)
    """
    system = platform.system().lower()
    logger.debug(f"Detected OS: {system}")
    return system


def is_tool_installed(tool_name: str) -> bool:
    """
    Checks if a command-line tool/executable is available in the system PATH.

    Args:
        tool_name (str): The name of the tool (e.g., 'ngspice', 'python')

    Returns:
        bool: True if found, False otherwise
    """
    found = shutil.which(tool_name) is not None
    logger.debug(f"Tool '{tool_name}' installed: {found}")
    return found


def run_command(command: list, description: str = "") -> tuple:
    """
    Runs a shell command and returns (success: bool, output: str).

    Args:
        command (list): Command as a list of strings e.g. ['pip', 'install', 'requests']
        description (str): Human-readable description for logging

    Returns:
        tuple: (True/False, output string)
    """
    if description:
        logger.info(f"Running: {description}")
    logger.debug(f"Command: {' '.join(command)}")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        if result.returncode == 0:
            logger.debug(f"Command succeeded: {result.stdout.strip()}")
            return True, result.stdout.strip()
        else:
            logger.warning(f"Command failed: {result.stderr.strip()}")
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {' '.join(command)}")
        return False, "Command timed out."
    except FileNotFoundError:
        logger.error(f"Command not found: {command[0]}")
        return False, f"'{command[0]}' is not recognized on this system."
    except Exception as e:
        logger.error(f"Unexpected error running command: {e}")
        return False, str(e)


def get_tool_version(tool_name: str, version_flag: str = "--version") -> str:
    """
    Attempts to get the version string of an installed tool.

    Args:
        tool_name (str): Name of the tool
        version_flag (str): Flag to get version (default: '--version')

    Returns:
        str: Version string or 'Unknown' if not found
    """
    success, output = run_command([tool_name, version_flag])
    if success and output:
        # Return just the first line of version output
        version = output.splitlines()[0]
        logger.debug(f"Version of '{tool_name}': {version}")
        return version
    return "Unknown / Not Installed"


def print_separator(char="─", length=55):
    """Prints a visual separator line in the terminal."""
    print(char * length)


def print_header(title: str):
    """Prints a formatted section header."""
    print()
    print_separator("═")
    print(f"  {title}")
    print_separator("═")


def confirm_action(prompt: str) -> bool:
    """
    Asks the user to confirm an action with Y/N.

    Args:
        prompt (str): The question to ask

    Returns:
        bool: True if user confirmed, False otherwise
    """
    while True:
        choice = input(f"\n  {prompt} [Y/N]: ").strip().lower()
        if choice in ('y', 'yes'):
            return True
        elif choice in ('n', 'no'):
            return False
        else:
            print("  Please enter Y or N.")