"""
installer.py
------------
Handles downloading and installing external tools required by eSim.
On Windows: Opens the official download page for manual install + guides the user.
Also supports auto-install of Python-based tools via pip.
"""

import webbrowser
import sys
from logger import get_logger
from utils import (is_tool_installed, run_command,
                   print_header, print_separator, confirm_action)

logger = get_logger()

# ── Tool registry with download URLs and pip equivalents ─────────────────────
INSTALLABLE_TOOLS = [
    {
        "id": 1,
        "name": "ngspice",
        "display_name": "Ngspice",
        "description": "Open-source circuit simulator used by eSim for SPICE simulation",
        "download_url": "https://ngspice.sourceforge.io/download.html",
        "pip_package": None,  # Not pip-installable; binary only
        "windows_note": "Download the Windows installer (.exe) from the link above.",
        "critical": True
    },
    {
        "id": 2,
        "name": "kicad",
        "display_name": "KiCad",
        "description": "Open-source EDA tool for schematic and PCB design",
        "download_url": "https://www.kicad.org/download/windows/",
        "pip_package": None,
        "windows_note": "Download the KiCad installer for Windows (.exe).",
        "critical": False
    },
    {
        "id": 3,
        "name": "git",
        "display_name": "Git",
        "description": "Version control system — required for contributing to eSim",
        "download_url": "https://git-scm.com/download/win",
        "pip_package": None,
        "windows_note": "Download Git for Windows installer.",
        "critical": False
    },
    {
        "id": 4,
        "name": "java",
        "display_name": "Java (JDK 17+)",
        "description": "Java Runtime Environment — needed by some eSim modules",
        "download_url": "https://adoptium.net/temurin/releases/",
        "pip_package": None,
        "windows_note": "Download Eclipse Temurin JDK for Windows.",
        "critical": False
    },
    {
        "id": 5,
        "name": "matplotlib",
        "display_name": "Matplotlib (Python)",
        "description": "Python plotting library for eSim waveform visualization",
        "download_url": None,
        "pip_package": "matplotlib",
        "windows_note": "Will be installed via pip automatically.",
        "critical": False
    },
    {
        "id": 6,
        "name": "numpy",
        "display_name": "NumPy (Python)",
        "description": "Numerical computation library used in eSim simulations",
        "download_url": None,
        "pip_package": "numpy",
        "windows_note": "Will be installed via pip automatically.",
        "critical": False
    },
    {
        "id": 7,
        "name": "psutil",
        "display_name": "Psutil (Python)",
        "description": "System and process utilities for the Tool Manager",
        "download_url": None,
        "pip_package": "psutil",
        "windows_note": "Will be installed via pip automatically.",
        "critical": False
    },
]


def list_tools():
    """
    Displays all installable tools with their status (installed/not installed).
    """
    print_header("Tool Installation Manager")
    print(f"  {'#':<5} {'Tool':<22} {'Status':<15} {'Description'}")
    print_separator()

    for tool in INSTALLABLE_TOOLS:
        # For pip packages check by trying to import; for system tools check PATH
        if tool["pip_package"]:
            try:
                __import__(tool["pip_package"].lower().replace("-", "_"))
                status = "✔  Installed"
            except ImportError:
                status = "✘  Missing"
        else:
            status = "✔  Installed" if is_tool_installed(tool["name"]) else "✘  Missing"

        print(f"  [{tool['id']}]  {tool['display_name']:<22} {status:<15} {tool['description'][:40]}")

    print()


def install_tool_menu():
    """
    Interactive menu to select and install a specific tool.
    """
    list_tools()
    print("  Enter the number of the tool you want to install.")
    print("  [0] Back to Main Menu")
    print_separator()

    choice = input("  Your choice: ").strip()
    if choice == "0":
        return

    try:
        tool_id = int(choice)
        tool = next((t for t in INSTALLABLE_TOOLS if t["id"] == tool_id), None)
        if not tool:
            print("  Invalid choice. Please select a valid number.")
            return
        install_single_tool(tool)
    except ValueError:
        print("  Please enter a number.")


def install_single_tool(tool: dict):
    """
    Installs a single tool — pip install for Python packages,
    or opens the download page for binary installers.

    Args:
        tool (dict): Tool entry from INSTALLABLE_TOOLS
    """
    print()
    print(f"  Installing: {tool['display_name']}")
    print(f"  Description: {tool['description']}")
    print_separator()

    # ── Python pip package ────────────────────────────────────────────────────
    if tool["pip_package"]:
        if confirm_action(f"Install {tool['display_name']} via pip now?"):
            print(f"\n  Running: pip install {tool['pip_package']}")
            success, output = run_command(
                [sys.executable, "-m", "pip", "install", tool["pip_package"]],
                description=f"Installing {tool['display_name']}"
            )
            if success:
                print(f"  ✔ {tool['display_name']} installed successfully!")
                logger.info(f"Successfully installed: {tool['display_name']}")
            else:
                print(f"  ✘ Installation failed. Error: {output}")
                logger.error(f"Failed to install {tool['display_name']}: {output}")

    # ── Binary installer (opens browser) ─────────────────────────────────────
    elif tool["download_url"]:
        print(f"\n  {tool['display_name']} requires a manual installer on Windows.")
        print(f"  Note: {tool['windows_note']}")
        print(f"  Download URL: {tool['download_url']}")

        if confirm_action("Open the download page in your browser now?"):
            webbrowser.open(tool["download_url"])
            logger.info(f"Opened download page for: {tool['display_name']}")
            print(f"\n  ✔ Browser opened with download page for {tool['display_name']}.")
            print("  After installation, restart your terminal and run a dependency check.")
    else:
        print("  No installation method available for this tool.")
        logger.warning(f"No install method for: {tool['display_name']}")


def install_all_pip_packages():
    """
    Installs ALL pip-installable tools in one go.
    """
    pip_tools = [t for t in INSTALLABLE_TOOLS if t["pip_package"]]
    print_header("Batch Install All Python Packages")
    print("  The following will be installed via pip:")
    for t in pip_tools:
        print(f"   - {t['display_name']} ({t['pip_package']})")
    print()

    if confirm_action("Proceed with batch installation?"):
        for tool in pip_tools:
            print(f"\n  → Installing {tool['display_name']}...")
            success, output = run_command(
                [sys.executable, "-m", "pip", "install", tool["pip_package"]],
                description=f"pip install {tool['pip_package']}"
            )
            if success:
                print(f"     ✔ Done.")
                logger.info(f"Installed: {tool['pip_package']}")
            else:
                print(f"     ✘ Failed: {output}")
                logger.error(f"Batch install failed for {tool['pip_package']}: {output}")
        print("\n  Batch installation complete.")