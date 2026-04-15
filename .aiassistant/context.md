# PROJECT CONTEXT: Mothership CLI

This document outlines the architecture, features, and core components of the Mothership CLI project.

## 1. Core Architecture & Purpose

- **Purpose**: A command-line and API-driven tool for assisting a "Mothership" Pen & Paper RPG session.
- **Primary Interface**: A Textual-based Terminal User Interface (TUI) in `mothership.ui.tui`.
- **Backend**: A modular Python package structured by domain (`core`, `data`, `services`, `ui`).

## 2. Component Breakdown

### `main.py`
- **Role**: Entry point of the application.
- **Functionality**: Starts the API Server (`mothership.ui.server`) and the TUI (`mothership.ui.tui`).

### `mothership.core`
- **`app.py`**: Contains `ApiWorker` (generic timer logic) and `TimerManager` (registry for named timers).
- **`config.py`**: Handles configuration and `.env` loading.
- **`utils.py`**: Provides logging and global exception handling.
- **`dice.py`**: Reusable dice rolling utility.

### `mothership.data`
- **`repository.py`**: Data Access Layer for local JSON files and external Vault Markdown files.
- **`json_parser.py`**: Utility for reading JSON resources.
- **`markdown_parser.py`**: Extensible Markdown parser for Obsidian integration.

### `mothership.services`
- **`facade.py`**: The `mothership_service` instance (single entry point). Manages the `TimerManager` registry.
- **`printer_delivery.py`**: Pure I/O for hardware printing.
- **`wound_service.py`**, `mission_service.py`, `billing_service.py`: Domain-specific logic.
- **`obsidian_service.py`**: Logic for Obsidian Vault integration.

### `mothership.ui`
- **`tui.py`**: The Textual-based Terminal UI. 
- **Available Commands**:
    - `start <timer-name> [interval]`: Engages a named background task (e.g., `oxygen-timer`).
    - `stop <timer-name>`: Disengages a named background task. Resumes from last progress if restarted.
    - `print <subcommand>`: Unified printing interface.
        - `print contract <id>`: Prints a specific mission contract.
        - `print mission <id>`: Prints mission details.
        - `print oxygen`: Prints an on-demand oxygen bill.
        - `print wound <type> [number]`: Prints a specific wound report.
        - `print all-contracts`: Batch prints all active contracts.
    - `theme <name>`: Switches UI aesthetic.
    - `exit`: Clean shutdown of all timers and uplink.
- **`theme.py`**: Aesthetic configuration and CSS generation.
- **`server.py`**: FastAPI-based HTTP API mirroring TUI capabilities.

## 3. Architectural Progress

- **[DONE] Refactor to Domain-Driven Structure**: Project reorganized into the `mothership` package.
- **[DONE] Implement Mission Markdown Parser**: Extensible parser for Obsidian mission templates.
- **[DONE] Generic Timer System**: 
    - `ApiWorker` is now agnostic (uses task callbacks).
    - `TimerManager` supports multiple named timers.
    - Wait-then-Act logic implemented (starts at 0%).
    - Support for pause/resume (progress retention).
- **[DONE] Natural Language Commands**: 
    - Commands updated to `start <timer-name> [interval]` and `stop <timer-name>`.
    - Autocomplete support for timer names.
- **[DONE] Documentation Consolidation**: Merged `gemini-rules.md` into `GEMINI.md` to eliminate instruction fragmentation. Transitioned to a "Two-File Architecture": `GEMINI.md` (Mandates/Style) and `.aiassistant/context.md` (State/Progress).
- **[TODO] Implement Entity Markdown Parser**: Create a concrete parser for the new Entity Markdown template.
- **[TODO] Implement Obsidian Vault Uplink (In-Memory Registry + Shadow Cache)**:
    - Implement Sync logic in `mothership.services.obsidian_service`.
