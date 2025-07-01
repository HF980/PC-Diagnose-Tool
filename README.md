[![Python application test](https://github.com/HF980/PC-Diagnose-Tool/actions/workflows/python-app.yml/badge.svg)](https://github.com/HF980/PC-Diagnose-Tool/actions/workflows/python-app.yml) ![License: GPL 3.0](https://img.shields.io/badge/License-GPL%203.0-4CAF50?style=flat-square)

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

```
.
├── LICENSE
├── PC_Diagnosis_Logs
│   ├── system_metrics.db
│   └── test_system_logs.db
└── src
    ├── db_manager.py
    ├── gui_elements.py
    ├── logging_db.py
    ├── main.py
    ├── system_info.py
    └── tests
    │   ├── test_logging_db.py
    │   └── test_system_info.py
    └── README.md
    └── requirements.txt
```

## Installation

1. Make sure Python 3.10+ is installed  
2. (Optional) Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies:
pip install -r requirements.txt
pip freeze > requirements.txts
