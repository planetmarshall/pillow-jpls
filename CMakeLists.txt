cmake_minimum_required(VERSION 3.18.2)

project(Pycharls CXX)
set(PYCHARLS_CONAN_COMMAND conan CACHE STRING "conan command")
set(PYBIND11_FINDPYTHON ON)

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
find_package(pybind11 REQUIRED)
find_package(charls REQUIRED)

add_compile_options(-Wall -Wextra -Wpedantic)
add_subdirectory(src)

