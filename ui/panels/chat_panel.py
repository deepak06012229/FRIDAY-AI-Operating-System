from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextBrowser, QLabel
from PyQt5.QtCore import pyqtSignal, Qt
from utils import logger

class ChatPanel(QWidget):
    """Provides a scrollable rich-text conversation interface and text command input."""
    text_query_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Title / Mode Label
        self.title_label = QLabel("COGNITIVE INTERFACE")
        self.title_label.setObjectName("PanelTitle")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #00F0FF; letter-spacing: 2px;")
        layout.addWidget(self.title_label)

        # Message Viewer
        self.chat_display = QTextBrowser()
        self.chat_display.setOpenExternalLinks(True)
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                background-color: #030F26;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #E2E8F0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.chat_display)

        # Bottom Input Area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(6)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter system command or query...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #051630;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #00F0FF;
                font-family: 'Consolas', monospace;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 1px solid #00F0FF;
            }
        """)
        self.input_field.returnPressed.connect(self.submit_query)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("RUN")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #0B1E36;
                border: 1px solid #00F0FF;
                border-radius: 4px;
                color: #00F0FF;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #00F0FF;
                color: #030F26;
            }
            QPushButton:pressed {
                background-color: #051630;
            }
        """)
        self.send_button.clicked.connect(self.submit_query)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        # Seed initial greeting
        self.add_system_message("FRIDAY AI Operating System Initialized. All systems operational.")

    def submit_query(self):
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()
            self.text_query_submitted.emit(text)

    def add_user_message(self, message):
        """Displays user's prompt in the chat."""
        html = f"""
        <div style="margin-bottom: 12px; border-left: 2px solid #00F0FF; padding-left: 8px;">
            <span style="color: #00F0FF; font-weight: bold;">[CHIEF]</span> 
            <span style="color: #88F5FF; font-size: 10px;">({self.get_time_stamp()})</span><br/>
            <span style="color: #E2E8F0;">{message}</span>
        </div>
        """
        self.chat_display.append(html)
        self.scroll_to_bottom()

    def add_friday_message(self, message):
        """Displays FRIDAY's reply, rendering markdown/code blocks cleanly."""
        # Simple rendering replacement for code blocks to look high-tech
        formatted_message = message
        
        # Replace json block styling
        formatted_message = formatted_message.replace(
            "```json", 
            "<pre style='background-color: #051630; border: 1px solid #00F0FF; padding: 6px; border-radius: 3px; color: #F59E0B;'>"
        ).replace("```", "</pre>")

        html = f"""
        <div style="margin-bottom: 12px; border-left: 2px solid #10B981; padding-left: 8px;">
            <span style="color: #10B981; font-weight: bold;">[FRIDAY]</span> 
            <span style="color: #8EF8C7; font-size: 10px;">({self.get_time_stamp()})</span><br/>
            <span style="color: #E2E8F0;">{formatted_message}</span>
        </div>
        """
        self.chat_display.append(html)
        self.scroll_to_bottom()

    def add_system_message(self, message):
        """Displays system status logs."""
        html = f"""
        <div style="margin-bottom: 12px; border-left: 2px solid #F59E0B; padding-left: 8px; font-style: italic;">
            <span style="color: #F59E0B; font-weight: bold;">[SYSTEM]</span> 
            <span style="color: #94A3B8;">{message}</span>
        </div>
        """
        self.chat_display.append(html)
        self.scroll_to_bottom()

    def get_time_stamp(self):
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

    def scroll_to_bottom(self):
        sb = self.chat_display.verticalScrollBar()
        sb.setValue(sb.maximum())
