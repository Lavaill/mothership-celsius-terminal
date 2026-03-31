from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal, VerticalScroll
from textual.widgets import Input, RichLog, Static, Label
from textual.suggester import Suggester
from textual import work
import asyncio
import os
import math
import time

from src.app import worker
from src.services.facade import mothership_service
from src.utils import logger
from src.theme import THEMES, TYPE_DELAY, LINE_DELAY

logger.info("TUI: Module loading...")

# --- Generate Theme CSS ---
THEME_CSS = ""
for name, data in THEMES.items():
    p = data['primary']
    s = data['secondary']
    THEME_CSS += f"""
    .{name} {{
        color: {p};
    }}
    .{name} #left-panel {{
        border-right: heavy {p};
    }}
    .{name} #header-box {{
        border-bottom: double {p};
        color: {p};
    }}
    .{name} RichLog {{
        color: {p};
    }}
    .{name} .prompt-label {{
        color: {p};
    }}
    .{name} TerminalInput {{
        color: {p};
    }}
    .{name} #logo-container {{
        border-bottom: heavy {p};
    }}
    .{name} .widget-box {{
        border: solid {p};
    }}
    .{name} #timer-visual {{
        color: {p};
    }}
    .{name} .label-title {{
        border-bottom: dashed {s};
    }}
    """
logger.info("TUI: Generated THEME_CSS.")

# --- Autocomplete Logic ---
def get_completions(value: str) -> list[str]:
    # Do NOT strip the value, as trailing spaces are significant for parsing arguments
    value_lower = value.lower()
    
    commands = ['start', 'stop', 'status', 'print', 'check', 'theme', 'wound', 'exit']
    
    # Level 1: Top-level commands
    # If there are no spaces, we are still typing the command
    if ' ' not in value:
        return [c for c in commands if c.startswith(value_lower)]
    
    # Level 2: Subcommands
    if value_lower.startswith('print'):
        parts = value_lower.split(' ')
        
        # If we have exactly 2 parts, we are typing the subcommand
        # "print " -> parts=['print', '']
        # "print c" -> parts=['print', 'c']
        if len(parts) == 2:
            prefix = parts[1]
            subcommands = ['contract', 'all-contracts', 'mission', 'oxygen']
            matches = [s for s in subcommands if s.startswith(prefix)]
            return [f"print {m}" for m in matches]
        
        # Level 3: IDs
        # "print contract " -> parts=['print', 'contract', '']
        if len(parts) >= 3:
            subcmd = parts[1]
            if subcmd in ['contract', 'mission']:
                typed_id = parts[2]
                ids = mothership_service.get_available_mission_ids()
                # IDs are data, so we keep them as returned (likely upper), but match lower
                return [f"print {subcmd} {mid}" for mid in ids if mid.lower().startswith(typed_id)]
    
    # Level 2: Theme Subcommands
    if value_lower.startswith('theme'):
        parts = value_lower.split(' ')
        if len(parts) == 2:
            prefix = parts[1]
            theme_names = list(THEMES.keys())
            return [f"theme {t}" for t in theme_names if t.startswith(prefix)]

    # Level 2: Wound Subcommands
    if value_lower.startswith('wound'):
        parts = value_lower.split(' ')
        if len(parts) == 2:
            prefix = parts[1]
            wound_types = mothership_service.get_wound_types()
            return [f"wound {w}" for w in wound_types if w.lower().startswith(prefix)]
        if len(parts) == 3:
            # Suggest numbers 1-10
            prefix = parts[2]
            numbers = [str(i) for i in range(1, 11)]
            return [f"wound {parts[1]} {n}" for n in numbers if n.startswith(prefix)]

    return []

class CommandSuggester(Suggester):
    async def get_suggestion(self, value: str) -> str | None:
        matches = get_completions(value)
        if len(matches) == 1:
            return matches[0]
        return None

class TerminalInput(Input):
    BINDINGS = [
        Binding("tab", "accept_suggestion", "Accept Suggestion", show=False),
    ]

    def action_accept_suggestion(self):
        matches = get_completions(self.value)
        if not matches:
            return
        
        common = os.path.commonprefix(matches)
        # If the common prefix is longer than what we have, auto-fill it
        if len(common) > len(self.value):
            self.value = common
            self.cursor_position = len(self.value)
        # If we can't auto-fill further but have multiple options, show them
        elif len(matches) > 1:
            self.app.display_completions(matches)

class MothershipApp(App):
    logger.info("TUI: Defining MothershipApp class...")
    CSS = THEME_CSS + """
    Screen {
        background: #050505;
    }

    /* --- LAYOUT --- */
    #main-split {
        layout: horizontal;
        height: 100%;
    }

    /* --- LEFT PANEL (75%) --- */
    #left-panel {
        width: 75%;
        height: 100%;
        layout: vertical;
    }

    #header-box {
        height: auto;
        padding: 1;
        text-align: center;
        text-style: bold underline;
    }
    
    /* --- TRUE CONSOLE LAYOUT --- */
    #console-scroll {
        height: 100%;
        overflow-y: scroll;
        scrollbar-size: 0 0;
    }

    RichLog {
        height: auto;
        min-height: 1;
        background: #050505;
        border: none;
        padding: 0;
        overflow: hidden;
    }
    
    .input-line {
        height: 1;
        width: 100%;
        margin-bottom: 5;
    }

    .prompt-label {
        width: auto;
        height: 1;
    }

    TerminalInput {
        width: 1fr;
        background: #050505;
        border: none;
        padding: 0;
        height: 1;
    }
    
    TerminalInput:focus {
        border: none;
    }

    /* --- RIGHT PANEL (25%) --- */
    #right-panel {
        width: 25%;
        height: 100%;
        layout: vertical;
    }

    #logo-container {
        height: auto;
        padding: 1;
        content-align: center middle;
    }

    #widgets-container {
        height: 1fr;
        padding: 1;
        layout: vertical;
    }

    .widget-box {
        padding: 1;
        margin-bottom: 1;
    }

    .label-title {
        text-style: bold;
        border-bottom: dashed #442200;
        margin-bottom: 1;
    }

    #timer-visual {
        height: 12;
        content-align: center middle;
    }

    .status-log {
        height: 8;
        overflow-y: auto;
        scrollbar-size: 0 0;
        color: #442200;
        padding-top: 1;
    }
    """

    def __init__(self):
        logger.info("TUI: MothershipApp.__init__ started")
        super().__init__()
        self.active_theme = "mothership"
        self.theme_data = THEMES[self.active_theme]
        logger.info(f"TUI: CSS Length: {len(self.CSS)}")
        logger.info("TUI: MothershipApp.__init__ finished")

    def on_load(self):
        logger.info("TUI: on_load started")
        logger.info("TUI: on_load finished")

    def compose(self) -> ComposeResult:
        logger.info("TUI: compose started")
        try:
            with Horizontal(id="main-split"):
                # --- LEFT PANEL ---
                logger.debug("Yielding Left Panel")
                with Vertical(id="left-panel"):
                    logger.debug("Yielding Header")
                    yield Static(self.theme_data["header"], id="header-box")
                    with VerticalScroll(id="console-scroll"):
                        # Disable highlight to prevent auto-coloring of dates/numbers
                        logger.debug("Yielding RichLog")
                        yield RichLog(id="game_log", highlight=False, markup=True, wrap=True)
                        with Horizontal(classes="input-line"):
                            yield Static("> ", classes="prompt-label")
                            logger.debug("Yielding Input")
                            yield TerminalInput(placeholder="", id="command_input", suggester=CommandSuggester())

                # --- RIGHT PANEL ---
                logger.debug("Yielding Right Panel")
                with Vertical(id="right-panel"):
                    logger.debug("Yielding Logo")
                    yield Container(Static(self.theme_data["logo"]), id="logo-container")
                    with Vertical(id="widgets-container"):
                        # Timer Widget
                        with Vertical(classes="widget-box"):
                            yield Label("TIMER STATUS", classes="label-title")
                            yield Static("OFFLINE", id="timer-state-text")
                            yield Static("", id="timer-visual")
                            yield Static("INT: --", id="timer-interval-text")
                            yield RichLog(id="timer-log", classes="status-log", highlight=False, markup=True)
                        
                        # Connection Widget
                        with Vertical(classes="widget-box"):
                            yield Label("PRINTER MODULE", classes="label-title")
                            yield Static("CONNECTION: [bold]SECURE[/]")
                            yield Static("TYPE:   JACK")
                            yield RichLog(id="network-log", classes="status-log", highlight=False, markup=True)
            logger.info("TUI: compose finished successfully")
        except Exception as e:
            logger.critical("TUI: compose failed", exc_info=True)
            raise e

    def on_mount(self) -> None:
        logger.info("TUI: on_mount started")
        try:
            self.screen.add_class(self.active_theme)
            self.query_one("#game_log").can_focus = False
            logger.set_callback(self.write_log_threadsafe)
            logger.set_network_callback(self.write_network_log_threadsafe)
            self.run_startup_sequence()
            self.query_one("#command_input").focus()
            self.set_interval(0.2, self.update_status_panel) # Faster refresh for wave animation
            # Ensure input is visible
            self.call_after_refresh(self.scroll_to_bottom)
            logger.info("TUI: on_mount finished")
        except Exception as e:
            logger.critical("TUI: on_mount failed", exc_info=True)
            raise e

    def on_click(self) -> None:
        """Focus the input when clicking anywhere in the app."""
        self.query_one("#command_input").focus()
        self.query_one("#console-scroll").scroll_end(animate=False)
        self.call_after_refresh(self.scroll_to_bottom)

    @work
    async def run_startup_sequence(self):
        lines = self.theme_data["startup"]
        for line in lines:
            self.write_to_console(f"> {line}", indent=False)
            await asyncio.sleep(LINE_DELAY)

    def write_log_threadsafe(self, message: str) -> None:
        self.call_from_thread(self._update_log_ui, message)

    def _update_log_ui(self, message: str) -> None:
        """Routes logs to the appropriate side panel widget."""
        msg_lower = message.lower()
        
        # Timer Logs
        if "timer" in msg_lower or "interval" in msg_lower:
            # Strip timestamp for cleaner side panel look if present
            clean_msg = message.split(" - ")[-1] if " - " in message else message
            self.query_one("#timer-log").write(f"> {clean_msg}")
            
        # Network/Printer Logs
        elif any(x in msg_lower for x in ["sending", "sent", "print", "connection", "api"]):
            clean_msg = message.split(" - ")[-1] if " - " in message else message
            self.query_one("#network-log").write(f"> {clean_msg}")
            
        # Fallback (System Logs) -> Network Panel
        else:
            clean_msg = message.split(" - ")[-1] if " - " in message else message
            self.query_one("#network-log").write(f"> {clean_msg}")

    def write_network_log_threadsafe(self, message: str) -> None:
        self.call_from_thread(self._update_network_log_ui, message)

    def _update_network_log_ui(self, message: str) -> None:
        self.query_one("#network-log").write(f"> {message}")

    def write_to_console(self, text: str, indent: bool = True) -> None:
        """Writes to the main history log and scrolls down."""
        if indent:
            # Add 5 spaces indentation to all lines for responses
            indented_text = "\n".join([f"     {line}" for line in text.split("\n")])
        else:
            indented_text = text
            
        self.query_one("#game_log").write(indented_text)
        # Scroll container to end to show input line
        self.call_after_refresh(self.scroll_to_bottom)

    def scroll_to_bottom(self) -> None:
        self.query_one("#console-scroll").scroll_end(animate=False)

    def display_completions(self, matches: list[str]) -> None:
        """Displays available autocomplete options in the log."""
        
        # Simulate terminal behavior: print current prompt, then options
        current_input = self.query_one("#command_input").value
        self.write_to_console(f"> {current_input}", indent=False)

        options = []
        for match in matches:
            parts = match.split()
            if parts:
                options.append(parts[-1])
        
        # Join them inline with a space separator
        options_str = "  ".join(options)
        
        sec_color = self.theme_data["secondary"]
        self.write_to_console(f"[{sec_color}]{options_str}[/{sec_color}]\n")

    def get_simple_bar_ascii(self, percent: float) -> str:
        """
        Generates a simple filling bar animation.
        """
        p = max(0.0, min(1.0, percent))
        width = 20
        filled = int(p * width)
        
        # Simple bar characters
        bar = "█" * filled + "░" * (width - filled)
        
        return f"\n\n[{bar}]\n   {int(p*100)}%"

    def update_status_panel(self) -> None:
        try:
            # Update State Text
            state = "ACTIVE" if worker.is_running else "OFFLINE"
            
            # Add wave effect to the status text if running
            if worker.is_running:
                wave_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▁"]
                t = time.time() * 10
                wave_idx = int(t) % len(wave_chars)
                wave = wave_chars[wave_idx]
                state_display = f"{state} {wave}"
            else:
                state_display = state

            self.query_one("#timer-state-text").update(f"STATE: {state_display}")
            self.query_one("#timer-interval-text").update(f"INT: {worker.interval}m")

            # Update Visual - Using Simple Bar
            art = self.get_simple_bar_ascii(worker.progress)
            self.query_one("#timer-visual").update(art)

        except Exception as e:
            logger.debug(f"Status update error: {e}")

    def apply_theme(self, theme_name: str) -> None:
        if theme_name not in THEMES:
            return
        
        self.screen.remove_class(self.active_theme)
        self.active_theme = theme_name
        self.theme_data = THEMES[theme_name]
        self.screen.add_class(self.active_theme)
        
        # Update Static Widgets
        self.query_one("#header-box").update(self.theme_data["header"])
        self.query_one("#logo-container Static").update(self.theme_data["logo"])
        
        # Reset Console
        self.query_one("#game_log").clear()
        self.query_one("#timer-log").clear()
        self.query_one("#network-log").clear()
        self.run_startup_sequence()

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        command = message.value.strip()
        if not command:
            # Handle empty enter: just print prompt and scroll
            self.write_to_console(f"> ", indent=False)
            self.query_one("#command_input").value = ""
            return

        logger.info(f"CMD: {command}")
        self.write_to_console(f"> {command}", indent=False)
        self.query_one("#command_input").value = ""

        try:
            parts = command.split()
            if not parts: return
            
            cmd = parts[0].lower()
            args = parts[1:]

            sec_color = self.theme_data["secondary"]

            if cmd == "exit":
                self.write_to_console(f"[{sec_color}]Terminating uplink session...[/{sec_color}]\n")
                worker.stop()
                self.exit()
            elif cmd == "start":
                interval = args[0] if len(args) > 0 else None
                if worker.start(interval):
                    self.write_to_console(f"[{sec_color}]Timer started (Interval: {worker.interval}m).[/{sec_color}]\n")
                    # FIX: Call _update_network_log_ui directly since we are in the main thread
                    self._update_network_log_ui("LOCAL: TIMER START")
                else:
                    self.write_to_console(f"[bold red]ERROR: Timer already active or invalid interval.[/]\n")
            elif cmd == "stop":
                if worker.stop():
                    self.write_to_console(f"[{sec_color}]Timer stopped.[/{sec_color}]\n")
                    # FIX: Call _update_network_log_ui directly since we are in the main thread
                    self._update_network_log_ui("LOCAL: TIMER STOP")
                else:
                    self.write_to_console(f"[{sec_color}]Timer is not currently active.[/{sec_color}]\n")
            elif cmd == "status":
                self.update_status_panel()
                self.write_to_console(f"[{sec_color}]Status report updated.[/{sec_color}]\n")
            elif cmd == "print":
                await self.handle_print_command(args)
            elif cmd == "check":
                self.write_to_console(f"[{sec_color}]DIAGNOSTIC: KERNEL OPTIMIZED. MEMORY LEAKS: 0. UPLINK STABLE.[/{sec_color}]\n")
            elif cmd == "theme":
                if len(args) > 0:
                    new_theme = args[0].lower()
                    if new_theme in THEMES:
                        self.apply_theme(new_theme)
                    else:
                        self.write_to_console(f"[{sec_color}]Unknown theme: {new_theme}[/{sec_color}]\n")
                else:
                    self.write_to_console(f"[{sec_color}]Usage: theme [mothership|prospero|helios|astra|parallax][/{sec_color}]\n")
            elif cmd == "wound":
                await self.handle_wound_command(args)
            else:
                self.write_to_console(f"[{sec_color}]Unknown command. Try 'start', 'print', 'check', 'theme', 'wound', or 'exit'.[/{sec_color}]\n")
        except Exception as e:
            logger.error(f"Command failed: {command}", exc_info=True)
            self.write_to_console(f"[bold red]ERROR: {e}[/]\n")

    async def handle_print_command(self, args):
        sec_color = self.theme_data["secondary"]
        if not args:
            self.write_to_console(f"[{sec_color}]Usage: print [contract|mission|oxygen] {id}[/{sec_color}]\n")
            return
        sub = args[0].upper() # Keep upper for backend logic if needed, or convert as required
        self.write_to_console(f"[{sec_color}]Print request for {sub.lower()} queued.[/{sec_color}]\n")
        self.run_print_task(sub, args)

    async def handle_wound_command(self, args):
        sec_color = self.theme_data["secondary"]
        if not args:
            self.write_to_console(f"[{sec_color}]Usage: wound [type] [optional: number][/{sec_color}]\n")
            return
        
        wound_type = args[0]
        wound_number = args[1] if len(args) > 1 else None
        
        self.write_to_console(f"[{sec_color}]Processing wound report...[/{sec_color}]\n")
        self.run_wound_task(wound_type, wound_number)

    @work(exclusive=True, thread=True)
    def run_print_task(self, sub, args):
        sec_color = self.theme_data["secondary"]
        try:
            if sub == "ALL-CONTRACTS":
                mothership_service.print_all_contracts()
            elif sub == "CONTRACT" and len(args) > 1:
                # args[1] is the ID. We assume the user might type lowercase, but files might be upper.
                # printer_service expects exact match. Let's try upper.
                mothership_service.print_contract(args[1].upper()) 
            elif sub == "MISSION" and len(args) > 1:
                mothership_service.print_mission(args[1].upper())
            elif sub == "OXYGEN":
                mothership_service.print_oxygen_bill()
            else:
                self.call_from_thread(self.write_to_console, f"[{sec_color}]Invalid print parameters.[/{sec_color}]\n")
        except Exception as e:
            logger.error(f"Print task failed: {sub}", exc_info=True)

    @work(exclusive=True, thread=True)
    def run_wound_task(self, wound_type, wound_number):
        sec_color = self.theme_data["secondary"]
        try:
            if mothership_service.print_wound(wound_type, wound_number):
                self.call_from_thread(self.write_to_console, f"[{sec_color}]Wound report printed successfully.[/{sec_color}]\n")
            else:
                self.call_from_thread(self.write_to_console, f"[{sec_color}]Failed to print wound report. Check logs.[/{sec_color}]\n")
        except Exception as e:
            logger.error(f"Wound task failed", exc_info=True)
