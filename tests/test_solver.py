"""
Unit tests for SudokuSolver (CSP Backtracking Search and MRV Heuristic).
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

    def test_solve_valid_sudoku_with_mrv(self) -> None:
        """Solver using MRV should find the correct solution for a known valid Sudoku."""
        board = SudokuBoard(self.solvable_puzzle)
        solved = self.solver.solve(board, use_mrv=True)

        self.assertTrue(solved)
        self.assertEqual(board.to_list(), self.expected_solution)
        self.assertTrue(board.is_valid_board())
        self.assertIsNone(board.find_empty_cell())

    def test_solve_valid_sudoku_simple_search(self) -> None:
        """Solver using simple variable selection should also find the correct solution."""
        board = SudokuBoard(self.solvable_puzzle)
        solved = self.solver.solve(board, use_mrv=False)

        self.assertTrue(solved)
        self.assertEqual(board.to_list(), self.expected_solution)
        self.assertTrue(board.is_valid_board())
        self.assertIsNone(board.find_empty_cell())

    def test_solve_resulting_grid_is_complete_and_valid(self) -> None:
        """The solved board must be fully filled with no zeroes and adhere to all rules."""
        board = SudokuBoard(self.solvable_puzzle)
        self.solver.solve(board, use_mrv=True)

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
        solved = self.solver.solve(board, use_mrv=True)

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
        """An unsolvable puzzle should return False."""
        blocked_grid = [
            [1, 2, 3, 4, 5, 6, 7, 8, 0],  # (0, 8) must be 9
            [0, 0, 0, 0, 0, 0, 0, 0, 9],  # Col 8 already has 9 at row 1
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        board = SudokuBoard(blocked_grid)
        solved = self.solver.solve(board, use_mrv=True)
        self.assertFalse(solved)

    def test_get_all_unassigned_candidates(self) -> None:
        """Verify get_all_unassigned_candidates returns domains for all empty cells."""
        board = SudokuBoard(self.solvable_puzzle)
        domains = self.solver.get_all_unassigned_candidates(board)

        # Count total empty cells in solvable_puzzle
        total_empty = sum(row.count(0) for row in self.solvable_puzzle)
        self.assertEqual(len(domains), total_empty)

        # Check domain for known cell (0, 2)
        self.assertEqual(domains[(0, 2)], [1, 2, 4])

        # Ensure no filled cells are in domains dictionary
        self.assertNotIn((0, 0), domains)
        self.assertNotIn((0, 1), domains)

    def test_select_unassigned_variable_mrv_selects_smallest_domain(self) -> None:
        """MRV should choose the cell with the smallest domain over row-major order."""
        # Create a board where cell (4, 4) has only 1 legal candidate, while (0, 2) has 3
        # In sample_valid_grid:
        # Let's construct a row where 8 numbers are filled in row 4:
        custom_grid = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],  # (0, 2) has 3 candidates [1, 2, 4]
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 2, 6, 8, 0, 3, 7, 9, 1],  # Cell (4, 4) only has candidate 5 (domain size 1)
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]
        board = SudokuBoard(custom_grid)

        # Simple selection would pick (0, 2)
        self.assertEqual(self.solver.select_unassigned_variable_simple(board), (0, 2))

        # MRV must pick (4, 4) because it has domain size 1
        self.assertEqual(self.solver.select_unassigned_variable_mrv(board), (4, 4))
        self.assertEqual(len(self.solver.get_candidates(board, 4, 4)), 1)

    def test_mrv_contradiction_handling_zero_candidates(self) -> None:
        """MRV should immediately select a cell with 0 candidates to trigger instant failure."""
        blocked_grid = [
            [1, 2, 3, 4, 5, 6, 7, 8, 0],  # Cell (0, 8) has 0 candidates due to 9 at (1, 8)
            [0, 0, 0, 0, 0, 0, 0, 0, 9],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        board = SudokuBoard(blocked_grid)

        # MRV identifies (0, 8) with domain size 0
        selected = self.solver.select_unassigned_variable_mrv(board)
        self.assertEqual(selected, (0, 8))
        self.assertEqual(len(self.solver.get_candidates(board, 0, 8)), 0)

    def test_mrv_vs_simple_performance_comparison(self) -> None:
        """MRV should dramatically reduce assignments and backtracks compared to simple search."""
        # 1. Solve with simple variable selection
        board_simple = SudokuBoard(self.solvable_puzzle)
        solver_simple = SudokuSolver()
        solved_simple = solver_simple.solve(board_simple, use_mrv=False)
        self.assertTrue(solved_simple)
        stats_simple = solver_simple.get_stats()

        # 2. Solve with MRV variable selection
        board_mrv = SudokuBoard(self.solvable_puzzle)
        solver_mrv = SudokuSolver()
        solved_mrv = solver_mrv.solve(board_mrv, use_mrv=True)
        self.assertTrue(solved_mrv)
        stats_mrv = solver_mrv.get_stats()

        # MRV should have significantly fewer assignments and backtracks
        self.assertLess(stats_mrv["assignments"], stats_simple["assignments"])
        self.assertLess(stats_mrv["backtracks"], stats_simple["backtracks"])
        self.assertGreater(stats_simple["assignments"], 1000)
        self.assertLess(stats_mrv["assignments"], 100)


if __name__ == "__main__":
    unittest.main()
