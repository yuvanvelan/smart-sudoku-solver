# Smart Sudoku Solver

A Foundations of AI mini-project implementing an intelligent 9×9 Sudoku puzzle generator and solver.

## Project Purpose
The purpose of this project is to explore and demonstrate core Artificial Intelligence problem-solving concepts by modeling Sudoku as a Constraint Satisfaction Problem (CSP) and solving it efficiently using intelligent search heuristics alongside an interactive graphical user interface (GUI).

The application will feature two primary user actions:
1. **Create Sudoku**: Generate valid standard 9×9 Sudoku puzzles.
2. **Solve Sudoku**: Solve Sudoku puzzles using AI algorithms and visualize the solution.

## Planned Technologies
- **Language**: Python (3.x)
- **GUI Framework**: Tkinter (Python standard library)
- **Data & Grid Operations**: NumPy

## Planned AI Techniques
- **Constraint Satisfaction Problem (CSP)**: Representing grid cells as variables with domains `1..9` and row/column/box uniqueness constraints.
- **Backtracking Search**: Systematic depth-first search for valid assignments satisfying all constraints.
- **Minimum Remaining Values (MRV) Heuristic**: Selecting the most constrained variable (the cell with the fewest legal values) first to prune the search space rapidly.

## Incremental Development
This project is being developed incrementally across structured phases:
- **Phase 1**: Project Setup & Environment Configuration *(Current Phase)*
- **Phase 2**: Core Sudoku Data Structure & Board Representation
- **Phase 3**: AI Solver (CSP, Backtracking, MRV)
- **Phase 4**: Sudoku Generator
- **Phase 5**: Interactive Tkinter GUI Integration
- **Phase 6**: Testing & Polish

---
*Note: This is currently in Phase 1 (Project Setup).*
