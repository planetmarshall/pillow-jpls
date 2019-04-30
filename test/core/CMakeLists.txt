include(GoogleTest)
add_executable(test_core 
    main.cpp
    test_version.cpp)

target_link_libraries(test_core
    PUBLIC
    GTest::GTest
    Sample::Core
)

add_test(
    NAME test_core
    COMMAND test_core
    )

