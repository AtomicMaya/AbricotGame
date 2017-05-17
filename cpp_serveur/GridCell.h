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

    void set_is_obstacle(bool);
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
};

#endif