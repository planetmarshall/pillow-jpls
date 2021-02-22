pybind11_add_module(_pycharls MODULE pycharls.cpp)

target_link_libraries( _pycharls
    PRIVATE
        pybind11::pybind11
        charls::charls
        )

install(TARGETS _pycharls
        DESTINATION .
        )