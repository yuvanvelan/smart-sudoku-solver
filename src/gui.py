"""
Sudoku Tkinter Graphical User Interface.

This module provides a sleek, modern Dark Mode desktop GUI for the Smart Sudoku Solver,
featuring custom 3D capsule/pill buttons with vibrant gradients, solid extruded drop shadows,
a 4-level difficulty selector, AI Constraint Satisfaction (CSP) solver integration,
and performance telemetry metrics.
"""

import math
import tkinter as tk
from tkinter import font as tkfont
from typing import Dict, List, Optional, Set, Tuple

from src.sudoku import SudokuBoard, InvalidSudokuBoardError
from src.solver import SudokuSolver
from src.generator import SudokuGenerator


def hex_to_rgb(hex_str: str) -> Tuple[int, int, int]:
    """Converts a hex color code (#RRGGBB) to an RGB tuple."""
    hex_clean = hex_str.lstrip("#")
    return tuple(int(hex_clean[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore


def rgb_to_hex(rgb: Tuple[float, float, float]) -> str:
    """Converts an RGB tuple to a hex color string."""
    r = max(0, min(255, int(rgb[0])))
    g = max(0, min(255, int(rgb[1])))
    b = max(0, min(255, int(rgb[2])))
    return f"#{r:02x}{g:02x}{b:02x}"


def interpolate_color(c1: Tuple[int, int, int], c2: Tuple[int, int, int], factor: float) -> str:
    """Linear color interpolation between two RGB color tuples."""
    return rgb_to_hex((
        c1[0] + (c2[0] - c1[0]) * factor,
        c1[1] + (c2[1] - c1[1]) * factor,
        c1[2] + (c2[2] - c1[2]) * factor,
    ))


def adjust_brightness(hex_str: str, factor: float) -> str:
    """Adjusts the brightness of a hex color string."""
    r, g, b = hex_to_rgb(hex_str)
    return rgb_to_hex((r * factor, g * factor, b * factor))


class Capsule3DButton(tk.Canvas):
    """
    Custom 3D Capsule / Pill Button widget.

    Features:
    - Fully rounded capsule pill shape (half-circle ends).
    - Thick solid black border and extruded 3D solid black drop shadow.
    - Smooth vibrant horizontal color gradient fills matching modern arcade/neo-brutalist styles.
    - Interactive hover brightening and satisfying mechanical press-down animations.
    """

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command=None,
        width: int = 150,
        height: int = 46,
        gradient_start: str = "#00F2FE",
        gradient_end: str = "#00C9A7",
        shadow_color: str = "#000000",
        border_color: str = "#000000",
        text_color: str = "#FFFFFF",
        font: Optional[Tuple[str, int, str]] = None,
        bg: str = "#0B0F19",
        shadow_offset: int = 5,
        border_width: int = 3,
        is_active: bool = False,
    ) -> None:
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0)
        self.text: str = text
        self.command = command
        self.btn_w: int = width
        self.btn_h: int = height
        self.gradient_start: str = gradient_start
        self.gradient_end: str = gradient_end
        self.shadow_color: str = shadow_color
        self.border_color: str = border_color
        self.text_color: str = text_color
        self.btn_font = font if font is not None else ("Helvetica", 11, "bold")
        self.shadow_offset: int = shadow_offset
        self.border_width: int = border_width
        self.is_pressed: bool = False
        self.is_hovered: bool = False
        self.is_active: bool = is_active
        self.bg_color: str = bg

        # Event bindings
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        try:
            cursor_type = "pointinghand" if self.tk.call("tk", "windowingsystem") == "aqua" else "hand2"
            self.config(cursor=cursor_type)
        except Exception:
            pass

        self.draw()

    def set_active(self, active: bool) -> None:
        """Sets active state for toggle pills."""
        self.is_active = active
        self.draw()

    def set_gradient(self, start_color: str, end_color: str) -> None:
        """Updates gradient colors and redraws."""
        self.gradient_start = start_color
        self.gradient_end = end_color
        self.draw()

    def set_text(self, text: str) -> None:
        """Updates button label."""
        self.text = text
        self.draw()

    def draw(self) -> None:
        """Renders the 3D capsule button with shadow, gradient, border, and text."""
        self.delete("all")

        pill_h = self.btn_h - self.shadow_offset - 2
        radius = pill_h / 2.0
        pill_w = self.btn_w - 6

        x0 = 3
        y0 = 1

        press_y = (self.shadow_offset - 1) if self.is_pressed else 0

        # 1. Solid Black 3D Extruded Base Shadow
        if not self.is_pressed:
            sh_x = x0 + 1
            sh_y = y0 + self.shadow_offset

            # Shadow Capsule (Left arc, middle rectangle, right arc)
            self.create_arc(
                sh_x, sh_y, sh_x + 2 * radius, sh_y + 2 * radius,
                start=90, extent=180, fill=self.shadow_color, outline=self.shadow_color
            )
            self.create_rectangle(
                sh_x + radius, sh_y, sh_x + pill_w - radius, sh_y + 2 * radius,
                fill=self.shadow_color, outline=self.shadow_color
            )
            self.create_arc(
                sh_x + pill_w - 2 * radius, sh_y, sh_x + pill_w, sh_y + 2 * radius,
                start=270, extent=180, fill=self.shadow_color, outline=self.shadow_color
            )
            # Solid vertical fill connecting shadow to pill base
            self.create_rectangle(
                sh_x + radius, y0 + radius, sh_x + pill_w - radius, sh_y + radius,
                fill=self.shadow_color, outline=self.shadow_color
            )

        # 2. Pill Gradient Body
        py = y0 + press_y
        g_start = self.gradient_start
        g_end = self.gradient_end

        if self.is_hovered and not self.is_pressed:
            g_start = adjust_brightness(g_start, 1.15)
            g_end = adjust_brightness(g_end, 1.15)

        c1 = hex_to_rgb(g_start)
        c2 = hex_to_rgb(g_end)

        # Left circular cap fill
        self.create_arc(
            x0, py, x0 + 2 * radius, py + 2 * radius,
            start=90, extent=180, fill=rgb_to_hex(c1), outline=""
        )

        # Middle horizontal gradient slices
        num_strips = 18
        strip_w = (pill_w - 2 * radius) / num_strips
        for i in range(num_strips):
            sx1 = x0 + radius + i * strip_w
            sx2 = sx1 + strip_w + 1
            factor = (i + 0.5) / num_strips
            col = interpolate_color(c1, c2, factor)
            self.create_rectangle(sx1, py, sx2, py + 2 * radius, fill=col, outline="")

        # Right circular cap fill
        self.create_arc(
            x0 + pill_w - 2 * radius, py, x0 + pill_w, py + 2 * radius,
            start=270, extent=180, fill=rgb_to_hex(c2), outline=""
        )

        # 3. Outer Solid Black Border
        self.create_arc(
            x0, py, x0 + 2 * radius, py + 2 * radius,
            start=90, extent=180, style=tk.ARC, outline=self.border_color, width=self.border_width
        )
        self.create_line(
            x0 + radius, py, x0 + pill_w - radius, py,
            fill=self.border_color, width=self.border_width
        )
        self.create_arc(
            x0 + pill_w - 2 * radius, py, x0 + pill_w, py + 2 * radius,
            start=270, extent=180, style=tk.ARC, outline=self.border_color, width=self.border_width
        )
        self.create_line(
            x0 + radius, py + 2 * radius, x0 + pill_w - radius, py + 2 * radius,
            fill=self.border_color, width=self.border_width
        )

        # 4. Centered Bold Text
        tx = x0 + pill_w / 2.0
        ty = py + radius
        self.create_text(tx, ty, text=self.text, fill=self.text_color, font=self.btn_font)

    def _on_enter(self, e: tk.Event) -> None:
        self.is_hovered = True
        self.draw()

    def _on_leave(self, e: tk.Event) -> None:
        self.is_hovered = False
        self.is_pressed = False
        self.draw()

    def _on_press(self, e: tk.Event) -> None:
        self.is_pressed = True
        self.draw()

    def _on_release(self, e: tk.Event) -> None:
        if self.is_pressed:
            self.is_pressed = False
            self.draw()
            if self.command:
                self.command()


class SudokuGUI:
    """
    Sleek Dark Mode User Interface for Smart Sudoku Solver with 3D Capsule Pill Buttons.

    Structure:
    1. Header: Title, glowing AI badge, and CSP heuristic subtitle.
    2. Difficulty Selector: Capsule pill buttons for Easy, Medium, Hard, and Expert.
    3. 9x9 Sudoku Grid: High-contrast cells with distinct 3x3 box borders and clue styling.
    4. Action Controls: 3D Capsule Buttons ('GENERATE', 'SOLVE', 'CLEAR') with reference gradients.
    5. Status & Metrics Card: Real-time telemetry, dot indicator, and solver performance.
    """

    # Theme Color Palette (Obsidian & Neon Accents)
    COLOR_BG = "#0B0F19"                # Deep obsidian background
    COLOR_CARD = "#111827"              # Dark container surface
    COLOR_CARD_BORDER = "#1F2937"       # Subtle card border
    COLOR_TEXT_TITLE = "#F8FAFC"        # Pure white/slate header
    COLOR_TEXT_MUTED = "#94A3B8"        # Soft muted slate text
    COLOR_BADGE_BG = "#1E293B"          # Header pill badge background
    COLOR_BADGE_FG = "#38BDF8"          # Bright cyan badge text

    # Grid & Cell Palette
    COLOR_GRID_OUTER = "#334155"        # Grid outer border
    COLOR_BOX_BORDER = "#475569"        # 3x3 block divider
    COLOR_CELL_BORDER = "#1E293B"       # Inner cell separator
    COLOR_CELL_EMPTY_BG = "#1E293B"     # Empty cell background
    COLOR_CELL_EMPTY_FG = "#F8FAFC"     # User-entered digit color
    COLOR_CELL_FOCUS_BG = "#0F172A"     # Focused cell background
    COLOR_CELL_FOCUS_BORDER = "#38BDF8" # Focused cell border highlight

    # Puzzle State Palette
    COLOR_CELL_CLUE_BG = "#0F172A"      # Distinct background for initial puzzle clues
    COLOR_CELL_CLUE_FG = "#FFFFFF"      # Crisp white for initial clues (Bold)
    COLOR_CELL_SOLVED_BG = "#172554"    # Indigo/Blue tint for AI-solved cells
    COLOR_CELL_SOLVED_FG = "#60A5FA"    # Vibrant electric blue for AI-solved numbers

    # Capsule Button Gradients (from Reference Design)
    GRADIENT_SIGN_UP = ("#FF758C", "#FF2A85")     # Pink / Magenta (Reference Button 1)
    GRADIENT_LOGIN = ("#8B5CF6", "#6366F1")       # Purple / Lavender (Reference Button 2)
    GRADIENT_PLAY = ("#00F2FE", "#00C9A7")        # Mint / Teal (Reference Button 3)
    GRADIENT_SETTINGS = ("#00D2FF", "#2563EB")    # Electric Sky / Royal Blue (Reference Button 4)

    # Difficulty Gradients
    DIFF_GRADIENTS = {
        "easy": ("#00F2FE", "#10B981"),      # Mint / Emerald
        "medium": ("#00D2FF", "#2563EB"),    # Sky / Royal Blue
        "hard": ("#FBBF24", "#EA580C"),      # Amber / Orange
        "expert": ("#FF758C", "#E11D48"),    # Pink / Rose
    }
    DIFF_INACTIVE_GRADIENT = ("#1E293B", "#334155")

    # Status Indicators & Accents
    COLOR_STATUS_INFO = "#38BDF8"       # Cyan
    COLOR_STATUS_SUCCESS = "#10B981"    # Emerald
    COLOR_STATUS_ERROR = "#F43F5E"      # Rose
    COLOR_STATUS_ACTIVE = "#F59E0B"     # Amber

    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the Sudoku GUI.

        :param root: The root Tkinter window instance.
        """
        self.root: tk.Tk = root
        self.root.title("Smart Sudoku Solver")
        self.root.configure(bg=self.COLOR_BG)
        self.root.geometry("560x740")
        self.root.resizable(False, False)

        # Backend Components
        self.solver: SudokuSolver = SudokuSolver()
        self.generator: SudokuGenerator = SudokuGenerator(solver=self.solver)

        # Current selected difficulty
        self.current_difficulty: str = "medium"

        # Tracks which cells were generated as initial puzzle clues (row, col)
        self.initial_clues: Set[Tuple[int, int]] = set()

        # Grid of 81 Entry widgets
        self.cells: List[List[tk.Entry]] = []

        # Difficulty toggle buttons lookup
        self.diff_buttons: Dict[str, Capsule3DButton] = {}

        # Build UI layout
        self._build_ui()
        self.set_status("Ready", "info")

    def _build_ui(self) -> None:
        """Constructs and arranges all UI widgets."""
        main_container = tk.Frame(self.root, bg=self.COLOR_BG, padx=24, pady=16)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Header Section
        header_frame = tk.Frame(main_container, bg=self.COLOR_BG)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Glowing Pill Badge
        badge_frame = tk.Frame(
            header_frame,
            bg=self.COLOR_BADGE_BG,
            highlightthickness=1,
            highlightbackground="#334155",
            padx=10,
            pady=3,
        )
        badge_frame.pack(pady=(0, 5))

        badge_font = tkfont.Font(family="Helvetica", size=9, weight="bold")
        badge_label = tk.Label(
            badge_frame,
            text="AI POWERED  •  CSP MRV SOLVER",
            font=badge_font,
            bg=self.COLOR_BADGE_BG,
            fg=self.COLOR_BADGE_FG,
        )
        badge_label.pack()

        # Main Title
        title_font = tkfont.Font(family="Helvetica", size=22, weight="bold")
        title_label = tk.Label(
            header_frame,
            text="Smart Sudoku Solver",
            font=title_font,
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_TITLE,
        )
        title_label.pack()

        # Subtitle
        subtitle_font = tkfont.Font(family="Helvetica", size=10)
        subtitle_label = tk.Label(
            header_frame,
            text="Constraint Satisfaction Search with Minimum Remaining Values",
            font=subtitle_font,
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED,
        )
        subtitle_label.pack(pady=(2, 0))

        # 2. Difficulty Selector Bar with 3D Capsule Buttons
        diff_container = tk.Frame(main_container, bg=self.COLOR_BG)
        diff_container.pack(fill=tk.X, pady=(0, 12))

        diff_title_font = tkfont.Font(family="Helvetica", size=9, weight="bold")
        diff_title = tk.Label(
            diff_container,
            text="DIFFICULTY:",
            font=diff_title_font,
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED,
        )
        diff_title.pack(side=tk.LEFT, padx=(0, 8))

        diff_bar = tk.Frame(diff_container, bg=self.COLOR_BG)
        diff_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        difficulties = [
            ("easy", "EASY"),
            ("medium", "MEDIUM"),
            ("hard", "HARD"),
            ("expert", "EXPERT"),
        ]

        for key, label in difficulties:
            btn = Capsule3DButton(
                diff_bar,
                text=label,
                command=lambda d=key: self.set_difficulty(d),
                width=88,
                height=34,
                gradient_start=self.DIFF_INACTIVE_GRADIENT[0],
                gradient_end=self.DIFF_INACTIVE_GRADIENT[1],
                font=("Helvetica", 9, "bold"),
                bg=self.COLOR_BG,
                shadow_offset=3,
                border_width=2,
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.diff_buttons[key] = btn

        self._refresh_difficulty_buttons()

        # 3. 9x9 Sudoku Grid Section
        board_outer_frame = tk.Frame(
            main_container,
            bg=self.COLOR_GRID_OUTER,
            padx=3,
            pady=3,
            relief=tk.FLAT,
        )
        board_outer_frame.pack(pady=(0, 14))

        # Register single-digit validation
        vcmd = (self.root.register(self._validate_cell_entry), "%P")
        cell_font = tkfont.Font(family="Helvetica", size=16, weight="bold")

        self.cells = [[None for _ in range(9)] for _ in range(9)]  # type: ignore

        for box_row in range(3):
            for box_col in range(3):
                box_frame = tk.Frame(
                    board_outer_frame,
                    bg=self.COLOR_BOX_BORDER,
                    padx=1,
                    pady=1,
                )
                box_frame.grid(
                    row=box_row,
                    column=box_col,
                    padx=1,
                    pady=1,
                )

                for inner_r in range(3):
                    for inner_c in range(3):
                        r = box_row * 3 + inner_r
                        c = box_col * 3 + inner_c

                        entry = tk.Entry(
                            box_frame,
                            width=2,
                            font=cell_font,
                            justify="center",
                            validate="key",
                            validatecommand=vcmd,
                            bg=self.COLOR_CELL_EMPTY_BG,
                            fg=self.COLOR_CELL_EMPTY_FG,
                            insertbackground=self.COLOR_CELL_FOCUS_BORDER,
                            relief=tk.FLAT,
                            highlightthickness=1,
                            highlightbackground=self.COLOR_CELL_BORDER,
                            highlightcolor=self.COLOR_CELL_FOCUS_BORDER,
                        )
                        entry.grid(
                            row=inner_r,
                            column=inner_c,
                            padx=1,
                            pady=1,
                            ipady=7,
                            ipadx=5,
                        )

                        # Keyboard navigation bindings
                        entry.bind("<Up>", lambda e, row=r, col=c: self._navigate_grid(row - 1, col))
                        entry.bind("<Down>", lambda e, row=r, col=c: self._navigate_grid(row + 1, col))
                        entry.bind("<Left>", lambda e, row=r, col=c: self._navigate_grid(row, col - 1))
                        entry.bind("<Right>", lambda e, row=r, col=c: self._navigate_grid(row, col + 1))

                        self.cells[r][c] = entry

        # 4. Action Buttons Section (3D Capsule / Pill Buttons from Reference)
        buttons_frame = tk.Frame(main_container, bg=self.COLOR_BG)
        buttons_frame.pack(fill=tk.X, pady=(0, 14))

        # Centered container for buttons
        buttons_inner = tk.Frame(buttons_frame, bg=self.COLOR_BG)
        buttons_inner.pack(anchor="center")

        # 1. GENERATE Button (Mint/Teal gradient matching 'PLAY' in reference)
        self.btn_create = Capsule3DButton(
            buttons_inner,
            text="GENERATE",
            command=self.on_create_sudoku,
            width=155,
            height=48,
            gradient_start=self.GRADIENT_PLAY[0],
            gradient_end=self.GRADIENT_PLAY[1],
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_BG,
            shadow_offset=5,
            border_width=3,
        )
        self.btn_create.pack(side=tk.LEFT, padx=6)

        # 2. SOLVE Button (Electric Blue gradient matching 'SETTINGS' / 'LOGIN' in reference)
        self.btn_solve = Capsule3DButton(
            buttons_inner,
            text="SOLVE",
            command=self.on_solve_sudoku,
            width=155,
            height=48,
            gradient_start=self.GRADIENT_SETTINGS[0],
            gradient_end=self.GRADIENT_SETTINGS[1],
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_BG,
            shadow_offset=5,
            border_width=3,
        )
        self.btn_solve.pack(side=tk.LEFT, padx=6)

        # 3. CLEAR Button (Pink/Magenta gradient matching 'SIGN UP' in reference)
        self.btn_clear = Capsule3DButton(
            buttons_inner,
            text="CLEAR",
            command=self.clear_grid,
            width=120,
            height=48,
            gradient_start=self.GRADIENT_SIGN_UP[0],
            gradient_end=self.GRADIENT_SIGN_UP[1],
            font=("Helvetica", 11, "bold"),
            bg=self.COLOR_BG,
            shadow_offset=5,
            border_width=3,
        )
        self.btn_clear.pack(side=tk.LEFT, padx=6)

        # 5. Status & Telemetry Dashboard Card
        status_frame = tk.Frame(
            main_container,
            bg=self.COLOR_CARD,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.COLOR_CARD_BORDER,
            padx=14,
            pady=10,
        )
        status_frame.pack(fill=tk.X)

        # Top row: Status dot + Message
        status_header = tk.Frame(status_frame, bg=self.COLOR_CARD)
        status_header.pack(fill=tk.X)

        self.status_dot = tk.Label(
            status_header,
            text="●",
            font=tkfont.Font(family="Helvetica", size=12, weight="bold"),
            bg=self.COLOR_CARD,
            fg=self.COLOR_STATUS_INFO,
        )
        self.status_dot.pack(side=tk.LEFT, padx=(0, 6))

        status_font = tkfont.Font(family="Helvetica", size=10, weight="bold")
        self.status_label = tk.Label(
            status_header,
            text="Ready",
            font=status_font,
            bg=self.COLOR_CARD,
            fg=self.COLOR_STATUS_INFO,
            anchor="w",
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Bottom row: Metrics
        self.metrics_frame = tk.Frame(status_frame, bg=self.COLOR_CARD)
        self.metrics_frame.pack(fill=tk.X, pady=(6, 0))

        metrics_font = tkfont.Font(family="Helvetica", size=9)
        self.metrics_label = tk.Label(
            self.metrics_frame,
            text="Telemetry: -- ms | 0 assignments | 0 backtracks",
            font=metrics_font,
            bg=self.COLOR_CARD,
            fg=self.COLOR_TEXT_MUTED,
            anchor="w",
        )
        self.metrics_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def set_difficulty(self, difficulty: str) -> None:
        """
        Sets the active generation difficulty.

        :param difficulty: One of 'easy', 'medium', 'hard', 'expert'.
        """
        if difficulty in self.DIFF_GRADIENTS:
            self.current_difficulty = difficulty
            self._refresh_difficulty_buttons()
            self.set_status(f"Difficulty set to {difficulty.capitalize()}", "info")

    def _refresh_difficulty_buttons(self) -> None:
        """Updates visual active/inactive states of difficulty capsule buttons."""
        for key, btn in self.diff_buttons.items():
            if key == self.current_difficulty:
                g_start, g_end = self.DIFF_GRADIENTS[key]
                btn.set_gradient(g_start, g_end)
                btn.set_active(True)
            else:
                btn.set_gradient(self.DIFF_INACTIVE_GRADIENT[0], self.DIFF_INACTIVE_GRADIENT[1])
                btn.set_active(False)

    def _validate_cell_entry(self, val: str) -> bool:
        """
        Validates user typing in cell entries.
        Allows either empty string or a single digit from 1 to 9.

        :param val: Candidate string value.
        :return: True if valid, False otherwise.
        """
        return val == "" or (len(val) == 1 and val in "123456789")

    def _navigate_grid(self, target_row: int, target_col: int) -> None:
        """Focuses the cell at target coordinates if within bounds."""
        if 0 <= target_row < 9 and 0 <= target_col < 9:
            self.cells[target_row][target_col].focus_set()

    def set_status(self, message: str, status_type: str = "info") -> None:
        """
        Updates the status message and dot indicator with context-appropriate styling.

        :param message: Text string to display.
        :param status_type: One of 'info', 'success', 'error', 'active'.
        """
        color_map = {
            "info": self.COLOR_STATUS_INFO,
            "success": self.COLOR_STATUS_SUCCESS,
            "error": self.COLOR_STATUS_ERROR,
            "active": self.COLOR_STATUS_ACTIVE,
        }
        fg_color = color_map.get(status_type, self.COLOR_STATUS_INFO)
        self.status_label.config(text=message, fg=fg_color)
        self.status_dot.config(fg=fg_color)
        self.root.update_idletasks()

    def set_metrics(self, execution_ms: float, assignments: int, backtracks: int) -> None:
        """Updates the performance telemetry label."""
        text = f"Telemetry: {execution_ms:.2f} ms | {assignments} assignments | {backtracks} backtracks"
        self.metrics_label.config(text=text, fg=self.COLOR_BADGE_FG)
        self.root.update_idletasks()

    def get_grid_values(self) -> List[List[int]]:
        """
        Reads the 9x9 grid of integers from the entry widgets.
        Empty cells are represented as 0.

        :return: 9x9 list of integers.
        """
        grid: List[List[int]] = []
        for r in range(9):
            row_vals: List[int] = []
            for c in range(9):
                val_str = self.cells[r][c].get().strip()
                if val_str == "":
                    row_vals.append(SudokuBoard.EMPTY_CELL)
                else:
                    row_vals.append(int(val_str))
            grid.append(row_vals)
        return grid

    def clear_grid(self) -> None:
        """Clears all cells on the board and resets clue styles."""
        for r in range(9):
            for c in range(9):
                self.cells[r][c].delete(0, tk.END)
                self.cells[r][c].config(
                    bg=self.COLOR_CELL_EMPTY_BG,
                    fg=self.COLOR_CELL_EMPTY_FG,
                )
        self.initial_clues.clear()
        self.set_status("Board cleared", "info")
        self.metrics_label.config(
            text="Telemetry: -- ms | 0 assignments | 0 backtracks",
            fg=self.COLOR_TEXT_MUTED,
        )

    def on_create_sudoku(self) -> None:
        """
        Action callback for 'GENERATE' button.
        Generates a new valid Sudoku puzzle and renders it on the grid with distinct clue styling.
        """
        self.set_status(f"Generating {self.current_difficulty.capitalize()} puzzle...", "active")
        self.clear_grid()

        # Generate playable puzzle with the selected difficulty
        puzzle = self.generator.generate_puzzle(difficulty=self.current_difficulty, ensure_unique=True)

        # Populate grid and style clue cells
        clue_count = 0
        for r in range(9):
            for c in range(9):
                val = puzzle.get_cell(r, c)
                if val != SudokuBoard.EMPTY_CELL:
                    self.cells[r][c].insert(0, str(val))
                    self.cells[r][c].config(
                        bg=self.COLOR_CELL_CLUE_BG,
                        fg=self.COLOR_CELL_CLUE_FG,
                    )
                    self.initial_clues.add((r, c))
                    clue_count += 1
                else:
                    self.cells[r][c].config(
                        bg=self.COLOR_CELL_EMPTY_BG,
                        fg=self.COLOR_CELL_EMPTY_FG,
                    )

        self.set_status(
            f"New Sudoku created ({clue_count} clues, {self.current_difficulty.capitalize()})",
            "success",
        )

    def on_solve_sudoku(self) -> None:
        """
        Action callback for 'SOLVE' button.
        Reads grid, validates puzzle constraints, solves via CSP MRV Backtracking,
        and displays the complete solution with telemetry metrics.
        """
        self.set_status("Solving with AI (CSP + MRV)...", "active")

        # 1. Read current grid
        try:
            grid = self.get_grid_values()
        except Exception:
            self.set_status("Invalid puzzle: non-numeric inputs", "error")
            return

        # Check if the board is completely empty
        if all(cell == 0 for row in grid for cell in row):
            self.set_status("Invalid puzzle: board is completely empty", "error")
            return

        # 2. Instantiate and validate starting board
        try:
            board = SudokuBoard(grid)
        except InvalidSudokuBoardError as err:
            self.set_status(f"Invalid puzzle: {err}", "error")
            return
        except Exception as err:
            self.set_status(f"Invalid puzzle: {err}", "error")
            return

        # 3. Solve puzzle with AI solver
        solved = self.solver.solve(board, use_mrv=True)
        stats = self.solver.get_stats()

        if solved:
            # Display solution and highlight solved values
            for r in range(9):
                for c in range(9):
                    val = board.get_cell(r, c)
                    self.cells[r][c].delete(0, tk.END)
                    self.cells[r][c].insert(0, str(val))

                    # If this cell was not an original clue, style as AI-solved
                    if (r, c) not in self.initial_clues:
                        self.cells[r][c].config(
                            bg=self.COLOR_CELL_SOLVED_BG,
                            fg=self.COLOR_CELL_SOLVED_FG,
                        )
                    else:
                        self.cells[r][c].config(
                            bg=self.COLOR_CELL_CLUE_BG,
                            fg=self.COLOR_CELL_CLUE_FG,
                        )

            elapsed_ms = stats.get("execution_time", 0.0) * 1000  # type: ignore
            assignments = stats.get("assignments", 0)
            backtracks = stats.get("backtracks", 0)

            self.set_metrics(elapsed_ms, assignments, backtracks)
            self.set_status(
                f"Solution found in {elapsed_ms:.1f} ms ({assignments} assignments, {backtracks} backtracks)",
                "success",
            )
        else:
            self.set_status("No solution exists for this configuration", "error")
