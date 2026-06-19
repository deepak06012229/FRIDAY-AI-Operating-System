import psutil
import time
from PyQt5.QtCore import QThread, pyqtSignal


class SystemMonitor:
    """Utility class for retrieving system metrics."""

    @staticmethod
    def cpu_percent() -> int:
        """Return current CPU usage percentage."""
        return int(psutil.cpu_percent(interval=0.1))

    @staticmethod
    def ram_percent() -> int:
        """Return current RAM usage percentage."""
        return int(psutil.virtual_memory().percent)

    @staticmethod
    def cpu_freq() -> float:
        """Return current CPU frequency in MHz."""
        freq = psutil.cpu_freq()
        return freq.current if freq else 0.0

    @staticmethod
    def disk_free_gb() -> float:
        """Return free disk space in gigabytes."""
        return psutil.disk_usage("/").free / (1024 ** 3)

    @staticmethod
    def ram_used_gb() -> float:
        """Return used RAM in gigabytes."""
        return psutil.virtual_memory().used / (1024 ** 3)

    @staticmethod
    def ram_total_gb() -> float:
        """Return total RAM in gigabytes."""
        return psutil.virtual_memory().total / (1024 ** 3)

    @staticmethod
    def uptime_seconds() -> int:
        """Return system uptime in seconds."""
        return int(time.time() - psutil.boot_time())

    @staticmethod
    def process_count() -> int:
        """Return number of running processes."""
        return len(psutil.pids())


class SystemMonitorThread(QThread):
    """QThread that periodically emits system stats."""
    stats_updated = pyqtSignal(dict)

    def __init__(self, parent=None, interval_ms: int = 2000):
        super().__init__(parent)
        self._running = True
        self.interval_ms = interval_ms

    def run(self):
        while self._running:
            stats = {
                "cpu_percent": SystemMonitor.cpu_percent(),
                "ram_percent": SystemMonitor.ram_percent(),
                "cpu_freq": SystemMonitor.cpu_freq(),
                "disk_free_gb": SystemMonitor.disk_free_gb(),
                "ram_used_gb": SystemMonitor.ram_used_gb(),
                "ram_total_gb": SystemMonitor.ram_total_gb(),
                "uptime_seconds": SystemMonitor.uptime_seconds(),
                "process_count": SystemMonitor.process_count(),
            }
            self.stats_updated.emit(stats)
            self.msleep(self.interval_ms)

    def stop(self):
        self._running = False
        self.wait()
