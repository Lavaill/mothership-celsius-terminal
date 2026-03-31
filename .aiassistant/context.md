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
- **Role**: Handles all data retrieval and external API calls to the printer service.
- **Functionality**:
    - `print_contract`, `print_mission`: Retrieves data from the `MissionRepository` and sends it to the printer.
    - `print_all_contracts`: Prints **only** from the `active` folder, using the `MissionRepository`.
    - `print_oxygen_bill`: Retrieves a random fortune from the `GeneratorRepository` and sends the oxygen bill payload. **This is a critical, existing feature.**
    - `print_wound`: Retrieves wound data from the `GeneratorRepository`, rolls a die (if needed), and sends the wound payload.
    - `get_available_mission_ids`, `get_wound_types`: Provides data for TUI autocomplete.

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
- `Wounds.json`: Contains a `wound-severity` map and a list of `wound-tables` by type.

## 4. Architectural TODOs

- **[TODO] Refactor `printer.py`**: The `Printer` class is becoming a "God Class". It should be broken down into smaller, more focused services (e.g., `WoundService`, `MissionService`).
- **[DONE] Create Data Access Layer**: The logic for finding all data files has been abstracted into the `repository.py` module. The `Printer` service now uses this layer to access data, decoupling it from the file system.
- **[TODO] Decouple TUI from Backend Services**: The TUI (`tui.py`) currently calls `printer_service` directly for autocomplete data. This creates a tight coupling. In the future, this could be routed through a "Facade" to make the UI more agnostic.
- **[LATER] Refactor `printer.py`**: Implement the service refactor (Point 1).
- **[LATER] Decouple TUI**: Implement the Facade pattern (Point 4).
