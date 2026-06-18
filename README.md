# 📦 FRIDAY AI Operating System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/Qt5-PyQt5%205.15%2B-brightgreen?logo=qt)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)
[![Stars](https://img.shields.io/github/stars/deepak06012229/FRIDAY-AI-OS?style=social)](https://github.com/deepak06012229/FRIDAY-AI-OS)

---

## 🎯 Introduction

**FRIDAY AI Operating System** is a modern, extensible AI‑driven personal assistant that turns your desktop into an intelligent operating environment. Built with a clean, maintainable architecture, FRIDAY integrates large‑language‑model (LLM) back‑ends, speech‑to‑text, and a high‑quality **Edge‑TTS** voice engine. The project showcases full‑stack AI engineering skills—perfect for recruiters, internship coordinators, and hiring managers looking for evidence of real‑world AI system development.

---

## 🛠️ What is FRIDAY?

FRIDAY is a Python‑based AI OS that can:
- Understand natural language queries.
- Execute local commands (open apps, run scripts, control hardware).
- Run AI workflows (search the web, fetch knowledge, manage memory).
- Provide spoken feedback using a modern, non‑blocking voice pipeline.

It is designed to be **plugin‑ready** so new skills, voice providers, or LLMs can be added with minimal friction.

---

## ✨ Key Features

- **🔊 Edge‑TTS Voice Engine** – Natural‑sounding speech (`en‑US‑JennyNeural` by default) with a clean queue architecture.
- **💬 Multi‑LLM Support** – Gemini, Ollama (local), and future OpenAI integration.
- **🧠 Context‑Aware Brain** – Persistent memory, workflow automation, and a plugin system.
- **🖥️ Rich PyQt5 UI** – Dashboard, voice diagnostics panel, and workflow visualizer.
- **⚙️ Hot‑Reloadable Config** – Change voice, LLM, or API keys at runtime without restarting.
- **🔧 Diagnostics Mode** – "Test Voice" button logs each voice pipeline stage.
- **📦 Modular Design** – Clear separation of UI, core, voice, and AI layers.
- **🪟 Windows‑First** – Tested on Windows, uses `QMediaPlayer` for audio playback.

---

## 🏗️ Architecture Overview

```
FRIDAY/
├─ ui/                     # PyQt5 UI (dashboard, panels)
│   └─ panels/
│       ├─ voice_panel.py   # Test‑voice button, diagnostics UI
│       └─ …
├─ ai/                     # LLM adapters (Gemini, Ollama)
│   └─ ollama_provider.py
├─ voice/                  # Voice subsystem
│   ├─ tts_worker.py       # Queue thread, provider abstraction
│   └─ device_manager.py
├─ config.py               # Global configuration (voice, LLM, paths)
├─ logs/                   # Runtime logs (friday_system.log)
├─ requirements.txt
└─ main.py                 # Application entry point
```

* **UI Layer** – Emits `speak_requested` signals.
* **Voice Layer** – `TTSWorker` pulls text from a thread‑safe queue, calls the selected **VoiceProvider** (`EdgeTTSProvider` or `DisabledProvider`), and plays audio with `QMediaPlayer`.
* **AI Layer** – Wraps LLM APIs; the Brain orchestrates prompting, memory, and command execution.
* **Config** – Centralized, hot‑reloadable settings for voice, LLM, and API keys.

---

## 📸 Screenshots

> *Replace the placeholders with actual screenshots in the `docs/` folder.*

| Dashboard | Voice Diagnostics |
|-----------|-------------------|
| ![Dashboard](docs/dashboard_placeholder.png) | ![Voice Diagnostics](docs/voice_diag_placeholder.png) |

---

## 🚀 Installation

```bash
# Clone the repository
git clone https://github.com/deepak06012229/FRIDAY-AI-OS.git
cd FRIDAY-AI-OS

# Create a virtual environment (recommended)
python -m venv .venv
\.venv\Scripts\activate   # PowerShell

# Install dependencies
pip install -r requirements.txt
```

---

## 🛠️ Setup Guide

### 1️⃣ Ollama (Local LLM)
```bash
# Download installer (Windows)
#   https://ollama.com/download/OllamaSetup.exe

# Start the Ollama server
ollama serve

# Pull a model (e.g., llama3)
ollama pull llama3
```
Add to `config.py` (or set env vars):
```python
OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"
DEFAULT_OLLAMA_MODEL = "llama3"
```

### 2️⃣ Gemini API (Google Gemini)
1. Create an API key in **Google AI Studio**.
2. Export the key:
```bash
# PowerShell
$env:GEMINI_API_KEY="YOUR_API_KEY"
# Bash/macOS
export GEMINI_API_KEY="YOUR_API_KEY"
```
Or place a `.env` file in the project root:
```
GEMINI_API_KEY=YOUR_API_KEY
```

### 3️⃣ Edge‑TTS (Voice Engine)
`edge‑tts` is installed via `requirements.txt`. No extra keys are needed. To change the default voice edit `config.py`:
```python
VOICE_DEFAULT = "en‑US‑JennyNeural"  # any voice from the Azure Speech service
VOICE_OPTIONS = [
    "en‑US‑AriaNeural",
    "en‑US‑JennyNeural",
    "en‑GB‑SoniaNeural",
]
```

---

## 💡 Usage Examples

```bash
# Start the application
python main.py
```
### Voice Interaction
- **Test voice** – Click the **TEST VOICE** button in the UI. You’ll hear three sequential phrases and see detailed logs.
- **Ask a question** – Type `What is the weather in London?` → FRIDAY replies in text and spoken audio.
- **Run a command** – Type `open chrome` → Chrome launches, and FRIDAY confirms audibly.
### CLI Samples
```bash
# Set environment variables (PowerShell)
$env:GEMINI_API_KEY="YOUR_KEY"

# Run a single query via the brain (example) – this is for debugging
python -c "from brain import FRIDAYBrain; FRIDAYBrain().process('Tell me a joke')"
```

---

## 📂 Project Structure

```
FRIDAY/
├─ .venv/                # Virtual environment (git‑ignored)
├─ ai/                   # LLM adapters
│   ├─ __init__.py
│   └─ ollama_provider.py
├─ config.py
├─ logs/                 # Runtime logs
│   └─ friday_system.log
├─ requirements.txt
├─ ui/
│   ├─ __init__.py
│   ├─ dashboard.py
│   └─ panels/
│       ├─ voice_panel.py
│       └─ …
├─ voice/
│   ├─ __init__.py
│   ├─ tts_worker.py
│   └─ device_manager.py
├─ main.py               # Entry point
└─ README.md
```

---

## 📅 Future Roadmap

- **🔌 Plugin System** – Dynamically load third‑party skills (home automation, calendar integration). 
- **🎤 ElevenLabs Voice Provider** – Add premium voice synthesis options. 
- **🗂️ Persistent Knowledge Graph** – Store facts in a vector database for faster recall. 
- **🌐 Web UI** – Optional Electron front‑end for cross‑platform access. 
- **🔐 Secure Credential Store** – Encrypt API keys via OS secret managers. 
- **📈 Automated Test Suite** – Full CI pipeline with unit, integration, and UI tests.

---

## 🛠️ Technologies Used

| Category | Library / Tool | Version |
|----------|----------------|---------|
| **Language** | Python | 3.11+ |
| **UI** | PyQt5 | 5.15.11 |
| **Voice** | edge‑tts | 7.2.8 |
| **Audio Playback** | QMediaPlayer (Qt) | – |
| **LLM** | Ollama (local) | 0.6.2 |
| | Gemini (REST) | – |
| **Async** | asyncio | – |
| **Logging** | custom `utils.logger` | – |
| **Testing** | pytest (dev) | – |

---

## 🤝 Contribution Guidelines

1. **Fork** the repository.
2. Create a **feature branch**: `git checkout -b feat/awesome-feature`.
3. Follow **PEP‑8** style; run `flake8` before committing.
4. Add or update **unit tests** in the `tests/` directory.
5. Ensure all CI checks pass (`python -m py_compile` and `pytest`).
6. Open a **Pull Request** with a clear description and link to any related issue.

> *Tip for hiring managers:* Contributions that add a new voice provider, improve diagnostics, or integrate a new LLM demonstrate strong engineering and problem‑solving abilities.

---

## 📄 License

This project is licensed under the **MIT License** – see the `LICENSE` file for details.

---

## 👤 Author

**Deepak Rajan Morje**
B.E. Computer Science Engineering (AI & ML)
SSPM College of Engineering, Mumbai University

GitHub: https://github.com/deepak06012229
LinkedIn: [Add my LinkedIn profile link]

**Project:** FRIDAY AI Operating System

> *Passionate AI, Robotics, and Software Engineering student focused on building intelligent systems, automation tools, and next‑generation AI assistants.*
