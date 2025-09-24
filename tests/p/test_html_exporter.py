import unittest
import sys
import os
import tempfile

# Add src/p to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'p'))

from html_exporter import HtmlExporter
from haba_parser import HabaParser, HabaData


class TestHtmlExporter(unittest.TestCase):
    """Unit tests for HtmlExporter class"""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.exporter = HtmlExporter()
        self.parser = HabaParser()
        
    def test_exporter_initialization(self):
        """Test that exporter initializes correctly"""
        self.assertIsInstance(self.exporter, HtmlExporter)
        
    def test_export_empty_haba_data(self):
        """Test exporting empty HabaData"""
        haba_data = HabaData()
        html = self.exporter.export_to_html(haba_data, "Test Document")
        
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<title>Test Document</title>", html)
        self.assertIn("<html>", html)
        self.assertIn("</html>", html)
        
    def test_export_content_only(self):
        """Test exporting HabaData with content only"""
        haba_data = HabaData()
        haba_data.content = "Hello World\nThis is a test"
        
        html = self.exporter.export_to_html(haba_data, "Content Test")
        
        self.assertIn("Hello World", html)
        self.assertIn("This is a test", html)
        self.assertIn("<title>Content Test</title>", html)
        
    def test_export_with_presentation_styles(self):
        """Test exporting HabaData with presentation styles"""
        haba_data = HabaData()
        haba_data.content = "Styled Content\nSecond Line"
        haba_data.presentation_items = [
            ("h1", "color: 'blue'; font-size: '24px'"),
            ("p", "color: 'red'; font-weight: 'bold'")
        ]
        
        html = self.exporter.export_to_html(haba_data, "Style Test")
        
        self.assertIn("Styled Content", html)
        self.assertIn("Second Line", html)
        self.assertIn("color: blue", html)  # CSS format
        self.assertIn("font-size: 24px", html)
        self.assertIn("color: red", html)
        self.assertIn("font-weight: bold", html)
        
    def test_export_with_script(self):
        """Test exporting HabaData with JavaScript"""
        haba_data = HabaData()
        haba_data.content = "Content with script"
        haba_data.script = "console.log('Hello from script');\nalert('Test');"
        
        html = self.exporter.export_to_html(haba_data, "Script Test")
        
        self.assertIn("Content with script", html)
        self.assertIn("<script>", html)
        self.assertIn("console.log('Hello from script');", html)
        self.assertIn("alert('Test');", html)
        self.assertIn("</script>", html)
        
    def test_export_complete_haba_data(self):
        """Test exporting complete HabaData with all layers"""
        haba_data = HabaData()
        haba_data.content = "Complete Document\nWith multiple lines\nAnd features"
        haba_data.presentation_items = [
            ("h1", "color: 'blue'; font-size: '28px'"),
            ("p", "color: 'green'; margin: '10px'"),
            ("div", "background: 'lightgray'; padding: '5px'")
        ]
        haba_data.script = """
function init() {
    console.log('Document ready');
}
init();
"""
        
        html = self.exporter.export_to_html(haba_data, "Complete Test")
        
        # Check HTML structure
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html>", html)
        self.assertIn("<head>", html)
        self.assertIn("<body>", html)
        self.assertIn("</html>", html)
        
        # Check content
        self.assertIn("Complete Document", html)
        self.assertIn("With multiple lines", html)
        self.assertIn("And features", html)
        
        # Check styles
        self.assertIn("color: blue", html)
        self.assertIn("font-size: 28px", html)
        self.assertIn("color: green", html)
        self.assertIn("background: lightgray", html)
        
        # Check script
        self.assertIn("function init()", html)
        self.assertIn("console.log('Document ready')", html)
        self.assertIn("init();", html)
        
    def test_export_to_file(self):
        """Test exporting to file"""
        haba_data = HabaData()
        haba_data.content = "File export test"
        haba_data.script = "console.log('exported');"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
            temp_path = temp_file.name
            
        try:
            self.exporter.export_to_file(haba_data, temp_path, "File Test")
            
            # Read the file and verify content
            with open(temp_path, 'r') as f:
                content = f.read()
                
            self.assertIn("File export test", content)
            self.assertIn("console.log('exported');", content)
            self.assertIn("<title>File Test</title>", content)
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def test_style_conversion(self):
        """Test conversion of Haba styles to CSS"""
        haba_data = HabaData()
        haba_data.content = "Style conversion test"
        haba_data.presentation_items = [
            ("div", "color: 'red'; font-size: '16px'; background: 'yellow'")
        ]
        
        html = self.exporter.export_to_html(haba_data, "Style Conversion")
        
        # Check that quotes are removed and styles are properly formatted
        self.assertIn("color: red", html)
        self.assertIn("font-size: 16px", html)
        self.assertIn("background: yellow", html)
        self.assertNotIn("'red'", html)  # Quotes should be removed
        self.assertNotIn("'16px'", html)
        self.assertNotIn("'yellow'", html)


class TestHtmlExporterBDD(unittest.TestCase):
    """BDD-style tests for HtmlExporter"""
    
    def setUp(self):
        self.exporter = HtmlExporter()
        
    def test_given_haba_data_when_exported_then_creates_valid_html(self):
        """
        Given: A HabaData object with content
        When: The data is exported to HTML
        Then: Creates valid HTML document structure
        """
        # Given
        haba_data = HabaData()
        haba_data.content = "Test content for HTML export"
        
        # When
        html = self.exporter.export_to_html(haba_data, "BDD Test")
        
        # Then
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<html>", html)
        self.assertIn("<head>", html)
        self.assertIn("<title>BDD Test</title>", html)
        self.assertIn("<body>", html)
        self.assertIn("Test content for HTML export", html)
        self.assertIn("</body>", html)
        self.assertIn("</html>", html)
        
    def test_given_presentation_styles_when_exported_then_applies_css_styles(self):
        """
        Given: HabaData with presentation styles
        When: The data is exported to HTML
        Then: Applies CSS styles correctly
        """
        # Given
        haba_data = HabaData()
        haba_data.content = "Styled content\nSecond line"
        haba_data.presentation_items = [
            ("h1", "color: 'blue'; font-weight: 'bold'"),
            ("p", "font-size: '14px'; margin: '10px'")
        ]
        
        # When
        html = self.exporter.export_to_html(haba_data, "Style Test")
        
        # Then
        self.assertIn("<style>", html)
        self.assertIn("</style>", html)
        self.assertIn("color: blue", html)
        self.assertIn("font-weight: bold", html)
        self.assertIn("font-size: 14px", html)
        self.assertIn("margin: 10px", html)
        
    def test_given_javascript_code_when_exported_then_includes_script_tags(self):
        """
        Given: HabaData with JavaScript code
        When: The data is exported to HTML
        Then: Includes script tags with the JavaScript
        """
        # Given
        haba_data = HabaData()
        haba_data.content = "Content with JavaScript"
        haba_data.script = """
function greet() {
    alert('Hello World!');
}
greet();
"""
        
        # When
        html = self.exporter.export_to_html(haba_data, "Script Test")
        
        # Then
        self.assertIn("<script>", html)
        self.assertIn("</script>", html)
        self.assertIn("function greet()", html)
        self.assertIn("alert('Hello World!')", html)
        self.assertIn("greet();", html)
        
    def test_given_complete_haba_data_when_exported_then_creates_complete_html(self):
        """
        Given: Complete HabaData with content, styles, and script
        When: The data is exported to HTML
        Then: Creates complete HTML document with all elements
        """
        # Given
        haba_data = HabaData()
        haba_data.content = "Complete test document\nWith multiple elements"
        haba_data.presentation_items = [
            ("h1", "color: 'navy'; text-align: 'center'"),
            ("p", "color: 'darkgreen'; line-height: '1.5'")
        ]
        haba_data.script = "console.log('Complete document loaded');"
        
        # When
        html = self.exporter.export_to_html(haba_data, "Complete Document")
        
        # Then
        # Check structure
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<title>Complete Document</title>", html)
        
        # Check content
        self.assertIn("Complete test document", html)
        self.assertIn("With multiple elements", html)
        
        # Check styles
        self.assertIn("<style>", html)
        self.assertIn("color: navy", html)
        self.assertIn("text-align: center", html)
        self.assertIn("color: darkgreen", html)
        self.assertIn("line-height: 1.5", html)
        
        # Check script
        self.assertIn("<script>", html)
        self.assertIn("console.log('Complete document loaded');", html)
        
    def test_given_file_path_when_exported_then_saves_html_file(self):
        """
        Given: A file path for export
        When: HabaData is exported to the file
        Then: Saves valid HTML file at the specified path
        """
        # Given
        haba_data = HabaData()
        haba_data.content = "File export test content"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
            file_path = temp_file.name
            
        try:
            # When
            self.exporter.export_to_file(haba_data, file_path, "File Export Test")
            
            # Then
            self.assertTrue(os.path.exists(file_path))
            
            with open(file_path, 'r') as f:
                content = f.read()
                
            self.assertIn("File export test content", content)
            self.assertIn("<title>File Export Test</title>", content)
            self.assertIn("<!DOCTYPE html>", content)
            
        finally:
            # Cleanup
            if os.path.exists(file_path):
                os.unlink(file_path)


class TestHtmlExporterIntegration(unittest.TestCase):
    """Integration tests for HtmlExporter with HabaParser"""
    
    def setUp(self):
        self.exporter = HtmlExporter()
        self.parser = HabaParser()
        
    def test_parse_then_export_workflow(self):
        """Test complete workflow: parse .haba content then export to HTML"""
        # Create sample .haba content
        haba_content = """Welcome to Integration Test
This tests the complete workflow.
From parsing to HTML export.

---PRESENTATION---
h1: color: 'purple'; font-size: '32px'
p: color: 'black'; margin: '15px'
div: border: '1px solid gray'; padding: '20px'

---SCRIPT---
console.log('Integration test loaded');
function showMessage() {
    alert('Integration test successful!');
}
showMessage();
"""
        
        # Parse the content
        haba_data = self.parser.parse(haba_content)
        
        # Export to HTML
        html = self.exporter.export_to_html(haba_data, "Integration Test")
        
        # Verify the complete workflow
        self.assertIn("Welcome to Integration Test", html)
        self.assertIn("This tests the complete workflow", html)
        self.assertIn("From parsing to HTML export", html)
        
        # Check styles were applied
        self.assertIn("color: purple", html)
        self.assertIn("font-size: 32px", html)
        self.assertIn("margin: 15px", html)
        self.assertIn("border: 1px solid gray", html)
        
        # Check script was included
        self.assertIn("console.log('Integration test loaded')", html)
        self.assertIn("function showMessage()", html)
        self.assertIn("showMessage();", html)


if __name__ == '__main__':
    unittest.main()
