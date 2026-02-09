from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Input, RichLog, Static, Label, ProgressBar
from textual.suggester import Suggester
from textual import work
import asyncio
import os

from src.app import worker
from src.printer import printer_service
from src.utils import logger

# --- Autocomplete Logic ---
def get_completions(value: str) -> list[str]:
    value_upper = value.upper()
    
    # Level 1: Commands
    commands = ['START', 'STOP', 'STATUS', 'PRINT', 'EXIT']
    
    if ' ' not in value:
        return [c for c in commands if c.startswith(value_upper)]
    
    # Level 2: Print Subcommands
    if value_upper.startswith('PRINT '):
        parts = value_upper.split(' ', 1)
        prefix = parts[1] if len(parts) > 1 else ""
        
        # Level 3: IDs (Dynamic)
        if prefix.startswith('CONTRACT ') or prefix.startswith('MISSION '):
            base_cmd = "PRINT CONTRACT " if prefix.startswith('CONTRACT') else "PRINT MISSION "
            try:
                typed_id = prefix.split(' ', 1)[1]
            except IndexError:
                typed_id = ""
            
            ids = printer_service.get_available_mission_ids()
            return [f"{base_cmd}{mid.upper()}" for mid in ids if mid.upper().startswith(typed_id)]

        subcommands = ['CONTRACT', 'ALL-CONTRACTS', 'MISSION', 'OXYGEN']
        matches = [s for s in subcommands if s.startswith(prefix)]
        return [f"PRINT {m}" for m in matches]

    return []

class CommandSuggester(Suggester):
    async def get_suggestion(self, value: str) -> str | None:
        matches = get_completions(value)
        if len(matches) == 1:
            return matches[0]
        return None

# --- Custom Input Widget ---
class TerminalInput(Input):
    """
    Custom Input widget that:
    1. Uses TAB to accept autocomplete suggestions.
    2. Prevents focus loss (mostly).
    """
    BINDINGS = [
        Binding("tab", "accept_suggestion", "Accept Suggestion", show=False),
    ]

    def action_accept_suggestion(self):
        matches = get_completions(self.value)
        if not matches:
            return

        # Fill as much as possible (Common Prefix)
        common = os.path.commonprefix(matches)
        
        if len(common) > len(self.value):
            self.value = common
            self.cursor_position = len(self.value)
        elif len(matches) > 1:
            self.app.display_completions(matches)

# --- Main Application ---
class MothershipApp(App):
    CSS = """
    /* --- CASSETTE FUTURISM THEME --- */
    $background: #050505;
    $foreground: #E09500; /* Muted Aged Amber */
    $border: #E09500;
    $dim: #553300;

    Screen {
        background: $background;
        color: $foreground;
    }

    /* --- LAYOUT --- */
    #sidebar {
        dock: right;
        width: 30;
        border-left: heavy $border;
        background: $background;
        padding: 1;
    }

    #main-container {
        height: 1fr;
        border: heavy $border;
        margin: 0 0;
    }

    /* --- WIDGETS --- */
    RichLog {
        background: $background;
        color: $foreground;
        scrollbar-color: $foreground;
        border: none;
    }

    Input {
        dock: bottom;
        border-top: heavy $border;
        background: $background;
        color: $foreground;
        border: none; /* We use the container border */
    }
    
    ProgressBar {
        color: $foreground;
        background: $dim;
    }

    Input:focus {
        border: none;
    }

    .header-text {
        text-align: center;
        text-style: bold;
        background: $foreground;
        color: $background;
        padding: 1;
    }

    #logo {
        color: $foreground;
        content-align: center middle;
        padding-bottom: 1;
        border-bottom: heavy $dim;
    }
    """

    ASCII_M = """
     ███╗   ███╗
     ████╗ ████║
     ██╔████╔██║
     ██║╚██╔╝██║
     ██║ ╚═╝ ██║
     ╚═╝     ╚═╝
     """


    ASCII_MOTHERSHIP = """
      __  __  ___ _____ _   _ _____ ____  ____  _   _ ___ ____  
     |  \/  |/ _ \_   _| | | | ____|  _ \/ ___|| | | |_ _|  _ \ 
     | |\/| | | | || | | |_| |  _| | |_) \___ \| |_| || || |_) |
     | |  | | |_| || | |  _  | |___|  _ < ___) |  _  || ||  __/ 
     |_|  |_|\___/ |_| |_| |_|_____|_| \_\____/|_| |_|___|_|    
    """

    def compose(self) -> ComposeResult:
        logger.info("TUI: compose started")
        try:
            # Top Header
            logger.debug("Yielding Header")
            yield Static("MOTHERSHIP UPLINK // TERMINAL ZERO", classes="header-text")

            # Main Body
            logger.debug("Yielding Main Container")
            with Horizontal():
                # Left: Main Log Output
                with Container(id="main-container"):
                    logger.debug("Yielding RichLog")
                    # can_focus=False ensures mouse clicks don't steal focus from Input
                    # Moved can_focus to on_mount to avoid potential init issues during compose
                    yield RichLog(id="game_log", highlight=True, markup=True, wrap=True)
                
                # Right: Status Sidebar
                with Vertical(id="sidebar"):
                    logger.debug("Yielding Sidebar")
                    yield Static(self.ASCII_M, id="logo")
                    yield Label("[BOLD UNDERLINE]SYSTEM STATUS[/]")
                    yield Static("UPLINK: ACTIVE", id="status_uplink")
                    yield Static("\n[BOLD UNDERLINE]TIMER[/]")
                    yield Static("STATE: STOPPED", id="status_timer")
                    yield Static("INTERVAL: --", id="status_interval")
                    logger.debug("Yielding ProgressBar")
                    yield ProgressBar(total=1.0, show_eta=False, id="timer_progress")

            # Bottom: Input
            logger.debug("Yielding Input")
            yield TerminalInput(placeholder="ENTER COMMAND...", id="command_input", suggester=CommandSuggester())
            
            logger.info("TUI: compose finished successfully")
        except Exception as e:
            logger.critical("TUI: compose failed", exc_info=True)
            raise e

    def on_mount(self) -> None:
        logger.info("TUI: on_mount started")
        try:
            # Disable focus on log widget safely after mount
            self.query_one("#game_log").can_focus = False

            # Hook up the logger to our Log widget
            logger.set_callback(self.write_log_threadsafe)
            
            logger.info("INITIALIZING SYSTEM...")
            logger.info("CONNECTION ESTABLISHED.")
            self.update_status_panel()
            # Ensure input is focused immediately
            self.query_one("#command_input").focus()
            
            # Start a background refresh for the progress bar
            self.set_interval(1.0, self.update_status_panel)
        except Exception as e:
            logger.error("Error during TUI mount", exc_info=True)

    def write_log_threadsafe(self, message: str) -> None:
        """Called by background threads via logger."""
        # IMPORTANT: Do not access widgets (query_one) here, as this runs in the worker thread.
        self.call_from_thread(self._update_log_ui, message)

    def _update_log_ui(self, message: str) -> None:
        """Actual UI update running on the main thread."""
        self.query_one("#game_log").write(message)
        self.update_status_panel()

    def update_status_panel(self) -> None:
        """Updates the sidebar status indicators."""
        timer_state = "RUNNING" if worker.is_running else "OFFLINE"
        color = "green" if worker.is_running else "red" # Textual supports standard color names in markup
        
        self.query_one("#status_timer").update(f"STATE: [{color}]{timer_state}[/]")
        self.query_one("#status_interval").update(f"Interval: {worker.interval}m")
        self.query_one("#timer_progress").progress = worker.progress

    def display_completions(self, matches: list[str]) -> None:
        log = self.query_one("#game_log")
        log.write(f"\n[bold]Available Options:[/]")
        # Join matches to save vertical space and rely on RichLog wrapping
        log.write("  " + "  ".join(matches))

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        try:
            command = message.value.strip()
            if not command:
                return

            log = self.query_one("#game_log")
            # Add a newline before the prompt to visually separate command blocks
            log.write(f"\n> {command}")
            self.query_one("#command_input").value = ""

            # Command Parsing
            parts = command.split()
            cmd = parts[0].upper()
            args = parts[1:]

            if cmd == "EXIT":
                worker.stop()
                self.exit()
            elif cmd == "START":
                logger.info(f"Command START received. Args: {args}")
                interval = args[0] if len(args) > 0 else None
                api_url = args[1] if len(args) > 1 else None
                if not worker.start(interval, api_url):
                    log.write("[BOLD RED]ERROR: COULD NOT START TIMER (CHECK LOGS)[/]")
            elif cmd == "STOP":
                worker.stop()
            elif cmd == "STATUS":
                self.update_status_panel()
                log.write(f"Worker Running: {worker.is_running}")
            elif cmd == "PRINT":
                await self.handle_print_command(args, log)
            else:
                log.write("[BOLD RED]ERROR: UNKNOWN COMMAND[/]")

            self.update_status_panel()
        except Exception as e:
            logger.error("Error processing command", exc_info=True)
            self.query_one("#game_log").write(f"[BOLD RED]SYSTEM ERROR: {e}[/]")

    async def handle_print_command(self, args, log):
        if not args:
            log.write("Usage: print [contract|mission|oxygen] {id}")
            return

        sub = args[0].upper()
        
        # Ensure ID is uppercase (for file matching)
        if len(args) > 1:
            args[1] = args[1].upper()
        
        # We run these in a worker to avoid freezing the UI during network/disk IO
        self.run_print_task(sub, args)

    @work(exclusive=True, thread=True)
    def run_print_task(self, sub, args):
        # Wrapper to call the synchronous printer service
        if sub == "ALL-CONTRACTS":
            printer_service.print_all_contracts()
        elif sub == "CONTRACT" and len(args) > 1:
            printer_service.print_contract(args[1])
        elif sub == "MISSION" and len(args) > 1:
            printer_service.print_mission(args[1])
        elif sub == "OXYGEN":
            printer_service.print_oxygen_bill()
        else:
            logger.warning("Invalid print command arguments.")