# eSim Automated Tool Manager

A Python-based command-line tool to automate the **installation, configuration, updating, and dependency management** of external tools and libraries required by the [eSim EDA platform](https://esim.fossee.in/) developed at IIT Bombay (FOSSEE).

---

## Features

| Feature | Description |
|---|---|
| **Dependency Checker** | Checks all system tools (Ngspice, KiCad, Git, Java) and Python libraries |
| **Tool Installer** | Installs Python packages via pip; guides binary installs via browser |
| **Update & Upgrade** | Checks PyPI for latest versions, upgrades outdated packages |
| **Configuration Manager** | Stores tool paths, sets environment variables, manages user preferences |
| **Activity Log** | Logs all actions to `logs/esim_tool_manager.log` |
| **System Info** | Displays OS, Python version, and working environment details |

---

## Requirements

- Python 3.10 or above
- Windows 10/11 (primary support) or Linux/macOS
- Internet connection (for update checks and downloads)

---

## Installation & Setup

### Step 1 - Clone the repository

```bash
git clone https://github.com/Ayushi596/esim-tool-manager.git
cd esim-tool-manager
```

### Step 2 - (Optional) Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate     # On Windows
source venv/bin/activate  # On Linux/macOS
```

### Step 3 - Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 - Run the tool

```bash
python main.py
```

---

## How to Use

When you run `python main.py`, you'll see the interactive CLI menu:

```
  ╔══════════════════════════════════════════════════════╗
  ║       eSim Automated Tool Manager  v1.0.0           ║
  ║       FOSSEE | IIT Bombay                           ║
  ╚══════════════════════════════════════════════════════╝

  MAIN MENU
  ─────────────────────────────────────────────────────
  [1]  Dependency Checker        — Check all required tools & libs
  [2]  Tool Installer            — Install eSim tools & dependencies
  [3]  Update & Upgrade          — Check for and apply updates
  [4]  Configuration Manager     — View/edit settings & env vars
  [5]  View Activity Log         — See log of recent actions
  [6]  System Info               — Show your system details
  [0]  Exit
```

### Menu Options Explained

**[1] Dependency Checker**
- Scans your system for Ngspice, KiCad, Git, Java, Python
- Checks all required Python libraries
- Reports what is missing, with install instructions
- Offers to auto-install missing Python packages

**[2] Tool Installer**
- View all tools and their installation status
- Install Python packages automatically via pip
- Opens browser to official download page for binary tools

**[3] Update & Upgrade**
- Connects to PyPI to check latest versions
- Shows installed vs. latest for all tracked packages
- One-click upgrade for all outdated packages

**[4] Configuration Manager**
- Store paths to eSim, Ngspice, KiCad installations
- Set environment variables for current session
- All settings saved in `config/settings.json`

**[5] View Activity Log**
- Shows last 30 lines of the activity log
- Full log at `logs/esim_tool_manager.log`

---

## Project Structure

```
esim-tool-manager/
│
├── main.py               # Entry point & main CLI menu
├── installer.py          # Tool Installation Management
├── updater.py            # Update & Upgrade System
├── config_handler.py     # Configuration Handling
├── dependency_checker.py # Dependency Checker
├── logger.py             # Centralized logging
├── utils.py              # Shared helper functions
│
├── config/
│   └── settings.json     # User configuration (auto-created)
│
├── logs/
│   └── esim_tool_manager.log  # Activity log (auto-created)
│
├── docs/
│   └── design_document.md     # Architecture & design doc
│
├── requirements.txt
└── README.md
```

---

## Supported Tools

### System Tools
- **Ngspice** - SPICE circuit simulator (core eSim dependency)
- **KiCad** - EDA tool for schematic and PCB design
- **Git** - Version control
- **Java JDK** - Required by some eSim modules
- **Python 3.10+** - Required runtime

### Python Libraries
- `requests`, `psutil`, `colorama`, `packaging`
- `PyYAML`, `matplotlib`, `numpy`, `Pillow`

---

## Logs

All actions are logged automatically:
- Location: `logs/esim_tool_manager.log`
- Format: `[YYYY-MM-DD HH:MM:SS] [LEVEL] message`
- Levels: DEBUG, INFO, WARNING, ERROR

---

## Author

Ayushi (Developed as a screening task for **eSim Summer Fellowship 2026**
FOSSEE Project, IIT Bombay)
