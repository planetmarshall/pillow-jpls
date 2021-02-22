pybind11_add_module(_pycharls MODULE pycharls.cpp)

target_link_libraries( _pycharls
    PRIVATE
        pybind11::headers
        Python::Module
        charls::charls
        )

install(TARGETS _pycharls
        DESTINATION .
        )