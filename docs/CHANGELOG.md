# Changelog – FRIDAY AI Operating System

## v1.0 – Stable Release (2026‑06‑18)

### Added
- Ollama integration for local LLM inference.
- Persistent SQLite memory system with automatic categorisation.
- Declarative JSON workflow engine.
- Voice interaction pipeline (Edge‑TTS with queue management).
- Dashboard telemetry (CPU/RAM metrics, HUD circle with dynamic states).
- Chief‑style personalization (all responses address the user as **Chief**).
- Memory categorisation (Personal, Project, Preference, Goal, Task).

### Improved
- Voice queue stability – eliminated dead‑locks and dropped frames.
- Workflow execution reliability and progress reporting.
- Signal‑slot connections across Brain, Dashboard, Voice, and Memory modules.
- Dashboard synchronization for real‑time HUD and metric updates.
- Memory retrieval speed and consistency.

### Fixed
- Broken pipeline connections between Brain and Voice Engine.
- Voice playback failures and intermittent audio glitches.
- Dashboard metric errors caused by stale `psutil` data.
- Memory recall failures after database restarts.
- Branding inconsistencies (logo, colour palette) across UI components.

---

*All entries follow the Keep a Changelog format and reflect verified functionality in the repository.*
