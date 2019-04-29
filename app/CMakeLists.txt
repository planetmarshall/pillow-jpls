add_executable(sample
    main.cpp)

target_link_libraries(sample
    Sample::Core
    )

install(TARGETS sample
        RUNTIME DESTINATION bin
        )
