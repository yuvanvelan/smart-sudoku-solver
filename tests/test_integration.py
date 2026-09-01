"""
End-to-End Integration Tests for Smart Sudoku Solver.

Verifies the complete application workflow across SudokuBoard, SudokuSolver,
SudokuGenerator, and SudokuGUI components.
"""

import unittest
import tkinter as tk
from src.gui import SudokuGUI
from src.sudoku import SudokuBoard


class TestFullApplicationIntegration(unittest.TestCase):
    """End-to-end integration test suite."""

    def setUp(self) -> None:
        """Create a hidden Tk instance and SudokuGUI application."""
        self.root = tk.Tk()
        self.root.withdraw()  # Headless test execution
        self.app = SudokuGUI(self.root)

    def tearDown(self) -> None:
        """Destroy the Tk root window."""
        self.root.destroy()

    def test_full_create_then_solve_flow(self) -> None:
        """
        End-to-end user workflow:
        1. Open app (starts at Ready)
        2. Click 'Create Sudoku'
        3. Verify valid playable puzzle is displayed
        4. Click 'Solve Sudoku'
        5. Verify complete valid board is displayed and status updated
        """
        # Initial state
        self.assertEqual(self.app.status_label.cget("text"), "Ready")

        # Step 1: Create Sudoku
        self.app.on_create_sudoku()
        created_grid = self.app.get_grid_values()
        created_board = SudokuBoard(created_grid)

        self.assertTrue(created_board.is_valid_board())
        self.assertIsNotNone(created_board.find_empty_cell())
        self.assertIn("New Sudoku created", self.app.status_label.cget("text"))
        initial_clues_count = len(self.app.initial_clues)
        self.assertGreater(initial_clues_count, 0)

        # Step 2: Solve Sudoku
        self.app.on_solve_sudoku()
        solved_grid = self.app.get_grid_values()
        solved_board = SudokuBoard(solved_grid)

        # Verify board is completely filled and satisfies all constraints
        self.assertTrue(solved_board.is_valid_board())
        self.assertIsNone(solved_board.find_empty_cell())
        self.assertIn("Solution found", self.app.status_label.cget("text"))

        # Verify initial clues were preserved in their exact positions
        for r, c in self.app.initial_clues:
            self.assertEqual(solved_grid[r][c], created_grid[r][c])

    def test_multiple_consecutive_create_and_solve_cycles(self) -> None:
        """
        Verifies that the application can perform multiple consecutive
        Create -> Solve cycles without state corruption or leakage.
        """
        for cycle in range(1, 6):
            # Create
            self.app.on_create_sudoku()
            grid_after_create = self.app.get_grid_values()
            board_after_create = SudokuBoard(grid_after_create)
            self.assertTrue(board_after_create.is_valid_board())
            self.assertIsNotNone(board_after_create.find_empty_cell())

            # Solve
            self.app.on_solve_sudoku()
            grid_after_solve = self.app.get_grid_values()
            board_after_solve = SudokuBoard(grid_after_solve)
            self.assertTrue(board_after_solve.is_valid_board())
            self.assertIsNone(board_after_solve.find_empty_cell())
            self.assertIn("Solution found", self.app.status_label.cget("text"))

    def test_invalid_manually_modified_puzzle_conflict(self) -> None:
        """
        Simulates user creating a puzzle, then typing a conflicting number into a row.
        Clicking 'Solve Sudoku' must display a clean error message and not crash.
        """
        self.app.on_create_sudoku()

        # Find an empty cell in row 0
        empty_col = None
        for c in range(9):
            if (0, c) not in self.app.initial_clues:
                empty_col = c
                break

        self.assertIsNotNone(empty_col)

        # Place a number that already exists in row 0
        row_0_vals = [self.app.cells[0][c].get() for c in range(9) if self.app.cells[0][c].get()]
        self.assertGreater(len(row_0_vals), 0)
        duplicate_val = row_0_vals[0]

        # Insert duplicate value
        self.app.cells[0][empty_col].delete(0, tk.END)
        self.app.cells[0][empty_col].insert(0, duplicate_val)

        # Attempt to solve
        self.app.on_solve_sudoku()

        status_text = self.app.status_label.cget("text")
        self.assertIn("Invalid puzzle", status_text)

    def test_unsolvable_puzzle_graceful_handling(self) -> None:
        """
        Simulates user inputting an unsolvable puzzle (valid initially, but no valid complete solution).
        Clicking 'Solve Sudoku' must report 'No solution exists' without crashing.
        """
        self.app.clear_grid()

        # Input a known unsolvable board:
        blocked_grid = [
            [1, 2, 3, 4, 5, 6, 7, 8, 0],  # (0, 8) needs 9, but col 8 already has 9 at row 1
            [0, 0, 0, 0, 0, 0, 0, 0, 9],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        for r in range(9):
            for c in range(9):
                val = blocked_grid[r][c]
                if val != 0:
                    self.app.cells[r][c].insert(0, str(val))

        self.app.on_solve_sudoku()

        status_text = self.app.status_label.cget("text")
        self.assertIn("No solution exists", status_text)

    def test_already_solved_puzzle_handling(self) -> None:
        """
        Solving an already completed puzzle should report success without error.
        """
        self.app.clear_grid()
        solved_grid = [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9],
        ]
        for r in range(9):
            for c in range(9):
                self.app.cells[r][c].insert(0, str(solved_grid[r][c]))

        self.app.on_solve_sudoku()

        status_text = self.app.status_label.cget("text")
        self.assertIn("Solution found", status_text)


if __name__ == "__main__":
    unittest.main()
