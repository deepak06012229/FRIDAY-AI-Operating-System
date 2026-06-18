import time
from PyQt5.QtCore import QThread, pyqtSignal
import psutil
from utils import logger

class SystemMonitorThread(QThread):
    stats_updated = pyqtSignal(dict)  # Emits dictionary of system stats

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self._start_time = time.time()

    def run(self):
        logger.info("System Monitor Thread started.")
        while self.running:
            try:
                # CPU and RAM Usage
                cpu_percent = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory()
                ram_percent = ram.percent
                ram_used_gb = ram.used / (1024 ** 3)
                ram_total_gb = ram.total / (1024 ** 3)

                # Disk Usage
                disk = psutil.disk_usage('/')
                disk_percent = disk.percent
                disk_free_gb = disk.free / (1024 ** 3)

                # CPU cores breakdown (average)
                cpu_freq = psutil.cpu_freq()
                cpu_freq_mhz = cpu_freq.current if cpu_freq else 0

                uptime = int(time.time() - self._start_time)

                stats = {
                    "cpu_percent": cpu_percent,
                    "ram_percent": ram_percent,
                    "ram_used_gb": ram_used_gb,
                    "ram_total_gb": ram_total_gb,
                    "disk_percent": disk_percent,
                    "disk_free_gb": disk_free_gb,
                    "cpu_freq": cpu_freq_mhz,
                    "uptime_seconds": uptime
                }

                self.stats_updated.emit(stats)
            except Exception as e:
                logger.error(f"Error in SystemMonitorThread: {e}")

            self.msleep(1000)  # Check every 1 second

    def stop(self):
        self.running = False
        self.wait()
        logger.info("System Monitor Thread stopped.")
