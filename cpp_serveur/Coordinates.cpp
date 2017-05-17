#include "Coordinates.h"
using namespace std;

Coordinates::Coordinates(int a, int b) {
    x = a;
    y = b;
}

int Coordinates::get_x() {
    return x;
}

int Coordinates::get_y() {
    return y;
}

string Coordinates::to_str(){
    ostringstream oss;
    oss.clear();
    oss << "(" << x << ", " << y << ")";
    return oss.str();
}

bool Coordinates::adjacent(Coordinates& other) {
    return !((x != other.get_x()) && (y != other.get_y()));

}
