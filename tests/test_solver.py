"""
Unit tests for SudokuSolver (CSP Backtracking Search).
"""

import unittest
from src.sudoku import SudokuBoard
from src.solver import SudokuSolver


class TestSudokuSolver(unittest.TestCase):
    """Test suite for SudokuSolver."""

    def setUp(self) -> None:
        """Set up test puzzles and solver instance."""
        self.solver = SudokuSolver()

        # Known solvable puzzle
        self.solvable_puzzle = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]

        self.expected_solution = [
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

        # Solved puzzle
        self.solved_puzzle = [
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

    def test_solve_valid_sudoku(self) -> None:
        """Solver should find the correct solution for a known valid Sudoku."""
        board = SudokuBoard(self.solvable_puzzle)
        solved = self.solver.solve(board)

        self.assertTrue(solved)
        self.assertEqual(board.to_list(), self.expected_solution)
        self.assertTrue(board.is_valid_board())
        self.assertIsNone(board.find_empty_cell())

    def test_solve_resulting_grid_is_complete_and_valid(self) -> None:
        """The solved board must be fully filled with no zeroes and adhere to all rules."""
        board = SudokuBoard(self.solvable_puzzle)
        self.solver.solve(board)

        for r in range(9):
            for c in range(9):
                val = board.get_cell(r, c)
                self.assertGreaterEqual(val, 1)
                self.assertLessEqual(val, 9)
                self.assertFalse(board.is_empty(r, c))

        self.assertTrue(board.is_valid_board())

    def test_solve_already_solved_puzzle(self) -> None:
        """Solving an already solved puzzle should immediately return True."""
        board = SudokuBoard(self.solved_puzzle)
        solved = self.solver.solve(board)

        self.assertTrue(solved)
        self.assertEqual(board.to_list(), self.solved_puzzle)
        stats = self.solver.get_stats()
        self.assertEqual(stats["assignments"], 0)
        self.assertEqual(stats["backtracks"], 0)

    def test_solve_invalid_input(self) -> None:
        """Passing non-board or malformed objects should return False."""
        self.assertFalse(self.solver.solve("not a board"))  # type: ignore
        self.assertFalse(self.solver.solve(None))  # type: ignore

    def test_solve_unsolvable_puzzle(self) -> None:
        """
        An unsolvable puzzle (where initial non-conflicting placements make
        a valid completion impossible) should return False.
        """
        # Puzzle with impossible configuration in the first box / row
        unsolvable_grid = [
            [5, 1, 6, 8, 4, 9, 7, 3, 2],
            [3, 0, 0, 6, 0, 5, 0, 0, 0],
            [8, 0, 9, 7, 0, 0, 0, 6, 5],
            [1, 3, 5, 0, 6, 0, 9, 0, 7],
            [4, 7, 2, 5, 9, 1, 0, 0, 6],
            [9, 6, 8, 3, 7, 0, 0, 5, 0],
            [2, 5, 3, 1, 8, 6, 0, 7, 4],
            [6, 8, 4, 2, 0, 7, 5, 0, 0],
            [7, 9, 1, 0, 5, 0, 6, 0, 8],
        ]
        # Force a contradiction: row 1 col 1 cannot take any number because 1..9 are blocked
        # Modify to ensure unsolvability
        unsolvable_grid[1][1] = 0
        unsolvable_grid[1][2] = 0

        # Construct a guaranteed unsolvable board:
        # e.g., cell (0, 0)=1, (0, 1)=2, (0, 2)=3, (1, 0)=4, (1, 1)=5, (1, 2)=6, (2, 0)=7, (2, 1)=8
        # and in row 2 all remaining cells block '9'
        blocked_grid = [
            [1, 2, 3, 4, 5, 6, 7, 8, 0],  # Cell (0, 8) must be 9
            [0, 0, 0, 0, 0, 0, 0, 0, 9],  # Col 8 has 9 at row 1
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        # (0, 8) needs 9 to complete row 0, but col 8 already has 9 at (1, 8).
        # This is a valid initial board (no duplicates in any row/col/box yet),
        # but (0, 8) has candidate domain empty!
        board = SudokuBoard(blocked_grid)
        solved = self.solver.solve(board)
        self.assertFalse(solved)

    def test_solver_statistics(self) -> None:
        """Verify solver records non-zero assignments and backtracks when solving a puzzle."""
        board = SudokuBoard(self.solvable_puzzle)
        self.solver.solve(board)

        stats = self.solver.get_stats()
        self.assertIn("assignments", stats)
        self.assertIn("backtracks", stats)
        self.assertGreater(stats["assignments"], 0)
        self.assertGreaterEqual(stats["backtracks"], 0)
        self.assertEqual(stats["assignments"], self.solver.assignments)
        self.assertEqual(stats["backtracks"], self.solver.backtracks)

    def test_get_candidates(self) -> None:
        """Verify get_candidates returns the correct legal domain for a given cell."""
        board = SudokuBoard(self.solvable_puzzle)
        # For cell (0, 2): row 0 has {5, 3, 7}, col 2 has {8}, box has {5, 3, 6, 9, 8}
        # Available values in 1..9 excluding {3, 5, 6, 7, 8, 9} -> {1, 2, 4}
        candidates = self.solver.get_candidates(board, 0, 2)
        self.assertEqual(candidates, [1, 2, 4])

    def test_select_unassigned_variable(self) -> None:
        """Verify select_unassigned_variable selects the first empty cell in row-major order."""
        board = SudokuBoard(self.solvable_puzzle)
        self.assertEqual(self.solver.select_unassigned_variable(board), (0, 2))


if __name__ == "__main__":
    unittest.main()
