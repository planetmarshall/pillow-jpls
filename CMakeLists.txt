cmake_minimum_required(VERSION 3.10)

project(SampleProject)

enable_testing()
find_package(GTest)

add_subdirectory(src)
add_subdirectory(app)
add_subdirectory(test)

