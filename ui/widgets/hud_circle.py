import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QRadialGradient

class HUDAntiGravityCircle(QWidget):
    """
    Futuristic custom QPainter widget drawing a Tony Stark inspired HUD circle.
    Displays rotating arcs, glowing rings, and transitions based on system state.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "Idle"  # Calibrating, Idle, Listening, Thinking, Speaking, Error
        self.angle_offset = 0.0
        self.scale_pulse = 1.0
        self.pulse_direction = 1
        self.volume_level = 0.0  # 0.0 to 100.0 (feeds Listening/Speaking size)
        
        # Start high-frequency animation timer (60 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)  # ~60 fps

        # Size constraints
        self.setMinimumSize(220, 220)

    def set_state(self, state):
        if self.state != state:
            self.state = state
            self.update()

    def set_volume_level(self, level):
        self.volume_level = float(level)
        self.update()

    def update_animation(self):
        # 1. Rotate arcs based on state
        if self.state == "Idle":
            self.angle_offset += 0.5
        elif self.state == "Listening":
            self.angle_offset += 1.5
        elif self.state == "Thinking":
            self.angle_offset += 3.0
        elif self.state == "Speaking":
            self.angle_offset += 1.0
        elif self.state == "Calibrating":
            self.angle_offset += 2.0
        else:  # Error
            self.angle_offset += 0.2

        # Wrap angle
        if self.angle_offset >= 360:
            self.angle_offset = 0

        # 2. Pulse scale factor
        if self.state == "Listening":
            # Pulse proportional to voice volume
            self.scale_pulse = 1.0 + (self.volume_level / 200.0)
        elif self.state == "Thinking":
            # Smooth sine wave pulse
            self.scale_pulse += 0.015 * self.pulse_direction
            if self.scale_pulse >= 1.15:
                self.pulse_direction = -1
            elif self.scale_pulse <= 0.95:
                self.pulse_direction = 1
        else:
            # Idle gentle pulse
            self.scale_pulse += 0.003 * self.pulse_direction
            if self.scale_pulse >= 1.03:
                self.pulse_direction = -1
            elif self.scale_pulse <= 0.97:
                self.pulse_direction = 1

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Center of widget
        width = self.width()
        height = self.height()
        center = QPoint(int(width / 2), int(height / 2))
        radius = min(width, height) / 2 * 0.8 * self.scale_pulse

        # State Colors
        # Default Cyan/Blue theme
        hud_color = QColor(0, 240, 255, 200)       # Cyan (Idle/Active)
        glow_color = QColor(0, 240, 255, 30)
        
        if self.state == "Calibrating":
            hud_color = QColor(245, 158, 11, 200)   # Yellow/Amber
            glow_color = QColor(245, 158, 11, 30)
        elif self.state == "Thinking":
            hud_color = QColor(234, 88, 12, 220)    # Dark Amber/Orange
            glow_color = QColor(234, 88, 12, 40)
        elif self.state == "Listening":
            # Dynamic green-tinted cyan based on mic level
            hud_color = QColor(0, 255, 210, 220)
            glow_color = QColor(0, 255, 210, 50)
        elif self.state == "Speaking":
            hud_color = QColor(16, 185, 129, 220)   # Green
            glow_color = QColor(16, 185, 129, 45)
        elif self.state == "Error":
            hud_color = QColor(239, 68, 68, 220)    # Red
            glow_color = QColor(239, 68, 68, 50)

        # Draw glowing radial background
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(hud_color.red(), hud_color.green(), hud_color.blue(), 10))
        gradient.setColorAt(0.7, QColor(hud_color.red(), hud_color.green(), hud_color.blue(), 5))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, int(radius * 1.2), int(radius * 1.2))

        # Reset Brush
        painter.setBrush(Qt.NoBrush)

        # ---------------- DRAW HUD ELEMENTS ----------------
        # 1. Outer Ring (thin dashed)
        pen = QPen(glow_color)
        pen.setWidth(1)
        pen.setStyle(Qt.DashLine)
        painter.setPen(pen)
        painter.drawEllipse(center, int(radius * 1.1), int(radius * 1.1))

        # 2. Main Outer Circular Arc (rotating)
        pen = QPen(hud_color)
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Rotating quadrants
        start_angle = int(self.angle_offset * 16)
        span_angle = 60 * 16
        
        for i in range(4):
            painter.drawArc(
                int(center.x() - radius), int(center.y() - radius),
                int(radius * 2), int(radius * 2),
                start_angle + (i * 90 * 16), span_angle
            )

        # 3. Inner Technical Tick Marks (drawing concentric tick rings)
        pen = QPen(glow_color)
        pen.setWidth(1)
        painter.setPen(pen)
        
        inner_r = radius * 0.8
        for i in range(0, 360, 15):
            rad = math.radians(i)
            # Short lines radiating outwards
            p1 = QPoint(
                int(center.x() + inner_r * math.cos(rad)),
                int(center.y() + inner_r * math.sin(rad))
            )
            p2 = QPoint(
                int(center.x() + (inner_r - 6) * math.cos(rad)),
                int(center.y() + (inner_r - 6) * math.sin(rad))
            )
            painter.drawLine(p1, p2)

        # 4. Secondary Counter-Rotating Arc (Opposite rotation)
        pen = QPen(hud_color)
        pen.setWidth(1)
        painter.setPen(pen)
        
        inner_r2 = radius * 0.7
        opp_angle = int(-self.angle_offset * 1.3 * 16)
        for i in range(2):
            painter.drawArc(
                int(center.x() - inner_r2), int(center.y() - inner_r2),
                int(inner_r2 * 2), int(inner_r2 * 2),
                opp_angle + (i * 180 * 16), 110 * 16
            )

        # 5. Glowing Center Core
        gradient_core = QRadialGradient(center, radius * 0.45)
        gradient_core.setColorAt(0, QColor(hud_color.red(), hud_color.green(), hud_color.blue(), 255))
        gradient_core.setColorAt(0.4, QColor(hud_color.red(), hud_color.green(), hud_color.blue(), 150))
        gradient_core.setColorAt(0.9, QColor(hud_color.red(), hud_color.green(), hud_color.blue(), 30))
        gradient_core.setColorAt(1, QColor(hud_color.red(), hud_color.green(), hud_color.blue(), 0))
        
        painter.setBrush(QBrush(gradient_core))
        painter.setPen(Qt.NoPen)
        # Pulse core radius
        core_r = radius * 0.35
        if self.state == "Speaking":
            # Pulse center core size on volume level
            core_r += (self.volume_level / 400.0) * radius
        painter.drawEllipse(center, int(core_r), int(core_r))
        
        # 6. Technical Text State in center (small tech font)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 180)))
        font = painter.font()
        font.setFamily("Consolas")
        font.setPointSize(8)
        font.setBold(True)
        painter.setFont(font)
        
        state_text = self.state.upper()
        # Draw status text centered
        painter.drawText(
            int(center.x() - 40), int(center.y() + 4), 80, 20,
            Qt.AlignCenter, state_text
        )
