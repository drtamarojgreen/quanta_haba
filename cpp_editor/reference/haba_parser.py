import re

class HabaData:
    """A simple data class to hold the parsed Haba file content."""
    def __init__(self):
        self.content = ""
        self.presentation_items = [] # A list of tuples (container_text, style_text)

class HabaParser:
    """
    A parser for the .haba file format.

    The format is described as an XML-like file where indentation is significant.
    It has a content_layer and a presentation_layer.
    In the presentation_layer, containers and styles are matched by order.
    """

    def parse(self, raw_text: str) -> HabaData:
        """
        Parses the raw text of a .haba file into a HabaData object.
        """
        data = HabaData()

        # Extract content layer
        content_match = re.search(r'<content_layer>(.*?)</content_layer>', raw_text, re.DOTALL)
        if content_match:
            data.content = content_match.group(1).strip()

        # Extract presentation layer
        presentation_match = re.search(r'<presentation_layer>(.*?)</presentation_layer>', raw_text, re.DOTALL)
        if presentation_match:
            presentation_text = presentation_match.group(1).strip()

            # Extract containers and styles
            containers_match = re.search(r'<containers>(.*?)</containers>', presentation_text, re.DOTALL)
            styles_match = re.search(r'<styles>(.*?)</styles>', presentation_text, re.DOTALL)

            containers = []
            if containers_match:
                # Assuming one container per line for now
                containers = [line.strip() for line in containers_match.group(1).strip().split('\n') if line.strip()]

            styles = []
            if styles_match:
                # Assuming one style per line for now
                styles = [line.strip() for line in styles_match.group(1).strip().split('\n') if line.strip()]

            # Match containers and styles by order
            for i in range(len(containers)):
                style = styles[i] if i < len(styles) else "" # Default to empty style if not enough styles
                data.presentation_items.append((containers[i], style))

        return data

    def build(self, haba_data: HabaData) -> str:
        """
        Builds a .haba file string from a HabaData object.
        """
        # Build content layer
        content_str = f"<content_layer>\n    {haba_data.content}\n</content_layer>\n"

        # Build presentation layer
        containers_str = "\n".join([f"        {item[0]}" for item in haba_data.presentation_items])
        styles_str = "\n".join([f"        {item[1]}" for item in haba_data.presentation_items])

        presentation_str = (
            "<presentation_layer>\n"
            "    <containers>\n"
            f"{containers_str}\n"
            "    </containers>\n"
            "    <styles>\n"
            f"{styles_str}\n"
            "    </styles>\n"
            "</presentation_layer>"
        )

        return content_str + presentation_str


# Example Usage (for testing purposes)
if __name__ == '__main__':
    example_haba_text = """
    <content_layer>
        This is the main text content.
        It can span multiple lines.
    </content_layer>
    <presentation_layer>
        <containers>
            <div>
            <p>
        </containers>
        <styles>
            { color: 'blue' }
            { font-size: '16px' }
        </styles>
    </presentation_layer>
    """

    parser = HabaParser()
    parsed_data = parser.parse(example_haba_text)

    print("--- PARSED DATA ---")
    print(f"Content: {parsed_data.content}")
    for i, (container, style) in enumerate(parsed_data.presentation_items):
        print(f"Item {i+1}: Container='{container}', Style='{style}'")

    print("\n--- REBUILT FILE ---")
    rebuilt_text = parser.build(parsed_data)
    print(rebuilt_text)
