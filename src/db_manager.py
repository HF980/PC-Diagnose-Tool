#********************************************#
# @ #!/usr/bin/env
# @Project: pc_diagnose_tool
# @file name: db_manager.py
# @creation date: 30.06.2025
# @lastmodified: 30.06.2025
# @version: 1.0
#********************************************#

#------------------------------------------------------------------------------
# Purpose

# This module provides a class called LoggingDBManager that handles the logging and management
# of system metrics such as CPU usage, RAM usage, and network traffic (sent/received data).
# It stores the logs in a local SQLite database for future analysis or monitoring purposes.

# Method                            Description
# -------                           -------------
# __init__()                        Creates the logging directory and initializes the SQLite database.
# _connect_db()                     Establishes a connection to the database file.
# _create_table()                   Creates the system_logs table if it doesn’t already exist.
# log_snapshot(data)                Inserts or updates a system snapshot (timestamp + metrics).
# get_all_logs()                    Returns all stored logs in chronological order.
# clear_all_logs()                  Deletes all records from the log table.
# close()                           Closes the database connection safely.

# Directory Structure
# -------------------

# PC_Diagnosis_Logs/
# └── system_metrics.db              SQLite database file containing log entries


# Use Case
# --------
# This database manager is ideal for:
#  Background system monitoring
#  Diagnostic snapshots
#  Exportable logs for performance analysis

#------------------------------------------------------------------------------

import sqlite3
import os

class LoggingDBManager:
    def __init__(self, db_path="PC_Diagnosis_Logs", db_name="system_metrics.db"):
        """
        Ensures the logging directory exists and initializes the SQLite database.
        Creates the directory if it doesn't exist, then connects to the DB and
        creates the system_logs table if needed.
        """
        self.log_dir = os.path.expanduser(db_path)  # Expand user (~) if present
        os.makedirs(self.log_dir, exist_ok=True)   # Create directory if missing
        self.db_name = os.path.join(self.log_dir, db_name)  # Full DB file path
        self.conn = None
        self.cursor = None
        self._connect_db()     # Establish DB connection
        self._create_table()   # Create logs table if it doesn't exist

    def _connect_db(self):
        """
        Connects to the SQLite database and creates a cursor.
        Prints an error if connection fails.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            # print(f"Database '{self.db_name}' successfully initialized.")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            self.conn = None
            self.cursor = None

    def _create_table(self):
        """
        Creates the 'system_logs' table with columns for timestamp and metrics.
        Uses IF NOT EXISTS to avoid errors if table is already there.
        """
        if self.cursor:
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    timestamp TEXT PRIMARY KEY,
                    cpu_percent REAL,
                    ram_percent REAL,
                    ram_used_gb REAL,
                    bytes_sent_gb REAL,
                    bytes_recv_gb REAL
                )
            ''')
            self.conn.commit()

    def log_snapshot(self, snapshot_data):
        """
        Inserts or replaces a snapshot entry into the system_logs table.
        snapshot_data should be a dict containing:
          timestamp, cpu_percent, ram_percent, ram_used_gb, bytes_sent_gb, bytes_recv_gb
        """
        if self.cursor:
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO system_logs 
                    (timestamp, cpu_percent, ram_percent, ram_used_gb, bytes_sent_gb, bytes_recv_gb)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    snapshot_data["timestamp"],
                    snapshot_data["cpu_percent"],
                    snapshot_data["ram_percent"],
                    snapshot_data["ram_used_gb"],
                    snapshot_data["bytes_sent_gb"],
                    snapshot_data["bytes_recv_gb"]
                ))
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Error writing log entry: {e}")

    def log_system_metrics(self, cpu, ram, used_gb, sent, recv):
        """
        Helper method to create a snapshot with the current datetime and log it.
        Parameters:
          cpu   - CPU usage percent
          ram   - RAM usage percent
          used_gb - RAM used in GB
          sent  - Bytes sent in GB
          recv  - Bytes received in GB
        """
        from datetime import datetime
        snapshot = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_percent": cpu,
            "ram_percent": ram,
            "ram_used_gb": used_gb,
            "bytes_sent_gb": sent,
            "bytes_recv_gb": recv
        }
        self.log_snapshot(snapshot)
        return True

    def get_all_logs(self):
        """
        Retrieves all log entries ordered by timestamp ascending.
        Returns a list of tuples or an empty list on failure.
        """
        if self.cursor:
            try:
                self.cursor.execute("SELECT * FROM system_logs ORDER BY timestamp ASC")
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error fetching logs: {e}")
        return []

    def clear_all_logs(self):
        """
        Deletes all records from the system_logs table.
        """
        if self.cursor:
            try:
                self.cursor.execute("DELETE FROM system_logs")
                self.conn.commit()
                # print("All logs successfully deleted.")
            except sqlite3.Error as e:
                print(f"Error deleting logs: {e}")

    def close(self):
        """
        Safely closes the database connection.
        """
        if self.conn:
            self.conn.close()
            # print("Database connection closed.")

