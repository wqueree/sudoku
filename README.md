# sudoku

## 1 - Introduction
Sudoku is one of the most common examples of a constraint satisfaction problem, loved by many for its place as a staple of newspaper puzzle pages. The principle is simple: given a 9x9 grid of filled and unfilled cells, fill in the blank cells such that no row, column, or 3x3 subgrid contain a duplicated value between 1 and 9. Despite their popularity, sudoku puzzles are a hard problems for computers to solve.

## 2 - Approach

As sudoku is a constraint satisfaction problem, it can be abstracted into a set of variables (the set of cells), domains (the row, column, and boxes for each cell), and constraints (that a value between 1 and 9 may not be duplicated in any cell's domain). As a result of this abstraction, it is possible to mechanically apply a backtracking depth-first-search (Russell and Norvig, 2016). This works by filling in test values from the set of possible values for each cell and recursively repeating this process until failure, in which case the algorithm will backtrack to the last valid state, or valid completion, where the grid is returned. As previously stated, the sudoku state is complete and valid when all cells contain a final value and the values comply with the constraints. At this point, the state's assignment is said to be complete and consistent. In my solution, this is implemented through two classes and some main solution logic functions. The classes mentioned are a cell class and a partial state class called `Cell` and `PartialSudokuState` respectively. These are inspired by the partial eight queens state solution (Ralph, 2021), and set out in section 2.1, with the solution logic in section 2.2.

The solver implementation does, however, not rely exclusively on depth first search and trialling a random value in a random cell. It is possible to optimise the problem further than this. Firstly, as constraint propagation is being used, the initial partial state can be iterated over to build the list of candidates for each cell, and in some cases it may even be possible to fill a value and propagate the result of that also. This means that before we even start the depth first search, it may be possible to solve the problem, or at least minimise it purely through eliminating values from each cell's candidates list. Secondly, it is possible to optimise both the selection of the next cell, and the next value to be trialled for that cell. For cell selection, this can be done with a quick iteration over each element in the partial state, and returning the unfilled cell with the fewest possible candidates to be trialled next in the depth first search. Once this cell has been obtained, its possible values is simply its candidates list. It should be noted here that a simple random shuffle of these elements does produce fast results, even with the hard problem set. However, a small optimisation can be gained through keeping track of the number of each value allocated in the state (the `allocations` list), and sorting the values in ascending order according to that list. This works because the fewer of a given number have been allocated, the more likely it becomes that that number will be allocated next.

In addition to optimising the problem itself and the cell/value selection, there are also opportunities to minimise the problem as the search goes on. For example, when a value is allocated and propagated to the cells it affects, it may then be the case that there are now cells with only one candidate. By iterating over the array and allocating these cells, the problem is further minimised, reducing computation time. The same minimising logic can be applied where only one cell has a particular candidate in its row, column, or 3x3 box; in that after each propagation, each row, column, and 3x3 box can be iterated over to determine if it contains a cell with a sole candidate within that scope. If one does exist, that value is filled and the search continues.

### 2.1 - Classes

#### 2.1.1 - `Cell`

##### 2.1.1.1 - Attributes
- `value`: The finalised value for each cell. Defaults to -1 if not specified. 0 indicates an unfilled cell.
- `candidates`: The list of possible candidates for each cell given the applied constraints.
- `row`: The row of the cell.
- `col`: The column of the cell.

##### 2.1.1.2 - Methods
- `get_candidates(self)`: Returns a copy of the `candidates` list.
- `get_singleton(self)`: If the cell has a single candidate in its candidates list, returns that value, else returns -1 to indicate erroneous call.

#### 2.1.2 - `PartialSudokuState`

##### 2.1.2.1 - Attributes
- `cells`: A 9x9 numpy array of `Cell` objects.
- `allocations` A list storing the number of allocations for each number between 1 and 9 in the sudoku.

##### 2.1.2.2 - Methods
- `is_goal(self)`: Returns `True` if all Cells have a value other than 0.
- `is_valid(self)`: Returns the logical conjunction of the valid_rows_and_cols() adn valid_boxes() methods.
- `valid_rows_and_cols(self)`: Iterates over each row and column, returning True if all contain exclusively different values greater than 0.
- `valid_boxes(self)`: Iterates over each 3x3 box, returning True if all contain exclusively different values greater than 0.
- `set_value(self, cell, new_value)`: Creates a copy of the current state and applies change specified by parameters cell and new_value. This is then simplified and returned.
- `set_value_in_state(self, cell, new_value)`: Sets value specified by parameters in the current state. Should be called when values are being set as a direct result of another insertion.
- `singleton_sweep(self)`: Sweeps to find any Cells with only one candidate and fills these values as final.
- `sole_appearance_sweep(self)`: Sweeps to find all cells where a given cell is the only one that contains a particular value in its row, column, and box. Fills these values.
- `sole_appearance_sweep_row(self)`: Sweeps to find all cells where a given cell is the only one that contains a particular value in its row. Fills these values.
- `sole_appearance_sweep_col(self)`: Sweeps to find all cells where a given cell is the only one that contains a particular value in its column. Fills these values.
- `sole_appearance_sweep_box(self)`: Sweeps to find all cells where a given cell is the only one that contains a particular value in its box. Fills these values.
- `propagate(self, cell)`: Propagates changes to the candidates array of Cells affected by insertion of a final value in the finalised cell's row, box, and column.
- `propagate_row(self, cell)`: Propagates changes to the candidates array of Cells affected by insertion of a final value in the finalised cell's row.
- `propagate_col(self, cell)`: Propagates changes to the candidates array of Cells affected by insertion of a final value in the finalised cell's column.
- `propagate_box(self, cell)`: Propagates changes to the candidates array of Cells affected by insertion of a final value in the finalised cell's 3x3 box.
- `minimise(self)`: Minimises problem in the initial state by eliminating impossible values from each Cell's candidates array.
- `update_candidates(self, cell)`: Sweeps to find any Cells with impossible candidates and eliminates these candidates from the Cell's candidates array.
- `update_box(self, cell)`: Sweeps to find any Cells with impossible candidates resulting from the Cell's box and eliminates these candidates from the Cell's candidates array.
- `update_row(self, cell)`: Sweeps to find any Cells with impossible candidates resulting from the Cell's row and eliminates these candidates from the Cell's candidates array.
- `update_col(self, cell)`: Sweeps to find any Cells with impossible candidates resulting from the Cell's column and eliminates these candidates from the Cell's candidates array.
- `get_allocations(self)`: Returns a copy of the state's allocations array.
- `to_array(self)`: Returns array of values in the state at the time of calling.

### 2.2 - Solution Functions

- `sudoku_solver(sudoku)`: Returns a solution, if one exists by minimising problem and performing a depth first search. If no solution exists returns 9x9 array of -1.
- `depth_first_search(state)`: Runs a depth first search on the problem, returning a solution state if one is found.
- `next_cell(state)`: Selects the next cell by returning the cell with the fewest candidates in its candidate array. Failing this, returns a random choice.
- `order_values(cell, state)`: Sorts values according to the number of allocations in the state and returns an array.

## 3 - Evaluation

The solution implemented works well, delivering a solution to almost all problems in approximately 0.1 seconds or less (on a University of Bath Library PC).

There are however, more efficient alternatives alternatives to applying a depth first search for solving sudoku. Donald E. Knuth (2000) suggested the use of the Dancing Links algorithm to solve a similar constraint satisfaction problem: n queens. Knuth suggests the use of a 0-1 exact cover matrix which could be extended to encompass the problem of sudoku. This is something I would look to use in extending or redeveloping my solution.



## References

Russel, S.J. and Norvig, P., 2016. *Artificial Intelligence: A Modern Approach* 3rd ed, global. Harlow: Pearson Education Limited.

Ralph, B., 2021. Eight Queens (with constraint satisfaction) [computer program]. Available from: https://moodle.bath.ac.uk/course/view.php?id=59592&section=6 [08/03/2021].

Knuth, D.E., 2000. Dancing Links. In: J. Davies, B. Roscoe, and J. Woodcock, eds. *Proceedings of the 1999 Oxford-Microsoft Symposium in Honour of Sir Tony Hoare*, 2000, Oxford. Red Globe Press, pp.187-214.


