import argparse
import sys
import os

from .script_runner import ScriptRunner

def main():
    """
    The main function for the CLI script runner.
    """
    parser = argparse.ArgumentParser(description="Run the script from a .haba file and get actionable tasks.")
    parser.add_argument("file", help="The path to the .haba file to run.")
    args = parser.parse_args()

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            haba_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{args.file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    print(f"Running script from '{args.file}'...")
    runner = ScriptRunner()
    logs, tasks = runner.run_script(haba_content)
    print("-" * 30)

    print("\n--- Console Output ---")
    if logs:
        for log in logs:
            print(log)
    else:
        print("No console output.")

    print("\n--- Actionable Tasks ---")
    if tasks:
        for task in tasks:
            print(f"- [{task['type'].upper()}] {task['description']}")
            if task.get('details'):
                print(f"  Details: {task['details']}")
    else:
        print("No actionable tasks found.")

if __name__ == "__main__":
    main()
