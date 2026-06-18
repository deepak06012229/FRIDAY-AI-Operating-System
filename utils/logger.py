import os
import sys
import logging
from datetime import datetime
import config

# Create logs directory if needed
log_dir = os.path.dirname(config.LOG_PATH)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Initialize standard Python logging
logger = logging.getLogger("FRIDAY")
logger.setLevel(logging.INFO)

# File Handler
file_handler = logging.FileHandler(config.LOG_PATH, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s: %(message)s'))
logger.addHandler(file_handler)

# Console Handler
class LogCallbackHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.callbacks = []

    def emit(self, record):
        log_entry = self.format(record)
        # Call all registered callbacks (e.g. GUI console updater)
        for callback in self.callbacks:
            try:
                callback(log_entry)
            except Exception:
                pass

callback_handler = LogCallbackHandler()
callback_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%H:%M:%S'))
logger.addHandler(callback_handler)

# Standard stream fallback
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%H:%M:%S'))
logger.addHandler(stream_handler)

def info(msg):
    logger.info(msg)

def warn(msg):
    logger.warning(msg)

def error(msg):
    logger.error(msg)

def debug(msg):
    logger.debug(msg)

def register_log_callback(cb):
    """Register a UI function to receive log strings in real time."""
    callback_handler.callbacks.append(cb)
    info("UI Activity Log channel connected.")
