"""
updater.py
----------
Checks for available updates for installed Python packages and system tools.
Uses pip's JSON API to compare installed vs. latest versions.
Provides one-command upgrade for all outdated packages.
"""

import sys
import json
import urllib.request
import urllib.error
from logger import get_logger
from utils import (run_command, get_tool_version, is_tool_installed,
                   print_header, print_separator, confirm_action)

logger = get_logger()

# Python packages to check for updates
TRACKED_PIP_PACKAGES = [
    "requests", "psutil", "colorama", "packaging",
    "PyYAML", "matplotlib", "numpy", "Pillow"
]

# System tools to check (tool name, version flag, official URL)
TRACKED_SYSTEM_TOOLS = [
    ("ngspice",    "--version", "https://ngspice.sourceforge.io/download.html"),
    ("kicad",      "--version", "https://www.kicad.org/download/"),
    ("git",        "--version", "https://git-scm.com/download/win"),
    ("python",     "--version", "https://www.python.org/downloads/"),
]


def get_latest_pip_version(package_name: str) -> str:
    """
    Fetches the latest version of a pip package from PyPI JSON API.

    Args:
        package_name (str): Package name as on PyPI

    Returns:
        str: Latest version string or 'Unavailable'
    """
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url, timeout=8) as response:
            data = json.loads(response.read().decode())
            latest = data["info"]["version"]
            return latest
    except urllib.error.URLError:
        logger.warning(f"Could not reach PyPI for package: {package_name}")
        return "Unavailable (no internet?)"
    except Exception as e:
        logger.error(f"Error fetching version for {package_name}: {e}")
        return "Unavailable"


def get_installed_pip_version(package_name: str) -> str:
    """
    Gets the currently installed version of a pip package.

    Args:
        package_name (str): Package name

    Returns:
        str: Installed version or 'Not installed'
    """
    success, output = run_command(
        [sys.executable, "-m", "pip", "show", package_name]
    )
    if success:
        for line in output.splitlines():
            if line.startswith("Version:"):
                return line.split(":", 1)[1].strip()
    return "Not installed"


def check_pip_updates() -> list:
    """
    Checks all tracked pip packages for available updates.

    Returns:
        list: List of dicts with update info for each package
    """
    print_header("Python Package Update Check")
    print("  Connecting to PyPI to check for updates...\n")
    print(f"  {'Package':<20} {'Installed':<15} {'Latest':<15} {'Status'}")
    print_separator()

    results = []
    for pkg in TRACKED_PIP_PACKAGES:
        installed = get_installed_pip_version(pkg)
        latest = get_latest_pip_version(pkg)

        if installed == "Not installed":
            status = "⊘  Not installed"
        elif latest == installed:
            status = "✔  Up to date"
        elif "Unavailable" in latest:
            status = "?  Cannot check"
        else:
            status = "↑  UPDATE AVAILABLE"

        print(f"  {pkg:<20} {installed:<15} {latest:<15} {status}")
        results.append({
            "package": pkg,
            "installed": installed,
            "latest": latest,
            "needs_update": (
                installed != "Not installed"
                and "Unavailable" not in latest
                and latest != installed
            )
        })
        logger.debug(f"Update check: {pkg} installed={installed}, latest={latest}")

    print()
    upgradeable = [r for r in results if r["needs_update"]]
    if upgradeable:
        print(f"  ↑  {len(upgradeable)} package(s) can be upgraded.")
    else:
        print("  All packages are up to date (or not installed).")

    logger.info("Pip package update check completed.")
    return results


def check_system_tool_versions():
    """
    Displays currently installed versions of system tools.
    (For binary tools like ngspice, we can't auto-upgrade on Windows
    but we show version and redirect to download page.)
    """
    print_header("System Tool Version Check")
    print(f"  {'Tool':<20} {'Installed Version':<35} {'Download / Update URL'}")
    print_separator()

    for tool_name, version_flag, url in TRACKED_SYSTEM_TOOLS:
        if is_tool_installed(tool_name):
            version = get_tool_version(tool_name, version_flag)
            version_str = version[:35] if version else "Unknown"
        else:
            version_str = "Not installed"

        print(f"  {tool_name:<20} {version_str:<35} {url}")
        logger.debug(f"System tool version: {tool_name} → {version_str}")

    print()
    print("  NOTE: To upgrade system tools (ngspice, KiCad, etc.) on Windows,")
    print("  visit the URLs above and download the latest installer.")
    logger.info("System tool version check completed.")


def upgrade_pip_packages(packages: list):
    """
    Upgrades a list of pip packages.

    Args:
        packages (list): List of package name strings
    """
    print()
    for pkg in packages:
        print(f"  Upgrading {pkg}...")
        success, output = run_command(
            [sys.executable, "-m", "pip", "install", "--upgrade", pkg],
            description=f"pip upgrade {pkg}"
        )
        if success:
            print(f"  ✔ {pkg} upgraded successfully.")
            logger.info(f"Upgraded: {pkg}")
        else:
            print(f"  ✘ Failed to upgrade {pkg}: {output}")
            logger.error(f"Upgrade failed for {pkg}: {output}")


def run_update_menu():
    """
    Main update menu: checks pip packages and offers to upgrade outdated ones.
    """
    results = check_pip_updates()
    check_system_tool_versions()

    upgradeable = [r["package"] for r in results if r["needs_update"]]

    if upgradeable:
        print(f"\n  Packages with updates: {', '.join(upgradeable)}")
        if confirm_action("Upgrade all outdated packages now?"):
            upgrade_pip_packages(upgradeable)
            print("\n  ✔ All upgrades complete.")
        else:
            print("  Skipped upgrade.")
    else:
        print("\n  Nothing to upgrade.")