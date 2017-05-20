#include <iostream>
#include <iomanip>
#include <queue>
#include <string>
#include <math.h>
#include <ctime>
#include <chrono>
#include "Coordinates.h"
using namespace std;
using namespace std::chrono;

const int map_width = 32; // horizontal size of the map
const int map_height = 18; // vertical size size of the map
static int map[map_width][map_height];
static int closed_nodes_map[map_width][map_height]; // map of closed (tried-out) nodes
static int open_nodes_map[map_width][map_height]; // map of open (not-yet-tried) nodes
static int dir_map[map_width][map_height]; // map of directions

const int available_directions = 4; 
static int dx[available_directions]={1, 0, -1, 0};
static int dy[available_directions]={0, 1, 0, -1};

class GridCell
{
	// current position
	int m_x;
	int m_y;
	// total distance already travelled to reach the node
	int level;
	// priority=level+remaining distance estimate
	int priority;  // smaller: higher priority

public:
	GridCell(int xp, int yp, int d, int p)
	{
		m_x = xp; m_y = yp; level = d; priority = p;
	}

	int get_x() const { return m_x; }
	int get_y() const { return m_y; }
	int get_Level() const { return level; }
	int get_Priority() const { return priority; }

	void update_Priority(const int & xDest, const int & yDest) {
		priority = level + heuristic(xDest, yDest) * 10;
	}

	void next_Level(const int & dir) { level += (available_directions == 8 ? (dir % 2 == 0 ? 10 : 14) : 10); }

	// Estimation function for the remaining distance to the goal.
	const int & heuristic(const int & xDest, const int & yDest) const {
		static int xd, yd, d;
		xd = xDest - m_x;
		yd = yDest - m_y;

		d = static_cast<int>(sqrt(xd*xd + yd*yd));		// Euclidian Distance

		return(d);
	}
};

bool operator<(const GridCell & a, const GridCell & b) { return a.get_Priority() > b.get_Priority(); }

// A-star algorithm.
// The route returned is a string of direction digits.
string pathFind(const int & xStart, const int & yStart,
	const int & xFinish, const int & yFinish)
{
	static priority_queue<GridCell> pq[2]; // list of open (not-yet-tried) nodes
	static int pqi; // pq index
	static GridCell* n0;
	static GridCell* m0;
	static int i, j, x, y, xdx, ydy;
	static char c;
	pqi = 0;

	// reset the node maps
	for (y = 0; y < map_height; y++) {
		for (x = 0; x<map_width; x++) {
			closed_nodes_map[x][y] = 0;
			open_nodes_map[x][y] = 0;
		}
	}

	// create the start node and push into list of open nodes
	n0 = new GridCell(xStart, yStart, 0, 0);
	n0->update_Priority(xFinish, yFinish);
	pq[pqi].push(*n0);
	open_nodes_map[x][y] = n0->get_Priority(); // mark it on the open nodes map


	while (!pq[pqi].empty())
	{
		n0 = new GridCell(pq[pqi].top().get_x(), pq[pqi].top().get_y(),
			pq[pqi].top().get_Level(), pq[pqi].top().get_Priority());

		x = n0->get_x(); y = n0->get_y();

		pq[pqi].pop();
		open_nodes_map[x][y] = 0;
		closed_nodes_map[x][y] = 1;
		if (x == xFinish && y == yFinish) {
			string path = "";
			while (!(x == xStart && y == yStart)) {
				j = dir_map[x][y];
				c = '0' + (j + available_directions / 2) % available_directions;
				path = c + path;
				x += dx[j];
				y += dy[j];
			}

			delete n0;
			while (!pq[pqi].empty()) pq[pqi].pop();
			return path;
		}

		for (i = 0; i<available_directions; i++)
		{
			xdx = x + dx[i]; ydy = y + dy[i];

			if (!(xdx<0 || xdx>map_width - 1 || ydy<0 || ydy>map_height - 1 || map[xdx][ydy] == 1
				|| closed_nodes_map[xdx][ydy] == 1))
			{
				m0 = new GridCell(xdx, ydy, n0->get_Level(),
					n0->get_Priority());
				m0->next_Level(i);
				m0->update_Priority(xFinish, yFinish);

				if (open_nodes_map[xdx][ydy] == 0)
				{
					open_nodes_map[xdx][ydy] = m0->get_Priority();
					pq[pqi].push(*m0);
					dir_map[xdx][ydy] = (i + available_directions / 2) % available_directions;
				}
				else if (open_nodes_map[xdx][ydy]>m0->get_Priority())
				{
					open_nodes_map[xdx][ydy] = m0->get_Priority();
					dir_map[xdx][ydy] = (i + available_directions / 2) % available_directions;

					while (!(pq[pqi].top().get_x() == xdx &&
						pq[pqi].top().get_y() == ydy))
					{
						pq[1 - pqi].push(pq[pqi].top());
						pq[pqi].pop();
					}
					pq[pqi].pop();
					if (pq[pqi].size()>pq[1 - pqi].size()) pqi = 1 - pqi;
					while (!pq[pqi].empty())
					{
						pq[1 - pqi].push(pq[pqi].top());
						pq[pqi].pop();
					}
					pqi = 1 - pqi;
					pq[pqi].push(*m0);
				}
				else delete m0; 
			}
		}
		delete n0;
	}
	return "";
}

string calculate_movement(Coordinates start, Coordinates end) {

	for (int y = 0; y<map_height; y++) {
		for (int x = 0; x<map_width; x++) map[x][y] = 0;
	}

	for (int x = map_width / 8; x<map_width * 7 / 8; x++) {
		map[x][map_height / 2] = 1;
	}
	for (int y = map_height / 8; y<map_height * 7 / 8; y++) {
		map[map_width / 2][y] = 1;
	}

	int x_start = start.m_x, y_start = start.m_y, x_end = end.m_x, y_end = end.m_y;

	high_resolution_clock::time_point t1 = high_resolution_clock::now();
	string route = pathFind(x_start, y_start, x_end, y_end);
	high_resolution_clock::time_point t2 = high_resolution_clock::now();
	auto duration1 = duration_cast<nanoseconds>(t2 - t1).count();
	cout << "Time to calculate the route (ns): " << duration1 << endl;
	return route;
}

int main() {
	Coordinates start = Coordinates(10, 12), end = Coordinates(21, 15);
	string path = calculate_movement(start, end);
	cout << path;
	getchar();
	return 0;
}