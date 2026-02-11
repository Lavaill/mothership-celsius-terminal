from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Input, RichLog, Static, Label
from textual.suggester import Suggester
from textual import work
import asyncio
import os
import math
import time

from src.app import worker
from src.printer import printer_service
from src.utils import logger

# --- CONSTANTS ---
TYPE_DELAY = 0.01
LINE_DELAY = 0.2
ORANGE_COLOR = "#FF9500"  # Deep Amber/Orange

# --- Autocomplete Logic ---
def get_completions(value: str) -> list[str]:
    # Do NOT strip the value, as trailing spaces are significant for parsing arguments
    value_upper = value.upper()
    
    commands = ['START', 'STOP', 'STATUS', 'PRINT', 'EXIT']
    
    # Level 1: Top-level commands
    # If there are no spaces, we are still typing the command
    if ' ' not in value:
        return [c for c in commands if c.startswith(value_upper)]
    
    # Level 2: Subcommands
    if value_upper.startswith('PRINT'):
        parts = value_upper.split(' ')
        
        # If we have exactly 2 parts, we are typing the subcommand
        # "PRINT " -> parts=['PRINT', '']
        # "PRINT C" -> parts=['PRINT', 'C']
        if len(parts) == 2:
            prefix = parts[1]
            subcommands = ['CONTRACT', 'ALL-CONTRACTS', 'MISSION', 'OXYGEN']
            matches = [s for s in subcommands if s.startswith(prefix)]
            return [f"PRINT {m}" for m in matches]
        
        # Level 3: IDs
        # "PRINT CONTRACT " -> parts=['PRINT', 'CONTRACT', '']
        if len(parts) >= 3:
            subcmd = parts[1]
            if subcmd in ['CONTRACT', 'MISSION']:
                typed_id = parts[2]
                ids = printer_service.get_available_mission_ids()
                return [f"PRINT {subcmd} {mid.upper()}" for mid in ids if mid.upper().startswith(typed_id)]

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
    CSS = f"""
    /* --- THEME VARIABLES --- */
    $orange: {ORANGE_COLOR};
    $bg: #050505;
    $dim: #442200;

    Screen {{
        background: $bg;
        color: $orange;
    }}

    /* --- LAYOUT --- */
    #main-split {{
        layout: horizontal;
        height: 100%;
    }}

    /* --- LEFT PANEL (75%) --- */
    #left-panel {{
        width: 75%;
        height: 100%;
        border-right: heavy $orange;
        layout: vertical;
    }}

    #header-box {{
        height: auto;
        border-bottom: double $orange;
        padding: 1;
        text-align: center;
        color: $orange;
    }}

    #console-area {{
        height: 1fr;
        layout: vertical;
    }}

    RichLog {{
        height: 1fr;
        background: $bg;
        color: $orange;
        border: none;
        scrollbar-color: $orange;
    }}

    TerminalInput {{
        dock: bottom;
        border-top: solid $orange;
        background: $bg;
        color: $orange;
        height: 3;
    }}
    
    TerminalInput:focus {{
        border-top: double $orange;
    }}

    /* --- RIGHT PANEL (25%) --- */
    #right-panel {{
        width: 25%;
        height: 100%;
        layout: vertical;
    }}

    #logo-container {{
        height: auto;
        border-bottom: heavy $orange;
        padding: 1;
        content-align: center middle;
    }}

    #widgets-container {{
        height: 1fr;
        padding: 1;
        layout: vertical;
    }}

    .widget-box {{
        border: solid $orange;
        padding: 1;
        margin-bottom: 1;
    }}

    .label-title {{
        text-style: bold;
        border-bottom: dashed $dim;
        margin-bottom: 1;
    }}

    #timer-visual {{
        height: 12;
        content-align: center middle;
        color: $orange;
    }}
    """

    LOGO_SMALL = """
   __  __ 
  |  \/  |
  | |\/| |
  |_|  |_|
    """

    HEADER_TEXT = "MOTHERSHIP UPLINK // TERMINAL ZERO"

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-split"):
            # --- LEFT PANEL ---
            with Vertical(id="left-panel"):
                yield Static(self.HEADER_TEXT, id="header-box")
                with Vertical(id="console-area"):
                    # Disable highlight to prevent auto-coloring of dates/numbers
                    yield RichLog(id="game_log", highlight=False, markup=True, wrap=True)
                    yield TerminalInput(placeholder="AWAITING INPUT...", id="command_input", suggester=CommandSuggester())

            # --- RIGHT PANEL ---
            with Vertical(id="right-panel"):
                yield Container(Static(self.LOGO_SMALL), id="logo-container")
                with Vertical(id="widgets-container"):
                    # Timer Widget
                    with Vertical(classes="widget-box"):
                        yield Label("TIMER STATUS", classes="label-title")
                        yield Static("OFFLINE", id="timer-state-text")
                        yield Static("", id="timer-visual")
                        yield Static("INT: --", id="timer-interval-text")
                    
                    # Connection Widget
                    with Vertical(classes="widget-box"):
                        yield Label("NETWORK", classes="label-title")
                        yield Static("UPLINK: [bold]SECURE[/]")
                        yield Static("PING:   12ms")

    def on_mount(self) -> None:
        self.query_one("#game_log").can_focus = False
        logger.set_callback(self.write_log_threadsafe)
        self.run_startup_sequence()
        self.query_one("#command_input").focus()
        self.set_interval(0.2, self.update_status_panel) # Faster refresh for wave animation

    @work
    async def run_startup_sequence(self):
        log = self.query_one("#game_log")

        #DO NOT EDIT UNLESS PROMPTED
        lines = [
            "Initializing Kernel...",
            "Loading Modules: [OXYGEN BILLING, LEDGERS, CONTRACT]... OK",
            "Mounting File System... OK",
            "Establishing Uplink... SUCCESS",
            "Welcome, User."
        ]
        for line in lines:
            log.write(f"> {line}")
            await asyncio.sleep(LINE_DELAY)

    def write_log_threadsafe(self, message: str) -> None:
        self.call_from_thread(self._update_log_ui, message)

    def _update_log_ui(self, message: str) -> None:
        self.query_one("#game_log").write(message)

    def display_completions(self, matches: list[str]) -> None:
        """Displays available autocomplete options in the log."""
        log = self.query_one("#game_log")
        
        # Extract just the last part of the command for display
        options = []
        for match in matches:
            parts = match.split()
            if parts:
                options.append(parts[-1])
        
        # Join them inline with a space separator (No pipe)
        options_str = " ".join(options)
        
        log.write(f"\n[dim]>> Options: {options_str}[/]")

    def get_complex_timer_ascii(self, percent: float) -> str:
        """
        Generates a 'Reactor Core' style ASCII art with a wave animation.
        """
        p = max(0.0, min(1.0, percent))
        
        # Wave Animation Frames
        wave_chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█", "▇", "▆", "▅", "▄", "▃", "▁"]
        
        if worker.is_running:
            # Calculate wave position based on time
            t = time.time() * 10  # Speed of wave
            wave_idx = int(t) % len(wave_chars)
            wave_char = wave_chars[wave_idx]
        else:
            wave_char = " "

        # 8 levels of charge for the core
        levels = 8
        filled = int(p * levels)
        
        # Construct the tower
        art = []
        art.append(f"  /==[{wave_char}]==\\  ")
        
        for i in range(levels):
            level_idx = levels - 1 - i
            if level_idx < filled:
                # Filled segment
                bar = "██████"
                art.append(f"  |{bar}|  ")
            else:
                # Empty segment
                bar = "......"
                art.append(f"  |{bar}|  ")
        
        art.append("  \\======/  ")
        art.append(f"   {int(p*100):3d}%   ")
        
        return "\n".join(art)

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

            # Update Visual
            art = self.get_complex_timer_ascii(worker.progress)
            self.query_one("#timer-visual").update(art)

        except Exception as e:
            logger.debug(f"Status update error: {e}")

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        command = message.value.strip()
        if not command:
            return

        logger.info(f"CMD: {command}")
        log = self.query_one("#game_log")
        log.write(f"\n[bold]> {command}[/]")
        self.query_one("#command_input").value = ""

        try:
            parts = command.split()
            if not parts: return
            
            cmd = parts[0].upper()
            args = parts[1:]

            if cmd == "EXIT":
                worker.stop()
                self.exit()
            elif cmd == "START":
                interval = args[0] if len(args) > 0 else None
                worker.start(interval)
            elif cmd == "STOP":
                worker.stop()
            elif cmd == "STATUS":
                self.update_status_panel()
            elif cmd == "PRINT":
                await self.handle_print_command(args, log)
            else:
                log.write("[dim]Unknown command. Try 'START', 'PRINT', or 'EXIT'.[/]")
        except Exception as e:
            logger.error(f"Command failed: {command}", exc_info=True)
            log.write(f"[bold]ERROR: {e}[/]")

    async def handle_print_command(self, args, log):
        if not args:
            log.write("Usage: PRINT [CONTRACT|MISSION|OXYGEN] {ID}")
            return
        sub = args[0].upper()
        self.run_print_task(sub, args)

    @work(exclusive=True, thread=True)
    def run_print_task(self, sub, args):
        try:
            if sub == "ALL-CONTRACTS":
                printer_service.print_all_contracts()
            elif sub == "CONTRACT" and len(args) > 1:
                printer_service.print_contract(args[1].upper())
            elif sub == "MISSION" and len(args) > 1:
                printer_service.print_mission(args[1].upper())
            elif sub == "OXYGEN":
                printer_service.print_oxygen_bill()
            else:
                self.call_from_thread(self._update_log_ui, "[bold]INVALID PRINT PARAMETERS[/]")
        except Exception as e:
            logger.error(f"Print task failed: {sub}", exc_info=True)
