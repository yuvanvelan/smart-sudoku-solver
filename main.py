"""
Smart Sudoku Solver
Main desktop application entry point.
"""

import tkinter as tk
from src.gui import SudokuGUI


def main() -> None:
    """Initializes and runs the Tkinter Smart Sudoku Solver application."""
    root = tk.Tk()
    app = SudokuGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
