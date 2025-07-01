[![Python application test](https://github.com/HF980/PC-Diagnose-Tool/actions/workflows/python-app.yml/badge.svg)](https://github.com/HF980/PC-Diagnose-Tool/actions/workflows/python-app.yml)

# PC Diagnose Tool

A powerful yet lightweight desktop application for **real-time system diagnostics**.  
Built with **Python** and **PyQt6**, it provides insights into CPU, memory, disk, network usage, and logs the data using **SQLite** — all without relying on external services.

---

## Features

- **Live system monitoring** – CPU, RAM, network, and running processes  
- **Local logging** – Saves diagnostics in SQLite for historical analysis  
- **Modern GUI** – Built with PyQt6 (optional but sleek)  
- **Modular structure** – Easy to maintain, extend, and test  
- **Cross-platform** – Runs on Windows, macOS, and Linux  

---

## Project Structure

```text
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

---

## ⚙️ Installation

1. Make sure Python 3.10 is installed  
2. (Optional) Create and activate a virtual environment:

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
pip install -r requirements.txt
pip freeze > requirements.txt
