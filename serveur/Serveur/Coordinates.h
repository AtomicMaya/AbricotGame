#ifndef COORDINATES
#define COORDINATES

#include <sstream>
class Coordinates
{
public:
    const int x, y;
    Coordinates();
    Coordinates(int, int);
    Coordinates operator+ (Coordinates const& rhs) const
    {
        return Coordinates(x + rhs.x, y + rhs.y);
    }
    Coordinates operator- (Coordinates const& rhs) const
    {
        return Coordinates(x - rhs.x, y - rhs.y);
    }
    bool operator< (Coordinates const& rhs) const
    {
        return x < rhs.x;
    }
    bool operator> (Coordinates const& rhs) const
    {
        return x > rhs.x;
    }
    bool operator== (Coordinates const& rhs) const
    {
        return (x == rhs.x) && (y == rhs.y);
    }
    std::string to_str() const;
};

#endif
