pybind11_add_module(_pycharls pycharls.cpp)

target_compile_features(_pycharls PRIVATE cxx_std_17)
if (MSVC)
    #various warnings introuced by external code
    target_compile_options(_pycharls PRIVATE /wd4191 /wd4686 /wd5045 /wd4710 /wd4711 /wd4868)
    # unknown pragmas used by GCC
    target_compile_options(_pycharls PRIVATE /wd4068)
endif()

target_link_libraries( _pycharls
    PRIVATE
        charls::charls
        Eigen3::Eigen3
        fmt::fmt
        )

install(TARGETS _pycharls
        LIBRARY DESTINATION .
        )