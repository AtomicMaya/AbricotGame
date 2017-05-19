#ifndef GRID_CELL
#define GRID_CELL

#include "Coordinates.h"
class GridCell : public Coordinates{
private:
    bool obstacle;
    unsigned int g = 0, h = 0, f = 0;
    GridCell* parent = NULL;

public:
    GridCell(int, int, bool);

    GridCell operator+ (GridCell &rhs) { return GridCell(x + rhs.x, x + rhs.x, obstacle); }
    GridCell operator- (GridCell &rhs) { return GridCell(x - rhs.x, y - rhs.y, obstacle); }
    bool operator< (GridCell &rhs) { return x < rhs.x; }
    bool operator> (GridCell &rhs) { return x > rhs.x; }
    bool operator== (GridCell &rhs) { return (x == rhs.x) && (y == rhs.y); }
    bool inferior_than(GridCell const& lhs) const;

    void set_parent(GridCell&);
    void set_g(unsigned int);
    void set_h(unsigned int);
    void set_f();

    bool get_is_obstacle();
    GridCell get_parent();
    unsigned int get_g();
    unsigned int get_h();
    unsigned int get_f();

    bool has_parent();
    std::string to_str();
};

#endif