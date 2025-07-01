#********************************************#
# @ #!/usr/bin/env
# @Project: pc_diagnose_tool
# @file name: main.py
# @creation date: 30.06.2025
# @lastmodified: 30.06.2025
# @version: 1.0
#********************************************#

#------------------------------------------------------------------------------
# Purpose

# This is the main entry point for the PC Diagnose Tool application.
# It initializes the PyQt6 GUI, sets up tabs for various system monitoring views,
# manages periodic data logging to the SQLite database, and updates all UI tabs accordingly.

# Class
# -----
# SystemDiagnosisApp              Main window class that organizes and updates all diagnostic tabs.

# Methods
# -------
# __init__()                     Sets up window, initializes system info fetcher, DB manager, and UI.
# setup_tabs()                   Creates and adds all tabs (Overview, CPU, Memory, Network, Processes,
#                               Programs, Logs, Graphs) to the main QTabWidget.
# setup_timer()                  Starts a QTimer to periodically log system snapshots and refresh tabs.
# log_and_update_all_tabs()      Captures system snapshot, logs it in the database,
#                               and updates all tab widgets.
# closeEvent(event)              Ensures DB connection is closed when app exits.

# Application Flow
# ----------------
# 1. On startup, system info fetcher and DB manager are initialized.
# 2. Tabs are created and added to main window.
# 3. A timer triggers periodic data logging and UI updates every 100 seconds.
# 4. User can view live system data, logs, and historical graphs.

# Technical Details
# -----------------
# - Dynamically adjusts Python path to locate project modules regardless of run context.
# - Integrates multiple custom widgets imported from 'src.gui.pyqt6.pc_diagnose_tool'.
# - Uses PyQt6 widgets, layouts, and signals for GUI.
# - Stores system snapshots in SQLite via LoggingDBManager.

# Use Case
# --------
# Designed for:
#  - Real-time system diagnostics and monitoring on desktop.
#  - Collecting and visualizing system metrics history.
#  - Extensible platform for additional diagnostic tools and data export.

# Directory Structure
# -------------------
# pc_diagnose_tool/
# ├── main.py                   This main application launcher script
# ├── logging_db.py             Database manager module
# ├── gui_elements.py           GUI tab widget definitions
# ├── system_info.py            System info fetching utilities
# └── PC_Diagnosis_Logs/
#     └── system_metrics.db     SQLite database file storing system logs

#------------------------------------------------------------------------------
# main.py
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Finde den Projekt-Root und füge ihn zum Python-Pfad hinzu
# Dies stellt sicher, dass 'src' gefunden wird, egal woher main.py gestartet wird.
# Dieser Pfad geht 4 Ebenen von 'main.py' (in pc_diagnose_tool) nach oben,
# um zum 'python_project'-Root zu gelangen.
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# DEBUG-Zeilen (können entfernt werden, sobald alles funktioniert)
print(f"DEBUG: sys.path is now: {sys.path}")
print(f"DEBUG: project_root calculated as: {project_root}")


from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import QTimer, Qt

# Importiere deine Module
# WICHTIG: system_info (mit Unterstrich) wurde korrigiert, und alle __init__.py-Dateien müssen existieren!
from src.system_info import SystemInfoFetcher
from src.db_manager import LoggingDBManager
from src.gui_elements import (
    OverviewLayout, CPULayout, MemoryLayout, NetworkLayout,
    ProcessesLayout, ProgramsLayout, LogsLayout, GraphLayout
)


class SystemDiagnosisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PC Diagnose Tool")
        self.setGeometry(100, 100, 1000, 700) # (x, y, Breite, Höhe)

        self.system_info_fetcher = SystemInfoFetcher()
        self.db_manager = LoggingDBManager()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        self.setup_tabs()
        self.setup_timer()

        # Initialer Log-Eintrag und erste Aktualisierung der Daten in allen Tabs
        self.log_and_update_all_tabs()

    def setup_tabs(self):
        # Übersicht Tab
        self.overview_tab_widget = OverviewLayout(self.system_info_fetcher)
        self.tab_widget.addTab(self.overview_tab_widget, "Übersicht")

        # CPU Tab
        self.cpu_tab_widget = CPULayout(self.system_info_fetcher)
        self.tab_widget.addTab(self.cpu_tab_widget, "CPU")

        # Speicher Tab
        self.memory_tab_widget = MemoryLayout(self.system_info_fetcher)
        self.tab_widget.addTab(self.memory_tab_widget, "Speicher")

        # Netzwerk Tab
        self.network_tab_widget = NetworkLayout(self.system_info_fetcher)
        self.tab_widget.addTab(self.network_tab_widget, "Netzwerk")

        # Prozesse Tab
        self.processes_tab_widget = ProcessesLayout(self.system_info_fetcher)
        self.tab_widget.addTab(self.processes_tab_widget, "Prozesse")

        # Programme Tab
        self.programs_tab_widget = ProgramsLayout(self.system_info_fetcher)
        self.tab_widget.addTab(self.programs_tab_widget, "Programme")

        # Logs Tab
        self.logs_tab_widget = LogsLayout(self.system_info_fetcher, self.db_manager)
        self.tab_widget.addTab(self.logs_tab_widget, "Logs")

        # Graphen Tab (NEU)
        self.graph_tab_widget = GraphLayout(self.system_info_fetcher, self.db_manager)
        self.tab_widget.addTab(self.graph_tab_widget, "Graphen")

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.setInterval(100000) # Aktualisiere alle 3 Sekunden
        self.timer.timeout.connect(self.log_and_update_all_tabs)
        self.timer.start()

    def log_and_update_all_tabs(self):
        # 1. System-Snapshot erfassen und in DB loggen
        snapshot = self.system_info_fetcher.get_system_snapshot()
        self.db_manager.log_snapshot(snapshot)

        # 2. Alle Tabs aktualisieren
        self.overview_tab_widget.update_data()
        self.cpu_tab_widget.update_data()
        self.memory_tab_widget.update_data()
        self.network_tab_widget.update_data()
        self.processes_tab_widget.update_data()
        self.programs_tab_widget.update_data()
        self.logs_tab_widget.update_data()
        self.graph_tab_widget.update_data() # Graphen-Tab auch aktualisieren

    def closeEvent(self, event):
        """Wird aufgerufen, wenn das Hauptfenster geschlossen wird."""
        self.db_manager.close() # Datenbankverbindung schließen
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SystemDiagnosisApp()
    window.show()
    sys.exit(app.exec())
