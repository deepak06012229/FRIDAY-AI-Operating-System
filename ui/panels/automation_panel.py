from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QLineEdit, QTextEdit
from PyQt5.QtCore import pyqtSignal, Qt
import requests
import json
from utils import logger
import config

class AutomationPanel(QWidget):
    """Lists automation workflows, displays execution logs, and manages n8n configurations."""
    run_workflow_requested = pyqtSignal(str)

    def __init__(self, workflow_engine, parent=None):
        super().__init__(parent)
        self.wf_engine = workflow_engine
        self.init_ui()
        self.refresh_workflows()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title Label
        self.title_label = QLabel("AUTOMATION SYSTEM MATRIX")
        self.title_label.setObjectName("PanelTitle")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #00F0FF; letter-spacing: 2px;")
        layout.addWidget(self.title_label)

        # List of Workflows
        wf_lbl = QLabel("SELECT ACTIVE WORKFLOW RECIPE:")
        wf_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold;")
        layout.addWidget(wf_lbl)

        self.wf_list = QListWidget()
        self.wf_list.setStyleSheet("""
            QListWidget {
                background-color: #030F26;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #E2E8F0;
                font-family: 'Consolas', monospace;
                padding: 6px;
            }
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #051630;
            }
            QListWidget::item:selected {
                background-color: #0B1E36;
                color: #00F0FF;
                border-left: 2px solid #00F0FF;
            }
            QListWidget::item:hover {
                background-color: #051630;
            }
        """)
        layout.addWidget(self.wf_list)

        # Trigger Workflow Button
        self.trigger_btn = QPushButton("DEPLOY AUTOMATION STREAM")
        self.trigger_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B1E36;
                border: 1px solid #00F0FF;
                border-radius: 4px;
                color: #00F0FF;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #00F0FF;
                color: #030F26;
            }
        """)
        self.trigger_btn.clicked.connect(self.trigger_selected_workflow)
        layout.addWidget(self.trigger_btn)

        # Execution Progress Console
        progress_lbl = QLabel("WORKFLOW EXECUTION STATUS:")
        progress_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold;")
        layout.addWidget(progress_lbl)

        self.progress_display = QTextEdit()
        self.progress_display.setReadOnly(True)
        self.progress_display.setStyleSheet("""
            QTextEdit {
                background-color: #030F26;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #94A3B8;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                height: 80px;
            }
        """)
        self.progress_display.setHtml("<span style='color: #475569;'>No workflow active. Telemetry stream idle.</span>")
        layout.addWidget(self.progress_display)

        # n8n Webhook Configuration
        webhook_lbl = QLabel("N8N WEBHOOK ROUTING REGISTRY:")
        webhook_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold; margin-top: 5px;")
        layout.addWidget(webhook_lbl)

        webhook_layout = QHBoxLayout()
        webhook_layout.setSpacing(6)

        self.webhook_input = QLineEdit()
        self.webhook_input.setText("http://localhost:5678/webhook-test/friday")
        self.webhook_input.setPlaceholderText("http://localhost:5678/webhook-test/friday")
        self.webhook_input.setStyleSheet("""
            QLineEdit {
                background-color: #051630;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #E2E8F0;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                padding: 6px;
            }
        """)
        webhook_layout.addWidget(self.webhook_input)

        self.webhook_test_btn = QPushButton("TEST POST")
        self.webhook_test_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B1E36;
                border: 1px solid #EAB308;
                border-radius: 4px;
                color: #EAB308;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #EAB308;
                color: #030F26;
            }
        """)
        self.webhook_test_btn.clicked.connect(self.test_webhook)
        webhook_layout.addWidget(self.webhook_test_btn)
        layout.addLayout(webhook_layout)

    def refresh_workflows(self):
        self.wf_list.clear()
        for name in self.wf_engine.workflows.keys():
            self.wf_list.addItem(name)
        if self.wf_list.count() > 0:
            self.wf_list.setCurrentRow(0)

    def trigger_selected_workflow(self):
        selected = self.wf_list.currentItem()
        if selected:
            name = selected.text()
            self.progress_display.setHtml(f"<span style='color: #00F0FF;'>Workflow '{name}' initiated...</span>")
            self.run_workflow_requested.emit(name)

    def on_step_started(self, step_info):
        idx = step_info["step_index"]
        act = step_info["action"].upper()
        param = step_info["param"]
        text = f"<span style='color: #F59E0B;'>Running step {idx + 1}: {act} ({param})</span>"
        self.progress_display.append(text)

    def on_step_completed(self, step_result):
        idx = step_result["step_index"]
        success = step_result["success"]
        msg = step_result["message"]
        
        if success:
            text = f"<span style='color: #10B981;'>&nbsp;&nbsp;&gt;&gt; Step {idx + 1} Success: {msg}</span>"
        else:
            text = f"<span style='color: #EF4444;'>&nbsp;&nbsp;&gt;&gt; Step {idx + 1} Failed: {msg}</span>"
        self.progress_display.append(text)

    def on_workflow_completed(self, success, summary):
        if success:
            text = f"<span style='color: #10B981; font-weight: bold;'>[COMPLETED] {summary}</span>"
        else:
            text = f"<span style='color: #EF4444; font-weight: bold;'>[HALTED] {summary}</span>"
        self.progress_display.append(text)

    def test_webhook(self):
        url = self.webhook_input.text().strip()
        if not url:
            self.progress_display.append("<span style='color: #EF4444;'>Error: Webhook URL is empty.</span>")
            return

        self.progress_display.append(f"<span style='color: #EAB308;'>Sending webhook diagnostic ping to {url}...</span>")
        try:
            payload = {"test": True, "sender": "FRIDAY OS", "timestamp": int(time.time())}
            # Simple async request mapping
            import threading
            def run_ping():
                try:
                    res = requests.post(url, json=payload, timeout=3)
                    self.progress_display.append(f"<span style='color: #10B981;'>Webhook ping response: {res.status_code}</span>")
                except Exception as e:
                    self.progress_display.append(f"<span style='color: #EF4444;'>Webhook ping failed: {e}</span>")
            threading.Thread(target=run_ping, daemon=True).start()
        except Exception as e:
            self.progress_display.append(f"<span style='color: #EF4444;'>Error scheduling webhook post: {e}</span>")
            
        import time # import local usage
