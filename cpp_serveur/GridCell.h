#ifndef GRID_CELL
#define GRID_CELL

class GridCell {
    int cell_x, cell_y;
    bool obstacle;
    int g, h, f;
    GridCell* parent;

public:
    GridCell(int, int, bool);
    void is_obstacle(bool);
    void set_parent(GridCell&);

    void set_g(int);
    void set_h(int);
    void calc_f();
};

#endif