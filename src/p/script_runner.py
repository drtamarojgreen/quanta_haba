import os
import tempfile
import subprocess
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from .haba_parser import HabaParser

class ScriptRunner:
    """
    Handles the execution of JavaScript from a .haba file in a headless browser.
    """
    def __init__(self):
        self.options = FirefoxOptions()
        self.options.add_argument("--headless")

    def run_script(self, haba_content):
        """
        Runs the script from a .haba file content in a headless Firefox browser
        and captures console logs.

        :param haba_content: The string content of the .haba file.
        :return: A list of console log messages.
        """
        parser = HabaParser()
        haba_data = parser.parse(haba_content)
        
        if not haba_data.script.strip():
            return [], [] # No script to run

        # Create a temporary HTML file to execute the script
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Haba Script Execution</title>
        </head>
        <body>
            {haba_data.content}
            <script>
                // Override console.log to store logs
                window.console_logs = [];
                window.js_error = null;
                const old_log = console.log;
                console.log = function(...args) {{
                    window.console_logs.push(args.map(arg => JSON.stringify(arg)).join(' '));
                    old_log.apply(console, args);
                }};
            </script>
            <script>
                try {{
                    {haba_data.script}
                }} catch (e) {{
                    window.js_error = {{
                        name: e.name,
                        message: e.message,
                        stack: e.stack
                    }};
                }}
            </script>
        </body>
        </html>
        """
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
            f.write(html_content)
            temp_html_path = f.name
            
        driver = None
        logs = []
        error = None
        try:
            driver = webdriver.Firefox(options=self.options)
            driver.get(f"file://{temp_html_path}")
            
            logs = driver.execute_script("return window.console_logs;")
            error = driver.execute_script("return window.js_error;")

        finally:
            if driver:
                driver.quit()
            if os.path.exists(temp_html_path):
                os.remove(temp_html_path)

        tasks = self._parse_tasks(logs, error)
        return logs, tasks

    def _parse_tasks(self, logs, error):
        """
        Parses console logs and a JS error to create a list of actionable tasks.
        """
        tasks = []
        if error:
            tasks.append({
                'type': 'error',
                'description': f"{error.get('name', 'Error')}: {error.get('message', 'An unknown error occurred.')}",
                'details': error.get('stack', '')
            })

        for log in logs:
            log_str = str(log)
            if 'TODO' in log_str or 'FIXME' in log_str:
                tasks.append({
                    'type': 'todo',
                    'description': log_str.strip().replace('"', ''),
                    'details': ''
                })
        
        return tasks


def run_python_script(script_content):
    """
    Runs a python script and captures its output.
    """
    logs = []
    tasks = []
    temp_py_path = None
    try:
        # Create a temporary file to write the script content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py', encoding='utf-8') as f:
            f.write(script_content)
            temp_py_path = f.name

        # Execute the script using subprocess
        result = subprocess.run(
            ['python', temp_py_path],
            capture_output=True,
            text=True,
            timeout=10  # 10 second timeout
        )

        # Process stdout
        if result.stdout:
            logs.extend(result.stdout.strip().split('\\n'))

        # Process stderr
        if result.stderr:
            stderr_lines = result.stderr.strip().split('\\n')
            logs.extend(stderr_lines)
            if stderr_lines:
                tasks.append({
                    'type': 'error',
                    'description': stderr_lines[-1]  # Get the last line of the error message
                })

    except subprocess.TimeoutExpired:
        logs.append("Script execution timed out after 10 seconds.")
        tasks.append({
            'type': 'error',
            'description': "Script execution timed out."
        })
    except Exception as e:
        logs.append(f"Failed to run python script: {e}")
        tasks.append({
            'type': 'error',
            'description': f"An unexpected error occurred while running the script: {e}"
        })
    finally:
        # Clean up the temporary file
        if temp_py_path and os.path.exists(temp_py_path):
            os.remove(temp_py_path)

    return logs, tasks
