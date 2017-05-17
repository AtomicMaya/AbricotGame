#include <iostream>
#include "GridCell.h"
using namespace std;

GridCell::GridCell(int x, int y, bool aBool){
    cell_x = x;
    cell_y = y;
    obstacle = aBool;
}

void GridCell::is_obstacle(bool aBool) { obstacle = aBool; }

void GridCell::set_parent(GridCell& aCell) { parent = &aCell; }

void GridCell::set_g(int aInt) { g = aInt; }

void GridCell::set_h(int aInt) { h = aInt; }

void GridCell::calc_f() { f = g + h; }
