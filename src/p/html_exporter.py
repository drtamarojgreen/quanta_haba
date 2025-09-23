"""
HTML Exporter for Haba files.
Converts .haba files to .html files with proper styling and structure.
"""

import re
try:
    from .haba_parser import HabaData
except ImportError:
    from haba_parser import HabaData

class HtmlExporter:
    """
    Exports HabaData to HTML format with proper styling and structure.
    """
    
    def __init__(self):
        pass
    
    def export_to_html(self, haba_data: HabaData, title: str = "Haba Output") -> str:
        """
        Converts HabaData to a complete HTML document.
        
        Args:
            haba_data: The parsed Haba data
            title: The title for the HTML document
            
        Returns:
            Complete HTML document as string
        """
        html_parts = []
        
        # HTML document structure
        html_parts.append("<!DOCTYPE html>")
        html_parts.append('<html lang="en">')
        html_parts.append("<head>")
        html_parts.append('    <meta charset="UTF-8">')
        html_parts.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append(f"    <title>{title}</title>")
        
        # Add styles
        html_parts.append("    <style>")
        html_parts.append("        /* Haba Generated Styles */")
        
        # Generate CSS classes for each container
        for i, (container, style) in enumerate(haba_data.presentation_items):
            class_name = f"haba-container-{i}"
            css_style = self._convert_haba_style_to_css(style)
            if css_style:
                html_parts.append(f"        .{class_name} {{ {css_style} }}")
        
        # Add default styling
        html_parts.append("        body { font-family: Arial, sans-serif; margin: 20px; }")
        html_parts.append("        .haba-content { max-width: 800px; margin: 0 auto; }")
        html_parts.append("    </style>")
        html_parts.append("</head>")
        html_parts.append("<body>")
        
        # Add content wrapped in containers
        content_html = self._wrap_content_in_containers(haba_data)
        html_parts.append(f'    <div class="haba-content">')
        html_parts.append(f"        {content_html}")
        html_parts.append("    </div>")
        
        # Add script if present
        if haba_data.script and haba_data.script.strip():
            html_parts.append("    <script>")
            html_parts.append(f"        {haba_data.script}")
            html_parts.append("    </script>")
        
        html_parts.append("</body>")
        html_parts.append("</html>")
        
        return "\n".join(html_parts)
    
    def _convert_haba_style_to_css(self, style_str: str) -> str:
        """
        Converts Haba style format to CSS.
        
        Args:
            style_str: Style string in Haba format (e.g., "{ color: 'blue', font-size: '16px' }")
            
        Returns:
            CSS style string
        """
        if not style_str or not style_str.strip():
            return ""
        
        # Remove outer braces and parse key-value pairs
        style_str = style_str.strip()
        if style_str.startswith('{') and style_str.endswith('}'):
            style_str = style_str[1:-1]
        
        css_parts = []
        
        # Parse style properties
        # Handle both 'key: value' and "key: 'value'" formats
        pairs = re.findall(r"([\w-]+)\s*:\s*['\"]?([^,'\"]*)['\"]?", style_str)
        
        for key, value in pairs:
            key = key.strip()
            value = value.strip()
            
            # Convert common style properties
            if key and value:
                css_parts.append(f"{key}: {value}")
        
        return "; ".join(css_parts)
    
    def _wrap_content_in_containers(self, haba_data: HabaData) -> str:
        """
        Wraps content in the specified containers with proper classes.
        
        Args:
            haba_data: The parsed Haba data
            
        Returns:
            HTML content wrapped in containers
        """
        content = haba_data.content
        
        # Start from the innermost container and work outward
        for i in reversed(range(len(haba_data.presentation_items))):
            container, _ = haba_data.presentation_items[i]
            class_name = f"haba-container-{i}"
            
            # Parse container tag and add class
            container = container.strip()
            if container.startswith('<') and '>' in container:
                # Find the tag name and add class attribute
                tag_end = container.find('>')
                if ' ' in container[:tag_end]:
                    # Tag already has attributes
                    container = container[:tag_end] + f' class="{class_name}"' + container[tag_end:]
                else:
                    # Simple tag, add class
                    container = container[:tag_end] + f' class="{class_name}"' + container[tag_end:]
                
                # Extract tag name for closing tag
                tag_name = container[1:container.find(' ') if ' ' in container else container.find('>')]
                closing_tag = f"</{tag_name}>"
                
                content = f"{container}\n{content}\n{closing_tag}"
            else:
                # Fallback: wrap in div if container format is unclear
                content = f'<div class="{class_name}">\n{content}\n</div>'
        
        return content
    
    def export_to_file(self, haba_data: HabaData, output_path: str, title: str = "Haba Output"):
        """
        Exports HabaData to an HTML file.
        
        Args:
            haba_data: The parsed Haba data
            output_path: Path to save the HTML file
            title: Title for the HTML document
        """
        html_content = self.export_to_html(haba_data, title)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
