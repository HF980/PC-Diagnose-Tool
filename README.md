PC Diagnose Tool

PC Diagnose Tool is a lightweight, cross-platform Python application designed to help users analyze the health and performance of their personal computers. It collects and displays key system information in real-time, making it ideal for troubleshooting, monitoring, and general diagnostics.
Features

    System Overview: OS, hostname, architecture, uptime
    CPU Information: Model name, per-core usage, temperature (if supported)
    Memory: Total, used, available, percentage used
    Disk Usage: Usage per partition, total and free space
    Network: Active interfaces, local IP, bandwidth monitoring
    Battery: Charge level, charging status, time remaining (on laptops)
    Export Reports: Output as .txt or .json
    GUI Interface (optional): User-friendly interface using PyQt6 or Tkinter

Tech Stack

    Language: Python 3.8+
    Core Libraries:
        psutil
        platform, socket, datetime
        Optional: PyQt6 or Tkinter for GUI

Getting Started
Prerequisites

    Python 3.8 or newer installed on your system

Installation

pip install psutil For GUI support (optional): pip install PyQt6
Usage

Command-line version: python diagnose.py

GUI version (if implemented): python gui_app.py
Project Structure
pc_diagnose_tool/
├── main.py               # Main launcher script for the GUI app
├── logging_db.py         # Module managing the SQLite database logging
├── system_info.py        # Fetches system info (CPU, RAM, network, processes)
├── gui_elements.py       # GUI components and tab widgets (PyQt6)
├── db_manager.py         # (optional) Base class for database abstraction

├── PC_Diagnosis_Logs/    # Folder for saved database files / logs
│   └── system_metrics.db     # SQLite DB storing logged metrics

├── resources/            # Icons, stylesheets, and other assets
│   └── icon.png              # Example icon

├── tests/                # Unit tests for modules
│   ├── test_system_info.py
│   └── test_logging_db.py

└── README.md             # Project description and usage guide
