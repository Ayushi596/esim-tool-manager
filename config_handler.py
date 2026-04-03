"""
config_handler.py
-----------------
Handles all configuration for eSim Tool Manager.
Stores tool paths, user preferences, and environment variable settings
in a local JSON file (config/settings.json).
"""

import json
import os
import sys
from logger import get_logger
from utils import print_header, print_separator

logger = get_logger()

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")

# Default configuration template
DEFAULT_CONFIG = {
    "esim_path": "",
    "ngspice_path": "",
    "kicad_path": "",
    "python_path": sys.executable,
    "user_name": "",
    "auto_update_check": True,
    "log_level": "INFO",
    "last_updated": ""
}


def load_config() -> dict:
    """
    Loads the configuration from settings.json.
    If the file doesn't exist, creates it with defaults.

    Returns:
        dict: Configuration dictionary
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_FILE):
        logger.info("No config file found. Creating default configuration.")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            logger.debug("Configuration loaded successfully.")
            return config
    except json.JSONDecodeError:
        logger.error("Config file is corrupted. Resetting to defaults.")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """
    Saves the configuration dictionary to settings.json.

    Args:
        config (dict): Configuration to save
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    from datetime import datetime
    config["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    logger.info("Configuration saved successfully.")


def view_config():
    """Displays the current configuration to the user in a readable format."""
    config = load_config()
    print_header("Current Configuration")
    print(f"  {'Key':<25} {'Value'}")
    print_separator()
    for key, value in config.items():
        display_value = value if value else "(not set)"
        print(f"  {key:<25} {display_value}")
    print()


def update_config():
    """
    Interactive menu to let the user update configuration settings.
    """
    config = load_config()
    print_header("Update Configuration")

    editable_keys = [
        ("esim_path", "Path to eSim installation folder"),
        ("ngspice_path", "Path to Ngspice executable"),
        ("kicad_path", "Path to KiCad installation folder"),
        ("user_name", "Your name (for logging purposes)"),
        ("auto_update_check", "Auto-check for updates on startup? (true/false)"),
        ("log_level", "Log level: DEBUG / INFO / WARNING / ERROR"),
    ]

    print("  Which setting do you want to update?\n")
    for i, (key, description) in enumerate(editable_keys, 1):
        current = config.get(key, "(not set)")
        print(f"  [{i}] {description}")
        print(f"      Current: {current}\n")

    print(f"  [0] Back to Main Menu")
    print_separator()

    choice = input("  Enter number: ").strip()

    if choice == "0":
        return

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(editable_keys):
            key, description = editable_keys[idx]
            new_value = input(f"\n  Enter new value for '{key}': ").strip()

            # Convert boolean strings
            if key == "auto_update_check":
                new_value = new_value.lower() in ("true", "yes", "1", "y")

            config[key] = new_value
            save_config(config)
            print(f"\n  ✔ '{key}' updated successfully.")
            logger.info(f"Config key '{key}' updated by user.")
        else:
            print("  Invalid choice.")
    except ValueError:
        print("  Please enter a valid number.")


def set_environment_variables():
    """
    Sets environment variables for configured tool paths.
    Note: On Windows, these apply only to the current process session.
    For permanent changes, user is guided to do it manually.
    """
    config = load_config()
    print_header("Environment Variable Configuration")

    env_map = {
        "ESIM_HOME": config.get("esim_path", ""),
        "NGSPICE_HOME": config.get("ngspice_path", ""),
        "KICAD_HOME": config.get("kicad_path", ""),
    }

    any_set = False
    for var, path in env_map.items():
        if path:
            os.environ[var] = path
            print(f"  ✔ Set {var} = {path}")
            logger.info(f"Environment variable set: {var} = {path}")
            any_set = True

    if not any_set:
        print("  ⚠ No tool paths are configured yet.")
        print("  Go to 'Update Configuration' first to set paths.")
    else:
        print()
        print("  NOTE: These variables are active for this session only.")
        print("  To make them permanent on Windows:")
        print("  → Search 'Environment Variables' in Start Menu")
        print("  → Edit System/User variables manually.")

    logger.info("Environment variables configured.")