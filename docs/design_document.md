# Design Document: eSim Automated Tool Manager

**Project:** eSim Summer Fellowship 2026 — Screening Task 5
**Tool:** eSim Automated Tool Manager
**Version:** 1.0.0
**Author:** Ayushi
**Institution:** VIT Bhopal University

---

## 1. Overview

The **eSim Automated Tool Manager** is a Python-based command-line application designed to automate the installation, configuration, dependency management, and update tracking of all external tools and libraries required by the eSim EDA platform developed at FOSSEE, IIT Bombay.

Managing eSim's external dependencies manually—across multiple operating systems and versions—is error-prone and time-consuming. This tool eliminates that friction by providing a unified, menu-driven interface to handle all tool management tasks in one place.

---

## 2. Goals

1. Reduce manual effort in setting up the eSim development environment
2. Detect and resolve missing or incompatible dependencies automatically
3. Keep all tools and Python libraries up-to-date with minimal user intervention
4. Provide transparent logging of all actions for debugging and auditing
5. Store and manage user configuration (tool paths, env vars) persistently

---

## 3. Architecture Overview

The application follows a **modular architecture** where each functional area is handled by a dedicated Python module. All modules share common utilities via `utils.py` and write to a centralized logger via `logger.py`.

```
┌─────────────────────────────────────────────────────────────┐
│                         main.py                             │
│              (CLI Entry Point & Menu Controller)            │
└────────┬──────────┬──────────┬──────────┬───────────────────┘
         │          │          │          │
         ▼          ▼          ▼          ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐
  │installer │ │ updater  │ │ config_  │ │  dependency_     │
  │   .py    │ │   .py    │ │ handler  │ │  checker.py      │
  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘
         │          │          │          │
         └──────────┴──────────┴──────────┘
                         │
              ┌──────────┴───────────┐
              │       utils.py       │
              │  (shared helpers)    │
              └──────────┬───────────┘
                         │
              ┌──────────┴───────────┐
              │       logger.py      │
              │  (centralized log)   │
              └──────────────────────┘
```

---

## 4. Module Breakdown

### 4.1 `main.py` — Entry Point & Menu Controller

**Responsibility:** Orchestrates the entire application. Renders the CLI menu. Routes user choices to appropriate module functions.

**Key Functions:**
- `print_banner()` — Displays the application header
- `print_main_menu()` — Renders the main menu
- `main()` — Main event loop handling user input
- `configuration_menu()` — Sub-menu for config options
- `installer_menu()` — Sub-menu for installation options
- `view_log()` — Displays recent activity log
- `show_system_info()` — Shows OS and runtime details

**Design Decisions:**
- Uses a `while True` loop with `input()` for the interactive menu — simple, cross-platform, no external dependencies
- Calls `os.system("cls")` to clear screen between menus for a clean UX

---

### 4.2 `dependency_checker.py` — Dependency Checker

**Responsibility:** Verifies that all required system tools and Python libraries are present and functional.

**Key Functions:**
- `check_system_tools()` — Scans PATH for ngspice, kicad, git, java, python, pip
- `check_python_libraries()` — Uses `importlib.import_module()` to test each library
- `install_missing_libraries()` — Auto-installs missing pip packages
- `run_full_check()` — Runs both checks and prints a summary

**Data Structures:**
- `SYSTEM_TOOLS` — List of dicts: `{name, version_flag, description, install_hint, critical}`
- `PYTHON_LIBRARIES` — List of dicts: `{import_name, pip_name, description}`

**Design Decisions:**
- Uses `importlib.import_module()` instead of `pip show` for library checks — more reliable, doesn't require subprocess
- Critical tools are flagged separately for prominence in output
- Auto-install only offered for pip packages (not binary installers, which require OS-level permissions)

---

### 4.3 `installer.py` — Tool Installation Management

**Responsibility:** Manages the installation of all external tools required by eSim.

**Key Functions:**
- `list_tools()` — Shows all tools with install status
- `install_tool_menu()` — Interactive menu to pick a tool to install
- `install_single_tool(tool)` — Installs one tool (pip or browser-guided)
- `install_all_pip_packages()` — Batch installs all Python packages

**Data Structures:**
- `INSTALLABLE_TOOLS` — Registry of all tools with: `{id, name, display_name, description, download_url, pip_package, windows_note, critical}`

**Design Decisions:**
- Binary tools (Ngspice, KiCad) cannot be silently installed on Windows without admin privileges and complex OS interaction. Instead, the tool opens the official download page in the user's default browser — this is both safe and user-friendly.
- Python pip packages are installed fully automatically using `subprocess` calling `pip`

---

### 4.4 `updater.py` — Update & Upgrade System

**Responsibility:** Checks for available updates for tracked tools and Python packages. Applies upgrades with user confirmation.

**Key Functions:**
- `get_latest_pip_version(package)` — Queries PyPI JSON API for latest version
- `get_installed_pip_version(package)` — Runs `pip show` to find installed version
- `check_pip_updates()` — Compares installed vs. latest for all tracked packages
- `check_system_tool_versions()` — Displays current system tool versions
- `upgrade_pip_packages(packages)` — Runs `pip install --upgrade` for a list
- `run_update_menu()` — Full update workflow with upgrade prompt

**External API Used:**
- PyPI JSON API: `https://pypi.org/pypi/{package}/json`
- No API key required; free and public

**Design Decisions:**
- Uses Python's built-in `urllib.request` instead of `requests` to avoid circular dependency (since `requests` itself is one of the tracked packages)
- System binary tools (Ngspice, KiCad) cannot be auto-updated on Windows; instead, user is shown their current version and directed to the official download page

---

### 4.5 `config_handler.py` — Configuration Handling

**Responsibility:** Stores and manages user settings persistently using a JSON file. Handles tool paths and environment variable configuration.

**Key Functions:**
- `load_config()` — Reads `config/settings.json`; creates default if missing
- `save_config(config)` — Writes config to JSON with timestamp
- `view_config()` — Pretty-prints current configuration
- `update_config()` — Interactive menu to edit individual settings
- `set_environment_variables()` — Sets env vars for current process session

**Storage Format:** `config/settings.json`
```json
{
    "esim_path": "C:\\eSim",
    "ngspice_path": "C:\\Ngspice\\bin",
    "kicad_path": "C:\\KiCad",
    "python_path": "C:\\Python310\\python.exe",
    "user_name": "Ayushi",
    "auto_update_check": true,
    "log_level": "INFO",
    "last_updated": "2026-04-04 10:00:00"
}
```

**Design Decisions:**
- JSON chosen over `.ini` or `.env` for readability and native Python support
- Environment variables are set using `os.environ` — they apply to the current process and child processes, but are not permanent. User is guided to set them permanently via Windows System Properties.

---

### 4.6 `logger.py` — Centralized Logging

**Responsibility:** Provides a single shared logger used by all modules.

**Key Design:**
- Uses Python's built-in `logging` module
- Dual output: file handler (DEBUG+) and console handler (INFO+)
- Log file: `logs/esim_tool_manager.log`
- Format: `[YYYY-MM-DD HH:MM:SS] [LEVEL] message`

---

### 4.7 `utils.py` — Shared Helper Functions

**Responsibility:** Provides reusable utility functions to avoid code duplication.

**Key Functions:**
- `get_os()` — Returns OS identifier string
- `is_tool_installed(name)` — Checks PATH using `shutil.which()`
- `run_command(command, description)` — Runs subprocess with error handling
- `get_tool_version(tool, flag)` — Gets version string of a tool
- `print_header()`, `print_separator()` — Terminal UI formatting
- `confirm_action(prompt)` — Y/N confirmation prompt

---

## 5. Data Flow

### Dependency Check Flow
```
User selects [1] → dependency_checker.run_full_check()
  → check_system_tools(): shutil.which() → print status table
  → check_python_libraries(): importlib.import_module() → print status table
  → if missing pip libs → confirm_action() → install_missing_libraries()
  → print summary
  → logger.info() at each step
```

### Update Flow
```
User selects [3] → updater.run_update_menu()
  → check_pip_updates(): for each package →
      get_installed_pip_version() via pip show subprocess
      get_latest_pip_version() via PyPI JSON API (urllib)
      compare → mark if update available
  → check_system_tool_versions()
  → if upgradeable packages → confirm_action()
  → upgrade_pip_packages() → pip install --upgrade subprocess
```

### Config Save Flow
```
User selects [4] → [2] update config
  → update_config() → show editable keys → user enters new value
  → save_config() → write JSON to config/settings.json with timestamp
  → logger.info()
```

---

## 6. Cross-Platform Considerations

| Feature | Windows | Linux/macOS |
|---|---|---|
| Screen clear | `cls` | `clear` |
| Binary tool install | Browser-guided download | Can extend to `apt`/`brew` |
| Python install | PATH auto-detected | PATH auto-detected |
| Env variables (permanent) | Windows System Properties | `~/.bashrc` / `~/.zshrc` |
| pip install | `python -m pip` | `python3 -m pip` |

The tool uses `platform.system()` to detect OS and adapts behavior accordingly.

---

## 7. Error Handling Strategy

- All subprocess calls wrapped in `try-except` with timeout
- JSON config corruption handled by resetting to defaults
- Network errors in updater handled gracefully (shows "Unavailable")
- Invalid menu inputs rejected with user-friendly messages
- All errors logged to file for post-mortem debugging

---

## 8. Future Enhancements

1. **GUI Version** using `tkinter` or `PyQt5`
2. **Linux apt/pacman support** for auto-installing system binaries
3. **eSim version manager** — switch between eSim 2.3 / 2.4 / 2.5
4. **Plugin system** — allow community modules for new tools
5. **Scheduled update checks** — run in background on system startup
6. **Docker integration** — spin up an isolated eSim environment

---

## 9. Testing

To test each module:

```bash
# Test dependency checker
python -c "import dependency_checker; dependency_checker.run_full_check()"

# Test installer listing
python -c "import installer; installer.list_tools()"

# Test updater
python -c "import updater; updater.check_pip_updates()"

# Test config
python -c "import config_handler; config_handler.view_config()"
```

---

## 10. Conclusion

The eSim Automated Tool Manager provides a complete, extensible solution for managing the eSim development environment. By modularizing each concern (installation, updates, configuration, dependency checking) into separate files, the codebase is maintainable and easy to extend. The tool significantly reduces the setup friction for new eSim contributors and ensures a consistent, reproducible environment across machines.