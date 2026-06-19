# Capability Report

## AI Features
- **LLM Integration** – Primary inference via local Ollama model (`qwen2.5-coder`). Falls back to Gemini cloud API when Ollama is unavailable.
- **Contextual Memory Injection** – Facts stored in SQLite are automatically injected into system prompts for richer responses.
- **Tool‑Block Execution** – JSON blocks returned by the LLM are parsed and executed (launch app, open URL, trigger workflow).

## Voice Features
- **Continuous Speech Capture** – Microphone input is streamed to the Intent Analyzer.
- **Text‑to‑Speech** – `voice/tts_worker.py` uses `edge‑tts` (or configured provider) to synthesize responses.
- **Voice Queue Management** – Responses are queued to avoid overlap; playback state is reflected in the HUD.

## Memory Features
- **SQLite Persistence** – All conversations, facts, and categorized memories are stored in `friday_memory.db`.
- **Automatic Categorization** – Heuristic keyword‑based categorisation into Personal, Project, Preference, Goal, Task, General.
- **Memory‑Update HUD State** – HUD circle shows *Memory Update* whenever a fact is learned or deleted.

## Workflow Features
- **Declarative JSON Workflows** – Defined in `workflows.json`; steps include speak, launch_app, wait, open_url, webhook.
- **Workflow Engine** – `automation/workflow_engine.py` executes steps sequentially and emits UI signals.

## Automation Features
- **App Launcher** – `automation/app_launcher.py` abstracts Windows program launching.
- **Browser Controller** – `automation/browser_controller.py` handles opening URLs.
- **Webhook Execution** – Supports HTTP POST calls for external automation (n8n integration).

## Dashboard Features
- **Dynamic HUD Circle** – Visualises system states: Idle, Listening, Thinking, Speaking, Workflow, Memory Update.
- **Tabbed Interface** – Chat, Voice diagnostics, System metrics, Automation, Memory browser.
- **Real‑time Telemetry** – CPU & RAM usage displayed via `psutil`.

## System Monitoring Features
- **Performance Metrics** – Collected by `psutil` and displayed on the Dashboard.
- **Signal‑Slot Health Checks** – All core connections verified during stability audit.

## Supported Commands
(See `docs/COMMANDS.md` for full details and examples.)

## Current Limitations
- Windows‑only support – uses Windows‑specific shortcuts for app launching.
- Wake‑word detection is simple keyword matching; may miss variations.
- No offline speech‑to‑text; relies on external STT services.
- Limited intent set – only commands explicitly defined in `IntentAnalyzer` are recognised.
- No multi‑language UI or voice support.
- Workflow engine executes linear steps; no branching or conditional logic.
