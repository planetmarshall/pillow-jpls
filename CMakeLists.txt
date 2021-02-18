cmake_minimum_required(VERSION 3.18.2)

project(PillowJpls)
set(PYBIND11_FINDPYTHON=ON)

include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()
list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
find_package(pybind11 REQUIRED)
find_package(charls REQUIRED)

enable_testing()

add_subdirectory(src)
add_subdirectory(app)
add_subdirectory(test)

