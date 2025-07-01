#********************************************#
# @ #!/usr/bin/env
# @Project: pc_diagnose_tool
# @file name: db_manager.py
# @creation date: 30.06.2025
# @lastmodified: 30.06.2025
# @version: 1.0
#********************************************#

# db_manager.py
import sqlite3
import os

class LoggingDBManager:
    def __init__(self, db_path="PC_Diagnosis_Logs", db_name="system_metrics.db"):
        # Stelle sicher, dass das Verzeichnis existiert
        self.log_dir = os.path.expanduser(db_path)
        os.makedirs(self.log_dir, exist_ok=True)
        self.db_name = os.path.join(self.log_dir, db_name)
        self.conn = None
        self.cursor = None
        self._connect_db()
        self._create_table()

    def _connect_db(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
            # print(f"Datenbank '{self.db_name}' erfolgreich initialisiert.")
        except sqlite3.Error as e:
            print(f"Fehler beim Verbinden mit der Datenbank: {e}")
            self.conn = None
            self.cursor = None

    def _create_table(self):
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
        if self.cursor:
            try:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO system_logs (timestamp, cpu_percent, ram_percent, ram_used_gb, bytes_sent_gb, bytes_recv_gb)
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
                print(f"Fehler beim Schreiben des Log-Eintrags: {e}")
    def test_log_and_retrieve(self):
        snapshot = {
            "timestamp": "2025-06-30 12:00:00",
            "cpu_percent": 10.5,
            "ram_percent": 20.5,
            "ram_used_gb": 3.2,
            "bytes_sent_gb": 1.1,
            "bytes_recv_gb": 2.2
        }
        self.db_manager.log_snapshot(snapshot)
        
        logs = self.db_manager.get_all_logs()
        self.assertTrue(len(logs) > 0)
        self.assertEqual(len(logs[0]), 6)  # timestamp + 5 metrics

    def log_system_metrics(self, cpu, ram, used_gb, sent, recv):
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
        if self.cursor:
            try:
                self.cursor.execute("SELECT * FROM system_logs ORDER BY timestamp ASC")
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Fehler beim Abrufen der Logs: {e}")
        return []

    def clear_all_logs(self):
        """Löscht alle Einträge aus der system_logs Tabelle."""
        if self.cursor:
            try:
                self.cursor.execute("DELETE FROM system_logs")
                self.conn.commit()
                # print("Alle Logs erfolgreich gelöscht.")
            except sqlite3.Error as e:
                print(f"Fehler beim Löschen der Logs: {e}")

    def close(self):
        if self.conn:
            self.conn.close()
            # print("Datenbankverbindung geschlossen.")

