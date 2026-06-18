import os

# ==================== GENERAL CONFIG ====================
SYSTEM_NAME = "FRIDAY"
USER_NAME = "Commander"
GREETING_FORMAT = "Good {time_of_day}, {user}. FRIDAY systems online."

# ==================== FILE PATHS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "memory", "friday_memory.db")
LOG_PATH = os.path.join(BASE_DIR, "logs", "friday_system.log")
WORKFLOW_PATH = os.path.join(BASE_DIR, "workflows.json")

# ==================== AUDIO CONFIG ====================
DEFAULT_SAMPLE_RATE = 16000  # Best for Speech Recognition
CHANNELS = 1
# Energy threshold for Voice Activity Detection (VAD)
VAD_ENERGY_THRESHOLD = 800   # Dynamic noise floor will adjust this
VAD_SILENCE_DURATION = 1.5   # Seconds of silence before stopping recording
VAD_MIN_DURATION = 0.5       # Min duration to avoid clipping short words
VAD_MAX_DURATION = 15.0      # Max recording time safety limit

# ==================== VOICE / TTS CONFIG ====================
# Default voice for Edge‑TTS
VOICE_DEFAULT = "en-US-JennyNeural"
# Available voice options (user can select via UI)
VOICE_OPTIONS = [
    "en-US-AriaNeural",
    "en-US-JennyNeural",
    "en-GB-SoniaNeural",
]
# Voice provider selection: "edge" (default), "disabled", "elevenlabs" (future)
VOICE_PROVIDER = "edge"

# ==================== LLM & AI CONFIG ====================
# Default model for reasoning
GEMINI_MODEL = "gemini-2.5-flash"
# Endpoint for direct REST calls (avoids SDK dependency issues on Python 3.14)
GEMINI_REST_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

# ==================== AUTOMATION REGISTRY ====================
# Mapping common application terms to their executables on Windows
APP_REGISTRY = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "google chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vs code": "C:\\Users\\Deepak\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "visual studio code": "C:\\Users\\Deepak\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "explorer": "explorer.exe",
    "cmd": "cmd.exe",
}

# Web shortcuts
WEB_REGISTRY = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
}
