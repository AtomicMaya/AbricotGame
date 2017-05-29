#pragma once

class GridCell {
private:
	int m_x, m_y; // Position of cell defined by x, y
	int level; // Distance from start : A* g(x)
	int priority; // Priority of cell : A* f(x)

public:
	GridCell(int, int, int, int);
	
	int get_x() const;
	int get_y() const;
	void set_x(int);
	void set_y(int);

	int get_level() const;
	int get_priority() const;
	void next_level(const int & direction);
	void update_priority(const int & x_end, const int & y_end);

	const int & heuristic(const int & x_end, const int & y_end) const;
	friend bool operator<(const GridCell & a, const GridCell & b) { return a.get_priority() > b.get_priority(); }
};
