#ifndef CELL_H
#define CELL_H

#include <vector>

class Cell {
  int value;
  const int row;
  const int column;
  std::vector<int> candidates;

  public:

    Cell(int value, int row, int column) : row(row), column(column) {
      if (value == 0)
        this->candidates = {1, 2, 3, 4, 5, 6, 7, 8, 9};
      else
        this->candidates = {};

      this->value = value;
    }

    int get_singleton() {
      if (this->candidates.size() == 1)
        return this->candidates[0];
      else
        return -1;
    }

    int get_value() {
      return this->value;
    }

    void set_value(int value) {
      this->value = value;
    }
};

#endif