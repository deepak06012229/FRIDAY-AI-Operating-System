from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QGridLayout, QMessageBox, QTabWidget
from PyQt5.QtCore import pyqtSignal, Qt
from utils import logger
import config

class MemoryPanel(QWidget):
    """Memory management control board. Handles profile properties, API keys, and database inspection."""
    api_key_updated = pyqtSignal(str)

    def __init__(self, brain_instance, parent=None):
        super().__init__(parent)
        self.brain = brain_instance
        self.memory = brain_instance.memory
        self.init_ui()
        self.refresh_memory_list()
        self.load_profile_fields()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title Label
        self.title_label = QLabel("MEMORY ENGINE DATABASE")
        self.title_label.setObjectName("PanelTitle")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #00F0FF; letter-spacing: 2px;")
        layout.addWidget(self.title_label)

        # Profile Settings Form
        pref_lbl = QLabel("USER MATRIX PREFERENCES:")
        pref_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold;")
        layout.addWidget(pref_lbl)

        grid = QGridLayout()
        grid.setSpacing(6)

        grid.addWidget(QLabel("USER DESIGNATION (NAME):"), 0, 0)
        self.name_input = QLineEdit()
        grid.addWidget(self.name_input, 0, 1)

        grid.addWidget(QLabel("PRIMARY TEXT EDITOR:"), 1, 0)
        self.editor_input = QLineEdit()
        grid.addWidget(self.editor_input, 1, 1)

        grid.addWidget(QLabel("GEMINI API KEY:"), 2, 0)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        grid.addWidget(self.api_key_input, 2, 1)

        # Apply settings styling
        for i in range(grid.count()):
            widget = grid.itemAt(i).widget()
            if isinstance(widget, QLabel):
                widget.setStyleSheet("font-family: 'Consolas', monospace; font-size: 11px; color: #94A3B8;")
            elif isinstance(widget, QLineEdit):
                widget.setStyleSheet("""
                    QLineEdit {
                        background-color: #051630;
                        border: 1px solid #0B1E36;
                        border-radius: 4px;
                        color: #E2E8F0;
                        font-family: 'Consolas', monospace;
                        font-size: 11px;
                        padding: 4px;
                    }
                """)
        
        layout.addLayout(grid)

        # Save Preferences Button
        self.save_pref_btn = QPushButton("COMMIT PROFILE SETTINGS")
        self.save_pref_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B1E36;
                border: 1px solid #00F0FF;
                border-radius: 4px;
                color: #00F0FF;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #00F0FF;
                color: #030F26;
            }
        """)
        self.save_pref_btn.clicked.connect(self.save_profile_fields)
        layout.addWidget(self.save_pref_btn)

        # Long Term Memories list
        mem_lbl = QLabel("LONG-TERM FACT ASSOCIATION REGISTRY:")
        mem_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold; margin-top: 10px;")
        layout.addWidget(mem_lbl)

        # Create tab widget with separate lists per category
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabBar::tab { padding: 4px 8px; }
        """)
        # Helper to create a styled QListWidget
        def create_list():
            lst = QListWidget()
            lst.setStyleSheet("""
                QListWidget {
                    background-color: #030F26;
                    border: 1px solid #0B1E36;
                    border-radius: 4px;
                    color: #E2E8F0;
                    font-family: 'Consolas', monospace;
                    font-size: 11px;
                    padding: 6px;
                }
                QListWidget::item { padding: 4px; }
                QListWidget::item:selected { background-color: #0B1E36; color: #00F0FF; }
            """)
            return lst
        self.personal_list = create_list()
        self.project_list = create_list()
        self.preference_list = create_list()
        self.goal_list = create_list()
        self.task_list = create_list()
        self.tab_widget.addTab(self.personal_list, "Personal")
        self.tab_widget.addTab(self.project_list, "Projects")
        self.tab_widget.addTab(self.preference_list, "Preferences")
        self.tab_widget.addTab(self.goal_list, "Goals")
        self.tab_widget.addTab(self.task_list, "Tasks")
        layout.addWidget(self.tab_widget)

        # Memory actions buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        self.forget_btn = QPushButton("FORGET FACT")
        self.forget_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B1E36;
                border: 1px solid #EF4444;
                border-radius: 4px;
                color: #EF4444;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #FFFFFF;
            }
        """)
        self.forget_btn.clicked.connect(self.forget_selected_fact)
        btn_layout.addWidget(self.forget_btn)

        self.purge_btn = QPushButton("PURGE MEMORY STORE")
        self.purge_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B1E36;
                border: 1px solid #EF4444;
                border-radius: 4px;
                color: #EF4444;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #B91C1C;
                color: #FFFFFF;
            }
        """)
        self.purge_btn.clicked.connect(self.purge_database)
        btn_layout.addWidget(self.purge_btn)

        layout.addLayout(btn_layout)

    def load_profile_fields(self):
        username = self.memory.get_profile_value("username", config.USER_NAME)
        preferred_editor = self.memory.get_profile_value("preferred_editor", "VS Code")
        api_key = self.memory.get_profile_value("gemini_api_key", "")

        self.name_input.setText(username)
        self.editor_input.setText(preferred_editor)
        self.api_key_input.setText(api_key)

        # Update config directly if API key was stored
        if api_key:
            self.brain.llm.update_api_key(api_key)

    def save_profile_fields(self):
        name = self.name_input.text().strip()
        editor = self.editor_input.text().strip()
        api_key = self.api_key_input.text().strip()

        if name:
            self.memory.set_profile_value("username", name)
            config.USER_NAME = name
        if editor:
            self.memory.set_profile_value("preferred_editor", editor)
            # Update app launcher registry mappings
            config.APP_REGISTRY["vs code"] = f"C:\\Users\\{name}\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            config.APP_REGISTRY["visual studio code"] = config.APP_REGISTRY["vs code"]
            
        self.memory.set_profile_value("gemini_api_key", api_key)
        self.brain.llm.update_api_key(api_key)
        
        logger.info("UI MemoryPanel: Profile preferences committed to database.")
        QMessageBox.information(self, "Memory System", "Profile credentials updated successfully.")

    def refresh_memory_list(self):
        # Clear each category list
        for lst in [self.personal_list, self.project_list, self.preference_list, self.goal_list, self.task_list]:
            lst.clear()
        # Populate lists by category
        category_map = {
            "personal": self.personal_list,
            "project": self.project_list,
            "preference": self.preference_list,
            "goal": self.goal_list,
            "task": self.task_list,
        }
        all_facts = self.memory.get_all_facts()
        for fact in all_facts:
            cat = fact.get("category", "general")
            target_lst = category_map.get(cat)
            if target_lst:
                target_lst.addItem(fact["fact"])
            else:
                # Fallback to personal if unknown category
                self.personal_list.addItem(fact["fact"])

    def forget_selected_fact(self):
        # Determine which list is currently visible (active tab)
        current_list = self.tab_widget.currentWidget()
        if not isinstance(current_list, QListWidget):
            return
        selected = current_list.currentItem()
        if not selected:
            return
        fact_text = selected.text()
        self.memory.delete_fact(fact_text)
        self.refresh_memory_list()
        logger.info(f"UI MemoryPanel: Removed fact from database: '{fact_text}'")

    def purge_database(self):
        reply = QMessageBox.question(
            self, 
            "Purge Confirmation", 
            "Are you absolutely sure you want to purge FRIDAY's memory? This action is irreversible.",
            QMessageBox.Yes | QMessageBox.No,  
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.memory.clear_all_memory()
            self.refresh_memory_list()
            self.load_profile_fields()
            QMessageBox.information(self, "Memory System", "System databases purged. Restored offline factory configurations.")
