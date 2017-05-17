cmake_minimum_required(VERSION 3.7)
project(cpp_serveur)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES
        GridCell.h GridCell.cpp
        pathfinding.cpp Coordinates.cpp Coordinates.h)

add_executable(cpp_serveur ${SOURCE_FILES} pathfinding.cpp)