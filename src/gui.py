"""
Sudoku Tkinter Graphical User Interface.

This module provides a clean, modern desktop GUI for the Smart Sudoku Solver,
allowing users to generate new Sudoku puzzles and solve them using the CSP AI solver.
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import Dict, List, Optional, Set, Tuple

from src.sudoku import SudokuBoard, InvalidSudokuBoardError
from src.solver import SudokuSolver
from src.generator import SudokuGenerator


class SudokuGUI:
    """
    Tkinter-based User Interface for Smart Sudoku Solver.

    Structure:
    1. Header: Application Title & Subtitle.
    2. 9x9 Sudoku Grid: Interactive cells with visually distinct 3x3 block borders.
    3. Action Buttons: 'Create Sudoku' and 'Solve Sudoku'.
    4. Status Area: Live feedback on actions, solver metrics, and validation errors.
    """

    # Color Palette (Tailored Slate & Vibrant Accents)
    COLOR_BG = "#F8FAFC"
    COLOR_CARD = "#FFFFFF"
    COLOR_BORDER_BOX = "#334155"       # Dark separator for 3x3 boxes
    COLOR_BORDER_CELL = "#CBD5E1"      # Subtle separator for cells
    COLOR_TEXT_MAIN = "#0F172A"
    COLOR_TEXT_MUTED = "#64748B"

    # Cell States
    COLOR_CELL_EMPTY_BG = "#FFFFFF"
    COLOR_CELL_EMPTY_FG = "#0F172A"

    COLOR_CELL_CLUE_BG = "#F1F5F9"      # Distinct soft background for generated clues
    COLOR_CELL_CLUE_FG = "#0F172A"      # Bold dark text for initial clues

    COLOR_CELL_SOLVED_BG = "#EFF6FF"    # Soft blue tint for AI-solved cells
    COLOR_CELL_SOLVED_FG = "#2563EB"    # Vibrant blue for AI-solved numbers

    # Buttons
    COLOR_BTN_CREATE = "#0D9488"        # Teal
    COLOR_BTN_CREATE_HOVER = "#0F766E"
    COLOR_BTN_SOLVE = "#2563EB"         # Royal Blue
    COLOR_BTN_SOLVE_HOVER = "#1D4ED8"
    COLOR_BTN_TEXT = "#FFFFFF"

    # Status Colors
    COLOR_STATUS_INFO = "#475569"
    COLOR_STATUS_SUCCESS = "#059669"
    COLOR_STATUS_ERROR = "#DC2626"
    COLOR_STATUS_ACTIVE = "#D97706"

    def __init__(self, root: tk.Tk) -> None:
        """
        Initialize the Sudoku GUI.

        :param root: The root Tkinter window instance.
        """
        self.root: tk.Tk = root
        self.root.title("Smart Sudoku Solver")
        self.root.configure(bg=self.COLOR_BG)
        self.root.geometry("540x660")
        self.root.resizable(False, False)

        # Backend Components
        self.solver: SudokuSolver = SudokuSolver()
        self.generator: SudokuGenerator = SudokuGenerator(solver=self.solver)

        # Tracks which cells were generated as initial puzzle clues (row, col)
        self.initial_clues: Set[Tuple[int, int]] = set()

        # Grid of 81 Entry widgets
        self.cells: List[List[tk.Entry]] = []

        # Build UI layout
        self._build_ui()
        self.set_status("Ready", "info")

    def _build_ui(self) -> None:
        """Constructs and arranges all UI widgets."""
        # Main container with padding
        main_container = tk.Frame(self.root, bg=self.COLOR_BG, padx=24, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)

        # 1. Header Section
        header_frame = tk.Frame(main_container, bg=self.COLOR_BG)
        header_frame.pack(fill=tk.X, pady=(0, 16))

        title_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        title_label = tk.Label(
            header_frame,
            text="Smart Sudoku Solver",
            font=title_font,
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MAIN,
        )
        title_label.pack()

        subtitle_font = tkfont.Font(family="Helvetica", size=10)
        subtitle_label = tk.Label(
            header_frame,
            text="Constraint Satisfaction AI with Backtracking & MRV",
            font=subtitle_font,
            bg=self.COLOR_BG,
            fg=self.COLOR_TEXT_MUTED,
        )
        subtitle_label.pack(pady=(2, 0))

        # 2. 9x9 Sudoku Grid Section
        # Outer border frame for the entire board
        board_outer_frame = tk.Frame(
            main_container,
            bg=self.COLOR_BORDER_BOX,
            padx=2,
            pady=2,
            relief=tk.FLAT,
        )
        board_outer_frame.pack(pady=(0, 20))

        # Register single-digit validation
        vcmd = (self.root.register(self._validate_cell_entry), "%P")

        cell_font = tkfont.Font(family="Helvetica", size=16, weight="bold")

        # Create 3x3 block subframes to achieve distinct thicker borders
        self.cells = [[None for _ in range(9)] for _ in range(9)]  # type: ignore

        for box_row in range(3):
            for box_col in range(3):
                box_frame = tk.Frame(
                    board_outer_frame,
                    bg=self.COLOR_BORDER_BOX,
                    padx=1,
                    pady=1,
                )
                box_frame.grid(
                    row=box_row,
                    column=box_col,
                    padx=1,
                    pady=1,
                )

                # Inside each 3x3 box frame, place 3x3 entry cells
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
                            relief=tk.FLAT,
                            highlightthickness=1,
                            highlightbackground=self.COLOR_BORDER_CELL,
                            highlightcolor=self.COLOR_BTN_SOLVE,
                        )
                        entry.grid(
                            row=inner_r,
                            column=inner_c,
                            padx=1,
                            pady=1,
                            ipady=8,
                            ipadx=6,
                        )

                        # Bind arrow keys for easy navigation
                        entry.bind("<Up>", lambda e, row=r, col=c: self._navigate_grid(row - 1, col))
                        entry.bind("<Down>", lambda e, row=r, col=c: self._navigate_grid(row + 1, col))
                        entry.bind("<Left>", lambda e, row=r, col=c: self._navigate_grid(row, col - 1))
                        entry.bind("<Right>", lambda e, row=r, col=c: self._navigate_grid(row, col + 1))

                        self.cells[r][c] = entry

        # 3. Action Buttons Section
        buttons_frame = tk.Frame(main_container, bg=self.COLOR_BG)
        buttons_frame.pack(fill=tk.X, pady=(0, 16))

        btn_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

        # Create Sudoku Button
        self.btn_create = tk.Button(
            buttons_frame,
            text="Create Sudoku",
            font=btn_font,
            bg=self.COLOR_BTN_CREATE,
            fg=self.COLOR_BTN_TEXT,
            activebackground=self.COLOR_BTN_CREATE_HOVER,
            activeforeground=self.COLOR_BTN_TEXT,
            relief=tk.FLAT,
            padx=16,
            pady=10,
            cursor="pointinghand" if self.root.tk.call("tk", "windowingsystem") == "aqua" else "hand2",
            command=self.on_create_sudoku,
        )
        self.btn_create.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 8))

        # Solve Sudoku Button
        self.btn_solve = tk.Button(
            buttons_frame,
            text="Solve Sudoku",
            font=btn_font,
            bg=self.COLOR_BTN_SOLVE,
            fg=self.COLOR_BTN_TEXT,
            activebackground=self.COLOR_BTN_SOLVE_HOVER,
            activeforeground=self.COLOR_BTN_TEXT,
            relief=tk.FLAT,
            padx=16,
            pady=10,
            cursor="pointinghand" if self.root.tk.call("tk", "windowingsystem") == "aqua" else "hand2",
            command=self.on_solve_sudoku,
        )
        self.btn_solve.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(8, 0))

        # 4. Status Area Section
        status_frame = tk.Frame(
            main_container,
            bg=self.COLOR_CARD,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=self.COLOR_BORDER_CELL,
            padx=12,
            pady=10,
        )
        status_frame.pack(fill=tk.X)

        status_font = tkfont.Font(family="Helvetica", size=11)
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=status_font,
            bg=self.COLOR_CARD,
            fg=self.COLOR_STATUS_INFO,
        )
        self.status_label.pack()

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
        Updates the status message with context-appropriate styling.

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
        """Clears all cells on the board."""
        for r in range(9):
            for c in range(9):
                self.cells[r][c].delete(0, tk.END)
                self.cells[r][c].config(
                    bg=self.COLOR_CELL_EMPTY_BG,
                    fg=self.COLOR_CELL_EMPTY_FG,
                )
        self.initial_clues.clear()

    def on_create_sudoku(self) -> None:
        """
        Action callback for 'Create Sudoku' button.
        Generates a new valid Sudoku puzzle and renders it on the grid.
        """
        self.set_status("Generating new Sudoku puzzle...", "active")
        self.clear_grid()

        # Generate playable puzzle
        puzzle = self.generator.generate_puzzle(difficulty="medium", ensure_unique=True)

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

        self.set_status(f"New Sudoku created ({clue_count} clues)", "success")

    def on_solve_sudoku(self) -> None:
        """
        Action callback for 'Solve Sudoku' button.
        Reads grid, validates puzzle constraints, solves via CSP MRV Backtracking,
        and displays the complete solution.
        """
        self.set_status("Solving...", "active")

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

            self.set_status(
                f"Solution found in {elapsed_ms:.1f} ms ({assignments} assignments, {backtracks} backtracks)",
                "success",
            )
        else:
            self.set_status("No solution exists for this configuration", "error")
