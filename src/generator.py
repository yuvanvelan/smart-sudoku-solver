"""
Sudoku Puzzle Generator.

This module implements algorithmic generation of valid, solvable, and unique
standard 9x9 Sudoku puzzles using randomized CSP completion and solution-counted
clue reduction.
"""

import random
from typing import List, Optional, Tuple
from src.sudoku import SudokuBoard
from src.solver import SudokuSolver


class SudokuGenerator:
    """
    Generates standard 9x9 Sudoku puzzles.

    Generation Workflow:
    1. Solution Generation: Creates a complete valid 9x9 Sudoku grid by randomly
       filling diagonal 3x3 boxes and solving the rest using randomized Backtracking Search.
    2. Clue Reduction: Systematically removes cell values in randomized order while
       verifying that the puzzle retains a unique solution (via solver solution counting).
    """

    # Target number of removed cells per difficulty level
    DIFFICULTY_REMOVALS = {
        "easy": 36,     # ~45 clues remaining (very accessible)
        "medium": 46,   # ~35 clues remaining (standard challenge)
        "hard": 52,     # ~29 clues remaining (demanding)
        "expert": 56,   # ~25 clues remaining (advanced)
    }

    def __init__(
        self,
        seed: Optional[int] = None,
        solver: Optional[SudokuSolver] = None,
    ) -> None:
        """
        Initialize the SudokuGenerator.

        :param seed: Optional integer seed for reproducible random generation.
        :param solver: Optional SudokuSolver instance to reuse.
        """
        self.rng: random.Random = random.Random(seed)
        self.solver: SudokuSolver = solver if solver is not None else SudokuSolver()

    def generate_complete_board(self) -> SudokuBoard:
        """
        Generates a valid, completely filled 9x9 Sudoku board.

        Fills the 3 independent diagonal 3x3 subgrids randomly, then uses
        randomized Backtracking Search with MRV to complete the remaining cells.

        :return: A fully solved, valid SudokuBoard instance.
        """
        board = SudokuBoard()

        # Step 1: Fill the three diagonal 3x3 subgrids (top-left, center, bottom-right).
        # These 3 boxes are completely independent of each other (share no rows or columns).
        for box_idx in range(0, board.GRID_SIZE, board.BOX_SIZE):
            digits = list(range(1, 10))
            self.rng.shuffle(digits)
            idx = 0
            for r in range(box_idx, box_idx + board.BOX_SIZE):
                for c in range(box_idx, box_idx + board.BOX_SIZE):
                    board.set_cell(r, c, digits[idx])
                    idx += 1

        # Step 2: Complete the remaining empty cells using randomized MRV search
        def _fill_randomized(b: SudokuBoard) -> bool:
            cell = self.solver.select_unassigned_variable_mrv(b)
            if cell is None:
                return True

            row, col = cell
            candidates = self.solver.get_candidates(b, row, col)
            self.rng.shuffle(candidates)

            for val in candidates:
                b.set_cell(row, col, val)
                if _fill_randomized(b):
                    return True
                b.set_cell(row, col, SudokuBoard.EMPTY_CELL)

            return False

        _fill_randomized(board)
        return board

    def has_unique_solution(self, board: SudokuBoard) -> bool:
        """
        Checks whether the given SudokuBoard has exactly one valid solution.

        :param board: The SudokuBoard to check.
        :return: True if exactly one solution exists, False otherwise.
        """
        return self.solver.count_solutions(board, limit=2) == 1

    def generate_puzzle(
        self,
        difficulty: str = "medium",
        removals: Optional[int] = None,
        ensure_unique: bool = True,
    ) -> SudokuBoard:
        """
        Generates a playable Sudoku puzzle with empty cells (represented by 0).

        :param difficulty: Difficulty level ('easy', 'medium', 'hard', 'expert').
        :param removals: Optional explicit count of cells to remove. Overrides difficulty.
        :param ensure_unique: Whether to guarantee the puzzle has a unique solution.
        :return: A playable SudokuBoard instance.
        """
        # Determine target number of cells to remove
        if removals is not None:
            target_removals = max(1, min(64, removals))
        else:
            target_removals = self.DIFFICULTY_REMOVALS.get(
                difficulty.lower(), self.DIFFICULTY_REMOVALS["medium"]
            )

        # 1. Start with a fully completed valid board
        complete_board = self.generate_complete_board()
        puzzle = complete_board.copy()

        # 2. Get all 81 cell coordinates and shuffle them
        all_cells: List[Tuple[int, int]] = [
            (r, c)
            for r in range(puzzle.GRID_SIZE)
            for c in range(puzzle.GRID_SIZE)
        ]
        self.rng.shuffle(all_cells)

        # 3. Iteratively remove cell values while maintaining solvability / uniqueness
        removed_count = 0
        for r, c in all_cells:
            if removed_count >= target_removals:
                break

            original_val = puzzle.get_cell(r, c)
            puzzle.set_cell(r, c, SudokuBoard.EMPTY_CELL)

            if ensure_unique:
                # Verify that removing this cell does not introduce multiple solutions
                if not self.has_unique_solution(puzzle):
                    # Uniqueness violated: restore cell value
                    puzzle.set_cell(r, c, original_val)
                    continue
            else:
                # Just verify it remains solvable
                if not self.solver.solve(puzzle.copy()):
                    puzzle.set_cell(r, c, original_val)
                    continue

            removed_count += 1

        return puzzle
