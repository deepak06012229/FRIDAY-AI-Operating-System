import math
from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import QTimer, Qt, QPoint, pyqtSignal, QSize
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QRadialGradient, QFont

class FridayCoreWidget(QWidget):
    """
    Futuristic custom QPainter widget drawing a multi-layered rotating HUD core.
    Reacts to speaker voice, input volume levels, and updates its core color
    to represent the FRIDAY operating system states.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "Idle"  # Idle, Listening, Processing, Thinking, Executing, Error, Speaking
        self.angle_offset = 0.0
        self.scale_pulse = 1.0
        self.pulse_direction = 1
        self.volume_level = 0.0  # 0 to 100
        self.ripple_radius = 0.0
        
        # High frequency animation timer (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)

        self.setMinimumSize(280, 280)

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.update()

    def set_volume_level(self, level):
        self.volume_level = float(level)
        self.update()

    def update_animation(self):
        # 1. Rotation speed based on states
        if self.state == "Idle":
            self.angle_offset += 0.4
        elif self.state == "Listening":
            self.angle_offset += 1.2
            self.ripple_radius += 2.0
            if self.ripple_radius > 120.0:
                self.ripple_radius = 20.0
        elif self.state == "Processing":
            self.angle_offset += 2.5
        elif self.state == "Thinking":
            self.angle_offset += 4.0
        elif self.state == "Executing":
            self.angle_offset += 3.0
        elif self.state == "Speaking":
            self.angle_offset += 0.8
        else: # Error
            self.angle_offset += 0.2

        if self.angle_offset >= 360.0:
            self.angle_offset = 0.0

        # 2. Main core pulsing
        if self.state == "Listening":
            self.scale_pulse = 1.0 + (self.volume_level / 250.0)
        elif self.state in ["Thinking", "Processing", "Executing"]:
            # Rapid breathing pulse
            self.scale_pulse += 0.015 * self.pulse_direction
            if self.scale_pulse >= 1.15:
                self.pulse_direction = -1
            elif self.scale_pulse <= 0.92:
                self.pulse_direction = 1
        else:
            # Slow steady idle pulse
            self.scale_pulse += 0.003 * self.pulse_direction
            if self.scale_pulse >= 1.04:
                self.pulse_direction = -1
            elif self.scale_pulse <= 0.96:
                self.pulse_direction = 1

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center = QPoint(int(width / 2), int(height / 2))
        base_radius = min(width, height) / 2 * 0.75
        radius = base_radius * self.scale_pulse

        # State Colors
        if self.state == "Listening":
            # Cyan
            core_color = QColor(0, 240, 255, 230)
            glow_color = QColor(0, 240, 255, 30)
        elif self.state == "Processing":
            # Green
            core_color = QColor(16, 185, 129, 230)
            glow_color = QColor(16, 185, 129, 30)
        elif self.state == "Thinking":
            # Purple
            core_color = QColor(139, 92, 246, 230)
            glow_color = QColor(139, 92, 246, 30)
        elif self.state == "Executing":
            # Orange
            core_color = QColor(245, 158, 11, 230)
            glow_color = QColor(245, 158, 11, 30)
        elif self.state == "Speaking":
            # Electric Blue / Green
            core_color = QColor(59, 130, 246, 230)
            glow_color = QColor(59, 130, 246, 30)
        elif self.state == "Error":
            # Red
            core_color = QColor(239, 68, 68, 230)
            glow_color = QColor(239, 68, 68, 40)
        else:
            # Idle - Royal Electric Blue
            core_color = QColor(26, 86, 219, 230)
            glow_color = QColor(26, 86, 219, 25)

        # 1. Glowing outer radial shadow
        gradient = QRadialGradient(center, radius * 1.3)
        gradient.setColorAt(0, QColor(core_color.red(), core_color.green(), core_color.blue(), 15))
        gradient.setColorAt(0.6, QColor(core_color.red(), core_color.green(), core_color.blue(), 5))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, int(radius * 1.3), int(radius * 1.3))
        painter.setBrush(Qt.NoBrush)

        # 2. Outer Ring: Thin dashed ring (slow rotation)
        pen_outer = QPen(glow_color)
        pen_outer.setWidth(1)
        pen_outer.setStyle(Qt.DashLine)
        painter.setPen(pen_outer)
        painter.drawEllipse(center, int(radius * 1.15), int(radius * 1.15))

        # 3. Rotating Arc Ring 1: Main quadrants (clockwise)
        pen_quad = QPen(core_color)
        pen_quad.setWidth(2)
        painter.setPen(pen_quad)
        start_ang1 = int(self.angle_offset * 16)
        span_ang1 = 45 * 16
        for i in range(4):
            painter.drawArc(
                int(center.x() - radius), int(center.y() - radius),
                int(radius * 2), int(radius * 2),
                start_ang1 + (i * 90 * 16), span_ang1
            )

        # 4. Rotating Arc Ring 2: Inner thin segments (counter-clockwise, faster)
        radius_inner_arc = radius * 0.85
        pen_quad.setWidth(1)
        painter.setPen(pen_quad)
        start_ang2 = int(-self.angle_offset * 1.7 * 16)
        span_ang2 = 90 * 16
        for i in range(2):
            painter.drawArc(
                int(center.x() - radius_inner_arc), int(center.y() - radius_inner_arc),
                int(radius_inner_arc * 2), int(radius_inner_arc * 2),
                start_ang2 + (i * 180 * 16), span_ang2
            )

        # 5. Technical Tick Marks Ring
        pen_ticks = QPen(glow_color)
        pen_ticks.setWidth(1)
        painter.setPen(pen_ticks)
        tick_r = radius * 0.72
        for i in range(0, 360, 10):
            rad = math.radians(i + self.angle_offset * 0.2)
            p1 = QPoint(
                int(center.x() + tick_r * math.cos(rad)),
                int(center.y() + tick_r * math.sin(rad))
            )
            p2 = QPoint(
                int(center.x() + (tick_r - 5) * math.cos(rad)),
                int(center.y() + (tick_r - 5) * math.sin(rad))
            )
            painter.drawLine(p1, p2)

        # 6. Ripple Waves (only in Listening/Speaking states)
        if self.state == "Listening" and self.ripple_radius > 10:
            rip_pen = QPen(QColor(core_color.red(), core_color.green(), core_color.blue(), int(150 * (1.0 - self.ripple_radius / 120.0))))
            rip_pen.setWidth(1)
            painter.setPen(rip_pen)
            painter.drawEllipse(center, int(self.ripple_radius), int(self.ripple_radius))

        # 7. Solid Center Core (pulsing size)
        gradient_core = QRadialGradient(center, radius * 0.45)
        gradient_core.setColorAt(0, QColor(core_color.red(), core_color.green(), core_color.blue(), 255))
        gradient_core.setColorAt(0.3, QColor(core_color.red(), core_color.green(), core_color.blue(), 180))
        gradient_core.setColorAt(0.7, QColor(core_color.red(), core_color.green(), core_color.blue(), 40))
        gradient_core.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(gradient_core))
        painter.setPen(Qt.NoPen)
        
        core_size_r = radius * 0.40
        if self.state == "Speaking":
            core_size_r += (self.volume_level / 300.0) * radius
            
        painter.drawEllipse(center, int(core_size_r), int(core_size_r))
        painter.setBrush(Qt.NoBrush)

        # 8. Technical text inside the core
        painter.setPen(QColor(255, 255, 255, 220))
        font = QFont("Consolas")
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        
        state_text = self.state.upper()
        painter.drawText(
            int(center.x() - 50), int(center.y() - 8), 100, 16,
            Qt.AlignCenter, state_text
        )


class FridayHUDCenterpiece(QWidget):
    """
    A widget acting as SIFRA/FRIDAY's centerpiece.
    Houses the animated FridayCoreWidget at the center and places
    10 custom circular buttons in a perfect ring layout.
    """
    button_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(420, 420)
        self.core = FridayCoreWidget(self)
        
        # Circular controls
        self.buttons_info = [
            ("CHAT", "Chat"),
            ("VOICE", "Voice Mode"),
            ("VISION", "Vision"),
            ("AUTO", "Automation"),
            ("FILES", "Files"),
            ("BROWSER", "Browser"),
            ("CODING", "Coding"),
            ("ROBOTICS", "Robotics"),
            ("MEMORY", "Memory"),
            ("SETTING", "Settings")
        ]
        
        self.buttons = []
        for key, name in self.buttons_info:
            btn = QPushButton(key, self)
            btn.setToolTip(name)
            btn.clicked.connect(lambda checked, n=name: self.button_clicked.emit(n))
            self.buttons.append(btn)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        h = self.height()
        cx = w / 2
        cy = h / 2
        
        # Calculate dynamic size based on centerpiece size
        size_ref = min(w, h)
        core_size = int(size_ref * 0.56)
        core_size = max(180, min(330, core_size)) # Clamp size
        
        self.core.setGeometry(int(cx - core_size / 2), int(cy - core_size / 2), core_size, core_size)
        
        # Calculate dynamic button radius and sizes
        radius = size_ref * 0.38
        radius = max(115.0, min(220.0, radius)) # Clamp radius
        
        btn_size = int(size_ref * 0.10)
        btn_size = max(42, min(56, btn_size)) # Clamp button size
        
        num_buttons = len(self.buttons)
        for i, btn in enumerate(self.buttons):
            btn.setFixedSize(btn_size, btn_size)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: rgba(5, 12, 24, 0.85);
                    border: 1px solid rgba(0, 240, 255, 0.4);
                    border-radius: {btn_size // 2}px;
                    color: #00F0FF;
                    font-family: 'Segoe UI', 'Consolas', sans-serif;
                    font-size: {max(7, int(btn_size * 0.15))}px;
                    font-weight: bold;
                    letter-spacing: 0.5px;
                }}
                QPushButton:hover {{
                    background-color: #00F0FF;
                    color: #050608;
                    border: 1px solid #FFFFFF;
                }}
                QPushButton:pressed {{
                    background-color: rgba(0, 240, 255, 0.4);
                }}
            """)
            
            # Angle starting from top (subtract pi/2)
            angle = i * (2 * math.pi / num_buttons) - (math.pi / 2)
            bx = cx + radius * math.cos(angle) - btn_size / 2
            by = cy + radius * math.sin(angle) - btn_size / 2
            btn.move(int(bx), int(by))
            
    def set_core_state(self, state):
        self.core.set_state(state)
        
    def set_volume_level(self, level):
        self.core.set_volume_level(level)
