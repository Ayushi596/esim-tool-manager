"""
main.py
-------
eSim Automated Tool Manager — Main Entry Point
A command-line tool to manage installation, updates, configuration,
and dependency checking for the eSim EDA environment.

Author: Ayushi
Version: 1.0.0
"""

import sys
import os
from logger import get_logger, LOG_FILE
from utils import print_header, print_separator, get_os

# Module imports
import dependency_checker
import installer
import updater
import config_handler

logger = get_logger()

VERSION = "1.0.0"
TOOL_NAME = "eSim Automated Tool Manager"


def print_banner():
    """Prints the startup banner."""
    os.system("cls" if get_os() == "windows" else "clear")
    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║                                                      ║")
    print("  ║       eSim Automated Tool Manager  v1.0.0           ║")
    print("  ║       FOSSEE | IIT Bombay                           ║")
    print("  ║                                                      ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()
    logger.info(f"eSim Tool Manager v{VERSION} started.")


def print_main_menu():
    """Prints the main menu options."""
    print_separator("─")
    print("  MAIN MENU")
    print_separator("─")
    print("  [1]  Dependency Checker        — Check all required tools & libs")
    print("  [2]  Tool Installer            — Install eSim tools & dependencies")
    print("  [3]  Update & Upgrade          — Check for and apply updates")
    print("  [4]  Configuration Manager     — View/edit settings & env vars")
    print("  [5]  View Activity Log         — See log of recent actions")
    print("  [6]  System Info               — Show your system details")
    print("  [0]  Exit")
    print_separator("─")


def view_log():
    """Displays the last 30 lines of the activity log."""
    print_header("Activity Log")
    if not os.path.exists(LOG_FILE):
        print("  No log file found yet.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    recent = lines[-30:] if len(lines) > 30 else lines
    if recent:
        for line in recent:
            print(f"  {line.rstrip()}")
    else:
        print("  Log is empty.")
    print()
    print(f"  Full log location: {os.path.abspath(LOG_FILE)}")


def show_system_info():
    """Shows basic system information relevant to eSim setup."""
    import platform
    print_header("System Information")
    print(f"  OS              : {platform.system()} {platform.release()}")
    print(f"  OS Version      : {platform.version()}")
    print(f"  Architecture    : {platform.machine()}")
    print(f"  Python Version  : {sys.version.split()[0]}")
    print(f"  Python Path     : {sys.executable}")
    print(f"  Working Dir     : {os.getcwd()}")
    print(f"  Log File        : {os.path.abspath(LOG_FILE)}")
    print()
    logger.info("System info displayed.")


def configuration_menu():
    """Sub-menu for configuration options."""
    while True:
        print_header("Configuration Manager")
        print("  [1]  View current configuration")
        print("  [2]  Update a configuration setting")
        print("  [3]  Set environment variables (session)")
        print("  [0]  Back to Main Menu")
        print_separator()
        choice = input("  Your choice: ").strip()

        if choice == "1":
            config_handler.view_config()
        elif choice == "2":
            config_handler.update_config()
        elif choice == "3":
            config_handler.set_environment_variables()
        elif choice == "0":
            break
        else:
            print("  Invalid choice. Try again.")

        input("\n  Press Enter to continue...")


def installer_menu():
    """Sub-menu for tool installation."""
    while True:
        print_header("Tool Installer")
        print("  [1]  View all tools & install status")
        print("  [2]  Install a specific tool")
        print("  [3]  Batch install all Python packages")
        print("  [0]  Back to Main Menu")
        print_separator()
        choice = input("  Your choice: ").strip()

        if choice == "1":
            installer.list_tools()
        elif choice == "2":
            installer.install_tool_menu()
        elif choice == "3":
            installer.install_all_pip_packages()
        elif choice == "0":
            break
        else:
            print("  Invalid choice. Try again.")

        input("\n  Press Enter to continue...")


def main():
    """Main application loop."""
    print_banner()

    # Auto-run dependency check on first launch if config doesn't exist
    if not os.path.exists("config/settings.json"):
        print("  Welcome! This looks like your first run.")
        print("  Let's check your environment first.\n")
        input("  Press Enter to run an initial dependency check...")
        dependency_checker.run_full_check()
        input("\n  Press Enter to continue to main menu...")
        print_banner()

    while True:
        print_main_menu()
        choice = input("  Enter your choice: ").strip()

        if choice == "1":
            dependency_checker.run_full_check()

        elif choice == "2":
            installer_menu()

        elif choice == "3":
            updater.run_update_menu()

        elif choice == "4":
            configuration_menu()

        elif choice == "5":
            view_log()

        elif choice == "6":
            show_system_info()

        elif choice == "0":
            print()
            print("  Thank you for using eSim Tool Manager.")
            print("  Goodbye!")
            logger.info("eSim Tool Manager exited by user.")
            sys.exit(0)

        else:
            print("  Invalid choice. Please enter a number from the menu.")

        print()
        input("  Press Enter to return to main menu...")
        print_banner()


if __name__ == "__main__":
    main()