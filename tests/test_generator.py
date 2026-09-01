"""
Unit tests for SudokuGenerator.
"""

import unittest
from src.sudoku import SudokuBoard
from src.solver import SudokuSolver
from src.generator import SudokuGenerator


class TestSudokuGenerator(unittest.TestCase):
    """Test suite for SudokuGenerator."""

    def setUp(self) -> None:
        """Initialize generator and solver instances."""
        self.generator = SudokuGenerator(seed=42)
        self.solver = SudokuSolver()

    def test_generate_complete_board_dimensions_and_validity(self) -> None:
        """Complete board must be a 9x9 grid with numbers 1-9, no empty cells, and valid constraints."""
        board = self.generator.generate_complete_board()

        self.assertIsInstance(board, SudokuBoard)
        self.assertTrue(board.is_valid_board())
        self.assertIsNone(board.find_empty_cell())

        # Check values
        for r in range(9):
            for c in range(9):
                val = board.get_cell(r, c)
                self.assertGreaterEqual(val, 1)
                self.assertLessEqual(val, 9)

    def test_generate_puzzle_dimensions_and_values(self) -> None:
        """Generated puzzle must be 9x9, contain values 0-9, and satisfy constraints."""
        puzzle = self.generator.generate_puzzle(difficulty="medium")

        self.assertIsInstance(puzzle, SudokuBoard)
        self.assertTrue(puzzle.is_valid_board())

        # Check values in 0..9
        for r in range(9):
            for c in range(9):
                val = puzzle.get_cell(r, c)
                self.assertGreaterEqual(val, 0)
                self.assertLessEqual(val, 9)

    def test_generate_puzzle_not_fully_solved(self) -> None:
        """Generated puzzle must contain empty cells (0s)."""
        puzzle = self.generator.generate_puzzle(difficulty="easy")

        empty_count = sum(row.count(0) for row in puzzle.to_list())
        self.assertGreater(empty_count, 0)
        self.assertIsNotNone(puzzle.find_empty_cell())

    def test_generate_puzzle_is_solvable(self) -> None:
        """The generated puzzle must be solvable to a complete valid board by SudokuSolver."""
        puzzle = self.generator.generate_puzzle(difficulty="medium")
        puzzle_copy = puzzle.copy()

        solved = self.solver.solve(puzzle_copy, use_mrv=True)
        self.assertTrue(solved)
        self.assertTrue(puzzle_copy.is_valid_board())
        self.assertIsNone(puzzle_copy.find_empty_cell())

    def test_generate_puzzle_has_unique_solution(self) -> None:
        """Generated puzzle with ensure_unique=True must have exactly one solution."""
        puzzle = self.generator.generate_puzzle(difficulty="easy", ensure_unique=True)
        self.assertTrue(self.generator.has_unique_solution(puzzle))
        self.assertEqual(self.solver.count_solutions(puzzle, limit=2), 1)

    def test_generate_multiple_puzzles_are_distinct(self) -> None:
        """Multiple generation calls with different random states should yield different puzzles."""
        gen_unseeded = SudokuGenerator()
        puzzles = [gen_unseeded.generate_puzzle(difficulty="easy").to_list() for _ in range(3)]

        # Verify not all 3 generated puzzles are identical
        self.assertTrue(
            puzzles[0] != puzzles[1] or puzzles[1] != puzzles[2],
            "Generated puzzles should vary with randomness.",
        )

    def test_generate_puzzle_difficulty_levels(self) -> None:
        """Higher difficulty levels should generally remove more cells."""
        puzzle_easy = self.generator.generate_puzzle(difficulty="easy")
        puzzle_hard = self.generator.generate_puzzle(difficulty="hard")

        empty_easy = sum(row.count(0) for row in puzzle_easy.to_list())
        empty_hard = sum(row.count(0) for row in puzzle_hard.to_list())

        self.assertGreater(empty_hard, empty_easy)


if __name__ == "__main__":
    unittest.main()
