#include "GridCell.h"
#include "Coordinates.h"
#include <iostream>
#include <vector>
#include <algorithm>
#include <set>
#include <chrono>

using namespace std;
using namespace std::chrono;

vector<Coordinates> bresenham(Coordinates start, Coordinates end) {
    int x1 = start.get_x(), y1 = start.get_y();
    int x2 = end.get_x(), y2 = end.get_y();
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

vector<Coordinates> linearize(vector<Coordinates> vec, vector<Coordinates> obstacles) {
    vector<Coordinates> out;
    int x_dir, y_dir;
    if (vec.front().get_x() < vec.back().get_x()) { x_dir = 1; }
    else { x_dir = -1; }
    if (vec.front().get_y() < vec.back().get_y()) { y_dir = 1; }
    else { y_dir = -1; }
    for(unsigned int i = 0; i < vec.size() - 1; i++) {
        out.emplace_back(vec.at(i));
        Coordinates next = vec.at(i + 1);
        if (!vec.at(i).adjacent(next)) {
            Coordinates option1 = Coordinates(vec.at(i).get_x() + x_dir, vec.at(i).get_y());
            if (find(begin(obstacles), end(obstacles), option1) == end(obstacles)) { out.push_back(option1); }
            else { out.push_back(Coordinates(vec.at(i).get_x(), vec.at(i).get_y() + y_dir)); }
        }
    }
    return out;
}

void vector_to_string(vector<Coordinates> vec) {
    cout << endl;
    for (unsigned int i = 0; i < vec.size() - 1; i++){
        cout << vec.at(i).to_str() << ", ";
    }
    cout << vec.back().to_str() << endl;
}

vector<Coordinates> aStar(Coordinates start, Coordinates end, vector<Coordinates> obstacles) {
    vector<Coordinates> open_list;
    make_heap(open_list.begin(), open_list.end());
    set<vector<Coordinates>> closed_list;
    vector<Coordinates> all_cells;

    int grid_height = 18, grid_width = 32;
    int start_x = start.get_x(), start_y = start.get_y();
    int end_x = end.get_x(), end_y = end.get_y();
    vector<Coordinates> temp_obstacles = obstacles;
    return temp_obstacles;
}

int main() {
    high_resolution_clock::time_point t1 = high_resolution_clock::now();
    Coordinates a = Coordinates(0, 0), b = Coordinates(32, 18);
    high_resolution_clock::time_point t2 = high_resolution_clock::now();
    vector<Coordinates> br = bresenham(a, b);
    high_resolution_clock::time_point t3 = high_resolution_clock::now();
    vector<Coordinates> lin = linearize(br, {Coordinates(0, 0)});
    high_resolution_clock ::time_point t4 = high_resolution_clock::now();
    auto duration1 = duration_cast<nanoseconds>(t2-t1).count();
    auto duration2 = duration_cast<nanoseconds>(t3-t2).count();
    auto duration3 = duration_cast<nanoseconds>(t4-t3).count();

    cout << a.to_str() << " / " << b.to_str() << " --- Calculated in : " << duration1 << " nanoseconds" << endl;
    vector_to_string(br);
    cout << "Bresenham calculated in : " << duration2 << " nanoseconds" << endl;
    vector_to_string(lin);
    cout << "Linearized  in : " << duration3 << " nanoseconds" << endl;
    return 0;
}