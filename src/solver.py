"""
Sudoku Constraint Satisfaction Problem (CSP) Solver.

This module implements Backtracking Search algorithms for solving standard
9x9 Sudoku puzzles modeled as a Constraint Satisfaction Problem, supporting both
simple variable selection and the Minimum Remaining Values (MRV) heuristic.
"""

import time
from typing import Dict, List, Optional, Tuple, Union
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

    Heuristics:
    - MRV (Minimum Remaining Values / Most Constrained Variable):
      Selects the unassigned cell with the smallest domain of legal candidates.
      Prunes the search space early by triggering fast failure detection on dead-ends.
    """

    def __init__(self) -> None:
        """Initialize solver metrics."""
        self.assignments: int = 0
        self.backtracks: int = 0
        self.execution_time: float = 0.0

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

    def get_all_unassigned_candidates(
        self, board: SudokuBoard
    ) -> Dict[Tuple[int, int], List[int]]:
        """
        Calculates candidate domains for all unassigned (empty) cells on the board.

        :param board: The SudokuBoard instance.
        :return: Dictionary mapping (row, col) coordinates to their list of candidate values.
        """
        domains: Dict[Tuple[int, int], List[int]] = {}
        for r in range(board.GRID_SIZE):
            for c in range(board.GRID_SIZE):
                if board.is_empty(r, c):
                    domains[(r, c)] = self.get_candidates(board, r, c)
        return domains

    def select_unassigned_variable_simple(
        self, board: SudokuBoard
    ) -> Optional[Tuple[int, int]]:
        """
        Selects an unassigned variable using a simple deterministic strategy
        (first empty cell in row-major order).

        :param board: The SudokuBoard instance.
        :return: (row, col) coordinates of first empty cell, or None if board is complete.
        """
        return board.find_empty_cell()

    def select_unassigned_variable_mrv(
        self, board: SudokuBoard
    ) -> Optional[Tuple[int, int]]:
        """
        Selects the unassigned variable with the Minimum Remaining Values (MRV).

        Finds the empty cell with the fewest legal candidate values.
        If an empty cell has 0 candidates (contradiction / dead-end), it is returned
        immediately to trigger an instant backtrack without expanding futile branches.

        :param board: The SudokuBoard instance.
        :return: (row, col) of the most constrained cell, or None if all cells are filled.
        """
        min_candidates_count = float("inf")
        best_cell: Optional[Tuple[int, int]] = None

        for r in range(board.GRID_SIZE):
            for c in range(board.GRID_SIZE):
                if board.is_empty(r, c):
                    num_candidates = len(self.get_candidates(board, r, c))

                    # Immediate contradiction: 0 candidates means this branch cannot succeed
                    if num_candidates == 0:
                        return (r, c)

                    if num_candidates < min_candidates_count:
                        min_candidates_count = num_candidates
                        best_cell = (r, c)

        return best_cell

    def select_unassigned_variable(
        self, board: SudokuBoard, use_mrv: bool = True
    ) -> Optional[Tuple[int, int]]:
        """
        Selects an unassigned variable using MRV (if use_mrv=True) or simple row-major order.

        :param board: The SudokuBoard instance.
        :param use_mrv: Whether to use Minimum Remaining Values heuristic.
        :return: (row, col) coordinates of chosen cell, or None if complete.
        """
        if use_mrv:
            return self.select_unassigned_variable_mrv(board)
        return self.select_unassigned_variable_simple(board)

    def solve(self, board: SudokuBoard, use_mrv: bool = True) -> bool:
        """
        Solves the given Sudoku board in-place using recursive Backtracking Search.

        :param board: The SudokuBoard to solve.
        :param use_mrv: Whether to enable the MRV variable-selection heuristic (default True).
        :return: True if a valid solution was found, False otherwise.
        """
        if not isinstance(board, SudokuBoard) or not board.is_valid_board():
            return False

        # Reset statistics for new solve run
        self.assignments = 0
        self.backtracks = 0
        self.execution_time = 0.0

        start_time = time.perf_counter()
        solved = self._backtrack(board, use_mrv=use_mrv)
        end_time = time.perf_counter()

        self.execution_time = end_time - start_time
        return solved

    def _backtrack(self, board: SudokuBoard, use_mrv: bool = True) -> bool:
        """
        Recursive depth-first backtracking search algorithm.

        Algorithm steps:
        1. Base Case: If all variables are assigned (no empty cells), return True.
        2. Variable Selection: Choose an unassigned cell using MRV or simple strategy.
        3. Domain Calculation: Retrieve legal candidate values for (row, col).
        4. Value Assignment:
           - For each candidate value:
             a. Assign value to the cell.
             b. Increment assignment counter.
             c. Recursively call _backtrack.
             d. If recursive call succeeds, propagate True.
             e. If recursive call fails, undo assignment (backtrack) and increment backtrack counter.
        5. Failure: If domain is empty or all candidates fail, return False.

        :param board: The SudokuBoard instance being modified in-place.
        :param use_mrv: Whether to use MRV heuristic for variable selection.
        :return: True if the subproblem is solvable, False otherwise.
        """
        # Step 1 & 2: Select an unassigned variable
        cell = self.select_unassigned_variable(board, use_mrv=use_mrv)
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
            if self._backtrack(board, use_mrv=use_mrv):
                return True

            # Step 4e: Backtrack - undo the assignment on failure
            board.set_cell(row, col, SudokuBoard.EMPTY_CELL)
            self.backtracks += 1

        # Step 5: No candidate led to a valid solution (contradiction or domain exhausted)
        return False

    def get_stats(self) -> Dict[str, Union[int, float]]:
        """
        Returns solver search statistics from the most recent run.

        :return: Dictionary containing 'assignments', 'backtracks', and 'execution_time'.
        """
        return {
            "assignments": self.assignments,
            "backtracks": self.backtracks,
            "execution_time": self.execution_time,
        }
