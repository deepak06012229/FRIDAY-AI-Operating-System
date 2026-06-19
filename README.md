# FRIDAY AI Operating System

## Project Overview
FRIDAY AI OS is a **personal AI assistant** built on a modular Python/PyQt5 architecture. It combines a **voice interface**, **LLM integration** (Ollama & Gemini), a **memory manager**, and a **workflow engine** to provide a conversational, hands‑free computing experience. The system is designed for local operation, respecting user privacy.

## Key Features
- **Voice Capture & Speech Synthesis** – Continuous microphone listening with real‑time waveform visualization and TTS output.
- **LLM Backend** – Primary inference via Ollama (qwen2.5‑coder). Falls back to Gemini if Ollama is unavailable.
- **Memory Management** – SQLite‑backed persistence of conversation logs, user profile, and categorized facts (Personal, Project, Preference, Goal, Task, General).
- **Dynamic HUD** – Futuristic HUD circle reflecting states: `Idle`, `Listening`, `Thinking`, `Speaking`, `Workflow`, `Memory Update`.
- **Workflow Engine** – Declarative JSON workflows that can launch apps, open URLs, or orchestrate multi‑step actions.
- **Dashboard UI** – Tabbed interface with chat panel, voice panel, system metrics, automation panel, and memory browser.
- **Personalization** – All responses address the user as **Chief** and incorporate stored memory facts.

## Screenshots
*(Add screenshots in the `assets/` folder and reference them here)*

![Dashboard](assets/dashboard.png)
![HUD Circle](assets/hud_circle.png)

## Architecture Overview
A high‑level diagram is provided in `docs/ARCHITECTURE.md`.

## Installation Guide
```bash
# Clone the repository
git clone https://github.com/yourusername/friday-ai-os.git
cd friday-ai-os

# Set up Python environment (recommended virtualenv)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Ollama and required model (optional for offline use)
ollama pull qwen2.5-coder:latest

# Configure environment variables (copy .env.example → .env)
cp .env.example .env
# Edit .env to add Gemini API key if you want cloud fallback
```

## Usage Guide
```bash
python main.py
```
- The UI launches with the HUD circle at the top‑right.
- Click **PAUSE LISTENING** to mute the voice engine.
- Use voice commands or type into the **Chat** tab.
- Available voice commands are listed in `docs/COMMANDS.md`.

## Memory System
- Persists conversation logs and facts in `friday_memory.db`.
- Facts are automatically categorized based on simple keyword heuristics.
- Use the **Memory** tab to view, add, or delete facts.
- Memory updates trigger the HUD state **Memory Update**.

## Workflow Engine
- Workflows are defined in `workflows.json`.
- Triggered via voice command `run workflow <name>` or programmatically.
- UI shows progress in the **Automation** tab.

## Voice System
- `voice_engine.py` handles audio capture, level visualisation, and wake‑word detection.
- `tts_worker.py` generates speech using the selected voice (Azure, Google, etc.).

## Dashboard Overview
- Tabbed layout: **Chat**, **Voice**, **System**, **Automation**, **Memory**.
- Real‑time CPU/Memory gauges, model/voice/workflow status.
- HUD circle reflects current processing state.

## Current Limitations
- Limited natural‑language command coverage; only predefined intents are supported.
- No multi‑language support – English only.
- Speech synthesis quality depends on external TTS service.
- Requires a working microphone and speaker.
- Workflow engine currently supports only linear step execution.

## Future Roadmap
- Expand intent parser for richer command set.
- Add multi‑language support.
- Implement plug‑in architecture for third‑party tools.
- Provide unit‑test suite and CI pipeline.
- Refine UI/UX with dark‑mode theming and accessibility options.

## License
This project is licensed under the **MIT License**.

## Author
**Deepak Rajan Morje** – Creator and maintainer.
