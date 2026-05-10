import unittest
import os
import sys

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

from workspace_manager import WorkspaceManager

class TestDataMgmt(unittest.TestCase):
    def setUp(self):
        self.wm = WorkspaceManager("tests/data/temp")
        if not os.path.exists("tests/data/temp"):
            os.makedirs("tests/data/temp")

    def test_session_management(self):
        self.wm.save_session("test.haba", 10)
        session = self.wm.load_session()
        self.assertEqual(session["last_file"], "test.haba")
        self.assertEqual(session["cursor_pos"], 10)

    def test_auto_save(self):
        self.wm.auto_save("Draft content", "tests/data/temp/test.haba")
        self.assertTrue(os.path.exists("tests/data/temp/test.haba.autosave"))
        with open("tests/data/temp/test.haba.autosave", 'r') as f:
            self.assertEqual(f.read(), "Draft content")

if __name__ == '__main__':
    unittest.main()
