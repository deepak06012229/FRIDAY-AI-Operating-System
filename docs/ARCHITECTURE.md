# Architecture Overview – FRIDAY AI Operating System

This document provides a high‑level view of the main subsystems that compose FRIDAY and how they interact.

---

## 1. Dashboard (UI Layer)

- **Location**: `ui/dashboard.py` and the various `ui/panels/*` modules.
- **Purpose**: Central hub for user interaction. Provides a text input, status HUD, and panels for voice diagnostics, workflow management, and settings.
- **Key Features**:
  - Circular HUD visualising FRIDAY states (Idle, Listening, Speaking).
  - Voice panel with **TEST VOICE** button and queue size display.
  - Workflow panel that lists available workflows for one‑click execution.
  - Settings dialog allowing runtime changes to voice provider, default voice, and LLM selection.

---

## 2. Brain (Core Logic)

- **Location**: `brain/` (not shown in the repo tree but conceptually present).
- **Purpose**: Orchestrates conversation flow, maintains context, decides when to invoke tools, workflows, or external services.
- **Responsibilities**:
  - Prompt templating and context window management.
  - Dispatching `speak_requested` signals to the **Voice System**.
  - Interpreting LLM responses to trigger commands, workflows, or web shortcuts.

---

## 3. Ollama Integration (Local LLM)

- **Location**: `ai/ollama_provider.py`.
- **Purpose**: Provides a thin wrapper around a locally‑running Ollama server (`http://localhost:11434`).
- **Usage**:
  - Configured via `config.DEFAULT_OLLAMA_MODEL`.
  - Automatically selected when `GEMINI_API_KEY` is absent or when the user explicitly chooses the "ollama" model in the Settings dialog.

---

## 4. Gemini Integration (Cloud LLM)

- **Location**: `ai/gemini_provider.py` (or similar). Uses the REST endpoint defined in `config.GEMINI_REST_URL`.
- **Purpose**: Gives access to Google Gemini models (default `gemini‑2.5‑flash`).
- **Authentication**: Requires `GEMINI_API_KEY` exported in the environment or placed in a `.env` file.
- **Switching**: Users can toggle between Gemini and Ollama at runtime via the Settings dialog (`set model gemini|ollama`).

---

## 5. Memory System

- **Location**: `memory/` (SQLite DB at `memory/friday_memory.db`).
- **Purpose**: Persistent storage of facts, embeddings, and any data the Brain wants to remember across sessions.
- **API**: `memory.store_fact(text)`, `memory.retrieve_fact(query)` – used internally by the Brain and can be extended for external plugins.
- **Maintenance**: CLI helper `python -m memory.clean` removes stale entries.

---

## 6. Voice System

- **Location**: `voice/tts_worker.py` and `voice/device_manager.py`.
- **Core Component**: `TTSWorker` (subclass of `QThread`).
- **Architecture**:
  1. UI emits `speak_requested` with text.
  2. `TTSWorker` enqueues the text in a thread‑safe `queue.Queue`.
  3. The worker uses a **VoiceProvider** abstraction – default is `EdgeTTSProvider` (Edge‑TTS library).
  4. Audio is generated to a temporary MP3 file (`tempfile.gettempdir()`) and played via `QMediaPlayer`.
  5. Signals (`speaking_started`, `speaking_finished`, `error_occurred`, `queue_size_changed`) keep the UI in sync.
- **Extensibility**: New providers (e.g., ElevenLabs) can be added by implementing the `VoiceProvider` abstract base class.

---

## 7. Workflow Engine (Automation Layer)

- **Location**: `automation/workflow_engine.py` and the JSON descriptor `workflows.json`.
- **Purpose**: Define reusable, parameterisable sequences of actions (open apps, speak text, wait, call APIs).
- **Execution**:
  - Workflows are triggered via the UI or `run workflow <name>` command.
  - Steps may be built‑in (open app, speak, delay) or custom Python classes.
  - Supports variable injection (`{{param}}`) and conditional error handling (`continue_on_error`).
- **User Extensibility**: Add new workflow definitions in `workflows.json` and, if needed, implement a new step class in `automation/steps/`.

---

## 8. Automation Layer (App & Web Shortcuts)

- **App Registry** – defined in `config.APP_REGISTRY`; maps friendly names to executable paths for Windows.
- **Web Shortcut Registry** – defined in `config.WEB_REGISTRY`; maps short names to URLs.
- **Command Dispatcher** – parses `open <app>` and `go to <shortcut>` commands, resolves the registry entry, and executes the appropriate system call (`subprocess.Popen` for apps, `QDesktopServices.openUrl` for URLs).

---

## Interaction Flow Example

```
User types: "open chrome"
→ Dashboard sends signal → Brain parses command → Dispatcher looks up APP_REGISTRY → subprocess.Popen launches Chrome → Brain replies "Chrome opened" → UI displays text and Voice System reads the reply.
```

---

**This architecture is deliberately modular so that new AI providers, voice engines, or automation steps can be plugged in with minimal changes to existing code.**
