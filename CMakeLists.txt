cmake_minimum_required(VERSION 3.18)

project(Pycharls VERSION 1.1.0)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
if(SKBUILD)
    set(PYCHARLS_CONAN_COMMAND conan CACHE STRING "conan command")
    set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
    set(Python_INCLUDE_DIR "${PYTHON_INCLUDE_DIR}")
    set(DUMMY "${PYTHON_VERSION_STRING}")  # Not needed, silences a warning
    find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

    execute_process(
            COMMAND
            "${Python3_EXECUTABLE}" -c
            "import pybind11; print(pybind11.get_cmake_dir())"
            OUTPUT_VARIABLE _tmp_dir
            OUTPUT_STRIP_TRAILING_WHITESPACE COMMAND_ECHO STDOUT)
    list(APPEND CMAKE_PREFIX_PATH "${_tmp_dir}")

    if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
        message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
        file(DOWNLOAD "https://github.com/conan-io/cmake-conan/raw/v0.15/conan.cmake" "${CMAKE_BINARY_DIR}/conan.cmake")
    endif()
    include(${CMAKE_BINARY_DIR}/conan.cmake)
    conan_cmake_configure()
    conan_cmake_autodetect(settings)
    conan_cmake_install(PATH_OR_REFERENCE . BUILD missing)
else()
    find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
    include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
    conan_basic_setup()
endif()

find_package(pybind11 REQUIRED)
find_package(charls REQUIRED)
find_package(fmt REQUIRED)
find_package(Eigen3 REQUIRED)

if (MSVC)
    add_compile_options(/Wall /permissive-)
else()
    add_compile_options(-Wall -Wextra -Wpedantic)
    if (CMAKE_CXX_COMPILER_ID MATCHES Clang$)
        add_compile_options(-Wconversion -Wconditional-uninitialized)
    endif()
endif()

add_subdirectory(src)

