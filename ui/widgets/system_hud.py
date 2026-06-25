from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QBrush

class HUDProgressCircle(QWidget):
    """
    A circular gauge widget displaying percentages.
    Draws a glowing arc representing value and handles color shifts
    (e.g., cyan -> orange -> red) based on threshold loads.
    """
    def __init__(self, title="", unit="%", parent=None):
        super().__init__(parent)
        self.title = title.upper()
        self.unit = unit
        self.value = 0
        self.setMinimumSize(85, 95)

    def setValue(self, val):
        self.value = max(0, min(100, int(val)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        
        # Determine center and radius
        cx = width / 2
        cy = (height - 15) / 2
        radius = min(width, height - 15) / 2 * 0.85
        
        # Color shifting based on metrics load
        if self.value < 70:
            arc_color = QColor(0, 240, 255, 220)   # Cyber Cyan
            glow_color = QColor(0, 240, 255, 30)
        elif self.value < 85:
            arc_color = QColor(245, 158, 11, 220)  # Warning Amber
            glow_color = QColor(245, 158, 11, 30)
        else:
            arc_color = QColor(239, 68, 68, 220)   # Danger Red
            glow_color = QColor(239, 68, 68, 40)

        # 1. Draw track ring (background circular track)
        track_pen = QPen(QColor(11, 30, 54, 150))
        track_pen.setWidth(4)
        painter.setPen(track_pen)
        painter.drawEllipse(QPoint(int(cx), int(cy)), int(radius), int(radius))

        # 2. Draw glowing active arc
        glow_pen = QPen(glow_color)
        glow_pen.setWidth(8)
        glow_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(glow_pen)
        # In QPainter, angles are specified in 1/16ths of a degree.
        # Start at 90 degrees (top center) and span counter-clockwise
        start_angle = 90 * 16
        span_angle = int(-self.value * 3.6 * 16)
        painter.drawArc(
            int(cx - radius), int(cy - radius),
            int(radius * 2), int(radius * 2),
            start_angle, span_angle
        )

        # Draw core arc line
        arc_pen = QPen(arc_color)
        arc_pen.setWidth(4)
        arc_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(arc_pen)
        painter.drawArc(
            int(cx - radius), int(cy - radius),
            int(radius * 2), int(radius * 2),
            start_angle, span_angle
        )

        # 3. Draw text in the center
        painter.setPen(QColor(255, 255, 255, 220))
        font_val = QFont("Consolas")
        font_val.setPointSize(10)
        font_val.setBold(True)
        painter.setFont(font_val)
        
        val_str = f"{self.value}{self.unit}"
        painter.drawText(
            int(cx - 30), int(cy - 10), 60, 20,
            Qt.AlignCenter, val_str
        )

        # 4. Draw label below
        painter.setPen(QColor(148, 163, 184, 255)) # Muted grey
        font_lbl = QFont("Segoe UI")
        font_lbl.setPointSize(7)
        font_lbl.setBold(True)
        font_lbl.setLetterSpacing(QFont.AbsoluteSpacing, 1)
        painter.setFont(font_lbl)
        
        painter.drawText(
            0, int(height - 14), width, 14,
            Qt.AlignCenter, self.title
        )
