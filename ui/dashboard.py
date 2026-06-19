import os
import time
import datetime
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QPushButton, QSplitter, QStyle, QProgressBar, QFileDialog, QGridLayout
import os
from PyQt5.QtCore import QTimer, Qt, pyqtSlot
from PyQt5.QtGui import QFont, QPixmap, QFontDatabase

# Import custom panels and widgets
from ui.widgets.hud_circle import HUDAntiGravityCircle
from utils.system_monitor import SystemMonitor
from ui.widgets.waveform_widget import HUDAntiGravityWaveform
from ui.panels.chat_panel import ChatPanel
from ui.panels.voice_panel import VoicePanel
from ui.panels.system_panel import SystemPanel
from ui.panels.automation_panel import AutomationPanel
from ui.panels.memory_panel import MemoryPanel
from PyQt5.QtWidgets import QDialog
# SecurityLoginDialog import removed
from PyQt5.QtWidgets import QMessageBox

from utils import logger
import config

class FRIDAYDashboard(QMainWindow):
    """
    Main HUD window representing the FRIDAY AI Operating System interface.
    Links the voice capture pipelines, system stats thread, and AI brain logic.
    """
    def __init__(self, brain_instance, voice_instance, monitor_thread, parent=None):
        super().__init__(parent)
        self.brain = brain_instance
        self.voice = voice_instance
        self.monitor = monitor_thread
        
        self.listening_active = True
        self.init_ui()
        self.connect_signals()
        # Prompt for authentication on startup
        # Authentication prompt removed

    def init_ui(self):
        self.setWindowTitle(f"{config.SYSTEM_NAME} AI Operating System")
        self.resize(1000, 680)

        # Global stylesheet setting up futuristic dark blue/cyan theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #030F26;
            }
            QWidget {
                color: #E2E8F0;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }
            QLabel {
                font-family: 'Consolas', monospace;
            }
            QTabWidget::pane {
                border: 1px solid #0B1E36;
                background-color: #030F26;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #051630;
                border: 1px solid #0B1E36;
                color: #94A3B8;
                padding: 8px 16px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                font-weight: bold;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #030F26;
                border-bottom: 2px solid #00F0FF;
                color: #00F0FF;
            }
            QTabBar::tab:hover {
                background-color: #0B1E36;
                color: #88F5FF;
            }
        """)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(10)

        # ==================== 1. TOP HEADER BAR ====================
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 5, 5, 5)

        # FRIDAY Logo/Title
        # Chief Profile Section
        self.avatar_lbl = QLabel()
        default_avatar = getattr(config, "AVATAR_DEFAULT", "")
        if default_avatar and os.path.isfile(default_avatar):
            self.avatar_lbl.setPixmap(QPixmap(default_avatar).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.avatar_lbl.setStyleSheet("background-color: #0B1E36; border-radius: 20px;")
        self.avatar_lbl.setFixedSize(40, 40)

        self.name_lbl = QLabel("Chief")
        self.name_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #00F0FF;")

        self.edit_profile_btn = QPushButton("Edit")
        self.edit_profile_btn.setFixedSize(30, 30)
        self.edit_profile_btn.setStyleSheet("background-color: #051630; border: 1px solid #00F0FF; color: #00F0FF;")
        self.edit_profile_btn.clicked.connect(self.edit_profile)

        profile_layout = QHBoxLayout()
        profile_layout.addWidget(self.avatar_lbl)
        profile_layout.addWidget(self.name_lbl)
        profile_layout.addWidget(self.edit_profile_btn)
        header_layout.addLayout(profile_layout)
        
        header_layout.addStretch()

        # Dynamic System Greeting (e.g. Good Afternoon, Chief)
        self.greeting_lbl = QLabel("Initializing biosync matrices...")
        self.greeting_lbl.setStyleSheet("font-size: 12px; color: #10B981; font-weight: bold;")
        header_layout.addWidget(self.greeting_lbl)

        header_layout.addSpacing(25)

        # Digital Clock
        self.clock_lbl = QLabel("00:00:00")
        self.clock_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #00F0FF; font-family: 'Consolas', monospace;")
        header_layout.addWidget(self.clock_lbl)

        main_layout.addLayout(header_layout)

        # Divider line
        div = QWidget()
        div.setFixedHeight(2)
        div.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F0FF, stop:0.5 #0B1E36, stop:1 #030F26);")
        main_layout.addWidget(div)

        # ------- Top‑Right HUD Info Panel -------
        self.info_panel = QWidget()
        self.info_panel.setObjectName("infoPanel")
        info_layout = QGridLayout(self.info_panel)
        info_layout.setSpacing(5)

        # AI Status (placeholder animated icon)
        self.ai_status_lbl = QLabel()
        self.ai_status_lbl.setObjectName("aiStatusLabel")
        self.ai_status_lbl.setFixedSize(24, 24)
        self.ai_status_lbl.setStyleSheet("background-color: #00F0FF; border-radius: 12px;")

        # CPU Usage
        self.cpu_label = QLabel("CPU")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        self.cpu_progress.setTextVisible(False)

        # Memory Usage
        self.mem_label = QLabel("Memory")
        self.mem_progress = QProgressBar()
        self.mem_progress.setMaximum(100)
        self.mem_progress.setTextVisible(False)

        # Model / Voice / Workflow
        self.model_lbl = QLabel("Model: N/A")
        self.voice_lbl = QLabel("Voice: N/A")
        self.workflow_lbl = QLabel("Workflow: N/A")

        # Assemble grid
        info_layout.addWidget(self.ai_status_lbl, 0, 0, Qt.AlignCenter)
        info_layout.addWidget(self.cpu_label, 0, 1)
        info_layout.addWidget(self.cpu_progress, 0, 2)
        info_layout.addWidget(self.mem_label, 1, 1)
        info_layout.addWidget(self.mem_progress, 1, 2)
        info_layout.addWidget(self.model_lbl, 2, 0, 1, 3)
        info_layout.addWidget(self.voice_lbl, 3, 0, 1, 3)
        info_layout.addWidget(self.workflow_lbl, 4, 0, 1, 3)

        main_layout.addWidget(self.info_panel)

        # ==================== 2. MAIN HUB INTERFACE ====================
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setHandleWidth(2)
        content_splitter.setStyleSheet("QSplitter::handle { background-color: #0B1E36; }")

        # Left Column - Visualizer Core
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 15, 5)
        left_layout.setSpacing(12)

        # HUD Center Indicator
        self.hud_circle = HUDAntiGravityCircle()
        left_layout.addWidget(self.hud_circle, alignment=Qt.AlignCenter)

        # Waveform graph
        self.waveform = HUDAntiGravityWaveform()
        left_layout.addWidget(self.waveform)

        # System state label
        self.status_desc_lbl = QLabel("CORE OPERATIONAL SYSTEM: SECURE")
        self.status_desc_lbl.setAlignment(Qt.AlignCenter)
        self.status_desc_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold; letter-spacing: 1px;")
        left_layout.addWidget(self.status_desc_lbl)

        # Quick Control Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.mic_toggle_btn = QPushButton("PAUSE LISTENING")
        self.mic_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #051630;
                border: 1px solid #10B981;
                border-radius: 4px;
                color: #10B981;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #10B981;
                color: #030F26;
            }
        """)
        self.mic_toggle_btn.clicked.connect(self.toggle_mic_listening)
        btn_row.addWidget(self.mic_toggle_btn)

        self.force_prompt_btn = QPushButton("FORCE ACTIVATE")
        self.force_prompt_btn.setStyleSheet("""
            QPushButton {
                background-color: #051630;
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
        self.force_prompt_btn.clicked.connect(self.trigger_force_active)
        btn_row.addWidget(self.force_prompt_btn)

        left_layout.addLayout(btn_row)
        left_layout.addStretch()

        content_splitter.addWidget(left_widget)

        # Right Column - Panels Container (Tab Control)
        self.panels_tab = QTabWidget()
        
        # Instantiate Panels
        self.chat_panel = ChatPanel()
        self.voice_panel = VoicePanel()
        self.system_panel = SystemPanel()
        self.automation_panel = AutomationPanel(self.brain.workflow_engine)
        self.memory_panel = MemoryPanel(self.brain)

        # Add tabs
        self.panels_tab.addTab(self.chat_panel, "AI COGNITION")
        self.panels_tab.addTab(self.voice_panel, "RECEIVER TELEMETRY")
        self.panels_tab.addTab(self.system_panel, "SYSTEM CORE")
        self.panels_tab.addTab(self.automation_panel, "WORKFLOW ENGINE")
        self.panels_tab.addTab(self.memory_panel, "MEMORY DATABASE")

        content_splitter.addWidget(self.panels_tab)
        
        # Set splitter proportions (30% left, 70% right)
        content_splitter.setSizes([320, 680])
        main_layout.addWidget(content_splitter)

        # ==================== 3. BOTTOM TICKER BAR ====================
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(5, 0, 5, 0)
        
        self.logs_ticker = QLabel("FRIDAY OS: Core networks loaded. Standing by for voice prompt.")
        self.logs_ticker.setStyleSheet("font-size: 10px; color: #475569; font-style: italic;")
        bottom_layout.addWidget(self.logs_ticker)
        
        bottom_layout.addStretch()
        
        status_point = QLabel("BIOSYNC LINK: OPTIMAL")
        status_point.setStyleSheet("font-size: 10px; color: #10B981; font-weight: bold;")
        bottom_layout.addWidget(status_point)

        main_layout.addLayout(bottom_layout)

        # Header Timers (Clock and Greeting)
        self.header_timer = QTimer(self)
        self.header_timer.timeout.connect(self.update_header_data)
        self.header_timer.start(500)

        # Run first time greet update
        self.update_header_data()

        # System metrics timer (updates HUD widgets every 2 seconds)
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_system_metrics)
        self.stats_timer.start(2000)

    def connect_signals(self):
        # 1. Connect Voice Panel Device Selector to Voice Engine
        self.voice_panel.device_changed.connect(self.voice.set_device)

        # 2. Connect Voice Engine Level/Waveform to UI Panels/Widgets
        self.voice.level_updated.connect(self.voice_panel.update_volume_level)
        self.voice.level_updated.connect(self.hud_circle.set_volume_level)
        self.voice.waveform_updated.connect(self.waveform.set_waveform_data)

        # 3. Connect Voice Engine Status notifications
        self.voice.status_changed.connect(self.on_voice_state_changed)
        self.voice.status_changed.connect(self.hud_circle.set_state)

        # 4. Connect Voice STT Transcript capture to AI Brain
        self.voice.transcript_ready.connect(self.handle_voice_transcript)

        # 5. Connect Brain responses to UI Panels/Speech synthesis
        self.brain.response_completed.connect(self.handle_brain_response)
        self.brain.speak_requested.connect(self.speak_text)
        self.brain.workflow_trigger.connect(self.trigger_workflow)
        self.brain.system_exit_triggered.connect(self.close)

        # 6. Connect Chat Manual Inputs to Brain
        self.chat_panel.text_query_submitted.connect(self.handle_manual_query)

        # 7. Connect System Stats Thread updates
        self.monitor.stats_updated.connect(self.system_panel.update_system_stats)

        # 8. Connect Automation Panel workflow trigger button
        self.automation_panel.run_workflow_requested.connect(self.trigger_workflow)

    def update_header_data(self):
        # Clock
        now = datetime.datetime.now()
        self.clock_lbl.setText(now.strftime("%H:%M:%S"))

        # Greeting logic
        hour = now.hour
        if 5 <= hour < 12:
            time_of_day = "morning"
        elif 12 <= hour < 18:
            time_of_day = "afternoon"
        elif 18 <= hour < 22:
            time_of_day = "evening"
        else:
            time_of_day = "night"

        username = self.brain.memory.get_profile_value("username", config.USER_NAME)
        greeting = config.GREETING_FORMAT.format(time_of_day=time_of_day, user=username)
        self.greeting_lbl.setText(greeting.upper())

    # ==================== UI SLOTS & TRIGGERS ====================
    @pyqtSlot(str)
    def on_voice_state_changed(self, state):
        self.status_desc_lbl.setText(f"FRIDAY OS STATUS: {state.upper()}")
        self.logs_ticker.setText(f"System status change: {state.upper()}")

    @pyqtSlot(str)
    def handle_voice_transcript(self, text):
        if not text.strip():
            # If listening was active but nothing heard
            return

        # Continuous mode / wake word detection check
        q = text.lower().strip()
        
        # Check if wake word is spoken when in continuous loop
        has_wake_word = any(ww in q for ww in config.WAKE_WORDS)

        if has_wake_word:
            # Strip the wake word
            clean_query = text
            for ww in config.WAKE_WORDS:
                clean_query = clean_query.replace(ww, "")
            clean_query = clean_query.strip()
            
            # Switch view to chat tab
            self.panels_tab.setCurrentIndex(0)
            self.chat_panel.add_user_message(text)
            
            if clean_query:
                # If command followed wake word directly
                self.brain.process_query(clean_query)
            else:
                # Just wake word spoken, prompt Chief
                username = self.brain.memory.get_profile_value("username", config.USER_NAME)
                response = f"At your service, {username}. How can I assist you?"
                self.chat_panel.add_friday_message(response)
                self.speak_text(response)
        else:
            # If chat tab is currently visible, user expects us to capture direct speech without wake words
            if self.panels_tab.currentIndex() == 0:
                self.chat_panel.add_user_message(text)
                self.brain.process_query(text)
            else:
                logger.info(f"FRIDAY Voice: Heard '{text}' but wake word not detected. Discarding.")

    @pyqtSlot(str)
    def handle_manual_query(self, query):
        """Processes text submitted manually via the Chat tab's RUN command."""
        self.chat_panel.add_user_message(query)
        self.hud_circle.set_state("Thinking")
        # Run process query in background to avoid freezing ui
        QTimer.singleShot(50, lambda: self.brain.process_query(query))

    @pyqtSlot(str, str)
    def handle_brain_response(self, user_msg, response_msg):
        self.chat_panel.add_friday_message(response_msg)
        self.memory_panel.refresh_memory_list()

    @pyqtSlot(str)
    def speak_text(self, text):
        """Triggers FRIDAY speak thread. Also notifies HUD circle."""
        self.voice_panel.diag_display.append(f"<span style='color: #10B981;'>[SPEECH SYNTHESIS] {text}</span>")
        
        # Connect speech worker animations
        # We temporarily change voice status to "Speaking"
        self.hud_circle.set_state("Speaking")
        
        # Trigger actual TTS
        from voice.tts_worker import TTSWorker
        # We check if voice engine has an active TTS thread
        if hasattr(self, 'tts_worker') and self.tts_worker.isRunning():
            self.tts_worker.speak(text)
        else:
            # Setup worker
            self.tts_worker = TTSWorker()
            self.tts_worker.speaking_finished.connect(lambda: self.hud_circle.set_state("Idle"))
            self.tts_worker.start()
            self.tts_worker.speak(text)

    @pyqtSlot(str)
    def trigger_workflow(self, name):
        """Starts a workflow thread sequence and tracks active workflow for HUD."""
        self.panels_tab.setCurrentIndex(3)  # Move to Workflow tab
        # Record currently executing workflow for HUD display
        self.brain._current_workflow = name
        self.brain.workflow_engine.execute_workflow(
            name,
            speak_cb=self.speak_text,
            step_start_cb=self.automation_panel.on_step_started,
            step_end_cb=self.automation_panel.on_step_completed,
            completed_cb=self.automation_panel.on_workflow_completed
        )

    def toggle_mic_listening(self):
        """Pauses/resumes the VoiceEngine sound capture loop."""
        if self.listening_active:
            self.listening_active = False
            self.voice.running = False  # Terminate loop
            self.mic_toggle_btn.setText("RESUME LISTENING")
            self.mic_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #051630;
                    border: 1px solid #EF4444;
                    border-radius: 4px;
                    color: #EF4444;
                    font-family: 'Consolas', monospace;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #EF4444;
                    color: #030F26;
                }
            """)
            self.hud_circle.set_state("Error")
            logger.info("VoiceEngine audio feed paused manually by User.")
        else:
            self.listening_active = True
            # Recreate/restart VoiceEngine capture thread
            self.voice.running = True
            # Since QThread can only be started once if stopped, we restart it safely or launch
            if not self.voice.isRunning():
                self.voice.start()
            self.mic_toggle_btn.setText("PAUSE LISTENING")
            self.mic_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #051630;
                    border: 1px solid #10B981;
                    border-radius: 4px;
                    color: #10B981;
                    font-family: 'Consolas', monospace;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #10B981;
                    color: #030F26;
                }
            """)
            self.hud_circle.set_state("Idle")
            logger.info("VoiceEngine audio feed resumed manually by User.")

    def trigger_force_active(self):
        """Wakes up the voice engine and forces it to start capturing speech right now."""
        if not self.listening_active:
            self.toggle_mic_listening()
        
        self.panels_tab.setCurrentIndex(0) # Open chat tab
        self.hud_circle.set_state("Listening")
        self.voice.is_recording = True
        self.voice.speech_start_time = time.time()
        self.voice.recording_buffer = []
        logger.info("Force activation trigger: FRIDAY listening...")

    def closeEvent(self, event):
        """Ensure all background threads stop safely when closing application."""
        logger.info("Closing FRIDAY Operating System. Stopping background threads...")
        self.monitor.stop()
        self.voice.stop()
        if hasattr(self, 'tts_worker'):
            self.tts_worker.stop()
        event.accept()

    # ---------------------------------------------------------------------
    # UI helper slots
    # ---------------------------------------------------------------------
    @pyqtSlot()
    def update_system_metrics(self):
        """Refresh HUD metric widgets with live system stats."""
        cpu = SystemMonitor.cpu_percent()
        mem = SystemMonitor.ram_percent()
        self.cpu_progress.setValue(cpu)
        self.cpu_label.setText(f"CPU {cpu}%")
        self.mem_progress.setValue(mem)
        self.mem_label.setText(f"Memory {mem}%")
        # Update model / voice / workflow labels via brain getters
        self.model_lbl.setText(f"Model: {self.brain.get_active_model()}")
        self.voice_lbl.setText(f"Voice: {self.brain.get_active_voice()}")
        self.workflow_lbl.setText(f"Workflow: {self.brain.get_active_workflow()}")

    @pyqtSlot()
    def edit_profile(self):
        """Open a file dialog to select a new avatar image."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Avatar Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.avatar_lbl.setPixmap(QPixmap(file_path).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            # Persist path in config for next launches
            setattr(config, "AVATAR_DEFAULT", file_path)

# Login dialog functionality removed after security system deletion
