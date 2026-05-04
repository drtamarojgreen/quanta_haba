import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../src/p")))
from haba_parser import HabaParser
from util.fact_utils import read_facts

def haba_parser_multiline_card(facts):
    """
    @Card: python_haba_parser_multiline_verification
    @Is multi_line_content_supported == true
    @Results python_haba_parser_multiline_operational == true
    """
    parser = HabaParser()
    raw_text = "<content_layer>\nLine 1\nLine 2\n</content_layer>"
    data = parser.parse(raw_text)

    operational = "Line 1" in data.content and "Line 2" in data.content
    print(f"python_haba_parser_multiline_operational = {str(operational).lower()}")

if __name__ == "__main__":
    facts = read_facts("python_haba_parser.facts")
    print("[SDD Card: python_haba_parser_multiline_verification]")
    haba_parser_multiline_card(facts)
