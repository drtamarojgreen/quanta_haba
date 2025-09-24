import unittest
import sys
import os

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

from haba_parser import HabaParser, HabaData


class TestHabaParser(unittest.TestCase):
    """Unit tests for HabaParser class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.parser = HabaParser()
        
    def test_parser_initialization(self):
        """Test that parser initializes correctly"""
        self.assertIsInstance(self.parser, HabaParser)
        
    def test_parse_empty_content(self):
        """Test parsing empty content"""
        result = self.parser.parse("")
        self.assertIsInstance(result, HabaData)
        self.assertEqual(result.content, "")
        self.assertEqual(len(result.presentation_items), 0)
        self.assertEqual(result.script, "")
        
    def test_parse_content_only(self):
        """Test parsing content without presentation or script layers"""
        content = "Hello World\nThis is a test"
        result = self.parser.parse(content)
        
        self.assertEqual(result.content, content)
        self.assertEqual(len(result.presentation_items), 0)
        self.assertEqual(result.script, "")
        
    def test_parse_with_presentation_layer(self):
        """Test parsing content with presentation layer"""
        haba_content = """Hello World
This is a test

---PRESENTATION---
div: color: 'blue'; font-size: '16px'
p: color: 'red'; font-weight: 'bold'
"""
        result = self.parser.parse(haba_content)
        
        self.assertEqual(result.content.strip(), "Hello World\nThis is a test")
        self.assertEqual(len(result.presentation_items), 2)
        self.assertEqual(result.presentation_items[0], ("div", "color: 'blue'; font-size: '16px'"))
        self.assertEqual(result.presentation_items[1], ("p", "color: 'red'; font-weight: 'bold'"))
        
    def test_parse_with_script_layer(self):
        """Test parsing content with script layer"""
        haba_content = """Hello World

---SCRIPT---
console.log('Hello from script');
alert('Test');
"""
        result = self.parser.parse(haba_content)
        
        self.assertEqual(result.content.strip(), "Hello World")
        self.assertEqual(result.script.strip(), "console.log('Hello from script');\nalert('Test');")
        
    def test_parse_complete_haba_file(self):
        """Test parsing complete .haba file with all layers"""
        haba_content = """Welcome to QuantaHaba!
This is a sample document.
Let's test all features.

---PRESENTATION---
h1: color: 'blue'; font-size: '24px'
p: color: 'black'; font-size: '14px'
div: background: 'lightgray'; padding: '10px'

---SCRIPT---
console.log('Document loaded');
function greet() {
    alert('Hello from QuantaHaba!');
}
greet();
"""
        result = self.parser.parse(haba_content)
        
        # Check content
        expected_content = "Welcome to QuantaHaba!\nThis is a sample document.\nLet's test all features."
        self.assertEqual(result.content.strip(), expected_content)
        
        # Check presentation items
        self.assertEqual(len(result.presentation_items), 3)
        self.assertEqual(result.presentation_items[0], ("h1", "color: 'blue'; font-size: '24px'"))
        self.assertEqual(result.presentation_items[1], ("p", "color: 'black'; font-size: '14px'"))
        self.assertEqual(result.presentation_items[2], ("div", "background: 'lightgray'; padding: '10px'"))
        
        # Check script
        expected_script = """console.log('Document loaded');
function greet() {
    alert('Hello from QuantaHaba!');
}
greet();"""
        self.assertEqual(result.script.strip(), expected_script)
        
    def test_build_from_haba_data(self):
        """Test building .haba content from HabaData object"""
        # Create HabaData object
        haba_data = HabaData()
        haba_data.content = "Test content\nSecond line"
        haba_data.presentation_items = [
            ("h1", "color: 'red'"),
            ("p", "font-size: '12px'")
        ]
        haba_data.script = "console.log('test');"
        
        # Build content
        result = self.parser.build(haba_data)
        
        # Verify structure
        self.assertIn("Test content\nSecond line", result)
        self.assertIn("---PRESENTATION---", result)
        self.assertIn("h1: color: 'red'", result)
        self.assertIn("p: font-size: '12px'", result)
        self.assertIn("---SCRIPT---", result)
        self.assertIn("console.log('test');", result)
        
    def test_parse_build_roundtrip(self):
        """Test that parsing and building are inverse operations"""
        original_content = """Test Document
Line two
Line three

---PRESENTATION---
h1: color: 'blue'
p: font-size: '14px'
span: font-weight: 'bold'

---SCRIPT---
console.log('roundtrip test');
var x = 42;
"""
        # Parse then build
        parsed = self.parser.parse(original_content)
        rebuilt = self.parser.build(parsed)
        
        # Parse the rebuilt content
        reparsed = self.parser.parse(rebuilt)
        
        # Compare original parsed with reparsed
        self.assertEqual(parsed.content.strip(), reparsed.content.strip())
        self.assertEqual(len(parsed.presentation_items), len(reparsed.presentation_items))
        self.assertEqual(parsed.script.strip(), reparsed.script.strip())


class TestHabaData(unittest.TestCase):
    """Unit tests for HabaData class"""
    
    def test_haba_data_initialization(self):
        """Test HabaData initialization"""
        data = HabaData()
        self.assertEqual(data.content, "")
        self.assertEqual(data.presentation_items, [])
        self.assertEqual(data.script, "")
        
    def test_haba_data_with_values(self):
        """Test HabaData with initial values"""
        data = HabaData()
        data.content = "Test content"
        data.presentation_items = [("div", "color: 'red'")]
        data.script = "console.log('test');"
        
        self.assertEqual(data.content, "Test content")
        self.assertEqual(len(data.presentation_items), 1)
        self.assertEqual(data.presentation_items[0], ("div", "color: 'red'"))
        self.assertEqual(data.script, "console.log('test');")


class TestHabaParserBDD(unittest.TestCase):
    """BDD-style tests for HabaParser"""
    
    def setUp(self):
        self.parser = HabaParser()
        
    def test_given_empty_haba_content_when_parsed_then_returns_empty_data(self):
        """
        Given: An empty .haba content string
        When: The content is parsed
        Then: Returns HabaData with empty fields
        """
        # Given
        empty_content = ""
        
        # When
        result = self.parser.parse(empty_content)
        
        # Then
        self.assertEqual(result.content, "")
        self.assertEqual(result.presentation_items, [])
        self.assertEqual(result.script, "")
        
    def test_given_content_with_presentation_when_parsed_then_extracts_styles(self):
        """
        Given: .haba content with presentation layer
        When: The content is parsed
        Then: Extracts presentation items correctly
        """
        # Given
        content_with_presentation = """Hello World

---PRESENTATION---
h1: color: 'blue'; font-size: '20px'
p: color: 'green'
"""
        
        # When
        result = self.parser.parse(content_with_presentation)
        
        # Then
        self.assertEqual(result.content.strip(), "Hello World")
        self.assertEqual(len(result.presentation_items), 2)
        self.assertEqual(result.presentation_items[0][0], "h1")
        self.assertIn("color: 'blue'", result.presentation_items[0][1])
        self.assertEqual(result.presentation_items[1][0], "p")
        self.assertIn("color: 'green'", result.presentation_items[1][1])
        
    def test_given_content_with_script_when_parsed_then_extracts_javascript(self):
        """
        Given: .haba content with script layer
        When: The content is parsed
        Then: Extracts JavaScript code correctly
        """
        # Given
        content_with_script = """Test Content

---SCRIPT---
function test() {
    console.log('Hello');
}
test();
"""
        
        # When
        result = self.parser.parse(content_with_script)
        
        # Then
        self.assertEqual(result.content.strip(), "Test Content")
        self.assertIn("function test()", result.script)
        self.assertIn("console.log('Hello')", result.script)
        self.assertIn("test();", result.script)
        
    def test_given_haba_data_when_built_then_creates_valid_haba_format(self):
        """
        Given: A HabaData object with content, presentation, and script
        When: The data is built into .haba format
        Then: Creates valid .haba content string
        """
        # Given
        haba_data = HabaData()
        haba_data.content = "Sample Content\nSecond Line"
        haba_data.presentation_items = [("h1", "color: 'red'"), ("p", "font-size: '14px'")]
        haba_data.script = "console.log('built');"
        
        # When
        result = self.parser.build(haba_data)
        
        # Then
        self.assertIn("Sample Content", result)
        self.assertIn("Second Line", result)
        self.assertIn("---PRESENTATION---", result)
        self.assertIn("h1: color: 'red'", result)
        self.assertIn("p: font-size: '14px'", result)
        self.assertIn("---SCRIPT---", result)
        self.assertIn("console.log('built');", result)
        
    def test_given_malformed_presentation_when_parsed_then_handles_gracefully(self):
        """
        Given: .haba content with malformed presentation layer
        When: The content is parsed
        Then: Handles errors gracefully without crashing
        """
        # Given
        malformed_content = """Content

---PRESENTATION---
invalid_line_without_colon
h1 color: 'blue'  # missing colon after tag
"""
        
        # When & Then (should not raise exception)
        try:
            result = self.parser.parse(malformed_content)
            self.assertEqual(result.content.strip(), "Content")
            # Should handle malformed lines gracefully
        except Exception as e:
            self.fail(f"Parser should handle malformed content gracefully, but raised: {e}")


if __name__ == '__main__':
    unittest.main()
