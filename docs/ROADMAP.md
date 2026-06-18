# Roadmap – FRIDAY AI Operating System

## Current Version
- **Version 1.0** – Initial release with core AI, voice (Edge‑TTS), workflow engine, and basic automation.

---

## Planned Features (next 3‑6 months)

| Feature | Description | Benefit |
|---------|-------------|--------|
| **ElevenLabs Voice Provider** | Add a new `VoiceProvider` subclass for ElevenLabs API. | High‑quality, multilingual voices; richer user experience. |
| **Scheduler / Cron Integration** | Introduce a `schedule` module to run workflows on cron expressions or one‑off timers. | Enables periodic reminders, nightly builds, automated reports. |
| **Explicit Memory Query (`recall`)** | Command that performs a `LIKE` search on the SQLite memory DB and returns matching facts. | Gives users direct access to stored knowledge. |
| **Multi‑User Profiles** | Store per‑user configuration files under `profiles/`. | Allows shared machines with separate settings. |
| **Browser Sub‑Agent** | Integrate `playwright`‑based automation to click, type, and capture screenshots. | Moves FRIDAY beyond opening URLs to full web‑app interaction. |
| **OAuth for Google Services** | Securely connect to Calendar, Gmail, Drive via OAuth. | Enables calendar scheduling and email automation. |
| **Docker Container** | Provide a `Dockerfile` for one‑click deployment and CI testing. | Simplifies onboarding for contributors and CI pipelines. |
| **Unit‑Test Coverage Dashboard** | Show test coverage badge in README and a UI panel summarising pass/fail status. | Improves code quality visibility. |

---

## Future AI Features (6‑12 months)

- **Hybrid Retrieval‑Augmented Generation (RAG)** – Index local documents with vector embeddings and retrieve relevant chunks for LLM prompts.
- **Tool‑Calling Extensions** – Allow the LLM to invoke custom Python functions (e.g., `get_weather()`, `create_issue()`).
- **Self‑Supervised Fine‑Tuning** – Provide a simple script to fine‑tune an Ollama model on user‑specific data.

---

## Robotics Integration Goals

| Goal | Description |
|------|-------------|
| **Serial Communication** | Add a `robotics/serial_bridge.py` module to send/receive commands over USB/Serial to Arduino/ESP devices. |
| **Voice‑Controlled Robot Actions** | Map voice commands (e.g., "move arm up") to robot actuation via the serial bridge. |
| **Sensor Feedback Loop** | Ingest sensor data (temperature, distance) and expose it to the Brain for context‑aware decisions. |

---

## Browser Automation Goals

| Goal | Description |
|------|-------------|
| **Full Page Interaction** | Using `playwright`, enable clicks, form filling, and screenshot capture based on natural‑language instructions. |
| **Headless Mode for CI** | Run browser automation headlessly for testing workflows without a UI. |
| **Visual Debugging** | Export a short video of the automated session for the diagnostics panel. |

---

*The roadmap is deliberately flexible; community contributions may reprioritise items based on interest and impact.*
