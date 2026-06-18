# Capability Report – FRIDAY AI Operating System

Below is a **complete overview** of everything FRIDAY can do today, how to invoke each feature, and concrete example commands you can type into the FRIDAY UI or the console.  The report is organized exactly as requested.

---

## 1. Core AI Capabilities

| What it does | How to use it | Example command |
|--------------|---------------|-----------------|
| **Natural‑language understanding & reasoning** using a multi‑LLM stack (Gemini REST API *or* local Ollama models) | • Set the desired model in `config.py` (`GEMINI_MODEL` or `DEFAULT_OLLAMA_MODEL`). <br>• Send any textual prompt to the Brain via the UI input box or the `process()` method. | `What is the capital of Norway?` |
| **Prompt templating & context management** – the Brain stores the last N exchanges (default 10) and feeds them back to the LLM for continuity. | No extra syntax required; just continue the conversation. | `Remind me of the last three things we discussed.` |
| **Tool‑calling style orchestration** – the Brain can decide to invoke a local command, a workflow, or a web shortcut based on the LLM’s response. | Handled automatically; you only need to phrase the request. | `Open my calendar for tomorrow.` |

---

## 2. Voice Features

| What it does | How to use it | Example command |
|--------------|---------------|-----------------|
| **Edge‑TTS speech synthesis** (default voice `en‑US‑JennyNeural`) – non‑blocking, queue‑based, uses `QMediaPlayer`. | • Anything the Brain replies with is automatically spoken. <br>• The **TEST VOICE** button in the *Voice* panel enqueues three diagnostic messages. | Press **TEST VOICE** → hears “Voice diagnostic one”, “two”, “three”. |
| **Voice Provider abstraction** – can be swapped to `DisabledProvider` (no audio) or extended to ElevenLabs later. | Change the provider via `config.VOICE_PROVIDER = "disabled"` or `"edge"` | `# In config.py` <br>`VOICE_PROVIDER = "disabled"` |
| **Diagnostics logging** – logs every stage (`Received text`, `Generating audio`, `Playback started`, `Playback completed`, `Queue size`). | View `friday_system.log` or the diagnostics panel. | (no explicit command) |

---

## 3. Memory Features

| What it does | How to use it | Example command |
|--------------|---------------|-----------------|
| **Persistent SQLite memory store** (`memory/friday_memory.db`). Stores facts, embeddings, and context for later recall. | Use the `memory` API (`store_fact`, `retrieve_fact`). The Brain automatically writes important facts (e.g., “User asked about weather”). | `Remember that my favorite coffee is latte.` |
| **Memory retrieval** – the LLM can query the DB when needed (e.g., “What did I tell you about my coffee?”). | Same as normal chat – the LLM decides when to query. | `What coffee do I like?` |
| **Memory cleanup** – a CLI helper (`python -m memory.clean`) removes old entries. | Run from terminal. | `python -m memory.clean --keep 30` |

---

## 4. Automation Features

| What it does | How to use it | Example command |
|--------------|---------------|-----------------|
| **Workflow engine** (`automation/workflow_engine.py`) – executes a series of pre‑defined steps (run a script, speak a message, wait, open a URL, etc.). | Invoke a workflow by name via the UI or `run workflow <name>`. Workflows are defined in `workflows.json`. | `run workflow daily‑briefing` |
| **Dynamic variable injection** – workflows can accept parameters (`{{param}}`). | Pass parameters after the workflow name. | `run workflow send‑email recipient=alice@example.com subject="Report"` |
| **Error handling & retry** – each step returns a success flag; the engine can abort or continue based on `continue_on_error`. | Handled internally. | (no explicit command) |

---

## 5. Workflow Features

| Workflow name (example) | Description | Typical steps |
|--------------------------|-------------|---------------|
| **daily‑briefing** | Gives a quick morning summary (weather, calendar, news). | 1️⃣ Query weather API → 2️⃣ Speak result → 3️⃣ Open calendar URL → 4️⃣ Speak completion. |
| **launch‑dev‑env** | Starts a development environment (VS Code, terminal, browser). | 1️⃣ Open VS Code → 2️⃣ Open terminal → 3️⃣ Launch local web server → 4️⃣ Speak “All set”. |
| **system‑report** | Collects CPU/memory stats and reads them aloud. | 1️⃣ Run `psutil` checks → 2️⃣ Speak summary → 3️⃣ Log to file. |

*You can add new workflows by editing `workflows.json` and implementing any custom Python step class.*

---

## 6. Application Control Features

| What it does | How to use it | Example command |
|--------------|---------------|-----------------|
| **App registry** – maps friendly names to executable paths (`chrome`, `vs code`, `notepad`, `calculator`, `explorer`, `cmd`). | Type `open <app>` in the chat box. The Brain resolves the name via `APP_REGISTRY` and launches it. | `open chrome` |
| **Web shortcuts** – maps names to URLs (`youtube`, `google`, `github`, `gmail`). | Type `go to <shortcut>` or simply the shortcut name. | `go to youtube` |
| **Shell command execution** – the `cmd` shortcut opens a PowerShell/Command Prompt window. | `open cmd` |
| **File explorer navigation** – `explorer` opens Windows Explorer at the current project root. | `open explorer` |

---

## 7. Browser Control Features

| What it does | How to use it | Example command |
|--------------|---------------|-----------------|
| **Open a URL** – via the web shortcuts or by specifying a full URL. | `open https://news.ycombinator.com` or `go to github`. | `open https://github.com/deepak06012229/FRIDAY-AI-OS` |
| **Search the web** – FRIDAY can forward a query to the default search provider (Google). | `search for best Python async tutorials`. | `search for “asyncio best practices”` |
| **Read web content** – (future feature, currently stubbed). | *Not yet implemented* – placeholder for future improvements. | — |

---

## 8. System Monitoring Features

| What it does | How to use it | Example command |
|--------------|---------------|-----------------|
| **Real‑time logs** – `friday_system.log` captures all voice, LLM, and command activity. | Open the log file or view the diagnostics panel. | (no command) |
| **CPU / Memory snapshot** – part of the *system‑report* workflow. | `run workflow system‑report` |
| **Worker status** – the UI shows `TTSWorker.is_running` and queue size. | Click the *Voice* panel or query: `what is the voice queue size?` | `what is the voice queue size` |
| **Health‑check endpoint** – (planned) a tiny HTTP server exposing `/health`. | *Future* | — |

---

## 9. Dashboard Features

| What it does | How to use it |
|--------------|---------------|
| **Main Dashboard (`ui/dashboard.py`)** – central hub with a text input, status indicators, and a circular “HUD” that shows FRIDAY’s current state (Idle, Listening, Speaking). | Launch via `python main.py`. |
| **Voice Panel** – includes the **TEST VOICE** button, queue size display, and worker status. | Click the button or watch the panel. |
| **Memory Panel** – visualizes stored facts (future UI). | *Present in code but not yet populated.* |
| **Workflow Panel** – lists available workflows and lets you trigger them with a click. | Click a workflow entry. |
| **Settings Dialog** – allows runtime changes to `VOICE_DEFAULT`, `VOICE_PROVIDER`, and LLM selection. | Open via the gear icon. |

---

## 10. Local LLM Features

| What it does | How to use it |
|--------------|---------------|
| **Ollama integration** – runs any local Ollama model (e.g., `llama3`, `phi3`). | Set `DEFAULT_OLLAMA_MODEL` in `config.py`. FRIDAY automatically falls back to Ollama if the Gemini API key is missing. |
| **Gemini REST API** – uses the Google Gemini model (default `gemini‑2.5‑flash`). | Export `GEMINI_API_KEY` in your environment or `.env`. |
| **Model switching at runtime** – via the Settings dialog or by editing `config.py`. | Change `config.GEMINI_MODEL` or `config.DEFAULT_OLLAMA_MODEL`. |

---

## 11. Available Commands

| Command | Description | Example |
|---------|-------------|---------|
| `open <app>` | Launch a registered desktop application. | `open notepad` |
| `go to <shortcut>` | Open a predefined website. | `go to github` |
| `search for <query>` | Perform a Google search in the default browser. | `search for “latest AI news”` |
| `run workflow <name> [param=value …]` | Execute a custom workflow defined in `workflows.json`. | `run workflow daily‑briefing` |
| `what is the voice queue size` | Returns the number of pending utterances in the TTS queue. | — |
| `test voice` | Triggers the built‑in diagnostic voice sequence. | (press button or type) |
| `set voice <provider>` | Switches the voice provider (`edge`, `disabled`). | `set voice disabled` |
| `set model <gemini|ollama>` | Switches LLM backend at runtime. | `set model ollama` |
| `list workflows` | Shows all available workflow names. | — |
| `list apps` | Shows the content of the `APP_REGISTRY`. | — |
| `list shortcuts` | Shows the web shortcuts. | — |
| `clear memory` | Purges the SQLite memory DB. | `clear memory` |
| `show log` | Opens `logs/friday_system.log` in the default editor. | `show log` |
| `help` | Show a quick help list of commands. | `help` |

*All commands are case‑insensitive and can be typed into the main text input box.*

---

## 12. Available Workflows

| Workflow | Brief purpose | How to invoke |
|----------|---------------|---------------|
| `daily‑briefing` | Summarizes weather, calendar, and top news. | `run workflow daily‑briefing` |
| `launch‑dev‑env` | Opens VS Code, a terminal, and starts a local server. | `run workflow launch‑dev‑env` |
| `system‑report` | Gathers CPU/memory stats and speaks them aloud. | `run workflow system‑report` |
| `send‑email` *(example placeholder)* | Sends an email via SMTP (requires credentials). | `run workflow send‑email recipient=alice@example.com subject="Report"` |
| `custom‑script` *(user‑defined)* | Executes any shell script defined in the workflow JSON. | `run workflow custom‑script script=backup.bat` |

*Add new workflows by editing `workflows.json` and adding a Python step class if needed.*

---

## 13. Limitations

| Limitation | Impact |
|------------|--------|
| **No native ElevenLabs integration** – only Edge‑TTS is available now. | Users cannot access ElevenLabs voices without custom coding. |
| **Browser automation limited to opening URLs** – no DOM interaction or form filling. | Advanced web‑scraping or UI automation must be added separately. |
| **Memory retrieval is implicit** – no explicit “search memory” command (the LLM decides). | Users cannot directly query the SQLite store without a custom prompt. |
| **No built‑in scheduling** – recurring tasks must be launched manually or via external cron. | Periodic reminders or automated runs need external tooling. |
| **Single‑language (English) voice** – voice provider defaults to English neural voices. | Non‑English speech requires additional voice selection logic. |
| **No multi‑user profile support** – configuration is global. | Cannot maintain separate settings per user. |
| **Limited error feedback in UI** – most errors are logged, not shown to the user. | End‑users may be unaware of why a command failed. |

---

## 14. Missing Features (Opportunities)

| Desired Feature | Why it matters |
|----------------|----------------|
| **ElevenLabs voice provider** – high‑quality, multilingual voices. |
| **Browser automation sub‑agent** – click, type, capture screenshots. |
| **Scheduler / Cron integration** – run workflows at specific times. |
| **Explicit memory query command** – e.g., `recall <keyword>`. |
| **Multi‑user profile & per‑user config** – useful for shared PCs. |
| **Real‑time transcription UI** – visual feedback while speaking. |
| **Plug‑in marketplace** – discoverable third‑party skills. |
| **Unit‑test coverage dashboard** – display test status on the UI. |
| **OAuth for Google APIs** – secure access to calendar, Gmail, etc. |
| **Docker container** – one‑click deployment for CI/CD or demos. |

---

## 15. Recommended Next Upgrades

1. **Add ElevenLabsProvider** – implement a new `VoiceProvider` subclass, expose a `voice` dropdown, and update `config.VOICE_OPTIONS`.  
2. **Integrate a lightweight browser sub‑agent** (e.g., using `playwright` or the existing `browser_subagent` tool) to enable click/typing automation.  
3. **Introduce a Scheduler service** (`schedule` module) that can run any workflow on a cron expression. Add a UI panel for managing schedules.  
4. **Expose a `recall <keyword>` command** that runs a simple SQL `LIKE` query against the memory DB and returns matches.  
5. **Improve UI error reporting** – surface `error_occurred` signals from `TTSWorker` and LLM failures as toast notifications.  
6. **Add multi‑user configuration** – store per‑user JSON files under `profiles/`.  
7. **Write comprehensive unit tests** for the workflow engine, voice provider abstraction, and command dispatcher; display the coverage badge in the README.

---

# 📖 Commander Operations Manual

> **All commands are typed in the main FRIDAY input box (or executed via the console if you prefer). Commands are case‑insensitive.**

| Command | Description | Syntax |
|---------|-------------|--------|
| **open** | Launch a desktop application from the built‑in registry. | `open <app_name>` |
| **go to** | Open a predefined web shortcut. | `go to <shortcut>` |
| **search for** | Perform a Google search for the given query. | `search for <search_terms>` |
| **run workflow** | Execute a workflow defined in `workflows.json`. Optional `key=value` parameters may follow. | `run workflow <workflow_name> [param1=val1 param2=val2 …]` |
| **list workflows** | Show all available workflow names. | `list workflows` |
| **list apps** | Show the application registry (executable paths). | `list apps` |
| **list shortcuts** | Show the web shortcut registry. | `list shortcuts` |
| **what is the voice queue size** | Returns the number of pending utterances in the TTS queue. | `what is the voice queue size` |
| **test voice** | Triggers the diagnostic voice sequence (“Voice diagnostic one / two / three”). | `test voice` (or click the **TEST VOICE** button) |
| **set voice** | Switch the voice provider (`edge` or `disabled`). | `set voice <edge|disabled>` |
| **set model** | Switch the LLM backend (`gemini` or `ollama`). | `set model <gemini|ollama>` |
| **clear memory** | Purge all stored facts from `friday_memory.db`. | `clear memory` |
| **show log** | Open `logs/friday_system.log` in the default editor. | `show log` |
| **help** | Show a quick help list of commands. | `help` |

### Quick‑start cheat‑sheet

```
open chrome                     # launch Chrome
go to youtube                   # open YouTube
search for “asyncio tutorial”  # Google search
run workflow daily‑briefing     # run the morning briefing workflow
test voice                      # run voice diagnostics
set voice disabled              # mute speech output
set model ollama                # switch to local LLM
list workflows                  # see what workflows exist
clear memory                    # wipe all saved facts
show log                        # open the log file
```
