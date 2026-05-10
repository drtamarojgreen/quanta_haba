import argparse
import sys
import os
import time

from .script_runner import ScriptRunner
from .haba_parser import HabaParser
from .html_exporter import HtmlExporter
from .workspace_manager import WorkspaceManager

def main():
    """
    The main function for the CLI script runner.
    """
    parser = argparse.ArgumentParser(description="Run the script from a .haba file and get actionable tasks.")
    parser.add_argument("file", help="The path to the .haba file to run.")
    parser.add_argument("--export-html", action="store_true", help="Export the .haba file to HTML.")
    parser.add_argument("--to-json", action="store_true", help="Convert .haba file to JSON.")
    parser.add_argument("--from-json", action="store_true", help="Load project from JSON file.")
    parser.add_argument("--save-project", help="Save project to .haba file.")
    parser.add_argument("--ci", action="store_true", help="CI mode (logging enabled).")
    args = parser.parse_args()

    start_time = time.time()
    wm = WorkspaceManager()
    parser_haba = HabaParser()

    if args.ci:
        wm.log_activity(f"CI run started for {args.file}")

    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            haba_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{args.file}'")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    if args.export_html:
        exporter = HtmlExporter()
        data = parser_haba.parse(haba_content)
        html = exporter.export_to_html(data, os.path.basename(args.file))
        output_path = args.file + ".html"
        with open(output_path, 'w') as f:
            f.write(html)
        print(f"Exported to {output_path}")

    if args.to_json:
        data = parser_haba.parse(haba_content)
        json_str = parser_haba.to_json(data)
        with open(args.file + ".json", 'w') as f:
            f.write(json_str)
        print(f"Converted to {args.file}.json")

    print(f"Running script from '{args.file}'...")
    runner = ScriptRunner()
    logs, tasks = runner.run_script(haba_content)
    print("-" * 30)

    if args.ci:
        duration = time.time() - start_time
        wm.log_activity(f"CI run completed for {args.file} in {duration:.4f}s")

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
