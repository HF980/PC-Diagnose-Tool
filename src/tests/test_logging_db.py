import sys
import os
import unittest

# Pfad zum src-Ordner hinzufügen, relativ zur Testdatei
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'src'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.db_manager import LoggingDBManager


class TestLoggingDBManager(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_system_logs.db"
        self.db_manager = LoggingDBManager(db_name=self.test_db)

    def tearDown(self):
        self.db_manager.close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_log_and_retrieve(self):
        success = self.db_manager.log_system_metrics(10.5, 20.5, 3.2, 1.1, 2.2)
        self.assertTrue(success)

        logs = self.db_manager.get_all_logs()
        self.assertTrue(len(logs) > 0)
        self.assertEqual(len(logs[0]), 6)  # 6 columns: timestamp + 5 metrics

if __name__ == "__main__":
    unittest.main()