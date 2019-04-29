#include <sample/version.hpp>

#include <iostream>

int main(int argc, char* argv[]) {
    std::cout << "Sample version: " << sample::version() << std::endl;
    return 0;
}
