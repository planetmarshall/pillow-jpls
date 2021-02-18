pybind11_add_module(pycharls MODULE pycharls.cpp)

install(TARGETS pycharls
        LIBRARY DESTINATION lib
        )