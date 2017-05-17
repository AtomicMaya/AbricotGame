#include "GridCell.h"
#include "Coordinates.h"
#include <iostream>
#include <list>
#include <vector>
#include <algorithm>
#include <set>
using namespace std;

int main() {
    return 0;
}

vector<Coordinates> bresenham(Coordinates start, Coordinates end) {
    int x1 = start.get(0), y1 = start.get(1);
    int x2 = end.get(0), y2 = end.get(1);
    int dx = x2 - x1, dy = y2 - y1;
    bool slope = abs(dy) > abs(dx);
    if (slope) {
        int temp_y1 = y1;
        y1 = x1;
        x1 = temp_y1;

        int temp_y2 = y2;
        y2 = x2;
        x2 = temp_y2;
    }
    bool switched = false;
    if (x1 > x2) {
        int temp_x1 = x1;
        x1 = x2;
        x2 = temp_x1;
        int temp_y1 = y1;
        y1 = y2;
        y2 = temp_y1;
        switched = true;
    }
    dx = x2 - x1, dy = y2 - y1;
    int error = int(dx / 2.0);
    int y_step = 0;
    if (y1 < y2) {
        y_step = 1;
    } else {
        y_step = -1;
    }
    vector<Coordinates> crossed_points;
    int y = y1;
    for (int x = x1; x < x2 + 1; x++) {
        if (slope) {
            Coordinates coord = Coordinates(y, x);
            crossed_points.push_back(coord);
        } else {
            Coordinates coord = Coordinates(x, y);
            crossed_points.push_back(coord);
        }
        error -= abs(dy);
        if (error < 0) {
            y += y_step;
            error += dx;
        }
    }
    if (switched) {
        reverse(crossed_points.begin(), crossed_points.end());
    }

    return crossed_points;
}

vector<Coordinates> aStar(Coordinates start, Coordinates end, vector<Coordinates> obstacles) {
    vector<Coordinates> open_list;
    make_heap(open_list.begin(), open_list.end());
    set<vector<Coordinates>> closed_list;
    vector<Coordinates> all_cells;

    int grid_height = 18, grid_width = 32;
    int start_x = start.get(0), start_y = start.get(1);
    int end_x = end.get(0), end_y = end.get(1);
    vector<Coordinates> temp_obstacles = obstacles;
    return temp_obstacles;
}
