import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from utils import logger
from utils.system_monitor import SystemMonitorThread
from voice.voice_engine import VoiceEngine
from ai.brain import FRIDAYBrain
from ui.dashboard import FRIDAYDashboard
import config

def load_environment_variables():
    """Loads settings from a local .env file if available in the workspace."""
    env_path = os.path.join(config.BASE_DIR, ".env")
    if os.path.exists(env_path):
        logger.info("Loading environment variables from local .env config...")
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, val = line.strip().split('=', 1)
                        os.environ[key.strip()] = val.strip()
            logger.info("Local environment loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to parse .env file: {e}")

def main():
    # 1. Set High-DPI and scaling attributes BEFORE creating the QApplication instance
    try:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        logger.info("High-DPI and screen scaling attributes configured.")
    except Exception as e:
        # Fallback logging if stream is not ready
        print(f"Warning: Failed to set High-DPI attributes: {e}")

    logger.info("Initializing FRIDAY AI Operating System Core Bootstrap...")
    
    # 2. Load env parameters (Gemini API keys, etc.)
    load_environment_variables()

    # 3. Start PyQt5 application context
    app = QApplication(sys.argv)
    app.setApplicationName("FRIDAY AI OS")

    # 4. Create the FRIDAY Brain (coordinates SQLite, local Intent rule mappings, and LLM REST client)
    brain = FRIDAYBrain()

    # 5. Initialize the continuous sound capture Voice Engine
    voice = VoiceEngine()

    # 6. Initialize hardware psutil performance monitor thread
    monitor = SystemMonitorThread()

    # 7. Initialize main HUD Dashboard window, connecting cross-module signals
    dashboard = FRIDAYDashboard(brain, voice, monitor)
    
    # 8. Boot up thread workers
    monitor.start()
    voice.start()

    logger.info("FRIDAY AI OS components successfully bound. Showing dashboard HUD...")
    dashboard.show()
    
    # Start main Qt event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
