pybind11_add_module(_pycharls MODULE pycharls.cpp)

target_compile_features(_pycharls PRIVATE cxx_std_17)
if (MSVC)
    #various warnings introuced by external code
    target_compile_options(_pycharls PRIVATE /wd4191 /wd4686 /wd5045 /wd4710 /wd4711 /wd4868)
endif()

target_link_libraries( _pycharls
    PRIVATE
        Python::Module
        pybind11::headers
        charls::charls
        Eigen3::Eigen3
        fmt::fmt
        )

install(TARGETS _pycharls
        LIBRARY DESTINATION .
        )