#include <gtest/gtest.h>
#include <sample/version.hpp>

TEST(TestVersion, VersionIsNotNull) {
    ASSERT_EQ("1.0.0", sample::version());
}
