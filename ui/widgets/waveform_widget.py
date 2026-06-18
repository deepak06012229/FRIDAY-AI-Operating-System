import numpy as np
import time
import math
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QPen, QColor, QPolygonF
from PyQt5.QtCore import QPointF

class HUDAntiGravityWaveform(QWidget):
    """
    Plots real-time audio buffers as a neon glowing waveform.
    If no speech data is active, it animates a standby electronic oscilloscope pattern.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buffer_data = np.zeros(128)
        self.is_active = False
        self.time_offset = 0.0

        # Run standby animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_standby)
        self.timer.start(30)  # ~33 fps

        self.setMinimumSize(220, 60)

    def set_waveform_data(self, numpy_array):
        """Passes a raw NumPy audio array to be rendered."""
        if numpy_array is None or len(numpy_array) == 0:
            return
        
        self.is_active = True
        
        # Downsample array to fit visual representation (e.g., 128 points)
        length = len(numpy_array)
        indices = np.linspace(0, length - 1, 128, dtype=int)
        raw_points = numpy_array[indices]
        
        # Scale range to normal coordinates
        # Max scale bounds
        peak = np.max(np.abs(raw_points))
        if peak > 0:
            self.buffer_data = raw_points / peak
        else:
            self.buffer_data = np.zeros(128)
            
        self.update()

    def update_standby(self):
        """Updates offset to animate the baseline standby sine wave."""
        self.time_offset += 0.1
        if self.time_offset > 2 * math.pi:
            self.time_offset = 0.0
        
        if not self.is_active:
            self.update()
            
        # Reset activity flag so it reverts to standby if no chunks are pushed
        self.is_active = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()
        center_y = height / 2

        # 1. Draw glowing grid lines in background
        grid_pen = QPen(QColor(0, 240, 255, 15))
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)
        
        # Vertical grid columns
        spacing = width / 10
        for i in range(1, 10):
            x = i * spacing
            painter.drawLine(int(x), 0, int(x), height)
        # Horizontal center line
        painter.drawLine(0, int(center_y), width, int(center_y))

        # 2. Plot the Waveform
        poly = QPolygonF()
        num_points = 128
        step_x = width / (num_points - 1)

        # Retrieve points
        points = []
        if self.is_active:
            # Render actual audio wave data
            for i in range(num_points):
                x = i * step_x
                y = center_y + (self.buffer_data[i] * (height / 2 * 0.85))
                points.append(QPointF(x, y))
        else:
            # Standby state: composite sine wave
            for i in range(num_points):
                x = i * step_x
                # Layer multiple sine frequencies for a organic electronic look
                val = (math.sin(i * 0.15 - self.time_offset) * 0.3 + 
                       math.sin(i * 0.35 + self.time_offset * 1.5) * 0.15 + 
                       math.sin(i * 0.05 - self.time_offset * 0.5) * 0.05)
                
                # Attenuate wave near edges (fade out at borders)
                gate = math.sin((i / (num_points - 1)) * math.pi)
                y = center_y + (val * gate * (height / 2 * 0.75))
                points.append(QPointF(x, y))

        # Draw main glow line
        glow_pen = QPen(QColor(0, 240, 255, 60))
        glow_pen.setWidth(3)
        painter.setPen(glow_pen)
        painter.drawPolyline(QPolygonF(points))

        # Draw core center line
        core_pen = QPen(QColor(255, 255, 255, 220))
        core_pen.setWidthF(1.5)
        painter.setPen(core_pen)
        painter.drawPolyline(QPolygonF(points))
