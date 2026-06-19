# Architecture Overview

## System Overview

```
User Input → Intent Analyzer → FRIDAY Brain → Memory Manager → Ollama / Gemini Provider → Workflow Engine → Voice Engine → Dashboard
```

The FRIDAY AI Operating System is built around a **Qt‑based event‑driven core** (`FRIDAYBrain`) that coordinates the various subsystems via **PyQt signal/slot** connections.

### Modules & Responsibilities

| Module | Path | Primary Responsibility |
|--------|------|------------------------|
| **User Input** | `main.py` (Qt widgets) | Captures voice or typed commands and forwards them to the Intent Analyzer. |
| **Intent Analyzer** | `ai/intent_analyzer.py` | Parses natural‑language queries into structured intents (e.g., `launch_app`, `open_url`, `learn_fact`). |
| **FRIDAY Brain** | `ai/brain.py` | Central orchestrator: manages memory, selects AI provider, runs local intents, emits signals for UI and other engines. |
| **Memory Manager** | `memory/memory_manager.py` | SQLite‑backed storage of conversations, facts, and categorized memories (Personal, Project, Preference, Goal, Task). |
| **Ollama / Gemini Provider** | `ai/ollama_provider.py` & `ai/llm_client.py` | Generates LLM responses; Ollama is primary, Gemini fallback. |
| **Workflow Engine** | `automation/workflow_engine.py` | Executes declarative JSON workflows defined in `workflows.json`. |
| **Voice Engine** | `voice/tts_worker.py` (and related helpers) | Text‑to‑speech synthesis, playback queue, and voice selection. |
| **Dashboard** | `ui/dashboard.py` & UI widgets | Visual front‑end: chat panel, HUD circle, system metrics, automation panel, memory browser. |

### Data Flow
1. **Input** → Intent Analyzer parses command.
2. **Local Intent** → Brain executes immediate actions (launch app, open URL, memory ops, workflow trigger).
3. **Non‑local** → Brain calls Ollama; on failure falls back to Gemini.
4. **Response** → Brain cleans JSON blocks, emits `speak_requested` and `response_completed` signals.
5. **Memory Update** → Facts are stored, `memory_updated` signal notifies UI.
6. **Workflow** → Triggered via `workflow_trigger` signal; Engine runs steps (speak, launch_app, wait, open_url, webhook).
7. **Voice** → TTS worker reads cleaned response.
8. **Dashboard** → HUD circle reflects current state (Idle, Listening, Thinking, Speaking, Workflow, Memory Update). 

## Project Folder Structure
```
├─ ai/                     # Core AI components (brain, intent_analyzer, providers)
├─ automation/            # Workflow engine and app launcher utilities
├─ memory/                # SQLite DB wrapper and memory categorization
├─ ui/                    # Qt UI components (dashboard, widgets, HUD)
├─ voice/                 # Text‑to‑speech worker and queue handling
├─ docs/                  # Documentation (this folder)
├─ assets/                # Images, screenshots used in README
├─ configs/ (config.py)   # Global configuration constants
├─ main.py                # Application entry point, wiring of components
├─ requirements.txt       # Python dependencies
├─ workflows.json        # Declarative workflow definitions
└─ README.md             # Project overview (already created)
```
