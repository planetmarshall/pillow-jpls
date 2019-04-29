
add_library(
    sample_core
    core/version.cpp
)

add_library(Sample::Core ALIAS sample_core)

target_include_directories(
    sample_core
    PUBLIC
    ${CMAKE_SOURCE_DIR}/include
)

install(
        TARGETS sample_core
        EXPORT SampleTargets
        LIBRARY DESTINATION lib
        ARCHIVE DESTINATION lib
        RUNTIME DESTINATION bin
        INCLUDES DESTINATION include
        )

install(
        DIRECTORY ${CMAKE_SOURCE_DIR}/include/sample
        DESTINATION include
        FILES_MATCHING PATTERN *.hpp
)

