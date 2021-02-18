cmake_minimum_required(VERSION 3.18.2)

project(Pycharls VERSION 0.0.1)
set(PYCHARLS_CONAN_COMMAND conan CACHE STRING "conan command")

if(SKBUILD)
    set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
    set(Python_INCLUDE_DIR "${PYTHON_INCLUDE_DIR}")
    set(Python_LIBRARY "${PYTHON_LIBRARY}")
    set(DUMMY "${PYTHON_VERSION_STRING}")  # Not needed, silences a warning
endif()

if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
    message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
    file(DOWNLOAD "https://github.com/conan-io/cmake-conan/raw/v0.15/conan.cmake" "${CMAKE_BINARY_DIR}/conan.cmake")
endif()

include(${CMAKE_BINARY_DIR}/conan.cmake)
conan_cmake_run(
        CONANFILE conanfile.txt
        BASIC_SETUP
        PROFILE_AUTO
        CONAN_COMMAND ${PYCHARLS_CONAN_COMMAND}
        BUILD outdated
)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
find_package(Python REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)
find_package(charls REQUIRED)

add_compile_options(-Wall -Wextra -Wpedantic)
add_subdirectory(src)

