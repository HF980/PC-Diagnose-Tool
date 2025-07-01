#********************************************#
# @ #!/usr/bin/env
# @Project: pc_diagnose_tool
# @file name: logging_db.py
# @creation date: 30.06.2025
# @lastmodified: 30.06.2025
# @version: 1.0
#********************************************#

# logging_db.py
import sqlite3
import os
import sys
from datetime import datetime

# Absolute path to the src folder
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from db_manager import LoggingDBManager  # Assuming this is used somewhere else

class LoggingDBManager:
    """
    Manages the SQLite database for system logging.
    Stores metrics such as CPU usage and RAM usage.
    """
    def __init__(self, db_name="system_logs.db"):
        self.db_name = db_name
        self.conn = None
        self.init_db()

    def init_db(self):
        """
        Initializes the database connection and creates the table if it doesn't exist.
        """
        try:
            self.conn = sqlite3.connect(self.db_name)
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    timestamp TEXT PRIMARY KEY,
                    cpu_percent REAL,
                    ram_percent REAL,
                    ram_used_gb REAL,
                    bytes_sent_gb REAL,
                    bytes_recv_gb REAL
                )
            ''')
            self.conn.commit()
            print(f"Database '{self.db_name}' successfully initialized.")
        except sqlite3.Error as e:
            print(f"Error initializing database '{self.db_name}': {e}")
            self.conn = None  # Invalidate connection on error

    def log_system_metrics(self, cpu_percent, ram_percent, ram_used_gb, bytes_sent_gb, bytes_recv_gb):
        """
        Stores current system metrics into the database.
        """
        if not self.conn:
            print("Error: Database connection is not active. Cannot log data.")
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO system_metrics (timestamp, cpu_percent, ram_percent, ram_used_gb, bytes_sent_gb, bytes_recv_gb)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, cpu_percent, ram_percent, ram_used_gb, bytes_sent_gb, bytes_recv_gb))
            self.conn.commit()
            # print(f"Logged: CPU={cpu_percent}%, RAM={ram_percent}%")
            return True
        except sqlite3.IntegrityError:  # Entry with this timestamp already exists
            # print(f"Warning: Entry for timestamp {timestamp} already exists, skipped.")
            return False
        except sqlite3.Error as e:
            print(f"Error logging data: {e}")
            self.conn.rollback()
            return False

    def get_all_logs(self):
        """
        Returns all stored metrics.
        Returns a list of tuples, each tuple is a row.
        """
        if not self.conn:
            print("Error: Database connection is not active. Cannot retrieve logs.")
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM system_metrics ORDER BY timestamp ASC")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving logs: {e}")
            return []

    def close_connection(self):
        """
        Closes the database connection.
        Should be called when the application is exiting.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            print(f"Database connection to '{self.db_name}' closed.")

# Example usage (for testing database functions)
if __name__ == "__main__":
    db_manager = LoggingDBManager("test_system_logs.db")

    # Log some data
    db_manager.log_system_metrics(25.5, 45.2, 8.1, 10.5, 20.3)
    import time
    time.sleep(1)  # Short pause to get different timestamps
    db_manager.log_system_metrics(30.1, 50.0, 9.2, 11.0, 21.5)

    print("\nAll stored logs:")
    for row in db_manager.get_all_logs():
        print(row)

    db_manager.close_connection()

    # Optional: delete test database file to start fresh each test
    if os.path.exists("test_system_logs.db"):
        os.remove("test_system_logs.db")
        print("Test database deleted.")
