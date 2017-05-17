#ifndef COORDINATES
#define COORDINATES

#include <sstream>
class Coordinates{
    int x;
    int y;

public:
    Coordinates(int, int);
    int get_x(), get_y();
    Coordinates operator+ (Coordinates &rhs) { return Coordinates(x + rhs.get_x(), y + rhs.get_x()); }
    Coordinates operator- (Coordinates &rhs) { return Coordinates(x - rhs.get_y(), y - rhs.get_y()); }
    bool operator< (Coordinates &rhs) { return x < rhs.get_x(); }
    bool operator> (Coordinates &rhs) { return x > rhs.get_x(); }
    bool operator== (Coordinates &rhs) { return (x == rhs.get_x()) && (y == rhs.get_y()); }
    std::string to_str();
};
#endif