from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QProgressBar, QSlider, QPushButton, QTextEdit
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from voice import device_manager
from voice.tts_worker import TTSWorker
from utils import logger
import config

class DiagnosticsWorker(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, device_id):
        super().__init__()
        self.device_id = device_id

    def run(self):
        result = device_manager.test_microphone_quality(self.device_id)
        self.finished.emit(result)


class VoicePanel(QWidget):
    """Voice configuration interface. Handles mic device switching, VAD sensitivity, and diagnostics."""
    device_changed = pyqtSignal(int)
    threshold_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_device_id = None
        self.init_ui()
        self.load_devices()
        # Diagnostic helper attributes
        self.diagnostic_tts_worker = None
        self.diagnostic_finished_count = 0

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Title Label
        self.title_label = QLabel("AUDIO CAPTURE TELEMETRY")
        self.title_label.setObjectName("PanelTitle")
        self.title_label.setStyleSheet("font-size: 11px; font-weight: bold; color: #00F0FF; letter-spacing: 2px;")
        layout.addWidget(self.title_label)

        # Device Selection Group
        dev_layout = QVBoxLayout()
        dev_layout.setSpacing(4)
        dev_label = QLabel("ACTIVE RECEIVER (MICROPHONE):")
        dev_label.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold;")
        dev_layout.addWidget(dev_label)

        self.device_combo = QComboBox()
        self.device_combo.setStyleSheet("""
            QComboBox {
                background-color: #051630;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #E2E8F0;
                padding: 6px;
                font-family: 'Consolas', monospace;
            }
            QComboBox QAbstractItemView {
                background-color: #030F26;
                color: #E2E8F0;
                selection-background-color: #0B1E36;
                selection-color: #00F0FF;
            }
        """)
        self.device_combo.currentIndexChanged.connect(self.on_device_selected)
        dev_layout.addWidget(self.device_combo)
        layout.addLayout(dev_layout)

        # Live Volume Level Meter
        level_layout = QVBoxLayout()
        level_layout.setSpacing(4)
        level_lbl = QLabel("RECEIVER INPUT LEVEL:")
        level_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold;")
        level_layout.addWidget(level_lbl)

        self.level_bar = QProgressBar()
        self.level_bar.setRange(0, 100)
        self.level_bar.setValue(0)
        self.level_bar.setTextVisible(False)
        self.level_bar.setStyleSheet("""
            QProgressBar {
                background-color: #051630;
                border: 1px solid #0B1E36;
                border-radius: 3px;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0066AA, stop:0.8 #00F0FF, stop:1 #10B981);
                border-radius: 2px;
            }
        """)
        level_layout.addWidget(self.level_bar)
        layout.addLayout(level_layout)

        # VAD Sensitivity Slider
        sens_layout = QVBoxLayout()
        sens_layout.setSpacing(4)
        
        self.sens_lbl = QLabel(f"SENSITIVITY THRESHOLD: {config.VAD_ENERGY_THRESHOLD}")
        self.sens_lbl.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold;")
        sens_layout.addWidget(self.sens_lbl)

        self.sens_slider = QSlider(Qt.Horizontal)
        self.sens_slider.setRange(100, 3000)
        self.sens_slider.setValue(config.VAD_ENERGY_THRESHOLD)
        self.sens_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #0B1E36;
                height: 6px;
                background: #051630;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00F0FF;
                border: 1px solid #00B3FF;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
        """)
        self.sens_slider.valueChanged.connect(self.on_slider_changed)
        sens_layout.addWidget(self.sens_slider)
        layout.addLayout(sens_layout)

        # Diagnostics section
        diag_layout = QVBoxLayout()
        diag_layout.setSpacing(6)
        
        diag_title = QLabel("HARDWARE CALIBRATION & TESTING")
        diag_title.setStyleSheet("font-size: 10px; color: #94A3B8; font-weight: bold; margin-top: 10px;")
        diag_layout.addWidget(diag_title)

        self.diag_btn = QPushButton("INITIATE MIC DIAGNOSTICS")
        self.diag_btn.setStyleSheet("""
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
            QPushButton:disabled {
                border-color: #0B1E36;
                color: #475569;
            }
        """)
        self.diag_btn.clicked.connect(self.run_diagnostics)
        diag_layout.addWidget(self.diag_btn)

        # TEST VOICE Diagnostics Button
        self.test_voice_btn = QPushButton("TEST VOICE")
        self.test_voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #0B1E36;
                border: 1px solid #10B981;
                border-radius: 4px;
                color: #10B981;
                font-family: 'Consolas', monospace;
                font-weight: bold;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #10B981;
                color: #030F26;
            }
        """)
        self.test_voice_btn.clicked.connect(self.run_voice_diagnostics)
        diag_layout.addWidget(self.test_voice_btn)

        # Diagnostic info labels
        info_layout = QHBoxLayout()
        self.output_device_lbl = QLabel("Output Device: N/A")
        self.worker_status_lbl = QLabel("Worker: Stopped")
        for lbl in (self.output_device_lbl, self.worker_status_lbl):
            lbl.setStyleSheet("font-size: 9px; color: #94A3B8;")
        info_layout.addWidget(self.output_device_lbl)
        info_layout.addStretch()
        info_layout.addWidget(self.worker_status_lbl)
        diag_layout.addLayout(info_layout)

        self.diag_display = QTextEdit()
        self.diag_display.setReadOnly(True)
        self.diag_display.setStyleSheet("""
            QTextEdit {
                background-color: #030F26;
                border: 1px solid #0B1E36;
                border-radius: 4px;
                color: #94A3B8;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                min-height: 110px;
            }
        """)
        self.diag_display.setHtml("<span style='color: #475569;'>Diagnostics standby. Run test to capture waveform metrics.</span>")
        diag_layout.addWidget(self.diag_display)

        layout.addLayout(diag_layout)

    def load_devices(self):
        self.device_combo.clear()
        devices = device_manager.get_input_devices()
        
        default_idx = 0
        for dev in devices:
            self.device_combo.addItem(f"[{dev['id']}] {dev['name']}", dev['id'])
            if dev['is_default']:
                default_idx = self.device_combo.count() - 1
                self.active_device_id = dev['id']
                
        if self.device_combo.count() > 0:
            self.device_combo.setCurrentIndex(default_idx)

    def on_device_selected(self, index):
        if index < 0:
            return
        dev_id = self.device_combo.itemData(index)
        self.active_device_id = dev_id
        self.device_changed.emit(dev_id)
        logger.info(f"UI VoicePanel: Active device changed to ID {dev_id}")

    def on_slider_changed(self, value):
        self.sens_lbl.setText(f"SENSITIVITY THRESHOLD: {value}")
        config.VAD_ENERGY_THRESHOLD = value
        self.threshold_changed.emit(value)

    def update_volume_level(self, level):
        """Called dynamically from the voice engine signal to update progress bar."""
        self.level_bar.setValue(int(level))

    def run_diagnostics(self):
        if self.active_device_id is None:
            self.diag_display.setHtml("<span style='color: #EF4444;'>No active microphone source.</span>")
            return

        self.diag_btn.setEnabled(False)
        self.diag_display.setHtml("<span style='color: #00F0FF;'>Recording 3 seconds diagnostic audio segment... Please speak normally into the receiver.</span>")
        
        self.worker = DiagnosticsWorker(self.active_device_id)
        self.worker.finished.connect(self.display_diagnostics)
        self.worker.start()

    def display_diagnostics(self, result):
        self.diag_btn.setEnabled(True)
        if not result.get("success", False):
            self.diag_display.setHtml(f"<span style='color: #EF4444;'>Diagnostic sweep failed: {result.get('error_msg')}</span>")
            return

        html = f"""
        <span style="color: #00F0FF; font-weight: bold;">[DIAGNOSTIC REPORT COMPLETED]</span><br/>
        ----------------------------------------<br/>
        Peak Amplitude: <span style="color: #FFFFFF;">{result['peak_amplitude']:.0f}</span> units<br/>
        Average Energy: <span style="color: #FFFFFF;">{result['average_energy']:.1f}</span> units<br/>
        Noise Floor Estimate: <span style="color: #FFFFFF;">{result['estimated_noise_floor']:.1f}</span> units<br/>
        Signal-to-Noise Ratio (SNR): <span style="color: #10B981; font-weight: bold;">{result['snr_db']} dB</span><br/>
        Capture Grade: <span style="color: #10B981; font-weight: bold;">{result['quality_status']}</span><br/>
        ----------------------------------------<br/>
        <span style="color: #E2E8F0;">Audio buffer channels optimized. Calibrations matching current environment noise profiles.</span>
        """
        self.diag_display.setHtml(html)
        # Ensure diagnostics UI updates
        self.output_device_lbl.setText("Output Device: N/A")
        self.worker_status_lbl.setText("Worker: Stopped")

    # ----- Voice Diagnostics Logic -----
    def run_voice_diagnostics(self):
        """Trigger three test voice messages and monitor queue/worker status."""
        logger.info("[VOICE] Started voice diagnostics")
        # Update output device label
        try:
            out_dev = device_manager.get_default_output_device()
            if out_dev:
                self.output_device_lbl.setText(f"Output Device: {out_dev['name']}")
            else:
                self.output_device_lbl.setText("Output Device: Unknown")
        except Exception as e:
            logger.error(f"[VOICE] Error getting output device: {e}")
            self.output_device_lbl.setText("Output Device: Error")

        # Initialize diagnostic TTS worker if needed
        if not self.diagnostic_tts_worker:
            self.diagnostic_tts_worker = TTSWorker()
            self.diagnostic_tts_worker.speaking_started.connect(self._on_diag_speaking_started)
            self.diagnostic_tts_worker.speaking_finished.connect(self._on_diag_speaking_finished)
            self.diagnostic_tts_worker.queue_size_changed.connect(self._on_diag_queue_size_changed)
            self.diagnostic_tts_worker.start()
        else:
            # Ensure worker is running
            if not self.diagnostic_tts_worker.isRunning():
                self.diagnostic_tts_worker.start()

        # Reset counter
        self.diagnostic_finished_count = 0
        # Queue three messages
        messages = ["Voice diagnostic one", "Voice diagnostic two", "Voice diagnostic three"]
        for msg in messages:
            self.diagnostic_tts_worker.speak(msg)
            logger.info(f"[VOICE] Queued diagnostic message: {msg}")

        self.worker_status_lbl.setText("Worker: Running")

    def _on_diag_speaking_started(self, text):
        logger.info(f"[VOICE] Diagnostic speech started: {text}")
        self.worker_status_lbl.setText("Worker: Speaking")
        self.diag_display.append(f"<span style='color: #10B981;'>[DIAG] Speaking: {text}</span>")

    def _on_diag_speaking_finished(self):
        logger.info("[VOICE] Diagnostic speech completed")
        self.diagnostic_finished_count += 1
        self.worker_status_lbl.setText("Worker: Idle")
        if self.diagnostic_finished_count >= 3:
            # All messages processed, generate report
            report = {
                "queue_size": self.diagnostic_tts_worker.queue.qsize(),
                "worker_running": self.diagnostic_tts_worker.is_running
            }
            self.diag_display.append("<span style='color: #00F0FF;'>[DIAG] Report: " + str(report) + "</span>")
            logger.info(f"[VOICE] Diagnostic report: {report}")
            self.worker_status_lbl.setText("Worker: Stopped")

    def _on_diag_queue_size_changed(self, size):
        logger.info(f"[VOICE] Queue size: {size}")
        self.diag_display.append(f"<span style='color: #94A3B8;'>[DIAG] Queue size: {size}</span>")
