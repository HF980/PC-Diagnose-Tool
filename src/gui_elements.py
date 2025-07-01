#********************************************#
# @ #!/usr/bin/env
# @Project: pc_diagnose_tool
# @file name: gui_elements.py
# @creation date: 30.06.2025
# @lastmodified: 30.06.2025
# @version: 1.0
#********************************************#


#------------------------------------------------------------------------------
# Purpose

# gui_elements.py – Modular PyQt6 Widgets for System Monitoring GUI

# This module provides a suite of PyQt6-based widget classes for building a 
# comprehensive system monitoring and diagnostics GUI. Each class encapsulates 
# the logic and layout for displaying real-time or historical system metrics, 
# including CPU, memory, disk, network, running processes, installed programs, 
# and system logs with graphical visualization.
#
# Widget Classes
# --------------
# - BaseInfoWidget          : Abstract base class for all info/monitoring widgets.
# - OverviewLayout          : Dashboard overview of OS, CPU, RAM, disk, and network.
# - CPULayout               : Detailed CPU metrics, including per-core usage.
# - MemoryLayout            : RAM and swap usage details.
# - NetworkLayout           : Network summary and interface details.
# - ProcessesLayout         : Live process table with resource usage.
# - ProgramsLayout          : List of installed programs.
# - LogsLayout              : Table view of logged system metrics, with export/clear options.
# - GraphLayout             : Interactive time-series graphs for CPU, RAM, and network.
# - DateAxisItem            : Custom axis for displaying datetime values in graphs.
#
# Key Features
# ------------
# - Modular, reusable widget classes for easy integration into PyQt6 applications.
# - Real-time data updates via `update_data()` methods.
# - Advanced plotting with PyQtGraph for historical trends.
# - Export and management of logs (CSV export, clearing).
# - Designed for extensibility and maintainability.
#
# Typical Use Case
# ----------------
# These widgets form the foundation of a PC diagnostic or monitoring tool, 
# enabling users to visualize and analyze system performance, resource usage, 
# and process activity in real time or from historical logs.
#
# ------------------------------------------------------------------------------

# gui_elements.py

# Import necessary PyQt6 components for UI creation
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QPushButton, QTabWidget, QDialog, QMessageBox,
    QFileDialog, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDateTime, QLocale
from PyQt6.QtGui import QColor, QPalette

# Import system monitoring and utility libraries
import psutil
import platform
import os
import csv
from datetime import datetime
import pyqtgraph as pg  # For advanced plotting
import numpy as np


# Base class for all information widgets
class BaseInfoWidget(QWidget):
    def __init__(self, system_info_fetcher, parent=None):
        super().__init__(parent)
        self.system_info_fetcher = system_info_fetcher  # Data source
        self.setup_ui()  # Initialize UI components
        self.update_data()  # Load initial data

    def setup_ui(self):
        """Must be implemented by subclasses to create UI layout"""
        raise NotImplementedError("setup_ui must be implemented in subclasses")

    def update_data(self):
        """Must be implemented by subclasses to refresh data"""
        raise NotImplementedError("update_data must be implemented in subclasses")


class OverviewLayout(BaseInfoWidget):
    """Main dashboard showing system summary (CPU, RAM, Disk, Network)"""
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # OS information label
        self.os_label = QLabel("<b>Operating system:</b> ")
        self.layout.addWidget(self.os_label)

        # CPU usage section
        self.cpu_label = QLabel("<b>CPU:</b> ")
        self.layout.addWidget(self.cpu_label)
        self.cpu_usage_progress = QProgressBar()
        self.cpu_usage_progress.setTextVisible(True)
        self.layout.addWidget(self.cpu_usage_progress)

        # RAM usage section
        self.ram_label = QLabel("<b>RAM:</b> ")
        self.layout.addWidget(self.ram_label)
        self.ram_usage_progress = QProgressBar()
        self.ram_usage_progress.setTextVisible(True)
        self.layout.addWidget(self.ram_usage_progress)

        # Disk usage section
        self.disk_label = QLabel("<b>hard drive (C: / Root):</b> ")
        self.layout.addWidget(self.disk_label)
        self.disk_usage_progress = QProgressBar()
        self.disk_usage_progress.setTextVisible(True)
        self.layout.addWidget(self.disk_usage_progress)
        
        # Network usage section
        self.network_label = QLabel("<b>network (Live):</b> ")
        self.layout.addWidget(self.network_label)

        self.layout.addStretch(1)  # Add spacing at bottom

    def update_data(self):
        # Update OS information
        self.os_label.setText(f"<b>Operating system:</b> {platform.system()} {platform.release()} ({platform.version()})")

        # Update CPU information
        cpu_data = self.system_info_fetcher.get_cpu_info()
        cpu_percent = cpu_data.get("total_percent", 0.0)
        cpu_model = self.system_info_fetcher.get_cpu_model()
        self.cpu_label.setText(f"<b>CPU:</b> {cpu_model} ({cpu_data.get('physical_cores', 'N/A')} Kerne, {cpu_data.get('logical_cores', 'N/A')} Threads)")
        self.cpu_usage_progress.setValue(int(cpu_percent))
        self.cpu_usage_progress.setFormat(f"CPU-Auslastung: {cpu_percent:.1f}%")

        # Update RAM information
        ram_data = self.system_info_fetcher.get_memory_info()
        ram_percent = ram_data.get("ram_percent", 0.0)
        total_ram = ram_data.get("total_ram_gb", 0.0)
        used_ram = ram_data.get("used_ram_gb", 0.0)
        self.ram_label.setText(f"<b>RAM:</b> {used_ram:.2f} GB / {total_ram:.2f} GB")
        self.ram_usage_progress.setValue(int(ram_percent))
        self.ram_usage_progress.setFormat(f"memory usage: {ram_percent:.1f}%")

        # Update disk information (system drive)
        try:
            # Handle OS-specific root path
            if platform.system() == "Windows":
                disk_usage = psutil.disk_usage('C:\\')
            else:
                disk_usage = psutil.disk_usage('/')
            
            disk_total_gb = round(disk_usage.total / (1024**3), 2)
            disk_used_gb = round(disk_usage.used / (1024**3), 2)
            disk_percent = disk_usage.percent

            self.disk_label.setText(f"<b>Hard drive:</b> {disk_used_gb:.2f} GB / {disk_total_gb:.2f} GB")
            self.disk_usage_progress.setValue(int(disk_percent))
            self.disk_usage_progress.setFormat(f"Festplattenauslastung: {disk_percent:.1f}%")
        except Exception as e:
            # Handle disk access errors
            self.disk_label.setText(f"<b>Hard drive:</b> Fehler ({e})")
            self.disk_usage_progress.setValue(0)
            self.disk_usage_progress.setFormat("Not available")

        # Update network information
        net_io_rates = self.system_info_fetcher.get_network_io_rates()
        sent_kbs = net_io_rates.get("bytes_sent_rate_kbs", 0.0)
        recv_kbs = net_io_rates.get("bytes_recv_rate_kbs", 0.0)
        self.network_label.setText(f"<b>Network (Live):</b> Upload: {sent_kbs:.1f} KB/s | Download: {recv_kbs:.1f} KB/s")


class CPULayout(BaseInfoWidget):
    """Detailed CPU monitoring view with per-core usage"""
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # CPU specification labels
        self.cpu_model_label = QLabel("<b>CPU Model:</b> ")
        self.layout.addWidget(self.cpu_model_label)
        self.physical_cores_label = QLabel("<b>Pphysical cores:</b> ")
        self.layout.addWidget(self.physical_cores_label)
        self.logical_cores_label = QLabel("<b>logical cores:</b> ")
        self.layout.addWidget(self.logical_cores_label)
        self.current_freq_label = QLabel("<b>Current Frequency:</b> ")
        self.layout.addWidget(self.current_freq_label)
        self.max_freq_label = QLabel("<b>Maximum Frequency:</b> ")
        self.layout.addWidget(self.max_freq_label)
        self.cpu_total_percent_label = QLabel("<b>Total CPU Usage:</b> ")
        self.layout.addWidget(self.cpu_total_percent_label)

        self.layout.addSpacing(10)  # Vertical spacing

        # Grid layout for per-core monitoring
        self.cores_grid_layout = QGridLayout()
        self.core_labels = []
        self.core_progress_bars = []

        # Create progress bars for each logical core
        logical_cores = self.system_info_fetcher.get_cpu_info().get("logical_cores", 0)
        for i in range(logical_cores):
            row = i // 2  # 2 columns per row
            col_label = (i % 2) * 2
            col_progress = (i % 2) * 2 + 1

            # Core label
            core_label = QLabel(f"Kern {i+1}:")
            self.cores_grid_layout.addWidget(core_label, row, col_label)
            self.core_labels.append(core_label)

            # Core progress bar
            progress_bar = QProgressBar()
            progress_bar.setTextVisible(True)
            self.cores_grid_layout.addWidget(progress_bar, row, col_progress)
            self.core_progress_bars.append(progress_bar)
        
        self.layout.addLayout(self.cores_grid_layout)
        self.layout.addStretch(1)  # Bottom spacing

    def update_data(self):
        # Get CPU data from fetcher
        cpu_data = self.system_info_fetcher.get_cpu_info()
        cpu_model = self.system_info_fetcher.get_cpu_model()

        # Update CPU specs
        self.cpu_model_label.setText(f"<b>CPU Modell:</b> {cpu_model}")
        self.physical_cores_label.setText(f"<b>Physische Kerne:</b> {cpu_data.get('physical_cores', 'N/A')}")
        self.logical_cores_label.setText(f"<b>Logische Kerne:</b> {cpu_data.get('logical_cores', 'N/A')}")
        
        # Update frequency info
        current_freq = cpu_data.get('current_frequency_mhz', 'N/A')
        if current_freq is not None:
            self.current_freq_label.setText(f"<b>Current Frequency:</b> {current_freq:.2f} MHz")
        else:
            self.current_freq_label.setText("<b>Current Frequency:</b> N/A")

        max_freq = cpu_data.get('max_frequency_mhz', 'N/A')
        if max_freq is not None:
            self.max_freq_label.setText(f"<b>Maximum Frequency:</b> {max_freq:.2f} MHz")
        else:
            self.max_freq_label.setText("<b>Maximum Frequency:</b> N/A")

        # Update total CPU usage
        total_percent = cpu_data.get('total_percent', 0.0)
        self.cpu_total_percent_label.setText(f"<b>Total Usage:</b> {total_percent:.1f}%")

        # Update per-core usage
        per_cpu_percent = cpu_data.get('per_cpu_percent', [])
        for i, percent in enumerate(per_cpu_percent):
            if i < len(self.core_progress_bars):
                self.core_progress_bars[i].setValue(int(percent))
                self.core_progress_bars[i].setFormat(f"Kern {i+1}: {percent:.1f}%")


class MemoryLayout(BaseInfoWidget):
    """Detailed memory (RAM + Swap) monitoring view"""
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # RAM section
        self.ram_total_label = QLabel("<b>Total Memory:</b> ")
        self.layout.addWidget(self.ram_total_label)
        self.ram_available_label = QLabel("<b>Available Memory:</b> ")
        self.layout.addWidget(self.ram_available_label)
        self.ram_used_label = QLabel("<b>Used Memory:</b> ")
        self.layout.addWidget(self.ram_used_label)
        self.ram_percent_label = QLabel("<b>Memory Usage:</b> ")
        self.layout.addWidget(self.ram_percent_label)
        self.ram_progress_bar = QProgressBar()
        self.ram_progress_bar.setTextVisible(True)
        self.layout.addWidget(self.ram_progress_bar)

        self.layout.addSpacing(20)  # Section spacing

        # Swap section
        self.swap_total_label = QLabel("<b>Total Swap:</b> ")
        self.layout.addWidget(self.swap_total_label)
        self.swap_used_label = QLabel("<b>Used Swap:</b> ")
        self.layout.addWidget(self.swap_used_label)
        self.swap_percent_label = QLabel("<b>Swap Usage:</b> ")
        self.layout.addWidget(self.swap_percent_label)
        self.swap_progress_bar = QProgressBar()
        self.swap_progress_bar.setTextVisible(True)
        self.layout.addWidget(self.swap_progress_bar)

        self.layout.addStretch(1)  # Bottom spacing

    def update_data(self):
        # Get memory data from fetcher
        mem_data = self.system_info_fetcher.get_memory_info()

        # Update RAM info
        self.ram_total_label.setText(f"<b>Total RAM:</b> {mem_data.get('total_ram_gb', 0.0):.2f} GB")
        self.ram_available_label.setText(f"<b>Available RAM:</b> {mem_data.get('available_ram_gb', 0.0):.2f} GB")
        self.ram_used_label.setText(f"<b>Used RAM:</b> {mem_data.get('used_ram_gb', 0.0):.2f} GB")
        
        ram_percent = mem_data.get('ram_percent', 0.0)
        self.ram_percent_label.setText(f"<b>RAM Usage:</b> {ram_percent:.1f}%")
        self.ram_progress_bar.setValue(int(ram_percent))
        self.ram_progress_bar.setFormat(f"Load: {ram_percent:.1f}%")

        # Update Swap info
        self.swap_total_label.setText(f"<b>Total Swap:</b> {mem_data.get('total_swap_gb', 0.0):.2f} GB")
        self.swap_used_label.setText(f"<b>Used Swap:</b> {mem_data.get('used_swap_gb', 0.0):.2f} GB")
        
        swap_percent = mem_data.get('swap_percent', 0.0)
        self.swap_percent_label.setText(f"<b>Swap Usage:</b> {swap_percent:.1f}%")
        self.swap_progress_bar.setValue(int(swap_percent))
        self.swap_progress_bar.setFormat(f"Load: {swap_percent:.1f}%")


class NetworkLayout(BaseInfoWidget):
    """Network interface and traffic monitoring view"""
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Network summary labels
        self.hostname_label = QLabel("<b>Hostname:</b> ")
        self.layout.addWidget(self.hostname_label)
        self.primary_ip_label = QLabel("<b>Primary IP Address:</b> ")
        self.layout.addWidget(self.primary_ip_label)
        self.bytes_sent_label = QLabel("<b>Sent:</b> ")
        self.layout.addWidget(self.bytes_sent_label)
        self.bytes_recv_label = QLabel("<b>Received:</b> ")
        self.layout.addWidget(self.bytes_recv_label)

        self.layout.addSpacing(20)  # Section spacing

        # Network interfaces table
        self.interfaces_table = QTableWidget()
        self.interfaces_table.setColumnCount(3)
        self.interfaces_table.setHorizontalHeaderLabels(["Interface", "Type", "Address"])
        self.interfaces_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.interfaces_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.layout.addWidget(self.interfaces_table)

        self.layout.addStretch(1)  # Bottom spacing

    def update_data(self):
        # Get network data from fetcher
        net_data = self.system_info_fetcher.get_network_info()

        # Update summary info
        self.hostname_label.setText(f"<b>Hostname:</b> {net_data['Hostname']}")
        self.primary_ip_label.setText(f"<b>Primary IP Address:</b> {net_data['Primary IP']}")
        self.bytes_sent_label.setText(f"<b>Sent:</b> {net_data['Bytes Sent (GB)']:.2f} GB")
        self.bytes_recv_label.setText(f"<b>Received:</b> {net_data['Bytes Received (GB)']:.2f} GB")

        # Update interfaces table
        interfaces_data = net_data.get("Interfaces", {})
        self.interfaces_table.setRowCount(0)  # Clear existing rows

        row_count = 0
        for if_name, if_addrs in interfaces_data.items():
            for addr_info in if_addrs:
                self.interfaces_table.insertRow(row_count)
                self.interfaces_table.setItem(row_count, 0, QTableWidgetItem(if_name))

                # Handle different address types (IPv4, IPv6, MAC)
                if "IPv4" in addr_info:
                    self.interfaces_table.setItem(row_count, 1, QTableWidgetItem("IPv4"))
                    self.interfaces_table.setItem(row_count, 2, QTableWidgetItem(f"{addr_info['IPv4']} (Netzmaske: {addr_info.get('Netzmaske', 'N/A')})"))
                elif "IPv6" in addr_info:
                    self.interfaces_table.setItem(row_count, 1, QTableWidgetItem("IPv6"))
                    self.interfaces_table.setItem(row_count, 2, QTableWidgetItem(addr_info['IPv6']))
                elif "MAC" in addr_info:
                    self.interfaces_table.setItem(row_count, 1, QTableWidgetItem("MAC"))
                    self.interfaces_table.setItem(row_count, 2, QTableWidgetItem(addr_info['MAC']))
                row_count += 1


class ProcessesLayout(BaseInfoWidget):
    """Process monitoring table with detailed metrics"""
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Process table setup
        self.processes_table = QTableWidget()
        self.processes_table.setColumnCount(8)
        self.processes_table.setHorizontalHeaderLabels([
            "PID", "Name", "CPU (%)", "RAM (RSS MB)", "RAM (VMS MB)", "Threads", "User", "Start Time"
        ])
        self.processes_table.setSortingEnabled(True)
        self.processes_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.processes_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.processes_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.layout.addWidget(self.processes_table)
        self.layout.addStretch(1)  # Bottom spacing

    def update_data(self):
        # Get process data from fetcher
        processes_data = self.system_info_fetcher.get_processes_info()
        
        # Populate table with process data
        self.processes_table.setRowCount(len(processes_data))
        for row_idx, proc in enumerate(processes_data):
            # PID
            self.processes_table.setItem(row_idx, 0, QTableWidgetItem(str(proc.get('pid', 'N/A'))))
            
            # Process name
            self.processes_table.setItem(row_idx, 1, QTableWidgetItem(proc.get('name', 'N/A')))
            
            # CPU usage (with numeric sorting support)
            cpu_item = QTableWidgetItem(f"{proc.get('cpu_percent', 0.0):.1f}")
            cpu_item.setData(Qt.ItemDataRole.DisplayRole, float(proc.get('cpu_percent', 0.0)))
            self.processes_table.setItem(row_idx, 2, cpu_item)

            # RAM usage - RSS (Resident Set Size)
            ram_rss_item = QTableWidgetItem(f"{proc.get('memory_rss_mb', 0.0):.1f}")
            ram_rss_item.setData(Qt.ItemDataRole.DisplayRole, float(proc.get('memory_rss_mb', 0.0)))
            self.processes_table.setItem(row_idx, 3, ram_rss_item)

            # RAM usage - VMS (Virtual Memory Size)
            ram_vms_item = QTableWidgetItem(f"{proc.get('memory_vms_mb', 0.0):.1f}")
            ram_vms_item.setData(Qt.ItemDataRole.DisplayRole, float(proc.get('memory_vms_mb', 0.0)))
            self.processes_table.setItem(row_idx, 4, ram_vms_item)

            # Thread count
            num_threads_item = QTableWidgetItem(str(proc.get('num_threads', 'N/A')))
            num_threads_item.setData(Qt.ItemDataRole.DisplayRole, int(proc.get('num_threads', 0)))
            self.processes_table.setItem(row_idx, 5, num_threads_item)

            # User and start time
            self.processes_table.setItem(row_idx, 6, QTableWidgetItem(proc.get('username', 'N/A')))
            self.processes_table.setItem(row_idx, 7, QTableWidgetItem(proc.get('create_time', 'N/A')))


class ProgramsLayout(BaseInfoWidget):
    """Installed programs list view"""
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Programs table setup
        self.programs_table = QTableWidget()
        self.programs_table.setColumnCount(1)
        self.programs_table.setHorizontalHeaderLabels(["Program Name"])
        self.programs_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.programs_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.programs_table.setSortingEnabled(True)

        self.layout.addWidget(self.programs_table)
        self.layout.addStretch(1)  # Bottom spacing

    def update_data(self):
        # Get installed programs from fetcher
        programs_list = self.system_info_fetcher.get_installed_programs()
        
        # Populate table with program names
        self.programs_table.setRowCount(len(programs_list))
        for row_idx, program_name in enumerate(programs_list):
            self.programs_table.setItem(row_idx, 0, QTableWidgetItem(program_name))


class LogsLayout(BaseInfoWidget):
    """System metrics logging view with export/clear functionality"""
    def __init__(self, system_info_fetcher, db_manager, parent=None):
        self.db_manager = db_manager  # Database access object
        super().__init__(system_info_fetcher, parent)

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Log table setup
        self.log_table = QTableWidget()
        self.log_table.setColumnCount(6)
        self.log_table.setHorizontalHeaderLabels([
            "Timestamp", "CPU (%)", "RAM (%)", "RAM (GB)", "Bytes Sent (GB)", "Bytes Recv (GB)"
        ])
        self.log_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.log_table.setSortingEnabled(True)
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.layout.addWidget(self.log_table)

        # Button panel
        button_layout = QHBoxLayout()
        
        # Refresh button
        self.refresh_button = QPushButton("Update Logs")
        self.refresh_button.clicked.connect(self.update_data)
        button_layout.addWidget(self.refresh_button)

        # Export button
        self.export_button = QPushButton("Export Logs (CSV)")
        self.export_button.clicked.connect(self.export_logs_to_csv)
        button_layout.addWidget(self.export_button)

        # Clear logs button
        self.clear_logs_button = QPushButton("Clear Logs")
        self.clear_logs_button.clicked.connect(self.confirm_clear_logs)
        button_layout.addWidget(self.clear_logs_button)
        
        self.layout.addLayout(button_layout)
        self.layout.addStretch(1)  # Bottom spacing

    def update_data(self):
        # Retrieve logs from database
        logs = self.db_manager.get_all_logs()

        if logs:
            # Populate table with log data
            self.log_table.setRowCount(len(logs))
            for row_idx, log_entry in enumerate(logs):
                # Timestamp
                self.log_table.setItem(row_idx, 0, QTableWidgetItem(log_entry[0]))
                
                # CPU usage (with numeric sorting)
                cpu_item = QTableWidgetItem(f"{log_entry[1]:.1f}")
                cpu_item.setData(Qt.ItemDataRole.DisplayRole, float(log_entry[1]))
                self.log_table.setItem(row_idx, 1, cpu_item)

                # RAM percentage (with numeric sorting)
                ram_percent_item = QTableWidgetItem(f"{log_entry[2]:.1f}")
                ram_percent_item.setData(Qt.ItemDataRole.DisplayRole, float(log_entry[2]))
                self.log_table.setItem(row_idx, 2, ram_percent_item)

                # RAM usage in GB (with numeric sorting)
                ram_gb_item = QTableWidgetItem(f"{log_entry[3]:.2f}")
                ram_gb_item.setData(Qt.ItemDataRole.DisplayRole, float(log_entry[3]))
                self.log_table.setItem(row_idx, 3, ram_gb_item)

                # Network sent (with numeric sorting)
                bytes_sent_item = QTableWidgetItem(f"{log_entry[4]:.2f}")
                bytes_sent_item.setData(Qt.ItemDataRole.DisplayRole, float(log_entry[4]))
                self.log_table.setItem(row_idx, 4, bytes_sent_item)

                # Network received (with numeric sorting)
                bytes_recv_item = QTableWidgetItem(f"{log_entry[5]:.2f}")
                bytes_recv_item.setData(Qt.ItemDataRole.DisplayRole, float(log_entry[5]))
                self.log_table.setItem(row_idx, 5, bytes_recv_item)
        else:
            # Handle no logs case
            self.log_table.setRowCount(1)
            self.log_table.setItem(0, 0, QTableWidgetItem("Keine Protokolleinträge gefunden."))
            self.log_table.setSpan(0, 0, 1, 6)  # Merge cells for message

    def export_logs_to_csv(self):
        """Export logs to CSV file"""
        # File save dialog
        options = QFileDialog.Option.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Logs",
                                                   "system_metrics.csv", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_name:
            logs = self.db_manager.get_all_logs()
            try:
                # Write CSV file
                with open(file_name, 'w', newline='', encoding='utf-8') as csvfile:
                    csv_writer = csv.writer(csvfile)
                    csv_writer.writerow(["Timestamp", "CPU (%)", "RAM (%)", "RAM (GB)", "Bytes Sent (GB)", "Bytes Recv (GB)"])
                    csv_writer.writerows(logs)
                # Success notification
                QMessageBox.information(self, "Export Successful", f"Logs were successfully exported to:\n{file_name}")
            except Exception as e:
                # Error handling
                QMessageBox.critical(self, "Export Error", f"Error exporting logs: {e}")

    def confirm_clear_logs(self):
        """Confirm log deletion with user"""
        reply = QMessageBox.question(self, "Clear Logs",
                                     "Are you sure you want to delete ALL system metric logs?\n
                                     "This action CANNOT be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Clear logs and update UI
            self.db_manager.clear_all_logs()
            self.update_data()
            QMessageBox.information(self, "Logs deleted", "All system metric logs have been deleted.")


class DateAxisItem(pg.AxisItem):
    """Custom axis for displaying datetime values"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        """Convert timestamp values to formatted datetime strings"""
        strings = []
        for val in values:
            try:
                # Convert Unix timestamp to QDateTime
                dt = QDateTime.fromSecsSinceEpoch(int(val))
                # Format according to system locale
                strings.append(dt.toString(QLocale.system().dateTimeFormat(QLocale.FormatType.ShortFormat)))
            except ValueError:
                strings.append('')
        return strings


class GraphLayout(BaseInfoWidget):
    """Interactive graphs for historical system metrics"""
    def __init__(self, system_info_fetcher, db_manager, parent=None):
        self.db_manager = db_manager  # Database access
        super().__init__(system_info_fetcher, parent)

    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Tab widget for different graph types
        self.graph_tab_widget = QTabWidget()
        self.layout.addWidget(self.graph_tab_widget)

        # --- CPU Graph Tab ---
        self.cpu_plot_widget = pg.PlotWidget(axisItems={'bottom': DateAxisItem(orientation='bottom')})
        self.cpu_plot_widget.setTitle("CPU Usage Over Time")
        self.cpu_plot_widget.setLabel('left', "CPU Usage", units='%')
        self.cpu_plot_widget.setLabel('bottom', "Time")
        self.cpu_plot_widget.addLegend()
        self.cpu_curve = self.cpu_plot_widget.plot(name="CPU (%)", pen='y')  # Yellow line
        self.graph_tab_widget.addTab(self.cpu_plot_widget, "CPU")

        # --- RAM Graph Tab ---
        self.ram_plot_widget = pg.PlotWidget(axisItems={'bottom': DateAxisItem(orientation='bottom')})
        self.ram_plot_widget.setTitle("RAM Usage Over Time")
        self.ram_plot_widget.setLabel('left', "RAM Usage", units='%')
        self.ram_plot_widget.setLabel('bottom', "Zeit")
        self.ram_plot_widget.addLegend()
        self.ram_curve_percent = self.ram_plot_widget.plot(name="RAM (%)", pen='b')  # Blue line
        self.ram_curve_gb = self.ram_plot_widget.plot(name="RAM (GB)", pen='r')  # Red line
        self.graph_tab_widget.addTab(self.ram_plot_widget, "RAM")

        # --- Netzwerk Graph Tab ---
        self.network_plot_widget = pg.PlotWidget(axisItems={'bottom': DateAxisItem(orientation='bottom')})
        self.network_plot_widget.setTitle("Network Throughput Over Time")
        self.network_plot_widget.setLabel('left', "Throughput", units='KB/s')
        self.network_plot_widget.setLabel('bottom', "Time")
        self.network_plot_widget.addLegend()
        self.bytes_sent_rate_curve = self.network_plot_widget.plot(name="Gesendet (KB/s)", pen='c')  # Cyan line
        self.bytes_recv_rate_curve = self.network_plot_widget.plot(name="Empfangen (KB/s)", pen='m')  # Magenta line
        self.graph_tab_widget.addTab(self.network_plot_widget, "Network")

        # Refresh button
        self.refresh_button = QPushButton("Update Graphs")
        self.refresh_button.clicked.connect(self.update_data)
        self.layout.addWidget(self.refresh_button)

        self.layout.addStretch(1)  # Bottom spacing

    def update_data(self):
        # Retrieve logs from database
        logs = self.db_manager.get_all_logs()

        if logs:
            # Initialize data arrays
            timestamps = []
            cpu_percents = []
            ram_percents = []
            ram_used_gbs = []
            bytes_sent_rates = []
            bytes_recv_rates = []

            # For network rate calculation
            prev_ts = None
            prev_bytes_sent_gb = None
            prev_bytes_recv_gb = None

            # Process each log entry
            for log_entry in logs:
                try:
                    # Convert timestamp to Unix time
                    current_ts_dt = datetime.strptime(log_entry[0], "%Y-%m-%d %H:%M:%S")
                    current_ts_unix = current_ts_dt.timestamp()

                    # Extract metrics
                    current_cpu_percent = log_entry[1]
                    current_ram_percent = log_entry[2]
                    current_ram_used_gb = log_entry[3]
                    current_bytes_sent_gb = log_entry[4]
                    current_bytes_recv_gb = log_entry[5]

                    # Append to data arrays
                    timestamps.append(current_ts_unix)
                    cpu_percents.append(current_cpu_percent)
                    ram_percents.append(current_ram_percent)
                    ram_used_gbs.append(current_ram_used_gb)

                    # Calculate network rates if possible
                    if prev_ts is not None and prev_bytes_sent_gb is not None and prev_bytes_recv_gb is not None:
                        time_diff_secs = current_ts_unix - prev_ts
                        if time_diff_secs > 0:
                            # Calculate rate in KB/s
                            diff_bytes_sent_gb = current_bytes_sent_gb - prev_bytes_sent_gb
                            diff_bytes_recv_gb = current_bytes_recv_gb - prev_bytes_recv_gb

                            bytes_sent_rate_kbs = (diff_bytes_sent_gb * (1024**2)) / time_diff_secs
                            bytes_recv_rate_kbs = (diff_bytes_recv_gb * (1024**2)) / time_diff_secs

                            bytes_sent_rates.append(max(0, bytes_sent_rate_kbs))
                            bytes_recv_rates.append(max(0, bytes_recv_rate_kbs))
                        else:
                            bytes_sent_rates.append(0.0)
                            bytes_recv_rates.append(0.0)
                    else:
                        # First data point
                        bytes_sent_rates.append(0.0)
                        bytes_recv_rates.append(0.0)
                    
                    # Update previous values for next calculation
                    prev_ts = current_ts_unix
                    prev_bytes_sent_gb = current_bytes_sent_gb
                    prev_bytes_recv_gb = current_bytes_recv_gb

                except (ValueError, TypeError) as e:
                    # Skip invalid entries
                    continue

            # Convert to numpy arrays for plotting
            x_data = np.array(timestamps)
            y_cpu = np.array(cpu_percents)
            y_ram_percent = np.array(ram_percents)
            y_ram_gb = np.array(ram_used_gbs)
            y_bytes_sent_rate = np.array(bytes_sent_rates)
            y_bytes_recv_rate = np.array(bytes_recv_rates)

            # Update graph curves
            self.cpu_curve.setData(x=x_data, y=y_cpu)
            self.ram_curve_percent.setData(x=x_data, y=y_ram_percent)
            self.ram_curve_gb.setData(x=x_data, y=y_ram_gb)
            self.bytes_sent_rate_curve.setData(x=x_data, y=y_bytes_sent_rate)
            self.bytes_recv_rate_curve.setData(x=x_data, y=y_bytes_recv_rate)

        else:
            # Clear graphs if no data
            self.cpu_curve.setData([], [])
            self.ram_curve_percent.setData([], [])
            self.ram_curve_gb.setData([], [])
            self.bytes_sent_rate_curve.setData([], [])
            self.bytes_recv_rate_curve.setData([], [])
