import os
import json
import time

class WorkspaceManager:
    def __init__(self, haba_dir="haba"):
        self.haba_dir = haba_dir
        self.session_file = os.path.join(haba_dir, "session.json")
        self.log_file = os.path.join(haba_dir, "activity.log")

    def save_session(self, current_file, cursor_pos=0):
        session_data = {
            "last_file": current_file,
            "cursor_pos": cursor_pos,
            "timestamp": time.time()
        }
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f)

    def load_session(self):
        if os.path.exists(self.session_file):
            with open(self.session_file, 'r') as f:
                return json.load(f)
        return None

    def auto_save(self, content, filepath):
        if not filepath:
            filepath = os.path.join(self.haba_dir, "autosave.haba")
        else:
            filepath = filepath + ".autosave"
        with open(filepath, 'w') as f:
            f.write(content)

    def log_activity(self, message):
        with open(self.log_file, 'a') as f:
            f.write(f"[{time.ctime()}] {message}\n")

    def save_workspace(self, workspace_name, files):
        workspace_file = os.path.join(self.haba_dir, f"{workspace_name}.habaworkspace")
        with open(workspace_file, 'w') as f:
            json.dump({"files": files}, f)

    def load_workspace(self, workspace_name):
        workspace_file = os.path.join(self.haba_dir, f"{workspace_name}.habaworkspace")
        if os.path.exists(workspace_file):
            with open(workspace_file, 'r') as f:
                return json.load(f)
        return None
