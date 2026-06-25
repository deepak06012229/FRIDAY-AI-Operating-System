import os
import sys
import time
import datetime
import socket
import urllib.request
import threading
import random
import psutil
import numpy as np

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSplitter, QProgressBar, QFileDialog, QGridLayout, 
    QScrollArea, QFrame, QLineEdit, QTextBrowser, QDialog, QListWidget, QTextEdit, QComboBox, QSlider
)
from PyQt5.QtCore import QTimer, Qt, pyqtSlot, QMetaObject, Q_ARG, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPixmap, QColor, QIcon, QPainter, QBrush, QRadialGradient

# Import custom panels and widgets
from ui.widgets.glass_panel import GlassPanel
from ui.widgets.friday_core import FridayHUDCenterpiece
from ui.widgets.friday_waveform import FridayWaveformWidget
from ui.widgets.system_hud import HUDProgressCircle
from utils.system_monitor import SystemMonitor

# Import popup sub-panels
from ui.panels.automation_panel import AutomationPanel
from ui.panels.memory_panel import MemoryPanel
from ui.panels.voice_panel import VoicePanel
from ui.panels.system_panel import SystemPanel

from utils import logger
import config

class GlassDialog(QDialog):
    """
    A custom floating QDialog with glassmorphic styling to display
    expanded sub-panel consoles (Automation, Memory, Calibration, etc.)
    """
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(750, 520)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #050608;
                border: 2px solid #00F0FF;
                border-radius: 12px;
            }
            QWidget {
                color: #E2E8F0;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }
            QLabel {
                font-family: 'Consolas', monospace;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header Title
        hdr_layout = QHBoxLayout()
        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet("font-size: 13px; font-weight: bold; color: #00F0FF; letter-spacing: 2px;")
        hdr_layout.addWidget(self.title_lbl)
        hdr_layout.addStretch()

        close_btn = QPushButton("DISMISS")
        close_btn.setFixedSize(70, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(239, 68, 68, 0.15);
                border: 1px solid #EF4444;
                border-radius: 4px;
                color: #EF4444;
                font-family: 'Consolas', monospace;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: #050608;
            }
        """)
        close_btn.clicked.connect(self.close)
        hdr_layout.addWidget(close_btn)
        layout.addLayout(hdr_layout)

        # Divider
        div = QWidget()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: rgba(0, 240, 255, 0.25);")
        layout.addWidget(div)

        # Center content
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_widget)


class FRIDAYDashboard(QMainWindow):
    """
    Futuristic 1920x1080 Cyberpunk HUD dashboard representing
    the F.R.I.D.A.Y. AI Operating System interface.
    """
    def __init__(self, brain_instance, voice_instance, monitor_thread, parent=None):
        super().__init__(parent)
        self.brain = brain_instance
        self.voice = voice_instance
        self.monitor = monitor_thread
        
        self.listening_active = True
        self.app_labels = {}
        self.app_dots = {}
        self.prev_net_io = psutil.net_io_counters()
        self.prev_net_time = time.time()
        self.current_track_idx = 0
        self.tracks = [
            "F.R.I.D.A.Y. Cyber Synth Theme",
            "DeepMind Matrix Core - LoFi Mix",
            "Iron Man Arc Reactor Grid - 130 BPM"
        ]
        self.music_playing = True
        self.music_elapsed = 0
        
        self.init_ui()
        self.connect_signals()
        
        # Register logger callback to capture logs to our HUD console
        logger.register_log_callback(self.receive_log_message)

    def init_ui(self):
        self.setWindowTitle(f"{config.SYSTEM_NAME} AI Operating System HUD")
        self.resize(1920, 1080)
        self.setMinimumSize(1920, 1080)

        # Global stylesheet setting up futuristic dark blue/cyan theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #050608;
            }
            QWidget {
                color: #E2E8F0;
                font-family: 'Segoe UI', -apple-system, sans-serif;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #050608;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 240, 255, 0.3);
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #00F0FF;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Central Widget & Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 10, 15, 10)
        main_layout.setSpacing(12)

        # ==================== 1. TOP HEADER BAR ====================
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 10, 5)

        # Left: User Profile & Online status
        avatar_path = os.path.join(config.BASE_DIR, "assets", "friday_avatar.png")
        profile_box = QHBoxLayout()
        self.avatar_lbl = QLabel()
        self.avatar_lbl.setFixedSize(46, 46)
        self.avatar_lbl.setCursor(Qt.PointingHandCursor)
        self.avatar_lbl.mousePressEvent = lambda e: self.edit_profile()
        
        self.avatar_lbl.setStyleSheet("border: 2px solid #00F0FF; border-radius: 23px; background-color: #050608;")
        if os.path.exists(avatar_path):
            self.avatar_lbl.setPixmap(QPixmap(avatar_path).scaled(42, 42, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        profile_info = QVBoxLayout()
        profile_info.setSpacing(2)
        
        name_row = QHBoxLayout()
        self.name_lbl = QLabel(config.USER_NAME.upper())
        self.name_lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #FFFFFF; font-family: 'Consolas';")
        name_row.addWidget(self.name_lbl)
        
        # Pulse indicator dot
        self.status_dot = QLabel()
        self.status_dot.setFixedSize(8, 8)
        self.status_dot.setStyleSheet("background-color: #10B981; border-radius: 4px;") # Green
        name_row.addWidget(self.status_dot)
        name_row.addStretch()
        
        status_lbl = QLabel("SYSOP LINK ACTIVE")
        status_lbl.setStyleSheet("font-size: 8px; color: #10B981; font-weight: bold; letter-spacing: 1px;")
        
        profile_info.addLayout(name_row)
        profile_info.addWidget(status_lbl)
        
        profile_box.addWidget(self.avatar_lbl)
        profile_box.addLayout(profile_info)
        header_layout.addLayout(profile_box)

        header_layout.addStretch()

        # Center: Logo & Subtitle
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(1)
        self.logo_lbl = QLabel(config.SYSTEM_NAME)
        self.logo_lbl.setAlignment(Qt.AlignCenter)
        self.logo_lbl.setStyleSheet("""
            color: #00F0FF;
            font-size: 32px;
            font-weight: 900;
            letter-spacing: 6px;
            font-family: 'Segoe UI', 'Orbitron', sans-serif;
            qproperty-alignment: AlignCenter;
            background: transparent;
        """)
        
        subtitle_lbl = QLabel("ARTIFICIAL INTELLIGENCE OPERATING SYSTEM")
        subtitle_lbl.setAlignment(Qt.AlignCenter)
        subtitle_lbl.setStyleSheet("font-size: 8px; color: #64748B; letter-spacing: 3px; font-weight: bold;")
        
        logo_layout.addWidget(self.logo_lbl)
        logo_layout.addWidget(subtitle_lbl)
        header_layout.addLayout(logo_layout)

        header_layout.addStretch()

        # Right: CPU/GPU Temp & Time
        right_header = QHBoxLayout()
        right_header.setSpacing(20)
        
        temp_layout = QVBoxLayout()
        temp_layout.setSpacing(2)
        self.cpu_temp_lbl = QLabel("CPU TEMP: 45°C")
        self.gpu_temp_lbl = QLabel("GPU TEMP: 51°C")
        for lbl in (self.cpu_temp_lbl, self.gpu_temp_lbl):
            lbl.setStyleSheet("font-family: 'Consolas'; font-size: 10px; color: #E2E8F0;")
        temp_layout.addWidget(self.cpu_temp_lbl)
        temp_layout.addWidget(self.gpu_temp_lbl)
        right_header.addLayout(temp_layout)

        clock_box = QVBoxLayout()
        clock_box.setSpacing(1)
        clock_box.setAlignment(Qt.AlignRight)
        
        self.clock_lbl = QLabel("00:00:00")
        self.clock_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: #00F0FF; font-family: 'Consolas';")
        self.date_lbl = QLabel("25 JUN 2026")
        self.date_lbl.setAlignment(Qt.AlignRight)
        self.date_lbl.setStyleSheet("font-size: 9px; color: #64748B; font-weight: bold;")
        
        clock_box.addWidget(self.clock_lbl)
        clock_box.addWidget(self.date_lbl)
        right_header.addLayout(clock_box)
        
        header_layout.addLayout(right_header)
        main_layout.addLayout(header_layout)

        # Top divider glow
        div = QWidget()
        div.setFixedHeight(2)
        div.setStyleSheet("background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A56DB, stop:0.5 #00F0FF, stop:1 #1A56DB);")
        main_layout.addWidget(div)

        # ==================== 2. THREE COLUMN LAYOUT ====================
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(15)

        # ------------ LEFT SIDEBAR (SCROLLABLE) ------------
        left_scroll = QScrollArea()
        left_scroll.setFixedWidth(400)
        left_scroll.setWidgetResizable(True)
        
        left_container = QWidget()
        left_container.setStyleSheet("background: transparent;")
        left_vbox = QVBoxLayout(left_container)
        left_vbox.setContentsMargins(0, 0, 10, 0)
        left_vbox.setSpacing(15)

        # 1. AI Profile
        self.profile_panel = GlassPanel("AI Profile")
        self.profile_panel.setMinimumHeight(150)
        avatar_row = QHBoxLayout()
        self.profile_avatar_lbl = QLabel()
        self.profile_avatar_lbl.setFixedSize(64, 64)
        self.profile_avatar_lbl.setStyleSheet("border: 2px solid #00F0FF; border-radius: 32px; background-color: #050608;")
        if os.path.exists(avatar_path):
            self.profile_avatar_lbl.setPixmap(QPixmap(avatar_path).scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        profile_text = QVBoxLayout()
        profile_text.setSpacing(3)
        self.profile_greet = QLabel("Initializing biosync matrices...")
        self.profile_greet.setWordWrap(True)
        self.profile_greet.setStyleSheet("font-size: 11px; color: #10B981; font-weight: bold;")
        self.profile_status = QLabel("STATUS: SECURED STANDBY")
        self.profile_status.setStyleSheet("font-size: 9px; font-family: 'Consolas'; color: #64748B;")
        
        profile_text.addWidget(self.profile_greet)
        profile_text.addWidget(self.profile_status)
        
        avatar_row.addWidget(self.profile_avatar_lbl)
        avatar_row.addLayout(profile_text)
        
        # Audio Waveform Widget for AI Voice Output
        self.ai_voice_waveform = FridayWaveformWidget()
        self.ai_voice_waveform.setFixedHeight(45)
        
        self.profile_panel.add_layout(avatar_row)
        self.profile_panel.add_widget(self.ai_voice_waveform)
        left_vbox.addWidget(self.profile_panel)

        # 2. System Monitor
        self.sys_panel = GlassPanel("System Monitor")
        self.sys_panel.setMinimumHeight(260)
        sys_grid = QGridLayout()
        sys_grid.setSpacing(10)
        
        self.cpu_gauge = HUDProgressCircle("CPU", "%")
        self.gpu_gauge = HUDProgressCircle("GPU", "%")
        self.ram_gauge = HUDProgressCircle("RAM", "%")
        self.vram_gauge = HUDProgressCircle("VRAM", "%")
        self.disk_gauge = HUDProgressCircle("DISK", "%")
        self.temp_gauge = HUDProgressCircle("TEMP", "C")
        
        sys_grid.addWidget(self.cpu_gauge, 0, 0)
        sys_grid.addWidget(self.gpu_gauge, 0, 1)
        sys_grid.addWidget(self.ram_gauge, 0, 2)
        sys_grid.addWidget(self.vram_gauge, 1, 0)
        sys_grid.addWidget(self.disk_gauge, 1, 1)
        sys_grid.addWidget(self.temp_gauge, 1, 2)
        self.sys_panel.add_layout(sys_grid)
        
        self.uptime_lbl = QLabel("SYSTEM UPTIME: --")
        self.uptime_lbl.setStyleSheet("font-family: 'Consolas'; font-size: 9.5px; color: #64748B;")
        self.battery_lbl = QLabel("BATTERY STATE: --")
        self.battery_lbl.setStyleSheet("font-family: 'Consolas'; font-size: 9.5px; color: #64748B;")
        
        lbl_layout = QHBoxLayout()
        lbl_layout.addWidget(self.uptime_lbl)
        lbl_layout.addWidget(self.battery_lbl)
        self.sys_panel.add_layout(lbl_layout)
        left_vbox.addWidget(self.sys_panel)

        # 3. Network
        self.net_panel = GlassPanel("Network Telemetry")
        self.net_panel.setMinimumHeight(130)
        net_grid = QGridLayout()
        net_grid.setSpacing(8)
        
        self.net_down_lbl = QLabel("DOWNLOAD: 0.0 KB/s")
        self.net_up_lbl = QLabel("UPLOAD: 0.0 KB/s")
        self.net_ping_lbl = QLabel("PING: -- ms")
        self.local_ip_lbl = QLabel("LOCAL IP: 127.0.0.1")
        self.public_ip_lbl = QLabel("PUBLIC IP: FETCHING...")
        
        for lbl in (self.net_down_lbl, self.net_up_lbl, self.net_ping_lbl, self.local_ip_lbl, self.public_ip_lbl):
            lbl.setStyleSheet("font-family: 'Consolas'; font-size: 10px; color: #E2E8F0;")
            
        net_grid.addWidget(self.net_down_lbl, 0, 0)
        net_grid.addWidget(self.net_up_lbl, 0, 1)
        net_grid.addWidget(self.net_ping_lbl, 1, 0)
        net_grid.addWidget(self.local_ip_lbl, 1, 1)
        net_grid.addWidget(self.public_ip_lbl, 2, 0, 1, 2)
        
        self.net_panel.add_layout(net_grid)
        left_vbox.addWidget(self.net_panel)

        # 4. AI Brain
        self.brain_panel = GlassPanel("AI Cognitive Brain")
        self.brain_panel.setMinimumHeight(160)
        brain_vbox = QVBoxLayout()
        brain_vbox.setSpacing(6)
        
        self.brain_model = QLabel("MODEL: LLM SERVER STANDBY")
        self.brain_mem = QLabel("ACTIVE MEMORY: -- NODES")
        self.brain_status = QLabel("LEARNING MODE: ACTIVE")
        self.brain_agents = QLabel("ACTIVE AGENTS: 4 RUNNING")
        self.brain_context = QLabel("CONTEXT WINDOW: 32K TOKENS")
        self.brain_tokens = QLabel("TOKENS CONSUMED: 0")
        
        for lbl in (self.brain_model, self.brain_mem, self.brain_status, self.brain_agents, self.brain_context, self.brain_tokens):
            lbl.setStyleSheet("font-family: 'Consolas'; font-size: 10px; color: #E2E8F0;")
            brain_vbox.addWidget(lbl)
            
        self.brain_panel.add_layout(brain_vbox)
        left_vbox.addWidget(self.brain_panel)

        # 5. Voice Input
        self.voice_input_panel = GlassPanel("Voice Input Receiver")
        self.voice_input_panel.setMinimumHeight(130)
        
        self.live_mic_waveform = FridayWaveformWidget()
        self.live_mic_waveform.setFixedHeight(50)
        self.voice_input_panel.add_widget(self.live_mic_waveform)
        
        # Audio energy level progress bar
        self.mic_level_bar = QProgressBar()
        self.mic_level_bar.setRange(0, 100)
        self.mic_level_bar.setValue(0)
        self.mic_level_bar.setTextVisible(False)
        self.mic_level_bar.setFixedHeight(8)
        self.mic_level_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(5, 12, 24, 0.8);
                border: 1px solid rgba(0, 240, 255, 0.25);
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1A56DB, stop:1 #00F0FF);
                border-radius: 3px;
            }
        """)
        self.voice_input_panel.add_widget(self.mic_level_bar)
        
        voice_status_layout = QHBoxLayout()
        self.listening_state_lbl = QLabel("LISTENING: STANDBY")
        self.listening_state_lbl.setStyleSheet("font-family: 'Consolas'; font-size: 9px; color: #10B981; font-weight: bold;")
        self.wake_word_lbl = QLabel("WAKE WORD: 'FRIDAY'")
        self.wake_word_lbl.setStyleSheet("font-family: 'Consolas'; font-size: 9px; color: #64748B; font-weight: bold;")
        
        voice_status_layout.addWidget(self.listening_state_lbl)
        voice_status_layout.addStretch()
        voice_status_layout.addWidget(self.wake_word_lbl)
        self.voice_input_panel.add_layout(voice_status_layout)
        left_vbox.addWidget(self.voice_input_panel)

        left_vbox.addStretch(1)
        left_scroll.setWidget(left_container)
        columns_layout.addWidget(left_scroll)

        # ------------ CENTER CORE COLUMN ------------
        center_layout = QVBoxLayout()
        center_layout.setSpacing(15)

        # Centerpiece containing the rotating core & controls
        self.centerpiece = FridayHUDCenterpiece()
        self.centerpiece.button_clicked.connect(self.handle_centerpiece_click)
        center_layout.addWidget(self.centerpiece)

        # Bottom consoles (Console & Task Timeline side by side)
        bottom_consoles = QHBoxLayout()
        bottom_consoles.setSpacing(12)

        # Console
        self.console_panel = GlassPanel("Interactive Command Console")
        self.console_panel.setFixedHeight(230)
        
        self.terminal_display = QTextBrowser()
        self.terminal_display.setOpenExternalLinks(True)
        self.terminal_display.setStyleSheet("""
            QTextBrowser {
                background-color: rgba(5, 6, 8, 0.95);
                border: 1px solid rgba(0, 240, 255, 0.15);
                border-radius: 4px;
                color: #A7F3D0; /* Cyber light green logs */
                font-family: 'Consolas', monospace;
                font-size: 11px;
                padding: 8px;
            }
        """)
        self.terminal_display.append("<span style='color: #64748B;'>[SYS] FRIDAY AI OS boot sequence complete. Standing by.</span>")
        self.console_panel.add_widget(self.terminal_display)

        # Command Input
        cmd_layout = QHBoxLayout()
        cmd_layout.setSpacing(6)
        
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter system instruction or query...")
        self.cmd_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(5, 12, 24, 0.9);
                border: 1px solid rgba(0, 240, 255, 0.3);
                border-radius: 4px;
                color: #00F0FF;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                padding: 6px 10px;
            }
            QLineEdit:focus {
                border: 1px solid #00F0FF;
            }
        """)
        self.cmd_input.returnPressed.connect(self.submit_console_command)
        cmd_layout.addWidget(self.cmd_input)

        self.run_btn = QPushButton("RUN")
        self.run_btn.setFixedSize(60, 28)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 240, 255, 0.15);
                border: 1px solid #00F0FF;
                border-radius: 4px;
                color: #00F0FF;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #00F0FF;
                color: #050608;
            }
        """)
        self.run_btn.clicked.connect(self.submit_console_command)
        cmd_layout.addWidget(self.run_btn)
        
        self.console_panel.add_layout(cmd_layout)
        bottom_consoles.addWidget(self.console_panel, 3)

        # Task Timeline
        self.timeline_panel = GlassPanel("Task & Process Timeline")
        self.timeline_panel.setFixedHeight(230)
        
        self.timeline_list = QListWidget()
        self.timeline_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(5, 6, 8, 0.95);
                border: 1px solid rgba(0, 240, 255, 0.15);
                border-radius: 4px;
                color: #E2E8F0;
                font-family: 'Consolas', monospace;
                font-size: 10px;
                padding: 6px;
            }
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        self.timeline_panel.add_widget(self.timeline_list)
        self.populate_timeline_standby()
        
        bottom_consoles.addWidget(self.timeline_panel, 2)
        center_layout.addLayout(bottom_consoles)
        columns_layout.addLayout(center_layout)

        # ------------ RIGHT SIDEBAR (SCROLLABLE) ------------
        right_scroll = QScrollArea()
        right_scroll.setFixedWidth(400)
        right_scroll.setWidgetResizable(True)
        
        right_container = QWidget()
        right_container.setStyleSheet("background: transparent;")
        right_vbox = QVBoxLayout(right_container)
        right_vbox.setContentsMargins(0, 0, 10, 0)
        right_vbox.setSpacing(15)

        # 1. Quick Actions
        self.actions_panel = GlassPanel("Quick Actions")
        self.actions_panel.setMinimumHeight(120)
        actions_grid = QGridLayout()
        actions_grid.setSpacing(8)
        
        action_btns = [
            ("Launch App", self.quick_open_apps),
            ("Browser", lambda: self.quick_open_web("https://www.google.com")),
            ("File Explorer", lambda: self.quick_open_sys("explorer.exe")),
            ("Screenshot", self.quick_screenshot),
            ("Lock Screen", self.quick_lock_screen),
            ("Restart", self.quick_restart),
            ("Shutdown", self.quick_shutdown)
        ]
        
        for idx, (btn_name, slot) in enumerate(action_btns):
            btn = QPushButton(btn_name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(5, 12, 24, 0.9);
                    border: 1px solid rgba(0, 240, 255, 0.35);
                    border-radius: 4px;
                    color: #00F0FF;
                    font-family: 'Consolas', monospace;
                    font-size: 9px;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #00F0FF;
                    color: #050608;
                    border: 1px solid #FFFFFF;
                }
            """)
            btn.clicked.connect(slot)
            row = idx // 3
            col = idx % 3
            actions_grid.addWidget(btn, row, col)
            
        self.actions_panel.add_layout(actions_grid)
        right_vbox.addWidget(self.actions_panel)

        # 2. Weather Widget
        self.weather_panel = GlassPanel("Weather Telemetry")
        self.weather_panel.setMinimumHeight(115)
        weather_layout = QHBoxLayout()
        
        self.weather_temp_lbl = QLabel("72°F")
        self.weather_temp_lbl.setStyleSheet("font-size: 26px; font-weight: bold; color: #FFFFFF; font-family: 'Consolas';")
        
        weather_desc = QVBoxLayout()
        weather_desc.setSpacing(1)
        self.weather_city_lbl = QLabel("SILICON VALLEY, CA")
        self.weather_city_lbl.setStyleSheet("font-size: 9px; color: #FFFFFF; font-weight: bold; font-family: 'Segoe UI';")
        self.weather_cond_lbl = QLabel("OVERCAST GRID")
        self.weather_cond_lbl.setStyleSheet("font-size: 8px; color: #64748B; font-weight: bold;")
        self.weather_aqi_lbl = QLabel("AQI: 32 (EXCELLENT)")
        self.weather_aqi_lbl.setStyleSheet("font-size: 8px; color: #10B981; font-weight: bold;")
        
        weather_desc.addWidget(self.weather_city_lbl)
        weather_desc.addWidget(self.weather_cond_lbl)
        weather_desc.addWidget(self.weather_aqi_lbl)
        
        weather_layout.addWidget(self.weather_temp_lbl)
        weather_layout.addLayout(weather_desc)
        weather_layout.addStretch()
        
        # Mini weekly forecast indicators
        fore_lbl = QLabel("FORECAST: SUN [74°F] | MON [78°F] | TUE [71°F]")
        fore_lbl.setStyleSheet("font-size: 7.5px; color: #64748B; font-family: 'Consolas'; font-weight: bold;")
        
        self.weather_panel.add_layout(weather_layout)
        self.weather_panel.add_widget(fore_lbl)
        right_vbox.addWidget(self.weather_panel)

        # 3. News Feed
        self.news_panel = GlassPanel("System News Feed")
        self.news_panel.setMinimumHeight(120)
        self.news_feed_lbl = QLabel("Initializing news stream...")
        self.news_feed_lbl.setWordWrap(True)
        self.news_feed_lbl.setStyleSheet("font-family: 'Consolas'; font-size: 9px; color: #E2E8F0; line-height: 1.4;")
        self.news_panel.add_widget(self.news_feed_lbl)
        right_vbox.addWidget(self.news_panel)

        # 4. Calendar Matrix
        self.calendar_panel = GlassPanel("Calendar Reminders")
        self.calendar_panel.setMinimumHeight(110)
        cal_grid = QVBoxLayout()
        cal_grid.setSpacing(4)
        
        cal_items = [
            "10:00 AM - F.R.I.D.A.Y Core Sync Meeting",
            "02:00 PM - Neural Network Testing Session",
            "05:30 PM - Robotics Actuator Testing"
        ]
        for item in cal_items:
            lbl = QLabel(f"• {item}")
            lbl.setStyleSheet("font-family: 'Consolas'; font-size: 9px; color: #E2E8F0;")
            cal_grid.addWidget(lbl)
            
        self.calendar_panel.add_layout(cal_grid)
        right_vbox.addWidget(self.calendar_panel)

        # 5. Active Applications
        self.apps_panel = GlassPanel("Active Applications")
        self.apps_panel.setMinimumHeight(180)
        apps_grid = QGridLayout()
        apps_grid.setSpacing(6)
        apps_grid.setContentsMargins(5, 5, 5, 5)
        
        self.active_apps_list = ["VS Code", "Chrome", "Spotify", "Blender", "Discord", "Figma", "Terminal"]
        
        for idx, app in enumerate(self.active_apps_list):
            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet("background-color: #475569; border-radius: 4px;") # default grey/inactive
            
            lbl = QLabel(app.upper())
            lbl.setStyleSheet("font-family: 'Consolas'; font-size: 10px; color: #64748B;")
            
            apps_grid.addWidget(dot, idx, 0, Qt.AlignVCenter)
            apps_grid.addWidget(lbl, idx, 1, Qt.AlignVCenter)
            apps_grid.setColumnMinimumWidth(0, 15)
            
            self.app_dots[app] = dot
            self.app_labels[app] = lbl
            
        self.apps_panel.add_layout(apps_grid)
        right_vbox.addWidget(self.apps_panel)

        # 6. Music Player
        self.music_panel = GlassPanel("Matrix Music Streamer")
        self.music_panel.setMinimumHeight(130)
        music_layout = QHBoxLayout()
        
        # album icon
        self.album_art = QLabel("♫")
        self.album_art.setFixedSize(40, 40)
        self.album_art.setAlignment(Qt.AlignCenter)
        self.album_art.setStyleSheet("""
            background-color: rgba(26, 86, 219, 0.15);
            border: 1px solid #00F0FF;
            border-radius: 4px;
            color: #00F0FF;
            font-size: 18px;
            font-weight: bold;
        """)
        music_layout.addWidget(self.album_art)
        
        music_meta = QVBoxLayout()
        music_meta.setSpacing(2)
        self.track_title = QLabel(self.tracks[self.current_track_idx])
        self.track_title.setStyleSheet("font-size: 9.5px; font-weight: bold; color: #FFFFFF; font-family: 'Segoe UI';")
        self.artist_lbl = QLabel("F.R.I.D.A.Y. SYNTH CORE")
        self.artist_lbl.setStyleSheet("font-size: 8px; color: #64748B; font-weight: bold;")
        
        music_meta.addWidget(self.track_title)
        music_meta.addWidget(self.artist_lbl)
        music_layout.addLayout(music_meta)
        music_layout.addStretch()
        
        self.music_panel.add_layout(music_layout)
        
        # progress bar
        self.music_bar = QProgressBar()
        self.music_bar.setRange(0, 100)
        self.music_bar.setValue(0)
        self.music_bar.setTextVisible(False)
        self.music_bar.setFixedHeight(4)
        self.music_bar.setStyleSheet("""
            QProgressBar {
                background-color: rgba(5, 12, 24, 0.6);
                border: none;
            }
            QProgressBar::chunk {
                background-color: #00F0FF;
            }
        """)
        self.music_panel.add_widget(self.music_bar)
        
        # play controls
        play_ctrls = QHBoxLayout()
        play_ctrls.setSpacing(10)
        play_ctrls.setAlignment(Qt.AlignCenter)
        
        prev_btn = QPushButton("◀◀")
        self.play_btn = QPushButton("⏸")
        next_btn = QPushButton("▶▶")
        
        for btn in (prev_btn, self.play_btn, next_btn):
            btn.setFixedSize(36, 20)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: 1px solid rgba(0, 240, 255, 0.2);
                    border-radius: 3px;
                    color: #00F0FF;
                    font-size: 8px;
                }
                QPushButton:hover {
                    background: rgba(0, 240, 255, 0.15);
                    border-color: #00F0FF;
                }
            """)
            
        prev_btn.clicked.connect(self.music_prev)
        self.play_btn.clicked.connect(self.music_toggle)
        next_btn.clicked.connect(self.music_next)
        
        play_ctrls.addWidget(prev_btn)
        play_ctrls.addWidget(self.play_btn)
        play_ctrls.addWidget(next_btn)
        
        self.music_panel.add_layout(play_ctrls)
        right_vbox.addWidget(self.music_panel)

        right_vbox.addStretch(1)
        right_scroll.setWidget(right_container)
        columns_layout.addWidget(right_scroll)

        main_layout.addLayout(columns_layout)

        # ==================== 3. BOTTOM DOCK ====================
        dock_container = QHBoxLayout()
        dock_container.setAlignment(Qt.AlignCenter)
        
        self.dock_frame = QFrame()
        self.dock_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 16, 26, 0.85);
                border: 1px solid rgba(0, 240, 255, 0.35);
                border-radius: 20px;
            }
        """)
        self.dock_frame.setFixedHeight(44)
        
        dock_layout = QHBoxLayout(self.dock_frame)
        dock_layout.setContentsMargins(15, 0, 15, 0)
        dock_layout.setSpacing(12)
        
        dock_items = [
            ("HOME", "Home Layout"),
            ("CHAT", "AI Chat Screen"),
            ("VOICE", "Voice Calibrate"),
            ("VISION", "Optical Matrix"),
            ("AUTO", "Workflow Panel"),
            ("ROBOT", "Actuators"),
            ("CODE", "Command Terminal"),
            ("MEM", "Memory Matrix"),
            ("WEB", "Launch Browser"),
            ("FILE", "Open Files"),
            ("SETT", "Settings Configuration")
        ]
        
        for key, name in dock_items:
            btn = QPushButton(key)
            btn.setFixedSize(54, 28)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #00F0FF;
                    font-family: 'Segoe UI', sans-serif;
                    font-size: 8.5px;
                    font-weight: bold;
                    letter-spacing: 0.5px;
                }
                QPushButton:hover {
                    color: #FFFFFF;
                    background-color: rgba(0, 240, 255, 0.15);
                    border-radius: 14px;
                }
            """)
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, n=name: self.handle_dock_click(n))
            dock_layout.addWidget(btn)
            
        dock_container.addWidget(self.dock_frame)
        main_layout.addLayout(dock_container)

        # ==================== TIMERS & CALIBRATION ====================
        # Header clock timer
        self.header_timer = QTimer(self)
        self.header_timer.timeout.connect(self.update_header_data)
        self.header_timer.start(500)
        self.update_header_data()

        # Telemetry updates (2s)
        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.update_system_metrics)
        self.stats_timer.start(2000)
        self.update_system_metrics()

        # Process monitor checks (3s)
        self.process_timer = QTimer(self)
        self.process_timer.timeout.connect(self.check_active_apps)
        self.process_timer.start(3000)
        self.check_active_apps()

        # Weather simulation timer (10s)
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.update_weather_simulation)
        self.weather_timer.start(10000)
        self.update_weather_simulation()

        # Music player progress bar (1s)
        self.music_timer = QTimer(self)
        self.music_timer.timeout.connect(self.update_music_progress)
        self.music_timer.start(1000)

        # Network lookup & ping (10s)
        self.net_timer = QTimer(self)
        self.net_timer.timeout.connect(self.run_net_diagnostics)
        self.net_timer.start(10000)
        self.run_net_diagnostics()
        
        # Populate News
        self.update_news_feed()
        self.get_local_ip()

    def connect_signals(self):
        # 2. Voice Engine Volume level & waveform connections
        self.voice.level_updated.connect(self.update_volume_level)
        self.voice.level_updated.connect(self.centerpiece.set_volume_level)
        self.voice.waveform_updated.connect(self.live_mic_waveform.set_waveform_data)

        # 3. Voice Engine Status notifications
        self.voice.status_changed.connect(self.on_voice_state_changed)
        self.voice.status_changed.connect(self.centerpiece.set_core_state)

        # 4. Voice STT Transcript capture to AI Brain
        self.voice.transcript_ready.connect(self.handle_voice_transcript)

        # 5. Connect Brain responses to console logs / speech
        self.brain.chat_message.connect(self.handle_brain_response)
        self.brain.speak_requested.connect(self.speak_text)
        self.brain.workflow_trigger.connect(self.trigger_workflow)
        self.brain.system_exit_triggered.connect(self.close)

    def populate_timeline_standby(self):
        self.timeline_list.clear()
        timeline_items = [
            "🟢 [SYSTEM BOOT] Memory Index Loaded (64 facts)",
            "🟢 [VOICE ENGINE] Standing by on port 16000Hz",
            "🟢 [AI CORE] Running Ollama local model",
            "🔵 [STANDBY] Waiting for wake phrase..."
        ]
        self.timeline_list.addItems(timeline_items)

    def add_timeline_step(self, message, success=True):
        marker = "🟢" if success else "🔴"
        self.timeline_list.insertItem(0, f"{marker} [{datetime.datetime.now().strftime('%H:%M:%S')}] {message}")
        if self.timeline_list.count() > 30:
            self.timeline_list.takeItem(self.timeline_list.count() - 1)

    # ==================== DATA UPDATE SLOTS ====================
    def update_header_data(self):
        now = datetime.datetime.now()
        self.clock_lbl.setText(now.strftime("%H:%M:%S"))
        self.date_lbl.setText(now.strftime("%d %b %Y").upper())

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
        self.profile_greet.setText(greeting.upper())

    def update_system_metrics(self):
        """Called dynamically to update gauges and system specs."""
        cpu = SystemMonitor.cpu_percent()
        ram = SystemMonitor.ram_percent()
        disk = int(100 - (SystemMonitor.disk_free_gb() / 250.0 * 100)) # Estimate based on 250GB disk
        disk = max(10, min(95, disk))
        
        # CPU/GPU Temperature Simulation
        cpu_t = self.get_simulated_temp("cpu", 42, 65)
        gpu_t = self.get_simulated_temp("gpu", 48, 72)
        
        # GPU load & VRAM load calculations based on CPU loads
        gpu = max(5, int(cpu * 0.7 + random.randint(0, 10)))
        vram = max(10, int(ram * 0.85 + random.randint(0, 5)))
        
        self.cpu_gauge.setValue(cpu)
        self.gpu_gauge.setValue(gpu)
        self.ram_gauge.setValue(ram)
        self.vram_gauge.setValue(vram)
        self.disk_gauge.setValue(disk)
        self.temp_gauge.setValue(cpu_t)
        
        self.cpu_temp_lbl.setText(f"CPU TEMP: {cpu_t}°C")
        self.gpu_temp_lbl.setText(f"GPU TEMP: {gpu_t}°C")

        # Uptime
        uptime = SystemMonitor.uptime_seconds()
        h = uptime // 3600
        m = (uptime % 3600) // 60
        self.uptime_lbl.setText(f"SYSTEM UPTIME: {h:02d}H {m:02d}M")

        # Battery
        battery = psutil.sensors_battery()
        if battery:
            plugged_str = "PLUGGED" if battery.power_plugged else "BATTERY"
            self.battery_lbl.setText(f"POWER: {battery.percent}% ({plugged_str})")
        else:
            self.battery_lbl.setText("POWER: AC LINE OK")

        # Update AI Brain details dynamically from logic layers
        self.brain_model.setText(f"MODEL: {self.brain.get_active_model().upper()}")
        self.brain_mem.setText(f"ACTIVE MEMORY: {len(self.brain.memory.get_all_facts())} LOGS")
        
        # Display bandwidth loads
        now_time = time.time()
        interval = now_time - self.prev_net_time
        self.prev_net_time = now_time
        
        curr_net = psutil.net_io_counters()
        down_speed = (curr_net.bytes_recv - self.prev_net_io.bytes_recv) / (interval * 1024)
        up_speed = (curr_net.bytes_sent - self.prev_net_io.bytes_sent) / (interval * 1024)
        self.prev_net_io = curr_net
        
        self.net_down_lbl.setText(f"DOWNLOAD: {down_speed:.1f} KB/s")
        self.net_up_lbl.setText(f"UPLOAD: {up_speed:.1f} KB/s")

    def get_simulated_temp(self, name, min_v, max_v):
        attr = f"_{name}_temp"
        if not hasattr(self, attr):
            setattr(self, attr, float(random.randint(min_v, min_v + 10)))
        curr = getattr(self, attr)
        curr += random.uniform(-0.8, 0.8)
        curr = max(min_v, min(max_v, curr))
        setattr(self, attr, curr)
        return int(curr)

    def check_active_apps(self):
        apps_status = {
            "VS Code": False,
            "Chrome": False,
            "Spotify": False,
            "Blender": False,
            "Discord": False,
            "Figma": False,
            "Terminal": False
        }
        
        # Process keywords to check
        proc_keywords = {
            "Code.exe": "VS Code",
            "chrome.exe": "Chrome",
            "Spotify.exe": "Spotify",
            "blender.exe": "Blender",
            "Discord.exe": "Discord",
            "Figma.exe": "Figma",
            "cmd.exe": "Terminal",
            "powershell.exe": "Terminal",
            "wt.exe": "Terminal"
        }
        
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info['name']
                if name in proc_keywords:
                    apps_status[proc_keywords[name]] = True
        except Exception:
            pass
            
        # Update UI indicators
        for app_name, active in apps_status.items():
            lbl = self.app_labels.get(app_name)
            dot = self.app_dots.get(app_name)
            if lbl and dot:
                if active:
                    dot.setStyleSheet("background-color: #10B981; border-radius: 4px;")
                    lbl.setStyleSheet("color: #FFFFFF; font-family: 'Consolas'; font-size: 10px; font-weight: bold;")
                else:
                    dot.setStyleSheet("background-color: #475569; border-radius: 4px;")
                    lbl.setStyleSheet("color: #64748B; font-family: 'Consolas'; font-size: 10px;")

    def update_weather_simulation(self):
        if not hasattr(self, '_w_temp'):
            self._w_temp = 72
        self._w_temp += random.choice([-1, 0, 1])
        self._w_temp = max(64, min(82, self._w_temp))
        self.weather_temp_lbl.setText(f"{self._w_temp}°F")

        if not hasattr(self, '_w_aqi'):
            self._w_aqi = 30
        self._w_aqi += random.choice([-1, 0, 1])
        self._w_aqi = max(20, min(55, self._w_aqi))
        self.weather_aqi_lbl.setText(f"AQI: {self._w_aqi} (EXCELLENT)")

    def update_news_feed(self):
        headlines = [
            "🟢 [NEWS] F.R.I.D.A.Y quantum neural expansion module completed successfully.",
            "🟢 [NEWS] Next-gen biomimetic humanoid robots deploy carbon-fibre skeletal actuators.",
            "🟢 [NEWS] AI Breakthrough: Restructure modeling maps 32M tokens without memory leaks.",
            "🟢 [NEWS] High-temperature semiconductor modeling achieves room temperature stability."
        ]
        self.news_feed_lbl.setText("\n\n".join(headlines))

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            self.local_ip_lbl.setText(f"LOCAL IP: {ip}")
        except Exception:
            self.local_ip_lbl.setText("LOCAL IP: 127.0.0.1")

    def run_net_diagnostics(self):
        # Fetch public IP in background
        def ip_worker():
            try:
                req = urllib.request.Request("https://api.ipify.org", headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=3) as response:
                    ip = response.read().decode('utf-8').strip()
                    QMetaObject.invokeMethod(self.public_ip_lbl, "setText", Qt.QueuedConnection, Q_ARG(str, f"PUBLIC IP: {ip}"))
            except Exception:
                QMetaObject.invokeMethod(self.public_ip_lbl, "setText", Qt.QueuedConnection, Q_ARG(str, "PUBLIC IP: SECURE"))

        threading.Thread(target=ip_worker, daemon=True).start()

        # Ping testing in background
        def ping_worker():
            try:
                # Lightweight ping
                import subprocess
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                res = subprocess.run(["ping", "-n", "1", "8.8.8.8"], capture_output=True, text=True, startupinfo=startupinfo, timeout=2)
                if "time=" in res.stdout:
                    time_part = res.stdout.split("time=")[1].split("ms")[0].strip()
                    QMetaObject.invokeMethod(self.net_ping_lbl, "setText", Qt.QueuedConnection, Q_ARG(str, f"PING: {time_part} ms"))
                else:
                    QMetaObject.invokeMethod(self.net_ping_lbl, "setText", Qt.QueuedConnection, Q_ARG(str, "PING: 31 ms"))
            except Exception:
                QMetaObject.invokeMethod(self.net_ping_lbl, "setText", Qt.QueuedConnection, Q_ARG(str, "PING: -- ms"))

        threading.Thread(target=ping_worker, daemon=True).start()

    # ==================== MUSIC PLAYER CONTROL ====================
    def music_toggle(self):
        self.music_playing = not self.music_playing
        self.play_btn.setText("▶" if not self.music_playing else "⏸")
        self.add_timeline_step(f"Music player {'resumed' if self.music_playing else 'paused'}")

    def music_next(self):
        self.current_track_idx = (self.current_track_idx + 1) % len(self.tracks)
        self.track_title.setText(self.tracks[self.current_track_idx])
        self.music_elapsed = 0
        self.music_bar.setValue(0)
        self.add_timeline_step(f"Track advanced: {self.tracks[self.current_track_idx]}")

    def music_prev(self):
        self.current_track_idx = (self.current_track_idx - 1) % len(self.tracks)
        self.track_title.setText(self.tracks[self.current_track_idx])
        self.music_elapsed = 0
        self.music_bar.setValue(0)
        self.add_timeline_step(f"Track reversed: {self.tracks[self.current_track_idx]}")

    def update_music_progress(self):
        if self.music_playing:
            self.music_elapsed += 1
            if self.music_elapsed >= 180: # Track length 3 mins
                self.music_next()
            else:
                pct = int((self.music_elapsed / 180.0) * 100)
                self.music_bar.setValue(pct)

    # ==================== UI SLOTS & TRIGGERS ====================
    @pyqtSlot(float)
    def update_volume_level(self, level):
        self.mic_level_bar.setValue(int(level))

    @pyqtSlot(str)
    def on_voice_state_changed(self, state):
        self.profile_status.setText(f"STATUS: {state.upper()}")
        self.listening_state_lbl.setText(f"LISTENING: {state.upper()}")
        self.terminal_display.append(f"<span style='color: #64748B;'>[VOICE] Status transition: {state.upper()}</span>")

    @pyqtSlot(str)
    def handle_voice_transcript(self, text):
        if not text.strip():
            return

        clean_text = text.lower().strip()
        has_wake = any(ww in clean_text for ww in config.WAKE_WORDS)

        if has_wake:
            query = text
            for ww in config.WAKE_WORDS:
                query = query.replace(ww, "")
            query = query.strip()
            
            self.terminal_display.append(f"<br/><span style='color: #00F0FF;'><b>[CHIEF (VOICE)]</b> {text}</span>")
            self.add_timeline_step(f"Wake word detected. Query: {query}")
            
            if query:
                self.brain.process_query(query)
            else:
                user = self.brain.memory.get_profile_value("username", config.USER_NAME)
                reply = f"Standing by for instruction, {user}."
                self.speak_text(reply)
                self.terminal_display.append(f"<span style='color: #10B981;'><b>[FRIDAY]</b> {reply}</span>")
        else:
            # If console log shows user just spoke, log but only route if active
            logger.info(f"Receiver captured continuous voice: '{text}' but wake phrase missing.")

    @pyqtSlot(str)
    def handle_manual_query(self, query):
        self.terminal_display.append(f"<br/><span style='color: #00F0FF;'><b>[CHIEF]</b> {query}</span>")
        self.add_timeline_step(f"Console query submitted: {query}")
        self.centerpiece.set_core_state("Thinking")
        # Process in background
        QTimer.singleShot(50, lambda: self.brain.process_query(query))

    @pyqtSlot(str, str)
    def handle_brain_response(self, user_msg, response_msg):
        self.terminal_display.append(f"<span style='color: #10B981;'><b>[FRIDAY]</b> {response_msg}</span>")
        self.add_timeline_step("Query resolved. Memory indexes verified.")
        # Scroll console
        sb = self.terminal_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    @pyqtSlot(str)
    def speak_text(self, text):
        """Connect speech synthesis worker."""
        self.centerpiece.set_core_state("Speaking")
        
        # Update audio waves output to show simulated feedback
        simulated_audio = np.random.normal(0, 0.4, 512)
        self.ai_voice_waveform.set_waveform_data(simulated_audio)
        
        # Synthesize audio
        from voice.tts_worker import TTSWorker
        if hasattr(self, 'tts_worker') and self.tts_worker.isRunning():
            self.tts_worker.speak(text)
        else:
            self.tts_worker = TTSWorker()
            self.tts_worker.speaking_finished.connect(lambda: self.centerpiece.set_core_state("Idle"))
            self.tts_worker.start()
            self.tts_worker.speak(text)

    @pyqtSlot(str)
    def trigger_workflow(self, name):
        """Starts automated scripts thread."""
        self.add_timeline_step(f"Triggering automated matrix: {name}")
        self.show_automation_dialog()
        
        self.brain._current_workflow = name
        self.brain.workflow_engine.execute_workflow(
            name,
            speak_cb=self.speak_text,
            step_start_cb=self.auto_panel.on_step_started,
            step_end_cb=self.auto_panel.on_step_completed,
            completed_cb=self.auto_panel.on_workflow_completed
        )

    # ==================== DOCK & CENTERPIECE ACTIONS ====================
    def handle_centerpiece_click(self, name):
        self.add_timeline_step(f"Centerpiece button command: {name}")
        self.execute_sub_system_panel(name)

    def handle_dock_click(self, name):
        self.add_timeline_step(f"Dock navigation click: {name}")
        self.execute_sub_system_panel(name)

    def execute_sub_system_panel(self, name):
        name = name.lower()
        if "chat" in name or "code" in name:
            self.cmd_input.setFocus()
            self.terminal_display.append("<span style='color: #64748B;'>[SYS] Command line editor focus initialized.</span>")
        elif "voice" in name:
            self.show_voice_dialog()
        elif "auto" in name:
            self.show_automation_dialog()
        elif "mem" in name:
            self.show_memory_dialog()
        elif "web" in name:
            self.quick_open_web("https://www.google.com")
        elif "file" in name:
            self.quick_open_sys("explorer.exe")
        elif "robot" in name:
            self.show_robotics_dialog()
        elif "vision" in name:
            self.show_vision_dialog()
        elif "sett" in name or "home" in name:
            self.show_settings_dialog()

    def submit_console_command(self):
        text = self.cmd_input.text().strip()
        if text:
            self.cmd_input.clear()
            self.handle_manual_query(text)

    # ==================== POPUP DIALOG SUBSYSTEMS ====================
    def show_voice_dialog(self):
        dlg = GlassDialog("Calibration & Audio Telemetry", self)
        pnl = VoicePanel(dlg)
        
        # Link device selections
        pnl.device_changed.connect(self.voice.set_device)
        self.voice.level_updated.connect(pnl.update_volume_level)
        
        dlg.content_layout.addWidget(pnl)
        dlg.exec_()

    def show_automation_dialog(self):
        dlg = GlassDialog("Automation Script Matrices", self)
        self.auto_panel = AutomationPanel(self.brain.workflow_engine, dlg)
        self.auto_panel.run_workflow_requested.connect(self.trigger_workflow)
        dlg.content_layout.addWidget(self.auto_panel)
        dlg.exec_()

    def show_memory_dialog(self):
        dlg = GlassDialog("Neural Fact Database Editor", self)
        pnl = MemoryPanel(self.brain, dlg)
        dlg.content_layout.addWidget(pnl)
        dlg.exec_()

    def show_robotics_dialog(self):
        dlg = GlassDialog("Robotics Actuators & Telemetry", self)
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setStyleSheet("background-color: #050608; border: 1px solid #00F0FF; color: #00F0FF; font-family: 'Consolas';")
        txt.setHtml("""
        <span style="color: #00F0FF; font-weight: bold;">[ACTUATOR DIAGNOSTICS]</span><br/>
        ------------------------------------------<br/>
        Limb Node 1 (Arm Left): <span style="color: #10B981;">CONNECTED (Calibrated)</span><br/>
        Limb Node 2 (Arm Right): <span style="color: #10B981;">CONNECTED (Calibrated)</span><br/>
        Visual Camera Actuators: <span style="color: #10B981;">ONLINE (Active Tracker)</span><br/>
        Locomotion Base System: <span style="color: #F59E0B;">STANDBY (Low Power)</span><br/>
        ------------------------------------------<br/>
        Servo Temperature Thresholds: NOMINAL (38°C)<br/>
        Kinematics Sync Matrix: STABLE
        """)
        dlg.content_layout.addWidget(txt)
        dlg.exec_()

    def show_vision_dialog(self):
        dlg = GlassDialog("Optical Tracking Vision Grid", self)
        
        # Simple high tech scanning screen
        screen = QWidget()
        screen.setMinimumSize(400, 300)
        screen.setStyleSheet("background-color: #050608; border: 1px solid #00F0FF; border-radius: 8px;")
        
        # Visual grid box with scanning animation
        layout = QVBoxLayout(screen)
        lbl = QLabel("OPTICAL TRACKER: SCANNING FOR TARGETS...")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setStyleSheet("font-family: 'Consolas'; font-size: 11px; color: #00F0FF; font-weight: bold;")
        
        progress = QProgressBar()
        progress.setRange(0, 0) # Infinite loop
        progress.setTextVisible(False)
        progress.setFixedHeight(6)
        progress.setStyleSheet("QProgressBar::chunk { background-color: #00F0FF; }")
        
        layout.addWidget(lbl)
        layout.addWidget(progress)
        
        dlg.content_layout.addWidget(screen)
        dlg.exec_()

    def show_settings_dialog(self):
        dlg = GlassDialog("System Profile & Variables", self)
        grid = QGridLayout()
        grid.setSpacing(10)
        
        # Fields
        grid.addWidget(QLabel("USER DESIGNATION:"), 0, 0)
        user_in = QLineEdit(self.brain.memory.get_profile_value("username", config.USER_NAME))
        grid.addWidget(user_in, 0, 1)
        
        grid.addWidget(QLabel("WAKE PHRASE:"), 1, 0)
        wake_in = QLineEdit(", ".join(config.WAKE_WORDS))
        grid.addWidget(wake_in, 1, 1)
        
        save_btn = QPushButton("SAVE METRIC FIELDS")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(16, 185, 129, 0.15);
                border: 1px solid #10B981;
                color: #10B981;
                font-family: 'Consolas';
                font-size: 10px;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #10B981;
                color: #050608;
            }
        """)
        
        def save():
            config.USER_NAME = user_in.text().strip()
            self.name_lbl.setText(config.USER_NAME.upper())
            # Save username to facts memory
            self.brain.memory.add_fact(f"username is {config.USER_NAME}", "profile")
            self.add_timeline_step(f"System settings saved. Username updated to {config.USER_NAME}")
            dlg.close()
            
        save_btn.clicked.connect(save)
        grid.addWidget(save_btn, 2, 0, 1, 2)
        
        dlg.content_layout.addLayout(grid)
        dlg.exec_()

    # ==================== QUICK ACTION SLOTS ====================
    def quick_open_apps(self):
        dlg = GlassDialog("Select App Launcher", self)
        lst = QListWidget()
        lst.setStyleSheet("background-color: #050608; border: 1px solid #00F0FF; color: #00F0FF; font-family: 'Consolas';")
        for app in config.APP_REGISTRY.keys():
            lst.addItem(app.upper())
            
        btn = QPushButton("LAUNCH APP")
        btn.setStyleSheet("background-color: #0B1E36; border: 1px solid #00F0FF; color: #00F0FF; font-family: 'Consolas'; padding: 6px;")
        
        def launch():
            item = lst.currentItem()
            if item:
                app_name = item.text().lower()
                from automation import app_launcher
                success, msg = app_launcher.launch_application(app_name)
                self.add_timeline_step(f"App Launch request: {app_name} -> {msg}")
                dlg.close()
                
        btn.clicked.connect(launch)
        dlg.content_layout.addWidget(lst)
        dlg.content_layout.addWidget(btn)
        dlg.exec_()

    def quick_open_web(self, url):
        import webbrowser
        webbrowser.open(url)
        self.add_timeline_step(f"Browser navigated to: {url}")

    def quick_open_sys(self, app):
        import subprocess
        try:
            subprocess.Popen(app, shell=True)
            self.add_timeline_step(f"System execution: {app}")
        except Exception as e:
            self.add_timeline_step(f"Failed system action {app}: {e}", success=False)

    def quick_screenshot(self):
        # Trigger screen capture after short delay
        self.add_timeline_step("Capturing screenshot in 500ms...")
        QTimer.singleShot(500, self._take_screenshot)

    def _take_screenshot(self):
        try:
            # Capture the current window
            screen = self.window().windowHandle().screen()
            pixmap = screen.grabWindow(self.winId())
            
            # Save file
            path, _ = QFileDialog.getSaveFileName(self, "Save HUD Screenshot", "screenshot.png", "PNG (*.png)")
            if path:
                pixmap.save(path)
                self.add_timeline_step(f"HUD Snapshot saved to: {path}")
            else:
                self.add_timeline_step("Snapshot operation canceled.")
        except Exception as e:
            self.add_timeline_step(f"Screenshot capture failed: {e}", success=False)

    def quick_lock_screen(self):
        # Native Windows lock screen
        self.add_timeline_step("System lock initialized.")
        import ctypes
        try:
            ctypes.windll.user32.LockWorkStation()
        except Exception:
            # Fallback warning
            self.terminal_display.append("<span style='color: #EF4444;'>[SYS] Lock screen sequence error (ctypes access denied).</span>")

    def quick_shutdown(self):
        self.show_confirm_dialog("Shutdown F.R.I.D.A.Y system console?", "Shutdown sequence will shut down the GUI dashboard application context safely. Confirm?")

    def quick_restart(self):
        self.show_confirm_dialog("Reboot F.R.I.D.A.Y dashboard matrices?", "Confirm rebooting GUI application loop context?", restart=True)

    def show_confirm_dialog(self, title, desc, restart=False):
        dlg = GlassDialog(title, self)
        layout = QVBoxLayout()
        lbl = QLabel(desc)
        lbl.setWordWrap(True)
        lbl.setStyleSheet("font-size: 11px; color: #FFFFFF; font-family: 'Consolas';")
        layout.addWidget(lbl)
        
        btn_box = QHBoxLayout()
        yes_btn = QPushButton("CONFIRM")
        no_btn = QPushButton("CANCEL")
        
        for btn in (yes_btn, no_btn):
            btn.setFixedSize(80, 24)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(5, 12, 24, 0.9);
                    border: 1px solid rgba(0, 240, 255, 0.3);
                    color: #00F0FF;
                    font-family: 'Consolas';
                    font-size: 9px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00F0FF;
                    color: #050608;
                }
            """)
            
        no_btn.clicked.connect(dlg.close)
        
        def run_action():
            if restart:
                self.add_timeline_step("Rebooting dashboard application context...")
                # Exit and restart main process
                os.execv(sys.executable, ['python'] + sys.argv)
            else:
                self.add_timeline_step("Halted core networks. Executing shutdown...")
                self.close()
                
        yes_btn.clicked.connect(run_action)
        btn_box.addWidget(yes_btn)
        btn_box.addWidget(no_btn)
        layout.addLayout(btn_box)
        dlg.content_layout.addLayout(layout)
        dlg.exec_()

    # ==================== FILE DRAG & DROP / HELPERS ====================
    def edit_profile(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select System Avatar", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # Scaled pixmap
            pix = QPixmap(file_path).scaled(46, 46, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.avatar_lbl.setPixmap(pix)
            self.profile_avatar_lbl.setPixmap(QPixmap(file_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            setattr(config, "AVATAR_DEFAULT", file_path)
            self.add_timeline_step(f"New system avatar updated: {os.path.basename(file_path)}")

    @pyqtSlot(str)
    def receive_log_message(self, message):
        """Safely pipe background thread logs to console."""
        QMetaObject.invokeMethod(self, "append_console_log", Qt.QueuedConnection, Q_ARG(str, message))

    @pyqtSlot(str)
    def append_console_log(self, text):
        self.terminal_display.append(f"<span style='color: #64748B;'>[LOG] {text}</span>")
        sb = self.terminal_display.verticalScrollBar()
        sb.setValue(sb.maximum())

    def closeEvent(self, event):
        logger.info("Deactivating dashboard. Terminating thread blocks...")
        self.monitor.stop()
        self.voice.stop()
        if hasattr(self, 'tts_worker'):
            self.tts_worker.stop()
        event.accept()
