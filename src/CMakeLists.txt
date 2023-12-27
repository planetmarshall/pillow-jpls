Python_add_library(_pycharls MODULE pycharls.cpp WITH_SOABI)

set_target_properties(_pycharls PROPERTIES
        INTERPROCEDURAL_OPTIMIZATION ON
        CXX_VISIBILITY_PRESET hidden
        VISIBILITY_INLINES_HIDDEN ON)

target_compile_features(_pycharls PRIVATE cxx_std_17)
target_compile_definitions(_pycharls PRIVATE VERSION_INFO=${PROJECT_VERSION})

if (MSVC)
    #various warnings introuced by external code
    target_compile_options(_pycharls PRIVATE /wd4191 /wd4686 /wd5045 /wd4710 /wd4711 /wd4868)
    # unknown pragmas used by GCC
    target_compile_options(_pycharls PRIVATE /wd4068)
endif()

target_link_libraries( _pycharls
    PRIVATE
        pybind11::headers
        charls
        Eigen3::Eigen
        fmt::fmt
        )

install(TARGETS _pycharls
        LIBRARY DESTINATION pillow_jpls
        )
