import os
import json
import time
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from utils import logger
import config
from automation import app_launcher, browser_controller

class WorkflowWorker(QThread):
    """Worker thread that executes a sequence of workflow steps asynchronously."""
    step_started = pyqtSignal(dict)  # Emits current step info
    step_completed = pyqtSignal(dict) # Emits step result
    workflow_finished = pyqtSignal(bool, str) # Emits success status, summary msg
    speak_requested = pyqtSignal(str) # Emits request for TTS to speak text

    def __init__(self, steps, parent=None):
        super().__init__(parent)
        self.steps = steps

    def run(self):
        logger.info(f"Workflow execution started. Total steps: {len(self.steps)}")
        
        for idx, step in enumerate(self.steps):
            action = step.get("action", "").lower().strip()
            param = step.get("param", "")
            
            step_info = {"step_index": idx, "action": action, "param": param}
            self.step_started.emit(step_info)
            
            success = False
            result_msg = ""
            
            try:
                if action == "speak":
                    self.speak_requested.emit(str(param))
                    # Wait briefly for TTS trigger lag
                    time.sleep(1.0)
                    success = True
                    result_msg = f"Spoke: {param}"
                    
                elif action == "launch_app":
                    status, msg = app_launcher.launch_application(str(param))
                    success = status
                    result_msg = msg
                    
                elif action == "open_url":
                    status, msg = browser_controller.open_url(str(param))
                    success = status
                    result_msg = msg
                    
                elif action == "webhook":
                    # n8n or generic API endpoint trigger
                    url = str(param)
                    data = step.get("data", {})
                    response = requests.post(url, json=data, timeout=5)
                    success = response.status_code in [200, 201]
                    result_msg = f"Webhook POST status: {response.status_code}"
                    
                elif action == "wait":
                    delay = float(param)
                    time.sleep(delay)
                    success = True
                    result_msg = f"Waited {delay} seconds"
                    
                else:
                    success = False
                    result_msg = f"Unknown action: {action}"
                    
            except Exception as e:
                logger.error(f"Error executing step {idx} ({action}): {e}")
                success = False
                result_msg = f"Exception: {e}"
                
            step_result = {"step_index": idx, "success": success, "message": result_msg}
            self.step_completed.emit(step_result)
            
            if not success and step.get("stop_on_error", True):
                logger.warn("Workflow halted due to error on critical step.")
                self.workflow_finished.emit(False, f"Halted at step {idx}: {result_msg}")
                return
                
        self.workflow_finished.emit(True, "Workflow completed successfully.")


class WorkflowEngine:
    def __init__(self):
        self.filepath = config.WORKFLOW_PATH
        self.workflows = {}
        self.active_worker = None
        self.load_workflows()

    def load_workflows(self):
        """Loads workflows from JSON. Seeds defaults if file is missing."""
        if not os.path.exists(self.filepath):
            self.seed_default_workflows()
            return
            
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.workflows = json.load(f)
            logger.info(f"Loaded {len(self.workflows)} workflows from {self.filepath}")
        except Exception as e:
            logger.error(f"Failed to load workflows: {e}")
            self.seed_default_workflows()

    def save_workflows(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.workflows, f, indent=4)
            logger.info("Saved workflows configuration.")
        except Exception as e:
            logger.error(f"Failed to save workflows: {e}")

    def seed_default_workflows(self):
        """Creates a default set of workflows for demonstration."""
        logger.info("Seeding default automation workflows...")
        self.workflows = {
            "Morning Dev Space": [
                {"action": "speak", "param": "Initializing morning coding suite. Preparing your workspace, Chief."},
                {"action": "launch_app", "param": "VS Code"},
                {"action": "wait", "param": 1.5},
                {"action": "open_url", "param": "github"},
                {"action": "wait", "param": 1.0},
                {"action": "open_url", "param": "gmail"}
            ],
            "System Diagnostics": [
                {"action": "speak", "param": "Running diagnostic sweep on CPU structures, RAM cores, and local databases."},
                {"action": "wait", "param": 2.0},
                {"action": "speak", "param": "Diagnostic complete. CPU, RAM, and Memory layers are fully optimized."}
            ],
            "n8n Core Test": [
                {"action": "speak", "param": "Triggering n8n automation webhook sequence."},
                {"action": "webhook", "param": "http://localhost:5678/webhook-test/friday", "data": {"event": "friday_activation", "status": "ok"}}
            ]
        }
        self.save_workflows()

    def execute_workflow(self, workflow_name, speak_cb=None, step_start_cb=None, step_end_cb=None, completed_cb=None):
        """Kicks off the workflow execution in a background thread."""
        if workflow_name not in self.workflows:
            logger.error(f"Workflow '{workflow_name}' not found.")
            return False
            
        if self.active_worker and self.active_worker.isRunning():
            logger.warn("A workflow is already executing. Rejecting run command.")
            return False
            
        steps = self.workflows[workflow_name]
        self.active_worker = WorkflowWorker(steps)
        
        # Connect callbacks
        if speak_cb:
            self.active_worker.speak_requested.connect(speak_cb)
        if step_start_cb:
            self.active_worker.step_started.connect(step_start_cb)
        if step_end_cb:
            self.active_worker.step_completed.connect(step_end_cb)
        if completed_cb:
            self.active_worker.workflow_finished.connect(completed_cb)
            
        self.active_worker.start()
        logger.info(f"Triggered workflow execution thread for '{workflow_name}'")
        return True
