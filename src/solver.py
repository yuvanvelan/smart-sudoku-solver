"""
Sudoku Constraint Satisfaction Problem (CSP) Solver.

This module implements a Backtracking Search algorithm for solving standard
9x9 Sudoku puzzles modeled as a Constraint Satisfaction Problem.
"""

from typing import Dict, List, Optional, Tuple
from src.sudoku import SudokuBoard


class SudokuSolver:
    """
    Solves a standard 9x9 Sudoku puzzle using recursive Backtracking Search.

    CSP Formulation:
    - Variables: Empty cells on the board (row, col).
    - Domains: Candidate values (integers 1 to 9) that satisfy row, column,
      and 3x3 subgrid constraints.
    - Constraints:
      1. Row Uniqueness: No duplicate values in any row.
      2. Column Uniqueness: No duplicate values in any column.
      3. Box Uniqueness: No duplicate values in any 3x3 subgrid.
    """

    def __init__(self) -> None:
        """Initialize solver metrics."""
        self.assignments: int = 0
        self.backtracks: int = 0

    def get_candidates(self, board: SudokuBoard, row: int, col: int) -> List[int]:
        """
        Calculates all legal candidate values (domain) for cell (row, col).

        :param board: The SudokuBoard instance.
        :param row: Row index (0-8).
        :param col: Column index (0-8).
        :return: List of legal values from 1 to 9.
        """
        candidates: List[int] = []
        for val in range(1, 10):
            if board.is_valid_move(row, col, val):
                candidates.append(val)
        return candidates

    def select_unassigned_variable(self, board: SudokuBoard) -> Optional[Tuple[int, int]]:
        """
        Selects an unassigned (empty) variable/cell from the board.

        For this phase, a simple deterministic strategy is used:
        finding the first empty cell in row-major order (top-to-bottom, left-to-right).

        :param board: The SudokuBoard instance.
        :return: (row, col) coordinates of the selected cell, or None if board is complete.
        """
        return board.find_empty_cell()

    def solve(self, board: SudokuBoard) -> bool:
        """
        Solves the given Sudoku board in-place using recursive Backtracking Search.

        :param board: The SudokuBoard to solve.
        :return: True if a valid solution was found, False otherwise.
        """
        if not isinstance(board, SudokuBoard) or not board.is_valid_board():
            return False

        # Reset statistics for new solve run
        self.assignments = 0
        self.backtracks = 0

        return self._backtrack(board)

    def _backtrack(self, board: SudokuBoard) -> bool:
        """
        Recursive depth-first backtracking search algorithm.

        Algorithm steps:
        1. Base Case: If all variables are assigned (no empty cells), return True.
        2. Variable Selection: Choose an unassigned cell (row, col).
        3. Domain Calculation: Find all legal candidate values for (row, col).
        4. Value Assignment:
           - For each candidate value:
             a. Assign value to the cell.
             b. Increment assignment counter.
             c. Recursively call _backtrack.
             d. If recursive call succeeds, propagate True.
             e. If recursive call fails, undo assignment (backtrack) and increment backtrack counter.
        5. Failure: If all candidate values fail, return False.

        :param board: The SudokuBoard instance being modified in-place.
        :return: True if the subproblem is solvable, False otherwise.
        """
        # Step 1 & 2: Select an unassigned variable
        cell = self.select_unassigned_variable(board)
        if cell is None:
            # Base Case: All cells are filled and constraints are satisfied
            return True

        row, col = cell

        # Step 3: Compute domain of legal candidate values
        candidates = self.get_candidates(board, row, col)

        # Step 4: Try each candidate value
        for value in candidates:
            # Assign candidate value
            board.set_cell(row, col, value)
            self.assignments += 1

            # Recursively attempt to solve remaining board
            if self._backtrack(board):
                return True

            # Step 4e: Backtrack - undo the assignment on failure
            board.set_cell(row, col, SudokuBoard.EMPTY_CELL)
            self.backtracks += 1

        # Step 5: No candidate led to a valid solution
        return False

    def get_stats(self) -> Dict[str, int]:
        """
        Returns solver search statistics from the most recent run.

        :return: Dictionary containing 'assignments' and 'backtracks' counts.
        """
        return {
            "assignments": self.assignments,
            "backtracks": self.backtracks,
        }
