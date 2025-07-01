import sys
import os
import unittest
from src.system_info import SystemInfoFetcher
# Absoluter Pfad zum src-Ordner
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))

if src_path not in sys.path:
    sys.path.insert(0, src_path)

class TestSystemInfoFetcher(unittest.TestCase):
    def setUp(self):
        self.fetcher = SystemInfoFetcher()

    def test_get_cpu_model(self):
        model = self.fetcher.get_cpu_model()
        self.assertIsInstance(model, str)
        self.assertTrue(len(model) > 0)

    def test_get_cpu_info(self):
        info = self.fetcher.get_cpu_info()
        self.assertIn("total_percent", info)
        self.assertIn("per_cpu_percent", info)
        self.assertIsInstance(info["per_cpu_percent"], list)

    def test_get_system_snapshot(self):
        snapshot = self.fetcher.get_system_snapshot()
        self.assertIn("cpu_percent", snapshot)
        self.assertIn("ram_percent", snapshot)
        self.assertIn("timestamp", snapshot)

if __name__ == "__main__":
    unittest.main()