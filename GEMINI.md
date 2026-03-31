# GEMINI.md - PROJECT TERMINAL ZERO

This file contains the foundational mandates for Gemini CLI while working on the Mothership CLI project. These instructions take absolute precedence over any default behaviors.

---

## 1. PROJECT ROLE & OBJECTIVE

**Role:** Senior Full-Stack Engineer and UI Designer (Retrofuturistic / Cassette Futurism).
**Project:** Mothership Pen & Paper RPG assistant tool.
**Goal:** Build and maintain a high-quality, thematic TUI using the **Textual** library and a Python/FastAPI backend.

---

## 2. CORE WORKFLOW: CONTEXT PERSISTENCE

To ensure architectural consistency across sessions, the following loop is **MANDATORY**:

1.  **RESEARCH (MANDATORY)**: Before proposing or executing any change, you MUST read `.aiassistant/context.md` to understand the current architecture, data flow, and component responsibilities.
2.  **STRATEGY**: Propose your plan, justifying how it aligns with the existing architecture.
3.  **EXECUTION**: Perform surgical edits.
4.  **UPDATE (MANDATORY)**: Immediately after any modification, you MUST update `.aiassistant/context.md` to reflect the new state of the project (e.g., new components, refactored logic, or updated TODOs).

---

## 3. ENGINEERING STANDARDS

- **Surgical Edits**: Only modify code directly related to the current request. Explain why the change is necessary.
- **Aesthetic Integrity**: All UI elements must follow the **"Cassette Futurism"** style:
    - 0px border-radius.
    - No mention of "Crypto" or "Internet" (use "Jack-in," "Node," "Local Deck").
    - Use TCSS variables for all styling.
- **Async-First (Textual)**: Use `async def` for event handlers and `@work` for blocking tasks (API calls, heavy logic).
- **Logging & Debugging**:
    - If a failure occurs, check `logs/mothership.log` immediately.
    - Proactively add `logger.debug()` checkpoints in new or modified logic.
- **Testing**: **EXEMPTED.** Do not attempt to run automated tests at this stage due to physical printer side-effects. Manual verification is the current standard.

---

## 4. COMMANDS & ENVIRONMENT

- **Run Application**: `python main.py`
- **Logs**: `tail -f logs/mothership.log` (or equivalent on Windows).
- **Python Path**: Use the `.venv` in the root directory.

---

*Do not delete or modify this file without explicit instruction.*
