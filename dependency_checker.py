"""
dependency_checker.py
---------------------
Checks all required tools and Python libraries needed for eSim.
Reports what is installed, what is missing, and what version is found.
Offers to install missing Python libraries automatically.
"""

import importlib
import subprocess
import sys
from logger import get_logger
from utils import (is_tool_installed, get_tool_version,
                   print_header, print_separator, confirm_action, run_command)

logger = get_logger()

# ── System tools to check (name, how to get version, install hint) ──────────
SYSTEM_TOOLS = [
    {
        "name": "python",
        "version_flag": "--version",
        "description": "Python Interpreter",
        "install_hint": "Download from https://www.python.org/downloads/",
        "critical": True
    },
    {
        "name": "pip",
        "version_flag": "-V",
        "description": "Python Package Manager (pip)",
        "install_hint": "Comes with Python. Try: python -m ensurepip",
        "critical": True
    },
    {
        "name": "git",
        "version_flag": "--version",
        "description": "Git Version Control",
        "install_hint": "Download from https://git-scm.com/download/win",
        "critical": False
    },
    {
        "name": "ngspice",
        "version_flag": "--version",
        "description": "Ngspice Circuit Simulator",
        "install_hint": "Download from https://ngspice.sourceforge.io/download.html",
        "critical": True
    },
    {
        "name": "kicad",
        "version_flag": "--version",
        "description": "KiCad EDA Tool",
        "install_hint": "Download from https://www.kicad.org/download/",
        "critical": False
    },
    {
        "name": "java",
        "version_flag": "-version",
        "description": "Java Runtime (needed by some eSim modules)",
        "install_hint": "Download JDK from https://adoptium.net/",
        "critical": False
    },
]

# ── Python libraries required by eSim environment ───────────────────────────
PYTHON_LIBRARIES = [
    {"import_name": "requests",      "pip_name": "requests",      "description": "HTTP requests library"},
    {"import_name": "psutil",        "pip_name": "psutil",        "description": "System & process utilities"},
    {"import_name": "colorama",      "pip_name": "colorama",      "description": "Terminal color support (Windows)"},
    {"import_name": "packaging",     "pip_name": "packaging",     "description": "Version parsing utilities"},
    {"import_name": "PyYAML",        "pip_name": "PyYAML",        "description": "YAML configuration support"},
    {"import_name": "matplotlib",    "pip_name": "matplotlib",    "description": "Plotting & waveform visualization"},
    {"import_name": "numpy",         "pip_name": "numpy",         "description": "Numerical computation"},
    {"import_name": "Pillow",        "pip_name": "Pillow",        "description": "Image processing (PIL)"},
]


def check_system_tools() -> list:
    """
    Checks all system-level tools and prints a status table.

    Returns:
        list: List of dicts with check results for each tool
    """
    print_header("System Tool Dependency Check")
    print(f"  {'Tool':<20} {'Status':<15} {'Version / Info'}")
    print_separator()

    results = []
    for tool in SYSTEM_TOOLS:
        name = tool["name"]
        installed = is_tool_installed(name)

        if installed:
            version = get_tool_version(name, tool["version_flag"])
            status = "✔  FOUND"
            version_str = version[:50]  # trim if too long
        else:
            status = "✘  MISSING"
            version_str = f"→ {tool['install_hint']}"

        tag = "[CRITICAL]" if tool["critical"] and not installed else ""
        print(f"  {name:<20} {status:<15} {version_str}  {tag}")
        logger.debug(f"Tool check: {name} | installed={installed}")

        results.append({
            "name": name,
            "installed": installed,
            "description": tool["description"],
            "install_hint": tool["install_hint"],
            "critical": tool["critical"]
        })

    print()
    missing_critical = [r for r in results if not r["installed"] and r["critical"]]
    if missing_critical:
        print(f"  ⚠  {len(missing_critical)} critical tool(s) are missing!")
        for t in missing_critical:
            print(f"     → {t['description']}: {t['install_hint']}")
    else:
        print("  All critical system tools are present.")

    logger.info("System tool dependency check completed.")
    return results


def check_python_libraries() -> list:
    """
    Checks if required Python libraries are importable.
    Offers to auto-install any missing ones.

    Returns:
        list: List of dicts with check results for each library
    """
    print_header("Python Library Dependency Check")
    print(f"  {'Library':<20} {'Status':<15} {'Description'}")
    print_separator()

    results = []
    missing = []

    for lib in PYTHON_LIBRARIES:
        import_name = lib["import_name"]
        try:
            module = importlib.import_module(import_name.lower().replace("-", "_"))
            version = getattr(module, "__version__", "installed")
            print(f"  {import_name:<20} {'✔  FOUND':<15} {lib['description']} (v{version})")
            results.append({**lib, "installed": True, "version": version})
        except ImportError:
            print(f"  {import_name:<20} {'✘  MISSING':<15} {lib['description']}")
            results.append({**lib, "installed": False, "version": None})
            missing.append(lib)
        logger.debug(f"Library check: {import_name}")

    print()

    if missing:
        print(f"  ⚠  {len(missing)} Python library/libraries are missing:")
        for lib in missing:
            print(f"     - {lib['pip_name']}")

        if confirm_action("Auto-install all missing Python libraries now?"):
            install_missing_libraries(missing)
    else:
        print("  All Python libraries are installed.")

    logger.info("Python library dependency check completed.")
    return results


def install_missing_libraries(missing_libs: list):
    """
    Installs a list of missing Python pip packages.

    Args:
        missing_libs (list): List of library dicts with 'pip_name' key
    """
    print()
    for lib in missing_libs:
        pip_name = lib["pip_name"]
        print(f"  Installing {pip_name}...")
        success, output = run_command(
            [sys.executable, "-m", "pip", "install", pip_name],
            description=f"pip install {pip_name}"
        )
        if success:
            print(f"  ✔ {pip_name} installed successfully.")
            logger.info(f"Installed Python library: {pip_name}")
        else:
            print(f"  ✘ Failed to install {pip_name}. Error: {output}")
            logger.error(f"Failed to install {pip_name}: {output}")


def run_full_check():
    """Runs both system tool and Python library checks."""
    print()
    print("  Starting complete dependency verification for eSim environment...")
    sys_results = check_system_tools()
    lib_results = check_python_libraries()

    # Summary
    print_header("Dependency Check Summary")
    total_sys = len(sys_results)
    ok_sys = sum(1 for r in sys_results if r["installed"])
    total_lib = len(lib_results)
    ok_lib = sum(1 for r in lib_results if r["installed"])

    print(f"  System Tools :  {ok_sys}/{total_sys} found")
    print(f"  Python Libs  :  {ok_lib}/{total_lib} found")
    print()

    if ok_sys == total_sys and ok_lib == total_lib:
        print("  ✔ Your environment is fully ready for eSim!")
    else:
        print("  ⚠ Some dependencies are missing. Please review above.")

    logger.info(f"Dependency summary: sys={ok_sys}/{total_sys}, libs={ok_lib}/{total_lib}")