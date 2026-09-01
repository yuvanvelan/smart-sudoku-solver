"""
Unit tests for the Tkinter SudokuGUI.
"""

import unittest
import tkinter as tk
from src.gui import SudokuGUI
from src.sudoku import SudokuBoard


class TestSudokuGUI(unittest.TestCase):
    """Test suite for SudokuGUI in headless/test mode."""

    def setUp(self) -> None:
        """Create a hidden Tk instance and SudokuGUI app for testing."""
        self.root = tk.Tk()
        self.root.withdraw()  # Keep window hidden during test runs
        self.app = SudokuGUI(self.root)

    def tearDown(self) -> None:
        """Destroy the Tk root window."""
        self.root.destroy()

    def test_gui_grid_initialization(self) -> None:
        """GUI should initialize with a 9x9 grid of Entry widgets."""
        self.assertEqual(len(self.app.cells), 9)
        for r in range(9):
            self.assertEqual(len(self.app.cells[r]), 9)
            for c in range(9):
                self.assertIsInstance(self.app.cells[r][c], tk.Entry)
                self.assertEqual(self.app.cells[r][c].get(), "")

    def test_cell_validation(self) -> None:
        """Validation helper should accept digits 1-9 or empty string, rejecting others."""
        self.assertTrue(self.app._validate_cell_entry(""))
        for digit in "123456789":
            self.assertTrue(self.app._validate_cell_entry(digit))

        self.assertFalse(self.app._validate_cell_entry("0"))
        self.assertFalse(self.app._validate_cell_entry("12"))
        self.assertFalse(self.app._validate_cell_entry("a"))
        self.assertFalse(self.app._validate_cell_entry("-1"))

    def test_create_sudoku_action(self) -> None:
        """Clicking 'Create Sudoku' should populate clues and update status."""
        self.app.on_create_sudoku()

        grid = self.app.get_grid_values()
        non_zero_cells = sum(1 for r in range(9) for c in range(9) if grid[r][c] != 0)

        self.assertGreater(non_zero_cells, 0)
        self.assertEqual(len(self.app.initial_clues), non_zero_cells)
        self.assertIn("New Sudoku created", self.app.status_label.cget("text"))

    def test_solve_sudoku_action(self) -> None:
        """Clicking 'Solve Sudoku' on a valid puzzle should complete the board."""
        # 1. Create a puzzle
        self.app.on_create_sudoku()
        initial_clues_count = len(self.app.initial_clues)

        # 2. Solve the puzzle
        self.app.on_solve_sudoku()

        solved_grid = self.app.get_grid_values()
        board = SudokuBoard(solved_grid)

        # Resulting board must be valid and complete
        self.assertTrue(board.is_valid_board())
        self.assertIsNone(board.find_empty_cell())
        self.assertIn("Solution found", self.app.status_label.cget("text"))

    def test_solve_empty_board_error(self) -> None:
        """Attempting to solve an empty grid should show an error message."""
        self.app.clear_grid()
        self.app.on_solve_sudoku()

        self.assertIn("Invalid puzzle", self.app.status_label.cget("text"))

    def test_solve_invalid_puzzle_conflict_error(self) -> None:
        """Attempting to solve a board with duplicate conflicting numbers should display an error."""
        self.app.clear_grid()
        # Put conflicting 5s in the same row
        self.app.cells[0][0].insert(0, "5")
        self.app.cells[0][1].insert(0, "5")

        self.app.on_solve_sudoku()

        status_text = self.app.status_label.cget("text")
        self.assertIn("Invalid puzzle", status_text)

    def test_difficulty_selection(self) -> None:
        """Setting difficulty should update current_difficulty and status."""
        for diff in ["easy", "medium", "hard", "expert"]:
            self.app.set_difficulty(diff)
            self.assertEqual(self.app.current_difficulty, diff)
            self.assertIn(diff.capitalize(), self.app.status_label.cget("text"))

    def test_clear_grid_action(self) -> None:
        """Clearing the grid should empty all cells and initial clues."""
        self.app.on_create_sudoku()
        self.assertGreater(len(self.app.initial_clues), 0)

        self.app.clear_grid()
        self.assertEqual(len(self.app.initial_clues), 0)
        grid = self.app.get_grid_values()
        self.assertTrue(all(val == 0 for row in grid for val in row))
        self.assertEqual(self.app.status_label.cget("text"), "Board cleared")


if __name__ == "__main__":
    unittest.main()
