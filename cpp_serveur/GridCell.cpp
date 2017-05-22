#include <math.h>
#include "GridCell.h"


GridCell::GridCell(int x, int y, int dist, int prio) {
	m_x = x; 
	m_y = y;
	level = dist;
	priority = prio;
}

int GridCell::get_x() const {
	return m_x;
}

int GridCell::get_y() const {
	return m_y;
}

void GridCell::set_x(int x) {
	m_x = x;
}
void GridCell::set_y(int y) {
	m_y = y;
}

int GridCell::get_level() const {
	return level;
}

int GridCell::get_priority() const {
	return priority;
}

void GridCell::next_level(const int & direction) {
	level += (4 == 8 ? (direction % 2 == 0 ? 10 : 14) : 10);
}

void GridCell::update_priority(const int & x_end, const int & y_end) {
	priority = level + heuristic(x_end, y_end) * 10;
}

const int & GridCell::heuristic(const int & x_end, const int & y_end) const {
	static int xd, yd, dist;
	xd = x_end - m_x;
	yd = y_end - m_y;
	dist = static_cast<int>(sqrt(xd * xd + yd * yd));		// Euclidian Distance
	return(dist);
}