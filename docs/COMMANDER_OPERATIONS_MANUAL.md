# Commander Operations Manual – FRIDAY AI Operating System

All commands are case‑insensitive and can be entered in the main FRIDAY text input box (or via the console for debugging).  The UI also provides buttons for the most common actions.

---

## Core Commands

| Command | Description | Example |
|---------|-------------|---------|
| `open <app>` | Launch a registered desktop application (e.g., `chrome`, `notepad`, `calculator`). | `open chrome` |
| `go to <shortcut>` | Open a predefined web shortcut (`youtube`, `github`, `gmail`). | `go to github` |
| `search for <query>` | Perform a Google search in the default browser. | `search for "latest AI news"` |
| `run workflow <name> [param=value …]` | Execute a workflow defined in `workflows.json`. Parameters are optional and injected as `{{param}}` placeholders. | `run workflow daily‑briefing` |
| `list workflows` | Show all workflow names available in the system. | `list workflows` |
| `list apps` | Display the `APP_REGISTRY` mapping. | `list apps` |
| `list shortcuts` | Display the web shortcut registry. | `list shortcuts` |
| `what is the voice queue size` | Return the current number of pending utterances in the TTS queue. | `what is the voice queue size` |
| `test voice` | Run the built‑in voice diagnostics (three spoken phrases). | `test voice` (or click the **TEST VOICE** button) |
| `set voice <provider>` | Switch the voice provider at runtime (`edge` or `disabled`). | `set voice disabled` |
| `set model <gemini|ollama>` | Switch the LLM backend at runtime. | `set model ollama` |
| `clear memory` | Purge all facts from the SQLite memory database. | `clear memory` |
| `show log` | Open `logs/friday_system.log` in the default editor. | `show log` |
| `help` | Show this quick‑help overview. | `help` |

---

## Quick‑Start Cheat Sheet

```
open chrome                     # launch Chrome
go to youtube                   # open YouTube
search for "asyncio tutorial"  # Google search
run workflow daily‑briefing     # morning briefing workflow
test voice                      # run voice diagnostics
set voice disabled              # mute speech output
set model ollama                # use local Ollama model
list workflows                  # list all workflows
clear memory                    # wipe stored facts
show log                        # view the log file
```

---

### Advanced Usage

- **Workflow parameters** – supply `key=value` pairs after the workflow name to customise execution, e.g., `run workflow send‑email recipient=alice@example.com subject="Report"`.
- **Scheduling (future)** – a future `schedule` command will allow cron‑style periodic workflow execution.
- **Memory recall (future)** – `recall <keyword>` will query the memory store directly.

Use the above commands to interact with FRIDAY, automate tasks, and explore the AI‑driven capabilities of the system.
