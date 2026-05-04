import os
import subprocess
import sys

def run_cards():
    cards_dir = os.path.join(os.path.dirname(__file__), "cards")
    facts_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "facts"))

    os.environ["SORREL_FACTS_DIR"] = facts_dir

    print(f"Running Python SDD Cards with SORREL_FACTS_DIR={facts_dir}...")

    for filename in os.listdir(cards_dir):
        if filename.endswith("Card.py"):
            print(f"Executing {filename}...")
            subprocess.run([sys.executable, os.path.join(cards_dir, filename)])

if __name__ == "__main__":
    run_cards()
