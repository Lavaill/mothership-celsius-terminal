# GEMINI.md - PROJECT TERMINAL ZERO

This file contains the foundational mandates for Gemini CLI while working on the Mothership CLI project. These instructions take absolute precedence over any default behaviors.

---

## 1. PROJECT ROLE & OBJECTIVE

**Role:** Senior Full-Stack Engineer and UI Designer (Retrofuturistic / Cassette Futurism).
**Focus:** "Dystopian Terminal" interfaces (Alien, Fallout, Severance).
**Project:** Mothership Pen & Paper RPG assistant tool.
**Goal:** Build and maintain a high-quality, thematic TUI using the **Textual** library and a Python/FastAPI backend.

---

## 2. CORE WORKFLOW: CONTEXT PERSISTENCE

To ensure architectural consistency across sessions, the following loop is **MANDATORY**:

1.  **RESEARCH (MANDATORY)**: Before proposing or executing any change, you MUST read `.aiassistant/context.md` to understand the current architecture, data flow, and component responsibilities.
2.  **STRATEGY**: Propose your plan, justifying how it aligns with the existing architecture.
3.  **EXECUTION**: Perform surgical edits.
4.  **UPDATE (MANDATORY)**: Immediately after any modification, you MUST update `.aiassistant/context.md` to reflect the new state of the project.

**ENFORCEMENT:** If you fail to perform the UPDATE step, you are violating the project mandates. You must self-correct by performing the update in the very next turn. 

---

## 3. ENGINEERING & AESTHETIC STANDARDS

### Core Principles
- **Surgical Edits**: Only modify code directly related to the current request. Justify why the change is necessary.
- **Async-First**: Use `async def` for event handlers and `@work` for blocking tasks.

### Aesthetic Integrity (Cassette Futurism)
- **Geometry**: Strictly **0px border-radius**. Use `solid`, `heavy`, `double`, or `dashed` borders.
- **Philosophy**: Think CRT monitors and bureaucratic brutality. Use ASCII/Block characters for graphical elements.
- **Vocabulary**: No mention of "Crypto," "Internet," or "Protocols." Use "Jack-in," "Node," or "Local Deck."
- **Colors**: High contrast. Backgrounds: Deep blacks (#050505), dark greys, or desaturated dark blues.
- **TCSS**: Use TCSS variables and layout with `Grid`, `Vertical`, or `Horizontal`.
- **Typography**: Terminals are monospace. Use `bold`, `reverse`, or `underline` for hierarchy.

### Logging & Debugging
- **Mandatory Log Check**: If a failure occurs, check `logs/mothership.log` immediately.
- **Proactive Logging**: Add `logger.debug()` or `logger.info()` checkpoints in new or suspected logic.

### Testing & Verification
- **Testing**: **EXEMPTED.** Do not attempt to run automated tests due to hardware side-effects. Manual verification is the standard.
- **Process Management**: **MANDATORY.** Always terminate background processes (e.g., port 8000) after verification. Do not leave persistent processes running.

---

## 4. COMMANDS & ENVIRONMENT

- **Run Application**: `python main.py`
- **Logs**: `tail -f logs/mothership.log` (or equivalent on Windows).
- **Python Path**: Use the `.venv` in the root directory.

---

*Do not delete or modify this file without explicit instruction.*
