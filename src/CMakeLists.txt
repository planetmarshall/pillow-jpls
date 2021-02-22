pybind11_add_module(_pycharls MODULE pycharls.cpp)

target_include_directories(_pycharls
        PRIVATE
        ${PYTHON_INCLUDE_DIRS}
        )

target_link_libraries( _pycharls
    PRIVATE
        pybind11::pybind11
        ${PYTHON_LIBRARIES}
        charls::charls
        )

install(TARGETS _pycharls
        DESTINATION .
        )