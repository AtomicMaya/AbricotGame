#include <iostream>
#include "GridCell.h"


using namespace std;

GridCell::GridCell(int x, int y, bool aBool): Coordinates(x, y){
    obstacle = aBool;
}

void GridCell::set_parent(GridCell& aCell) { parent = &aCell; }

void GridCell::set_g(unsigned int aInt) { g = aInt; }

void GridCell::set_h(unsigned int aInt) { h = aInt; }

void GridCell::set_f() { f = g + h; }

bool GridCell::get_is_obstacle() { return obstacle; }

GridCell GridCell::get_parent() { return *parent; }

unsigned int GridCell::get_g() { return g; }

unsigned int GridCell::get_h() { return h; }

unsigned int GridCell::get_f() { return f; }

bool GridCell::has_parent() {
        return parent != NULL;
}

bool GridCell::inferior_than(GridCell const& lhs) const { return x < lhs.x; }

string GridCell::to_str(){
    ostringstream oss;
    oss.clear();
    oss << "(" << x << ", " << y << ")";
    return oss.str();
}
