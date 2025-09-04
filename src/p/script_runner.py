import os
import tempfile
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
