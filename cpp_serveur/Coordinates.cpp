#include "Coordinates.h"
using namespace std;

Coordinates::Coordinates(int a, int b) {
    m_x = a;
    m_y = b;
}

int Coordinates::get_x() {
    return m_x;
}

int Coordinates::get_y() {
    return m_y;
}

string Coordinates::to_str() {  // Debug Function
    ostringstream oss;
    oss.clear();
    oss << "(" << m_x << ", " << m_y << ")";
    return oss.str();
}
