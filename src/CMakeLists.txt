pybind11_add_module(_pycharls MODULE pycharls.cpp)

target_link_libraries( _pycharls
    PRIVATE
        Python::Module
        pybind11::headers
        charls::charls
        )

install(TARGETS _pycharls
        DESTINATION .
        )