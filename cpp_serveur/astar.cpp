#include <iostream>
#include <queue>
#include <chrono>
#include <list>
#include <vector>
#include "Coordinates.h"
#include "GridCell.h"
using namespace std;
using namespace std::chrono;

const int map_width = 32; // Horizontal size of map
const int map_height = 18; // Vertical size of map
static int closed_nodes_map[map_height][map_width]; // Closed-node list
static int open_nodes_map[map_height][map_width]; // Open-node list
static int dir_map[map_height][map_width]; // Direction map

const enum Movement { RIGHT = 0, DOWN = 1, LEFT = 2, UP = 3 }; // All movements
static int dx[4] = { 1, 0, -1, 0 }; // X variation of movements
static int dy[4] = { 0, 1, 0, -1 }; // Y variation of movements

deque<Movement> pathFind(int xStart, int yStart, int xFinish, int yFinish, int current_map[map_height][map_width]) { // Returns route taken
	static priority_queue<GridCell> p_queue[2]; // Queue
	static int p_queue_index; // Index in queue
	static GridCell* n0;
	static GridCell* m0;
	static int c, i, j, x, y, xdx, ydy;
	p_queue_index = 0;

	// Reset Nodes
	for (y = 0; y < map_height; y++) {
		for (x = 0; x < map_width; x++) {
			closed_nodes_map[y][x] = 0;
			open_nodes_map[y][x] = 0;
		}
	}

	// Create Start node
	n0 = new GridCell(xStart, yStart, 0, 0);
	n0 -> update_priority(xFinish, yFinish);
	p_queue[p_queue_index].push(*n0);
	open_nodes_map[y][x] = n0 -> get_priority(); // Mark in Open-node list

	// Main loop
	while (!p_queue[p_queue_index].empty()) { // As long as the Open-node list contains a Cell
		n0 = new GridCell(p_queue[p_queue_index].top().get_x(), p_queue[p_queue_index].top().get_y(),
			p_queue[p_queue_index].top().get_level(), p_queue[p_queue_index].top().get_priority());

		x = n0 -> get_x(); y = n0 -> get_y();

		p_queue[p_queue_index].pop();
		open_nodes_map[y][x] = 0;
		closed_nodes_map[y][x] = 1;
		if (x == xFinish && y == yFinish) {
			deque<Movement> path = {};
			while (!(x == xStart && y == yStart)) { // If end of path was reached
				j = dir_map[y][x]; // Get the direction at that index
				c = (j + 2) % 4; // Reverse it
				path.push_front(Movement(c));
				x += dx[j];
				y += dy[j];
			}
			delete n0; // Shave time
			while (!p_queue[p_queue_index].empty()) p_queue[p_queue_index].pop();
			return path;
		}

		for (i = 0; i < 4; i++) {
			xdx = x + dx[i]; ydy = y + dy[i];

			if (!(xdx < 0 || xdx > map_width - 1 || ydy < 0 || ydy > map_height - 1 || current_map[ydy][xdx] == 1 || current_map[ydy][xdx] ==  2
				|| closed_nodes_map[ydy][xdx] == 1 || closed_nodes_map[ydy][xdx] == 2)) {
				m0 = new GridCell(xdx, ydy, n0 -> get_level(),
					n0 -> get_priority()); // Generate neighboring cell
				m0 -> next_level(i); // Update distance from origin
				m0 -> update_priority(xFinish, yFinish); // Calculate heuristic

				if (open_nodes_map[ydy][xdx] == 0) { // If node not visited
					open_nodes_map[ydy][xdx] = m0 -> get_priority();
					p_queue[p_queue_index].push(*m0);
					dir_map[ydy][xdx] = (i + 2) % 4; // Update dir
				}

				else if (open_nodes_map[ydy][xdx] > m0 -> get_priority()) { // If new cell has better priority 
					open_nodes_map[ydy][xdx] = m0 -> get_priority();
					dir_map[ydy][xdx] = (i + 2) % 4;

					while (!(p_queue[p_queue_index].top().get_x() == xdx &&
						p_queue[p_queue_index].top().get_y() == ydy)) {
						p_queue[1 - p_queue_index].push(p_queue[p_queue_index].top());
						p_queue[p_queue_index].pop();
					}
					p_queue[p_queue_index].pop();
					if (p_queue[p_queue_index].size() > p_queue[1 - p_queue_index].size()) p_queue_index = 1 - p_queue_index;
					while (!p_queue[p_queue_index].empty()) {
						p_queue[1 - p_queue_index].push(p_queue[p_queue_index].top());
						p_queue[p_queue_index].pop();
					}
					p_queue_index = 1 - p_queue_index;
					p_queue[p_queue_index].push(*m0);
				}
				else delete m0;
			}
		}
		delete n0;
	}
	return {};
}

deque<Movement> calculate_movement(Coordinates start, Coordinates end, int current_map[map_height][map_width]) {
	int x_start = start.m_x, y_start = start.m_y, x_end = end.m_x, y_end = end.m_y;
	deque<Movement> route = pathFind(x_start, y_start, x_end, y_end, current_map);
	return route;
}

int main() {
	Coordinates start = Coordinates(3, 9), end = Coordinates(22, 9);
	int x_start = start.m_x, y_start = start.m_y, x_end = end.m_x, y_end = end.m_y;
	int c_map[map_height][map_width] = { 
	{ 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
	{ 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
	{ 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
	{ 0, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0 },
	{ 0, 1, 2, 2, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0 },
	{ 0, 0, 2, 2, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
	{ 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
	{ 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
	{ 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 },
	{ 0, 0, 3, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0 },
	{ 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 2, 1, 2, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0 },
	{ 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0 },
	{ 0, 0, 2, 2, 0, 0, 0, 2, 2, 0, 1, 1, 2, 2, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0 },
	{ 1, 1, 1, 0, 0, 0, 0, 2, 2, 0, 1, 1, 2, 2, 2, 2, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0 },
	{ 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 0 },
	{ 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 2, 2, 1, 1, 0, 0 },
	{ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0 },
	{ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0 }};
	high_resolution_clock::time_point t1 = high_resolution_clock::now();
	deque<Movement> route = pathFind(x_start, y_start, x_end, y_end, c_map);
	high_resolution_clock::time_point t2 = high_resolution_clock::now();
	auto duration1 = duration_cast<microseconds>(t2 - t1).count();
	cout << "Time to calculate the route (mus): " << duration1 << endl;
	for (Movement m : route) {
		cout << m;
	}
	getchar();
	return 0;
}