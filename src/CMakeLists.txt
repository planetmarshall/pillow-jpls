pybind11_add_module(_pycharls MODULE pycharls.cpp)

target_link_libraries( _pycharls
    PRIVATE
        Python3::Module
        charls::charls
        )

install(TARGETS _pycharls
        DESTINATION .
        )