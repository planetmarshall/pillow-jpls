from conans import (
    ConanFile,
    CMake,
    tools
)


class SampleConan(ConanFile):
    name = 'sample'
    version = '0.1.0'
    url = 'https://github.com/planetmarshall/cpp_sample_project'
    description = 'Sample C++ Project using Conan and CMake'
    license = 'https://www.apache.org/licenses/LICENSE-2.0'
    settings = 'build_type', 'compiler', 'os', 'arch'
    generators = 'cmake','cmake_find_package'
    build_requires = (
        'gtest/1.8.1'
    )

    def source(self):
        git = tools.Git()
        git.clone('git@github.com:planetmarshall/cpp_sample_project.git')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ['sample_core']
