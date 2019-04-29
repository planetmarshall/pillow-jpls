add_library(
    sample_core
    core/version.cpp
)

add_library( Sample::Core ALIAS sample_core)

target_include_directories(
    sample_core
    PUBLIC
    ${CMAKE_SOURCE_DIR}/include
)

