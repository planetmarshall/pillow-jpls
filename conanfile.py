from os import path

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
    generators = 'cmake'
    requires = (
        'gtest/1.8.1@bincrafters/stable'
    )
    staging_dir = 'conan_stage'

    def source(self):
        git = tools.Git()
        git.clone('git@github.com:planetmarshall/cpp_sample_project.git')


    def build(self):
        cmake = CMake(self)
        cmake_definitions = {
            'CMAKE_INSTALL_PREFIX': self.staging_dir
        }
        cmake.definitions.update(cmake_definitions)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy('*', src=self.staging_dir)


    def package_info(self):
        self.cpp_info.libs = ['sample_core']


