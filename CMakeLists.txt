cmake_minimum_required(VERSION 3.24)

project(Pycharls VERSION 1.3.0)

find_package(Python COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
find_package(charls CONFIG REQUIRED)
find_package(fmt CONFIG REQUIRED)
find_package(Eigen3 CONFIG REQUIRED)

if (MSVC)
    add_compile_options(/Wall /permissive-)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Wno-unknown-pragmas)
    if (CMAKE_CXX_COMPILER_ID MATCHES Clang$)
        add_compile_options(-Wconversion -Wconditional-uninitialized)
    endif()
endif()

add_subdirectory(src)
