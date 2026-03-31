# PROJECT CONTEXT: Mothership CLI

This document outlines the architecture, features, and core components of the Mothership CLI project. Its purpose is to serve as a reference to ensure all future modifications are consistent with the existing design and functionality.

## 1. Core Architecture & Purpose

- **Purpose**: A command-line and API-driven tool for assisting a "Mothership" Pen & Paper RPG session.
- **Primary Interface**: A Textual-based Terminal User Interface (TUI) that provides an immersive, retro-futuristic "in-game" feel.
- **Backend**: A Python backend that handles logic, data parsing, and external API calls.
- **Key Principle**: Strict separation of concerns. Theming, backend logic, and UI are in separate, dedicated modules.

## 2. Component Breakdown

### `main.py`
- **Role**: Entry point of the application.
- **Functionality**:
    - Initializes and starts the `run_server` in a background thread.
    - Initializes and runs the `MothershipApp` (TUI) in the main thread.
    - Registers global exception handlers via `src.utils`.

### `run.cmd`
- **Role**: Windows batch script to launch the application.
- **Functionality**:
    - Ensures the correct virtual environment (`.venv`) is used.
    - Provides a portable way to start the app without manually activating the environment.

### `.env`
- **Role**: User configuration file in the project root.
- **Functionality**:
    - Stores sensitive or user-specific paths like `VAULT_PATH` and `CACHE_PATH`.
    - Allows for configuration overrides without modifying the source code.

### `src/tui.py`
- **Role**: The main user interface (`MothershipApp`).
- **Functionality**:
    - **Layout**: Defines the two-panel layout (Left: Console, Right: Status Widgets).
    - **Command Handling**:
        - Captures user input via `TerminalInput`.
        - Parses commands (`start`, `stop`, 'print', 'wound', 'theme', 'exit', etc.).
        - Delegates tasks to background workers (`@work`) to keep the UI responsive.
    - **Display**:
        - `RichLog` (`#game_log`): Displays command history and responses.
        - Side Panels (`#timer-log`, `#network-log`): Display specific, filtered log messages.
    - **Theme Switching**: Implements the `apply_theme` method to change the visual appearance by swapping CSS classes based on `src/theme.py`.
    - **Autocomplete**: The `get_completions` function provides suggestions for commands and their arguments.

### `src/theme.py`
- **Role**: Central repository for all aesthetic and thematic elements. **This file is a configuration file and should be treated as read-only unless explicitly asked to modify a theme.**
- **Functionality**:
    - `THEMES` (dict): A dictionary containing multiple theme definitions (`mothership`, `prospero`, etc.). Each theme has:
        - `primary`, `secondary` colors.
        - `header` text.
        - `logo` ASCII art.
        - `startup` message list.
    - `get_css()`: A function that generates the dynamic CSS for all themes.

### `src/config.py`
- **Role**: Centralizes data source paths.
- **Functionality**: Stores the string paths for all data files and directories, making them easily configurable.

### `src/repository.py`
- **Role**: Data Access Layer for all data files.
- **Functionality**:
    - `MissionRepository` (class): Abstracts the file system for mission data.
    - `GeneratorRepository` (class): Abstracts the file system for random generator data (`Wounds.json`, `OxygenFortunes.json`).

### `src/app.py`
- **Role**: Manages the main background process (the timer).
- **Functionality**:
    - `ApiWorker` (class): A thread-safe class that runs a loop.
    - **Timer**: When `start()` is called, it periodically triggers `printer_service.print_oxygen_bill()`. The default interval is **20 minutes**.
    - `progress` (property): Calculates the completion percentage of the current timer interval for the UI.

### `src/printer.py`
- **Role**: Pure I/O service for hardware delivery.
- **Functionality**:
    - `Printer` (class): Sends finalized JSON payloads to the printer hardware.
    - Decoupled from all business logic (no knowledge of wounds or missions).

### `src/services/`
- **Role**: Business logic layer for specific game features.
- **Components**:
    - `wound_service.py`: Logic for wounds, dice rolls, and severity mapping.
    - `mission_service.py`: Logic for mission/contract data and payload formatting.
    - `billing_service.py`: Logic for oxygen bills and fortunes.
    - `facade.py`: The `mothership_service` instance, providing a unified entry point for the TUI and API.

### `src/server.py`
- **Role**: Provides an HTTP API to control the application.
- **Functionality**:
    - Exposes GET endpoints for:
        - `/start`, `/stop`, `/status`, `/exit`
        - `/print/contract/{id}`, `/print/mission/{id}`, `/print/contracts`
        - `/print/oxygen`
        - `/print/wound/{type}`

### `src.utils.py`
- **Role**: Provides shared utilities, primarily logging.
- **Functionality**:
    - `LoggerWrapper` (class): A sophisticated logger that:
        - Writes detailed logs to `logs/mothership.log`.
        - Forwards formatted messages to the TUI via callbacks.
    - **Callbacks**:
        - `set_callback()`: For general logs, routed to different widgets in the TUI.
        - `set_network_callback()`: For specific network messages.
    - **Global Exception Handling**: Catches all uncaught exceptions and writes them to the log file, preventing silent crashes.

### `src/dice.py`
- **Role**: A simple, reusable dice rolling utility.
- **Functionality**:
    - `DiceRoller` (class): Contains a static `roll()` method.

### `src/jsonParser.py`
- **Role**: Handles reading and parsing JSON files from the `resources` directory.
- **Functionality**:
    - `JsonParser` (class): Provides a `read_json_file()` method that takes a relative path within `resources`.

## 3. Data Structure (`resources/`)

- `data/missions/active/`: Contains JSON files for missions that are included in `print all`.
- `data/missions/inactive/`: Contains JSON files for missions that are available for individual printing but excluded from `print all`.
- `data/random-generators/`: Contains data for randomized events, like `Wounds.json` and `OxygenFortunes.json`.
- `data/templates/`: Obsidian Markdown templates used for external vault integration and testing.
- `Wounds.json`: Contains a `wound-severity` map and a list of `wound-tables` by type.

## 4. Architectural TODOs

- **[DONE] Refactor `printer.py` into specialized services**: Logic has been moved to `src/services/` (Wound, Mission, Billing).
- **[DONE] Decouple TUI via Facade**: The TUI now interacts exclusively with the `mothership_service` facade.
- **[TODO] Implement Obsidian Vault Uplink (In-Memory Registry + Shadow Cache)**:
    - Add `VAULT_PATH` and `CACHE_PATH` to `src/config.py`.
    - Create `VaultRepository` to manage the external Obsidian file system.
    - Create `ObsidianService` to handle Markdown parsing and JSON mirroring to the shadow cache.
- **[LATER] Decommission Internal Data**: Once the Obsidian integration is stable, remove `resources/data/missions` and rely entirely on the external Vault.