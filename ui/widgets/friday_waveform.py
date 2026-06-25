import numpy as np
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt, QPointF
from PyQt5.QtGui import QPainter, QPen, QColor, QPolygonF

class FridayWaveformWidget(QWidget):
    """
    Electronic oscilloscope audio waveform widget.
    Draws active microphone capture streams or an organic standby signal
    represented by overlaying multiple sine wave frequencies.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buffer_data = np.zeros(128)
        self.is_active = False
        self.time_offset = 0.0

        # Standby animation timer (~30 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_standby)
        self.timer.start(33)

        self.setMinimumSize(220, 60)

    def set_waveform_data(self, numpy_array):
        """Processes and loads raw voice audio buffers to be plotted."""
        if numpy_array is None or len(numpy_array) == 0:
            return
        
        self.is_active = True
        
        # Downsample array to fit visual representation (128 points)
        length = len(numpy_array)
        indices = np.linspace(0, length - 1, 128, dtype=int)
        raw_points = numpy_array[indices]
        
        peak = np.max(np.abs(raw_points))
        if peak > 0:
            self.buffer_data = raw_points / peak
        else:
            self.buffer_data = np.zeros(128)
            
        self.update()

    def update_standby(self):
        """Animates standby waveform scrolling."""
        self.time_offset += 0.08
        if self.time_offset > 2 * math.pi:
            self.time_offset = 0.0
        
        if not self.is_active:
            self.update()
            
        # Revert back to standby if no new voice buffers are supplied
        self.is_active = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_y = height / 2

        # 1. Draw glowing grid lines in background
        grid_pen = QPen(QColor(0, 240, 255, 12))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        
        # Draw columns
        spacing = width / 12
        for i in range(1, 12):
            x = i * spacing
            painter.drawLine(int(x), 0, int(x), height)
            
        # Center reference line
        center_line_pen = QPen(QColor(0, 240, 255, 20))
        painter.setPen(center_line_pen)
        painter.drawLine(0, int(center_y), width, int(center_y))

        # 2. Draw wave points
        poly = QPolygonF()
        num_points = 128
        step_x = width / (num_points - 1)
        points = []

        if self.is_active:
            # Active voice plotting
            for i in range(num_points):
                x = i * step_x
                y = center_y + (self.buffer_data[i] * (height / 2 * 0.85))
                points.append(QPointF(x, y))
        else:
            # Multi-layered standby sine wave
            for i in range(num_points):
                x = i * step_x
                val = (math.sin(i * 0.12 - self.time_offset) * 0.25 + 
                       math.sin(i * 0.28 + self.time_offset * 1.3) * 0.12 + 
                       math.sin(i * 0.04 - self.time_offset * 0.4) * 0.04)
                
                # Window function to fade out at edges
                gate = math.sin((i / (num_points - 1)) * math.pi)
                y = center_y + (val * gate * (height / 2 * 0.8))
                points.append(QPointF(x, y))

        polygon = QPolygonF(points)

        # 3. Paint glow line
        glow_pen = QPen(QColor(0, 240, 255, 55))
        glow_pen.setWidth(4)
        painter.setPen(glow_pen)
        painter.drawPolyline(polygon)

        # 4. Paint core line
        core_pen = QPen(QColor(255, 255, 255, 220))
        core_pen.setWidthF(1.2)
        painter.setPen(core_pen)
        painter.drawPolyline(polygon)
