cmake_minimum_required(VERSION 3.18)

project(Pycharls VERSION 1.1.0)

option(PYCHARLS_COMPILE_STRICT "Treat compiler warnings as errors" ON)
list(APPEND CMAKE_MODULE_PATH ${CMAKE_BINARY_DIR})
if(SKBUILD)
    set(Python_EXECUTABLE "${PYTHON_EXECUTABLE}")
    find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

    if(NOT EXISTS "${CMAKE_BINARY_DIR}/conan.cmake")
        message(STATUS "Downloading conan.cmake from https://github.com/conan-io/cmake-conan")
        file(DOWNLOAD "https://github.com/conan-io/cmake-conan/raw/v0.16.1/conan.cmake" "${CMAKE_BINARY_DIR}/conan.cmake")
    endif()
    include(${CMAKE_BINARY_DIR}/conan.cmake)
    conan_cmake_configure()
    conan_cmake_autodetect(settings)
    conan_cmake_install(
            PATH_OR_REFERENCE ${CMAKE_SOURCE_DIR}
            BUILD missing
            SETTINGS ${settings}
    )
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
    if (PYCHARLS_COMPILE_STRICT)
        add_compile_options(/WX)
    endif()
else()
    add_compile_options(-Wall -Wextra -Wpedantic -Wno-unknown-pragmas)
    if (CMAKE_CXX_COMPILER_ID MATCHES Clang$)
        add_compile_options(-Wconversion -Wconditional-uninitialized)
    endif()
    if (PYCHARLS_COMPILE_STRICT)
        add_compile_options(-Werror)
    endif()
endif()

add_subdirectory(src)

