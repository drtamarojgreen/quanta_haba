import unittest
import sys
import os
import json

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

from haba_parser import HabaParser, HabaData

class TestIO(unittest.TestCase):
    def setUp(self):
        self.parser = HabaParser()
        self.temp_dir = "tests/data/temp"

    def test_json_serialization_roundtrip(self):
        data = HabaData()
        data.content = "JSON Test"
        data.presentation_items = [("div", "color: blue")]
        data.script = "alert(1);"
        data.to_do = "Integrate AI"

        json_str = self.parser.to_json(data)
        reparsed = self.parser.from_json(json_str)

        self.assertEqual(data.content, reparsed.content)
        self.assertEqual(data.presentation_items, reparsed.presentation_items)
        self.assertEqual(data.script, reparsed.script)
        self.assertEqual(data.to_do, reparsed.to_do)

if __name__ == '__main__':
    unittest.main()
