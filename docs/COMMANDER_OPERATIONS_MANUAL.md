# Chief Operations Manual – FRIDAY AI Operating System

## Introduction

This manual guides **Chief** through operating the FRIDAY AI Operating System. All commands are case‑insensitive and can be entered via the text box on the Dashboard or spoken using the microphone.

## System Startup

1. Launch the application with `python main.py`.
2. The Dashboard appears with the HUD circle indicating **Idle**.
3. Ensure the microphone is enabled; FRIDAY will listen for the wake‑word *“Hey Friday”* (configurable).

## Voice Commands

| Command | Description | Example |
|---------|-------------|---------|
| `test voice` | Run built‑in voice diagnostics (three spoken phrases). | `test voice` |
| `set voice <provider>` | Switch TTS provider (`edge` or `disabled`). | `set voice disabled` |
| `set model <gemini|ollama>` | Change the active LLM backend. | `set model ollama` |
| `what is the voice queue size` | Returns the number of pending utterances. | `what is the voice queue size` |
| `shutdown` (or `exit`, `quit`) | Terminates FRIDAY gracefully. | `shutdown` |

## Memory Commands

| Command | Description | Example |
|---------|-------------|---------|
| `remember that <fact> as <category>` | Save a fact to a specific category (`personal`, `project`, `preference`, `goal`, `task`). | `remember that I prefer dark mode as preference` |
| `remember that <fact>` | Save a fact to the default `general` category. | `remember that the deadline is Friday` |
| `show <category>` | List all facts in a category (`personal`, `project`, `preference`, `goal`, `task`). | `show goals` |
| `what do you know about me` | Retrieve all stored facts. | `what do you know about me` |
| `clear memory` | Purge all facts from the SQLite memory store. | `clear memory` |
| `forget <fact>` | Delete a specific fact. | `forget the deadline is Friday` |

## Workflow Commands

| Command | Description | Example |
|---------|-------------|---------|
| `run workflow <name> [param=value …]` | Execute a JSON‑defined workflow. Optional parameters are injected into the workflow. | `run workflow morning workspace` |
| `list workflows` | Display all available workflow names. | `list workflows` |
| `list apps` | Show the application registry mapping. | `list apps` |
| `list shortcuts` | Show the web shortcut registry. | `list shortcuts` |

## Browser Commands

| Command | Description | Example |
|---------|-------------|---------|
| `go to <shortcut>` | Open a predefined web shortcut (`youtube`, `github`, `gmail`, `google`). | `go to github` |
| `search for <query>` | Perform a Google search for the given query. | `search for "latest AI news"` |

## Application Commands

| Command | Description | Example |
|---------|-------------|---------|
| `open <app>` | Launch a registered desktop application (`chrome`, `notepad`, `calculator`, `cmd`, `explorer`). | `open chrome` |
| `list apps` | List all available applications. | `list apps` |

## Troubleshooting

- **No response** – Verify the microphone is not muted and the HUD shows *Listening*.
- **Incorrect command** – Re‑phrase using the exact wording from the tables above.
- **Workflow hangs** – Open the *Automation* tab to view progress; cancel with the *Stop* button.
- **Memory not updating** – Ensure the HUD displays *Memory Update* after a `remember` or `forget` command.

## Best Practices

- Use specific phrasing from the command tables to improve recognition reliability.
- Group related actions into a single workflow to reduce UI interaction.
- Periodically run `clear memory` to keep the SQLite store tidy.
- Monitor the HUD circle for state feedback; unexpected colours may indicate an error.

---

*All commands listed are verified against the current codebase; no unimplemented functionality is included.*
