"""System to solve sudoku using a backtracking, preproccessing DFS approach."""

import random
import copy
import time
from typing import List

import numpy as np


class Cell:

    """
    Class abstracting the properties of a single 9x9 cell in a sudoku problem.
    Attributes include value for finalised cells, and a list of candidates for non-finalised
    cells.
    """

    def __init__(self, value: int = -1, row: int = -1, col: int = -1) -> None:
        """Cell constructor. Requires a value, row, and column for full functionality."""
        if value == 0:
            self._candidates: List[int] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        else:
            self._candidates: List[int] = []
        self._value: int = value
        self._row: int = row
        self._col: int = col

    def get_singleton(self) -> int:
        """If the cell has a single candidate in its candidates list,
        returns that value, else returns -1 to indicate erroneous call."""
        if len(self.candidates) == 1:
            return self.candidates[0]
        else:
            return -1

    @property
    def candidates(self) -> List[int]:
        """The possible candidates of the cell."""
        return self._candidates

    @candidates.setter
    def candidates(self, candidates_: List[int]) -> None:
        self._candidates = candidates_

    @property
    def value(self) -> int:
        """The value of the cell."""
        return self._value

    @value.setter
    def value(self, value_: int) -> None:
        self._value = value_

    @property
    def row(self) -> int:
        """The row of the cell."""
        return self._row

    @row.setter
    def row(self, row_: int) -> None:
        self._row = row_

    @property
    def col(self) -> int:
        """The col of the cell."""
        return self._col

    @col.setter
    def col(self, col_: int) -> None:
        self._col = col_


class PartialSudokuState:

    """
    Class abstracting the properties of a whole sudoku through use of the Cell class.
    Represents the current state of the problem using a 9x9 grid of Cells.
    """

    def __init__(self, sudoku: np.ndarray) -> None:
        """PartialSudokuState constructor. Takes a 9x9 integer array as input and
        reads into 9x9 Cell array."""
        self._allocations: List[int] = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self._cells: np.ndarray = np.empty([9, 9], dtype=Cell)
        for i in range(len(sudoku)):
            for j, cell in enumerate(sudoku[i]):
                if cell > 0:
                    self._allocations[cell - 1] += 1
                self._cells[i][j] = Cell(value=cell, row=i, col=j)

    @property
    def allocations(self) -> List[int]:
        """The number of each possible value that has been allocated."""
        return self._allocations

    @allocations.setter
    def allocations(self, allocations_: List[int]) -> None:
        self._allocations = allocations_

    @property
    def cells(self) -> np.ndarray:
        """A 9x9 numpy array of the current state."""
        return self._cells

    @cells.setter
    def cells(self, cells_: np.ndarray) -> None:
        self._cells = cells_

    def is_goal(self) -> bool:
        """Returns True if all Cells have a value other than 0."""
        return all(all(value != 0 for value in row) for row in self.to_array())

    def is_valid(self) -> bool:
        """Returns the logical conjunction of the valid_rows_and_cols and valid_boxes methods."""
        return self.valid_rows_and_cols() and self.valid_boxes()

    def valid_rows_and_cols(self) -> bool:
        """Iterates over each row and column, returning True if all contain exclusively
        different values greater than 0."""
        row_valid = True
        col_valid = True
        for i in range(9):
            row_appeared = set()
            col_appeared = set()

            for j in range(9):
                row_current = self.cells[i][j].value
                col_current = self.cells[j][i].value

                if row_current > 0:
                    if row_current in row_appeared:
                        row_valid = False
                    row_appeared.add(row_current)

                if col_current > 0:
                    if col_current in col_appeared:
                        col_valid = False
                    col_appeared.add(col_current)

        return row_valid and col_valid

    def valid_boxes(self) -> bool:
        """Iterates over each 3x3 box, returning True if all contain exclusively
        different values greater than 0."""
        valid = True
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                appeared = set()
                for k in range(i, i + 3):
                    for l in range(j, j + 3):
                        current = self.cells[k][l].value
                        if current > 0:
                            if current in appeared:
                                valid = False
                            appeared.add(current)
        return valid

    def set_value(self, cell: Cell, new_value: int) -> "PartialSudokuState":
        """Creates a copy of the current state and applies change specified by parameters
        cell and new_value. This is then simplified and returned."""
        state = copy.deepcopy(self)
        state.set_value_in_state(cell, new_value)
        state.sole_appearance_sweep()
        return state

    def set_value_in_state(self, cell: Cell, new_value: int) -> None:
        """Sets value specified by parameters in the current state. Should be called when
        values are being set as a direct result of another insertion."""
        new_cell = Cell(value=new_value, row=cell.row, col=cell.col)
        self.cells[cell.row][cell.col] = new_cell
        self.allocations[new_value - 1] += 1
        self.propagate(new_cell)
        self.singleton_sweep()

    def sole_appearance_sweep(self) -> None:
        """Sweeps to find all cells where a given cell is the only one that contains a particular
        value in its row, column, and box. Fills these values."""
        self.sole_appearance_sweep_row()
        self.sole_appearance_sweep_col()
        self.sole_appearance_sweep_box()

    def sole_appearance_sweep_row(self) -> None:
        """Sweeps to find all cells where a given cell is the only one that contains a particular
        value in its row. Fills these values."""
        for i in range(9):
            row_candidates = []
            duplicates = set()
            for j in range(9):
                current = self.cells[i][j]
                if current.value == 0:
                    for m in range(len(current.candidates)):
                        if (
                            current.candidates[m] not in row_candidates
                            and current.candidates[m] not in duplicates
                        ):
                            row_candidates.append(current.candidates[m])
                        elif current.candidates[m] not in duplicates:
                            row_candidates.remove(current.candidates[m])
                            duplicates.add(current.candidates[m])

            for k in range(len(row_candidates)):
                for j in range(9):
                    current = self.cells[i][j]
                    if row_candidates[k] in current.candidates:
                        self.set_value_in_state(current, row_candidates[k])
                        self.sole_appearance_sweep()

    def sole_appearance_sweep_col(self) -> None:
        """Sweeps to find all cells where a given cell is the only one that contains a particular
        value in its column. Fills these values."""
        for i in range(9):
            col_candidates = []
            duplicates = set()
            for j in range(9):
                current = self.cells[j][i]
                if current.value == 0:
                    for m in range(len(current.candidates)):
                        if (
                            current.candidates[m] not in col_candidates
                            and current.candidates[m] not in duplicates
                        ):
                            col_candidates.append(current.candidates[m])
                        elif current.candidates[m] not in duplicates:
                            col_candidates.remove(current.candidates[m])
                            duplicates.add(current.candidates[m])

            for k in range(len(col_candidates)):
                for j in range(9):
                    current = self.cells[j][i]
                    if col_candidates[k] in current.candidates:
                        self.set_value_in_state(current, col_candidates[k])
                        self.sole_appearance_sweep()

    def sole_appearance_sweep_box(self) -> None:
        """Sweeps to find all cells where a given cell is the only one that contains a particular
        value in its box. Fills these values."""
        for i in range(0, 9, 3):
            for j in range(0, 9, 3):
                box_candidates = []
                duplicates = set()
                for k in range(i, i + 3):
                    for l in range(j, j + 3):
                        current = self.cells[k][l]
                        if current.value == 0:
                            for m in range(len(current.candidates)):
                                if (
                                    current.candidates[m] not in box_candidates
                                    and current.candidates[m] not in duplicates
                                ):
                                    box_candidates.append(current.candidates[m])
                                elif current.candidates[m] not in duplicates:
                                    box_candidates.remove(current.candidates[m])
                                    duplicates.add(current.candidates[m])

                for m in range(len(box_candidates)):
                    for k in range(i, i + 3):
                        for l in range(j, j + 3):
                            current = self.cells[k][l]
                            if box_candidates[m] in current.candidates:
                                self.set_value_in_state(current, box_candidates[m])
                                self.sole_appearance_sweep()

    def propagate(self, cell: Cell) -> None:
        """Propagates changes to the candidates array of Cells affected by insertion of a final
        value in the finalised cell's row, box, and column."""
        self.propagate_row(cell)
        self.propagate_col(cell)
        self.propagate_box(cell)

    def propagate_row(self, cell: Cell) -> None:
        """Propagates changes to the candidates array of Cells affected by insertion of a final
        value in the finalised cell's row."""
        for i in range(9):
            current = self.cells[cell.row][i]
            if current.value == 0 and cell.value in current.candidates:
                current.candidates.remove(cell.value)

    def propagate_col(self, cell: Cell) -> None:
        """Propagates changes to the candidates array of Cells affected by insertion of a final
        value in the finalised cell's column."""
        for i in range(9):
            current = self.cells[i][cell.col]
            if current.value == 0 and cell.value in current.candidates:
                current.candidates.remove(cell.value)

    def propagate_box(self, cell: Cell) -> None:
        """Propagates changes to the candidates array of Cells affected by insertion of a final
        value in the finalised cell's box."""
        box_row_start = 0
        box_col_start = 0

        if cell.row > 2:
            box_row_start += 3
        if cell.row > 5:
            box_row_start += 3

        if cell.col > 2:
            box_col_start += 3
        if cell.col > 5:
            box_col_start += 3

        for i in range(box_row_start, box_row_start + 3):
            for j in range(box_col_start, box_col_start + 3):
                current = self.cells[i][j]
                if current.value == 0 and cell.value in current.candidates:
                    current.candidates.remove(cell.value)

    def minimise(self) -> None:
        """Minimises problem in the initial state by eliminating impossible values from each
        Cell's candidates array."""
        for i in range(len(self.cells)):
            for cell in self.cells[i]:
                if cell.value == 0:
                    self.update_candidates(cell)
                    if len(cell.candidates) == 1:
                        self.set_value_in_state(cell, cell.get_singleton())

    def singleton_sweep(self) -> None:
        """Sweeps to find any Cells with only one candidate and fills these values as final."""
        for i in range(len(self.cells)):
            for cell in self.cells[i]:
                if len(cell.candidates) == 1:
                    self.set_value_in_state(cell, cell.get_singleton())

    def update_candidates(self, cell: Cell) -> None:
        """Sweeps to find any Cells with impossible candidates and eliminates these candidates from
        the Cell's candidates array."""
        self.update_row(cell)
        self.update_box(cell)
        self.update_col(cell)

    def update_box(self, cell: Cell) -> None:
        """Sweeps to find any Cells with impossible candidates resulting from the Cell's box and
        eliminates these candidates from the Cell's candidates array."""
        box_row_start = 0
        box_col_start = 0

        if cell.row > 2:
            box_row_start += 3
        if cell.row > 5:
            box_row_start += 3

        if cell.col > 2:
            box_col_start += 3
        if cell.col > 5:
            box_col_start += 3

        for p in range(box_row_start, box_row_start + 3):
            for q in range(box_col_start, box_col_start + 3):
                current = self.cells[p][q].value
                if current in cell.candidates:
                    cell.candidates.remove(current)

    def update_row(self, cell: Cell) -> None:
        """Sweeps to find any Cells with impossible candidates resulting from the Cell's row and
        eliminates these candidates from the Cell's candidates array."""
        for i in range(9):
            current = self.cells[cell.row][i].value
            if current in cell.candidates:
                cell.candidates.remove(current)

    def update_col(self, cell: Cell) -> None:
        """Sweeps to find any Cells with impossible candidates resulting from the Cell's column and
        eliminates these candidates from the Cell's candidates array."""
        for i in range(9):
            current = self.cells[i][cell.col].value
            if current in cell.candidates:
                cell.candidates.remove(current)

    def get_allocations(self):
        """Returns a copy of the state's allocations array."""
        return self.allocations.copy()

    def to_array(self):
        """Returns array of values in the state at the time of calling."""
        a = np.empty([9, 9], dtype=np.int8)
        for i in range(len(self.cells)):
            for j, cell in enumerate(self.cells[i]):
                a[i][j] = cell.value
        return a


def depth_first_search(state):
    """Runs a depth first search on the problem, returning a solution state if one is found."""
    cell = next_cell(state)
    values = order_values(cell, state)

    for value in values:
        new_state = state.set_value(cell, value)
        if new_state.is_valid():
            if new_state.is_goal():
                return new_state
            deep_state = depth_first_search(new_state)
            if deep_state is not None and deep_state.is_goal():
                return deep_state
    return None


def next_cell(state):
    """Selects the next cell by returning the cell with the fewest candidates in its candidate
    array. Failing this, returns a random choice."""
    min_cell = Cell(value=0)
    cell_choices = []
    for i in range(len(state.cells)):
        for cell in state.cells[i]:
            if cell.value == 0:
                cell_choices.append(cell)
    chosen = False
    for cell in cell_choices:
        if len(cell.candidates) < len(min_cell.candidates):
            min_cell = cell
            chosen = True

    if not chosen:
        return random.choice(cell_choices)
    return min_cell


def order_values(cell, state):
    """Sorts values according to the number of allocations in the state and returns an array."""
    values = cell.candidates
    allocations = state.get_allocations()
    return [value for allocation, value in sorted(zip(allocations, values))]


def sudoku_solver(sudoku):
    """Returns a solution, if one exists by minimising problem and performing a depth first search.
    If no solution exists returns 9x9 array of -1."""
    state = PartialSudokuState(sudoku)
    state.minimise()

    if state.is_valid() and state.is_goal():
        return state.to_array()

    if not state.is_valid():
        return np.full((9, 9), -1)

    solution = depth_first_search(state)

    if solution is None:
        return np.full((9, 9), -1)
    return solution.to_array()


difficulties = ["very_easy", "easy", "medium", "hard"]

for difficulty in difficulties:
    print(f"Testing {difficulty} sudokus")

    sudokus = np.load(f"data/{difficulty}_puzzle.npy")
    solutions = np.load(f"data/{difficulty}_solution.npy")

    count = 0
    for i in range(len(sudokus)):
        sudoku = sudokus[i].copy()
        print(f"This is {difficulty} sudoku number", i + 1)
        print(sudoku)

        start_time = time.process_time()
        your_solution = sudoku_solver(sudoku)
        end_time = time.process_time()

        print(f"This is the algorithm's solution for {difficulty} sudoku number", i + 1)
        print(your_solution)

        print("Is this solution correct?")
        if np.array_equal(your_solution, solutions[i]):
            print("Yes! Correct solution.")
            count += 1
        else:
            print("No, the correct solution is:")
            print(solutions[i])

        print("This sudoku took", end_time - start_time, "seconds to solve.\n")

    print(f"{count}/{len(sudokus)} {difficulty} sudokus correct")
    if count < len(sudokus):
        break
