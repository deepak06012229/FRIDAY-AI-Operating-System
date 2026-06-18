from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPlainTextEdit, QGridLayout
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG, pyqtSlot
from utils import logger
import config

class SystemPanel(QWidget):
    """Monitors CPU/RAM hardware details, diagnostic parameters, and streams real-time console logs."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
        # Connect FRIDAY logger callbacks to stream inside the UI console log
        logger.register_log_callback(self.receive_log_message)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title Label
        self.title_label = QLabel("SYSTEM METRICS TELEMETRY")
        self.title_label.setObjectName("PanelTitle")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #00F0FF; letter-spacing: 2px;")
        layout.addWidget(self.title_label)

        # CPU/RAM Progress Bar layout
        grid = QGridLayout()
        grid.setSpacing(8)

        # CPU
        cpu_lbl = QLabel("CPU CORES LOAD:")
        cpu_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold;")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)
        self.cpu_bar.setTextVisible(True)
        self.cpu_bar.setAlignment(Qt.AlignCenter)
        self.cpu_bar.setStyleSheet("""
            QProgressBar {
                background-color: #051630;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #FFFFFF;
                font-family: 'Consolas', monospace;
                font-size: 10px;
                font-weight: bold;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #005080, stop:1 #00F0FF);
                border-radius: 3px;
            }
        """)
        grid.addWidget(cpu_lbl, 0, 0)
        grid.addWidget(self.cpu_bar, 0, 1)

        # RAM
        ram_lbl = QLabel("RAM CORE POOL:")
        ram_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold;")
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setValue(0)
        self.ram_bar.setTextVisible(True)
        self.ram_bar.setAlignment(Qt.AlignCenter)
        self.ram_bar.setStyleSheet("""
            QProgressBar {
                background-color: #051630;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #FFFFFF;
                font-family: 'Consolas', monospace;
                font-size: 10px;
                font-weight: bold;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #005080, stop:1 #00F0FF);
                border-radius: 3px;
            }
        """)
        grid.addWidget(ram_lbl, 1, 0)
        grid.addWidget(self.ram_bar, 1, 1)

        layout.addLayout(grid)

        # Hardware metrics labels
        info_layout = QGridLayout()
        info_layout.setSpacing(6)
        
        self.uptime_lbl = QLabel("SYSTEM UPTIME: 0s")
        self.cpu_freq_lbl = QLabel("CPU FREQUENCY: --")
        self.disk_free_lbl = QLabel("FREE STORAGE: --")
        self.ram_used_lbl = QLabel("MEMORY ALLOC: -- / --")

        labels = [self.uptime_lbl, self.cpu_freq_lbl, self.disk_free_lbl, self.ram_used_lbl]
        for idx, lbl in enumerate(labels):
            lbl.setStyleSheet("font-family: 'Consolas', monospace; font-size: 11px; color: #E2E8F0;")
            row = idx // 2
            col = idx % 2
            info_layout.addWidget(lbl, row, col)

        layout.addLayout(info_layout)

        # Rolling Console Logger
        log_lbl = QLabel("REAL-TIME CORE LOG STREAM:")
        log_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold; margin-top: 5px;")
        layout.addWidget(log_lbl)

        self.console_log = QPlainTextEdit()
        self.console_log.setReadOnly(True)
        self.console_log.setMaximumBlockCount(200)  # Keep logs lean
        self.console_log.setStyleSheet("""
            QPlainTextEdit {
                background-color: #030f26;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #A7F3D0; /* Light green tech logs */
                font-family: 'Consolas', monospace;
                font-size: 10.5px;
                line-height: 1.4;
            }
        """)
        layout.addWidget(self.console_log)

    def update_system_stats(self, stats):
        """Called dynamically from the monitor thread to update labels and progress bars."""
        self.cpu_bar.setValue(int(stats["cpu_percent"]))
        self.ram_bar.setValue(int(stats["ram_percent"]))

        self.cpu_freq_lbl.setText(f"CPU CORE FREQ: {stats['cpu_freq']:.0f} MHz")
        self.disk_free_lbl.setText(f"FREE STORAGE: {stats['disk_free_gb']:.1f} GB")
        self.ram_used_lbl.setText(f"MEMORY ALLOC: {stats['ram_used_gb']:.1f} / {stats['ram_total_gb']:.1f} GB")
        
        # Format uptime string
        uptime = stats["uptime_seconds"]
        h = uptime // 3600
        m = (uptime % 3600) // 60
        s = uptime % 60
        self.uptime_lbl.setText(f"FRIDAY RUNTIME: {h:02d}:{m:02d}:{s:02d}")

    def receive_log_message(self, message):
        """Receives log strings from logger thread safely using Qt MetaObject system (since logger might run in background)."""
        QMetaObject.invokeMethod(self, "append_log", Qt.QueuedConnection, Q_ARG(str, message))

    # Declaring append_log as a Qt Slot to accept the queued log string safely
    @pyqtSlot(str)
    def append_log(self, text):
        self.console_log.appendPlainText(text)
        sb = self.console_log.verticalScrollBar()
        sb.setValue(sb.maximum())
