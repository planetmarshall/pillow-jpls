pybind11_add_module(_pycharls MODULE pycharls.cpp)

target_compile_features(_pycharls PRIVATE cxx_std_17)

target_link_libraries( _pycharls
    PRIVATE
        Python::Module
        pybind11::headers
        charls::charls
        Eigen3::Eigen3
        fmt::fmt
        range-v3::range-v3
        )

install(TARGETS _pycharls
        LIBRARY DESTINATION .
        )