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
from datetime import datetime

# Absoluter Pfad zum src-Ordner
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from db_manager import LoggingDBManager

class LoggingDBManager:
    """
    Verwaltet die SQLite-Datenbank für die Systemprotokollierung.
    Speichert Metriken wie CPU-Auslastung und RAM-Nutzung.
    """
    def __init__(self, db_name="system_logs.db"):
        self.db_name = db_name
        self.conn = None
        self.init_db()

    def init_db(self):
        """
        Initialisiert die Datenbankverbindung und erstellt die Tabelle, falls sie nicht existiert.
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
            print(f"Datenbank '{self.db_name}' erfolgreich initialisiert.")
        except sqlite3.Error as e:
            print(f"Fehler beim Initialisieren der Datenbank '{self.db_name}': {e}")
            self.conn = None # Verbindung bei Fehler ungültig machen

    def log_system_metrics(self, cpu_percent, ram_percent, ram_used_gb, bytes_sent_gb, bytes_recv_gb):
        """
        Speichert aktuelle Systemmetriken in der Datenbank.
        """
        if not self.conn:
            print("Fehler: Datenbankverbindung nicht aktiv. Kann nicht protokollieren.")
            return False

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO system_metrics (timestamp, cpu_percent, ram_percent, ram_used_gb, bytes_sent_gb, bytes_recv_gb)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (timestamp, cpu_percent, ram_percent, ram_used_gb, bytes_sent_gb, bytes_recv_gb))
            self.conn.commit()
            # print(f"Protokolliert: CPU={cpu_percent}%, RAM={ram_percent}%")
            return True
        except sqlite3.IntegrityError: # Falls ein Eintrag mit diesem Timestamp bereits existiert
            # print(f"Warnung: Eintrag für Timestamp {timestamp} existiert bereits, übersprungen.")
            return False
        except sqlite3.Error as e:
            print(f"Fehler beim Protokollieren der Daten: {e}")
            self.conn.rollback()
            return False

    def get_all_logs(self):
        """
        Gibt alle gespeicherten Metriken zurück.
        Rückgabe: Liste von Tupeln, jede Tupel ist eine Zeile.
        """
        if not self.conn:
            print("Fehler: Datenbankverbindung nicht aktiv. Kann keine Logs abrufen.")
            return []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM system_metrics ORDER BY timestamp ASC")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Fehler beim Abrufen der Logs: {e}")
            return []

    def close_connection(self):
        """
        Schließt die Datenbankverbindung.
        Sollte beim Beenden der Anwendung aufgerufen werden.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            print(f"Datenbankverbindung zu '{self.db_name}' geschlossen.")

# Beispielnutzung (zum Testen der Datenbankfunktionen)
if __name__ == "__main__":
    db_manager = LoggingDBManager("test_system_logs.db")

    # Daten protokollieren
    db_manager.log_system_metrics(25.5, 45.2, 8.1, 10.5, 20.3)
    import time
    time.sleep(1) # Kurze Pause, um unterschiedliche Timestamps zu erhalten
    db_manager.log_system_metrics(30.1, 50.0, 9.2, 11.0, 21.5)

    print("\nAlle gespeicherten Logs:")
    for row in db_manager.get_all_logs():
        print(row)

    db_manager.close_connection()

    #Optional: Datenbankdatei löschen, um bei jedem Test neu zu starten
    if os.path.exists("test_system_logs.db"):
        os.remove("test_system_logs.db")
        print("Test-Datenbank gelöscht.")
