from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class GlassPanel(QFrame):
    """
    A premium glassmorphic panel container for HUD elements.
    Provides a dark semi-transparent background, subtle glow borders, and thin uppercase headings.
    """
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title_text = title.upper()
        self.init_ui()

    def init_ui(self):
        # Set stylesheet with semi-transparent background and neon-cyan borders
        self.setStyleSheet("""
            GlassPanel {
                background-color: rgba(10, 16, 26, 0.75);
                border: 1px solid rgba(0, 240, 255, 0.25);
                border-radius: 8px;
            }
            GlassPanel:hover {
                border: 1px solid rgba(0, 240, 255, 0.5);
                background-color: rgba(12, 20, 32, 0.8);
            }
        """)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(10)

        # Title block if provided
        if self.title_text:
            self.title_label = QLabel(self.title_text)
            self.title_label.setStyleSheet("""
                QLabel {
                    color: #00F0FF;
                    font-family: 'Segoe UI', 'Orbitron', sans-serif;
                    font-size: 11px;
                    font-weight: bold;
                    letter-spacing: 2px;
                    border: none;
                    background: transparent;
                }
            """)
            self.main_layout.addWidget(self.title_label)
            
    def add_widget(self, widget):
        """Helper to append a child widget to this glass panel layout."""
        self.main_layout.addWidget(widget)

    def add_layout(self, layout):
        """Helper to append a child layout to this glass panel layout."""
        self.main_layout.addLayout(layout)
