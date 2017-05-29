#include "Coordinates.h"
using namespace std;

Coordinates::Coordinates():x(-1),y(-1) {}

Coordinates::Coordinates(int a, int b):x(a),y(b) {}

string Coordinates::to_str() const
{
    ostringstream oss;
    oss.clear();
    oss << "(" << x << ", " << y << ")";
    return oss.str();
}
