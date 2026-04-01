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
- **`app.py`**: Manages the main background worker/timer.
- **`config.py`**: Handles configuration and `.env` loading.
- **`utils.py`**: Provides logging and global exception handling.
- **`dice.py`**: Reusable dice rolling utility.

### `mothership.data`
- **`repository.py`**: Data Access Layer for local JSON files and external Vault Markdown files.
- **`json_parser.py`**: Utility for reading JSON resources.

### `mothership.services`
- **`facade.py`**: The `mothership_service` instance (single entry point).
- **`printer_delivery.py`**: Pure I/O for hardware printing.
- **`wound_service.py`**, `mission_service.py`, `billing_service.py`: Domain-specific logic.
- **`obsidian_service.py`**: Logic for Obsidian Vault integration.

### `mothership.ui`
- **`tui.py`**: The Textual-based Terminal UI.
- **`theme.py`**: Aesthetic configuration and CSS generation.
- **`server.py`**: FastAPI-based (or similar) HTTP API.

### `resources/templates`
- **`Mission-Template.md`**: Markdown template for Obsidian missions.
- **`Entity-Template.md`**: Markdown template for Obsidian entities.
- **`Mission-Template.json`**: JSON template for mission data structures.
- **`Entity-Template.json`**: JSON template for entity data structures.

## 3. Architectural TODOs

- **[DONE] Refactor to Domain-Driven Structure**: Project reorganized into the `mothership` package.
- **[DONE] Define Obsidian Mission Template**: New Markdown-based template created in `resources/data/templates/Mission-Template.md`.
- **[DONE] Create JSON Data Templates**: Standardized JSON templates for Missions and Entities added to `resources/templates/`.
- **[DONE] Implement Mission Markdown Parser**: Created `mothership.data.markdown_parser` with an extensible base class and a `MissionMarkdownParser` implementation, verified with tests.
- **[TODO] Implement Entity Markdown Parser**: Create a concrete parser for the new Entity Markdown template.
- **[TODO] Implement Obsidian Vault Uplink (In-Memory Registry + Shadow Cache)**:
    - Implement Sync logic in `mothership.services.obsidian_service`.
