"""
Sudoku Board Model and Validation Utilities.

This module provides the core data structure and validation rules for
a standard 9x9 Sudoku puzzle.
"""

from typing import List, Optional, Tuple, Sequence


class InvalidSudokuBoardError(ValueError):
    """Exception raised when a Sudoku board has invalid dimensions, values, or constraint violations."""
    pass


class SudokuBoard:
    """
    Represents a standard 9x9 Sudoku board.

    Empty cells are internally represented by the integer 0.
    Filled cells contain integers from 1 to 9.
    """

    GRID_SIZE: int = 9
    BOX_SIZE: int = 3
    EMPTY_CELL: int = 0

    def __init__(self, initial_grid: Optional[Sequence[Sequence[int]]] = None) -> None:
        """
        Initialize the Sudoku board.

        If initial_grid is provided, it is validated and copied.
        If None, an empty 9x9 board (filled with 0s) is created.

        :param initial_grid: Optional 9x9 2D sequence of integers (0-9).
        :raises InvalidSudokuBoardError: If initial_grid does not meet Sudoku requirements.
        """
        if initial_grid is None:
            # Create an empty 9x9 board initialized with 0s
            self._grid: List[List[int]] = [
                [self.EMPTY_CELL for _ in range(self.GRID_SIZE)]
                for _ in range(self.GRID_SIZE)
            ]
        else:
            self._validate_and_load_grid(initial_grid)

    def _validate_and_load_grid(self, grid: Sequence[Sequence[int]]) -> None:
        """
        Validates the structure, types, values, and constraints of an input grid.

        :param grid: 2D sequence representing the candidate board.
        :raises InvalidSudokuBoardError: On any format or constraint violation.
        """
        # 1. Validate outer structure (must be a sequence of length 9)
        if not hasattr(grid, "__len__") or len(grid) != self.GRID_SIZE:
            raise InvalidSudokuBoardError(
                f"Board must have exactly {self.GRID_SIZE} rows. Found: {len(grid) if hasattr(grid, '__len__') else 'invalid'}"
            )

        new_grid: List[List[int]] = []

        # 2. Validate row dimensions, data types, and value ranges
        for r_idx, row in enumerate(grid):
            if not hasattr(row, "__len__") or len(row) != self.GRID_SIZE:
                raise InvalidSudokuBoardError(
                    f"Row {r_idx} must have exactly {self.GRID_SIZE} columns."
                )

            current_row: List[int] = []
            for c_idx, val in enumerate(row):
                # Ensure val is an integer and NOT a boolean (since bool is a subclass of int in Python)
                if type(val) is not int:
                    raise InvalidSudokuBoardError(
                        f"Cell at ({r_idx}, {c_idx}) must be an integer (0-9). Found type: {type(val).__name__} with value: {val!r}"
                    )
                if val < 0 or val > 9:
                    raise InvalidSudokuBoardError(
                        f"Cell at ({r_idx}, {c_idx}) must be an integer between 0 and 9. Found: {val}"
                    )
                current_row.append(val)
            new_grid.append(current_row)

        self._grid = new_grid

        # 3. Validate initial Sudoku constraints (no duplicates in rows, columns, or 3x3 boxes)
        if not self._check_all_constraints():
            raise InvalidSudokuBoardError(
                "Initial board violates Sudoku rules (duplicate numbers found in a row, column, or 3x3 box)."
            )

    def _check_all_constraints(self) -> bool:
        """
        Checks if the current board configuration satisfies row, column, and box constraints.
        Empty cells (0) are ignored.

        :return: True if valid, False otherwise.
        """
        for i in range(self.GRID_SIZE):
            if not self.is_row_valid(i):
                return False
            if not self.is_col_valid(i):
                return False

        for box_row in range(0, self.GRID_SIZE, self.BOX_SIZE):
            for box_col in range(0, self.GRID_SIZE, self.BOX_SIZE):
                if not self.is_box_valid(box_row, box_col):
                    return False

        return True

    def _validate_coordinates(self, row: int, col: int) -> None:
        """
        Validates that row and col indices are within board bounds (0 to 8).

        :param row: Row index (0-8).
        :param col: Column index (0-8).
        :raises IndexError: If coordinates are out of bounds.
        """
        if not (0 <= row < self.GRID_SIZE and 0 <= col < self.GRID_SIZE):
            raise IndexError(
                f"Coordinates ({row}, {col}) out of bounds for a {self.GRID_SIZE}x{self.GRID_SIZE} board."
            )

    def get_cell(self, row: int, col: int) -> int:
        """
        Returns the value at the given cell coordinates.

        :param row: Row index (0-8).
        :param col: Column index (0-8).
        :return: Integer value from 0 to 9.
        """
        self._validate_coordinates(row, col)
        return self._grid[row][col]

    def set_cell(self, row: int, col: int, value: int) -> None:
        """
        Sets the value of a specific cell.

        :param row: Row index (0-8).
        :param col: Column index (0-8).
        :param value: Integer value between 0 and 9.
        :raises IndexError: If coordinates are out of bounds.
        :raises TypeError: If value is not an integer.
        :raises ValueError: If value is not in range 0..9.
        """
        self._validate_coordinates(row, col)
        if type(value) is not int:
            raise TypeError(f"Value must be an integer (0-9). Got {type(value).__name__}.")
        if value < 0 or value > 9:
            raise ValueError(f"Value must be between 0 and 9. Got {value}.")

        self._grid[row][col] = value

    def is_empty(self, row: int, col: int) -> bool:
        """
        Checks whether the specified cell is empty (contains 0).

        :param row: Row index (0-8).
        :param col: Column index (0-8).
        :return: True if the cell is 0, False otherwise.
        """
        return self.get_cell(row, col) == self.EMPTY_CELL

    def find_empty_cell(self) -> Optional[Tuple[int, int]]:
        """
        Finds the first empty cell on the board using row-major order.

        :return: (row, col) tuple of the first empty cell, or None if the board is complete.
        """
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                if self._grid[r][c] == self.EMPTY_CELL:
                    return (r, c)
        return None

    def get_row(self, row: int) -> List[int]:
        """Returns a copy of the specified row as a list."""
        if not (0 <= row < self.GRID_SIZE):
            raise IndexError(f"Row index {row} out of bounds.")
        return list(self._grid[row])

    def get_col(self, col: int) -> List[int]:
        """Returns a copy of the specified column as a list."""
        if not (0 <= col < self.GRID_SIZE):
            raise IndexError(f"Column index {col} out of bounds.")
        return [self._grid[r][col] for r in range(self.GRID_SIZE)]

    def get_box(self, row: int, col: int) -> List[int]:
        """
        Returns all values in the 3x3 subgrid containing cell (row, col).

        :param row: Row index (0-8).
        :param col: Column index (0-8).
        :return: List of 9 integers representing the 3x3 box contents.
        """
        self._validate_coordinates(row, col)
        start_row = (row // self.BOX_SIZE) * self.BOX_SIZE
        start_col = (col // self.BOX_SIZE) * self.BOX_SIZE

        box_values: List[int] = []
        for r in range(start_row, start_row + self.BOX_SIZE):
            for c in range(start_col, start_col + self.BOX_SIZE):
                box_values.append(self._grid[r][c])
        return box_values

    def is_row_valid(self, row: int) -> bool:
        """
        Validates that a row contains no duplicate numbers (ignoring 0).

        :param row: Row index (0-8).
        :return: True if row is valid, False otherwise.
        """
        values = [v for v in self.get_row(row) if v != self.EMPTY_CELL]
        return len(values) == len(set(values))

    def is_col_valid(self, col: int) -> bool:
        """
        Validates that a column contains no duplicate numbers (ignoring 0).

        :param col: Column index (0-8).
        :return: True if column is valid, False otherwise.
        """
        values = [v for v in self.get_col(col) if v != self.EMPTY_CELL]
        return len(values) == len(set(values))

    def is_box_valid(self, row: int, col: int) -> bool:
        """
        Validates that the 3x3 subgrid containing cell (row, col) contains no duplicates (ignoring 0).

        :param row: Any row index within the box (0-8).
        :param col: Any column index within the box (0-8).
        :return: True if the subgrid is valid, False otherwise.
        """
        values = [v for v in self.get_box(row, col) if v != self.EMPTY_CELL]
        return len(values) == len(set(values))

    def is_valid_move(self, row: int, col: int, value: int) -> bool:
        """
        Checks whether placing 'value' at (row, col) is legal according to Sudoku rules.

        A move is valid if:
        1. 1 <= value <= 9
        2. 'value' does not already appear in the same row (excluding cell itself)
        3. 'value' does not already appear in the same column (excluding cell itself)
        4. 'value' does not already appear in the same 3x3 box (excluding cell itself)

        :param row: Row index (0-8).
        :param col: Column index (0-8).
        :param value: Candidate value to check (1-9).
        :return: True if the move is legal, False otherwise.
        """
        self._validate_coordinates(row, col)

        if type(value) is not int or value < 1 or value > 9:
            return False

        # Check row constraint
        for c in range(self.GRID_SIZE):
            if c != col and self._grid[row][c] == value:
                return False

        # Check column constraint
        for r in range(self.GRID_SIZE):
            if r != row and self._grid[r][col] == value:
                return False

        # Check 3x3 box constraint
        start_row = (row // self.BOX_SIZE) * self.BOX_SIZE
        start_col = (col // self.BOX_SIZE) * self.BOX_SIZE
        for r in range(start_row, start_row + self.BOX_SIZE):
            for c in range(start_col, start_col + self.BOX_SIZE):
                if (r != row or c != col) and self._grid[r][c] == value:
                    return False

        return True

    def is_valid_board(self) -> bool:
        """
        Verifies if the entire current board violates any Sudoku constraints.

        :return: True if all rows, columns, and 3x3 boxes are valid.
        """
        return self._check_all_constraints()

    def to_list(self) -> List[List[int]]:
        """
        Returns a deep copy of the board as a 9x9 list of integers.

        :return: 2D list copy of the grid.
        """
        return [list(row) for row in self._grid]

    def copy(self) -> "SudokuBoard":
        """
        Creates an independent deep copy of this SudokuBoard instance.

        :return: A new SudokuBoard with identical state.
        """
        return SudokuBoard(self.to_list())

    def __str__(self) -> str:
        """
        Returns a formatted, human-readable ASCII representation of the board.
        """
        lines: List[str] = []
        for r in range(self.GRID_SIZE):
            if r > 0 and r % self.BOX_SIZE == 0:
                lines.append("------+-------+------")
            row_chars = []
            for c in range(self.GRID_SIZE):
                if c > 0 and c % self.BOX_SIZE == 0:
                    row_chars.append("|")
                val = self._grid[r][c]
                row_chars.append(str(val) if val != self.EMPTY_CELL else ".")
            lines.append(" ".join(row_chars))
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"SudokuBoard(grid={self._grid!r})"
