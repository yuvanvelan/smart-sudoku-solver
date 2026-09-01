"""
Unit tests for the SudokuBoard model and validation utilities.
"""

import unittest
from src.sudoku import SudokuBoard, InvalidSudokuBoardError


class TestSudokuBoard(unittest.TestCase):
    """Test suite for SudokuBoard."""

    def setUp(self) -> None:
        """Sample valid boards for testing."""
        self.sample_valid_grid = [
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

        self.sample_solved_grid = [
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

    # --- 1. Valid Board Creation Tests ---
    def test_create_default_empty_board(self) -> None:
        """Creating a board without arguments should create an empty 9x9 board with all zeros."""
        board = SudokuBoard()
        for r in range(9):
            for c in range(9):
                self.assertEqual(board.get_cell(r, c), 0)
                self.assertTrue(board.is_empty(r, c))
        self.assertTrue(board.is_valid_board())

    def test_create_valid_board_from_grid(self) -> None:
        """Creating a board from a valid partially-filled grid should succeed."""
        board = SudokuBoard(self.sample_valid_grid)
        self.assertEqual(board.get_cell(0, 0), 5)
        self.assertEqual(board.get_cell(0, 1), 3)
        self.assertEqual(board.get_cell(0, 2), 0)
        self.assertTrue(board.is_valid_board())

    def test_create_valid_solved_board(self) -> None:
        """Creating a board from a complete valid grid should succeed."""
        board = SudokuBoard(self.sample_solved_grid)
        self.assertTrue(board.is_valid_board())
        self.assertIsNone(board.find_empty_cell())

    # --- 2. Invalid Dimensions Tests ---
    def test_invalid_row_count_too_few(self) -> None:
        """Board with fewer than 9 rows should raise InvalidSudokuBoardError."""
        short_grid = [[0] * 9 for _ in range(8)]
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(short_grid)

    def test_invalid_row_count_too_many(self) -> None:
        """Board with more than 9 rows should raise InvalidSudokuBoardError."""
        long_grid = [[0] * 9 for _ in range(10)]
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(long_grid)

    def test_invalid_column_count_too_few(self) -> None:
        """Board with a row of fewer than 9 columns should raise InvalidSudokuBoardError."""
        invalid_cols_grid = [[0] * 9 for _ in range(8)] + [[0] * 8]
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(invalid_cols_grid)

    def test_invalid_column_count_too_many(self) -> None:
        """Board with a row of more than 9 columns should raise InvalidSudokuBoardError."""
        invalid_cols_grid = [[0] * 9 for _ in range(8)] + [[0] * 10]
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(invalid_cols_grid)

    # --- 3. Invalid Values and Types Tests ---
    def test_invalid_negative_value(self) -> None:
        """Board with negative values should raise InvalidSudokuBoardError."""
        grid = [row[:] for row in self.sample_valid_grid]
        grid[0][2] = -1
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(grid)

    def test_invalid_value_greater_than_nine(self) -> None:
        """Board with values greater than 9 should raise InvalidSudokuBoardError."""
        grid = [row[:] for row in self.sample_valid_grid]
        grid[0][2] = 10
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(grid)

    def test_invalid_type_string(self) -> None:
        """Board with non-integer types (string) should raise InvalidSudokuBoardError."""
        grid = [row[:] for row in self.sample_valid_grid]
        grid[0][2] = "5"  # type: ignore
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(grid)

    def test_invalid_type_float(self) -> None:
        """Board with float values should raise InvalidSudokuBoardError."""
        grid = [row[:] for row in self.sample_valid_grid]
        grid[0][2] = 5.0  # type: ignore
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(grid)

    def test_invalid_type_boolean(self) -> None:
        """Board with boolean values (True/False) should raise InvalidSudokuBoardError."""
        grid = [row[:] for row in self.sample_valid_grid]
        grid[0][2] = True  # type: ignore
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(grid)

    # --- 4. Constraint Violations in Initial Board ---
    def test_duplicate_in_row_raises_error(self) -> None:
        """Initial board containing duplicate non-zero numbers in a row should raise InvalidSudokuBoardError."""
        grid = [row[:] for row in self.sample_valid_grid]
        grid[0][2] = 5  # Row 0 already has 5 at (0, 0)
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(grid)

    def test_duplicate_in_column_raises_error(self) -> None:
        """Initial board containing duplicate non-zero numbers in a column should raise InvalidSudokuBoardError."""
        grid = [row[:] for row in self.sample_valid_grid]
        grid[2][0] = 5  # Col 0 already has 5 at (0, 0)
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(grid)

    def test_duplicate_in_box_raises_error(self) -> None:
        """Initial board containing duplicate non-zero numbers in a 3x3 box should raise InvalidSudokuBoardError."""
        grid = [row[:] for row in self.sample_valid_grid]
        # Box top-left (0..2, 0..2) contains 5, 3, 6, 9, 8
        grid[1][1] = 8  # (2, 2) is already 8
        with self.assertRaises(InvalidSudokuBoardError):
            SudokuBoard(grid)

    # --- 5. Candidate Move Validation Tests (is_valid_move) ---
    def test_legal_candidate_move(self) -> None:
        """Placing a non-conflicting number in an empty cell should return True."""
        board = SudokuBoard(self.sample_valid_grid)
        # Cell (0, 2) is empty. Checking 4 (not in row 0, col 2, or top-left box)
        self.assertTrue(board.is_valid_move(0, 2, 4))
        # Checking 1 (not in row 0, col 2, or top-left box)
        self.assertTrue(board.is_valid_move(0, 2, 1))

    def test_illegal_candidate_row_conflict(self) -> None:
        """Candidate that appears in the same row should be rejected."""
        board = SudokuBoard(self.sample_valid_grid)
        # Row 0 contains 5, 3, 7. Trying to place 7 at (0, 2) should fail.
        self.assertFalse(board.is_valid_move(0, 2, 7))

    def test_illegal_candidate_col_conflict(self) -> None:
        """Candidate that appears in the same column should be rejected."""
        board = SudokuBoard(self.sample_valid_grid)
        # Col 2 contains 8. Trying to place 8 at (0, 2) should fail.
        self.assertFalse(board.is_valid_move(0, 2, 8))

    def test_illegal_candidate_box_conflict(self) -> None:
        """Candidate that appears in the same 3x3 box should be rejected."""
        board = SudokuBoard(self.sample_valid_grid)
        # Top-left box contains 5, 3, 6, 9, 8. Trying to place 9 at (0, 2) should fail.
        self.assertFalse(board.is_valid_move(0, 2, 9))

    def test_illegal_candidate_out_of_range(self) -> None:
        """Candidate values < 1 or > 9 or invalid types should return False."""
        board = SudokuBoard(self.sample_valid_grid)
        self.assertFalse(board.is_valid_move(0, 2, 0))
        self.assertFalse(board.is_valid_move(0, 2, 10))
        self.assertFalse(board.is_valid_move(0, 2, -1))
        self.assertFalse(board.is_valid_move(0, 2, "4"))  # type: ignore

    # --- 6. Finding Empty Cell Tests ---
    def test_find_empty_cell_present(self) -> None:
        """find_empty_cell should locate the first 0 cell in row-major order."""
        board = SudokuBoard(self.sample_valid_grid)
        # For sample_valid_grid, (0, 0)=5, (0, 1)=3, (0, 2)=0 -> first empty is (0, 2)
        self.assertEqual(board.find_empty_cell(), (0, 2))

    def test_find_empty_cell_empty_board(self) -> None:
        """On an empty board, the first empty cell should be (0, 0)."""
        board = SudokuBoard()
        self.assertEqual(board.find_empty_cell(), (0, 0))

    def test_find_empty_cell_full_board(self) -> None:
        """On a completed board, find_empty_cell should return None."""
        board = SudokuBoard(self.sample_solved_grid)
        self.assertIsNone(board.find_empty_cell())

    # --- 7. Cell Get/Set & Boundary Checking ---
    def test_get_and_set_cell(self) -> None:
        """Setting and getting cell values should accurately update state."""
        board = SudokuBoard()
        board.set_cell(4, 4, 9)
        self.assertEqual(board.get_cell(4, 4), 9)
        self.assertFalse(board.is_empty(4, 4))

        board.set_cell(4, 4, 0)
        self.assertEqual(board.get_cell(4, 4), 0)
        self.assertTrue(board.is_empty(4, 4))

    def test_out_of_bounds_coordinates(self) -> None:
        """Coordinates outside 0..8 should raise IndexError."""
        board = SudokuBoard()
        with self.assertRaises(IndexError):
            board.get_cell(-1, 0)
        with self.assertRaises(IndexError):
            board.get_cell(0, 9)
        with self.assertRaises(IndexError):
            board.set_cell(9, 9, 1)

    def test_set_cell_invalid_values(self) -> None:
        """Setting invalid values should raise ValueError or TypeError."""
        board = SudokuBoard()
        with self.assertRaises(ValueError):
            board.set_cell(0, 0, 10)
        with self.assertRaises(ValueError):
            board.set_cell(0, 0, -1)
        with self.assertRaises(TypeError):
            board.set_cell(0, 0, "5")  # type: ignore

    # --- 8. Copy and Isolation Tests ---
    def test_board_copy_isolation(self) -> None:
        """Mutating a copied board should not affect the original board."""
        board = SudokuBoard(self.sample_valid_grid)
        copied = board.copy()
        copied.set_cell(0, 2, 4)
        self.assertEqual(copied.get_cell(0, 2), 4)
        self.assertEqual(board.get_cell(0, 2), 0)


if __name__ == "__main__":
    unittest.main()
