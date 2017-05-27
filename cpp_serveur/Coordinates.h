#pragma once
#include <sstream>
class Coordinates{

public:
    int m_x, m_y;

    Coordinates(int, int);
    int get_x(), get_y();
    Coordinates operator+ (Coordinates &rhs) { return Coordinates(m_x + rhs.get_x(), m_y + rhs.get_y()); }
    Coordinates operator- (Coordinates &rhs) { return Coordinates(m_x - rhs.get_x(), m_y - rhs.get_y()); }
    bool operator< (Coordinates &rhs) { return m_x < rhs.get_x(); }
    bool operator> (Coordinates &rhs) { return m_x > rhs.get_x(); }
    bool operator== (Coordinates &rhs) { return (m_x == rhs.get_x()) && (m_y == rhs.get_y()); }
    std::string to_str();
};
