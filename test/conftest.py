import os

import pytest


_profile_keyword = "profile"


def pytest_addoption(parser):
    default_data_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "data"))
    parser.addoption( f"--{_profile_keyword}", action="store_true", default=False, help="run profiling tests" )
    parser.addoption( "--data", action="store", default=default_data_path, help="data folder location")


def pytest_configure(config):
    config.addinivalue_line("markers", f"{_profile_keyword}: mark test as profiling test")


def pytest_collection_modifyitems(config, items):
    if config.getoption(f"--{_profile_keyword}"):
        return
    skip_profiling = pytest.mark.skip(reason="profiling test")
    for item in items:
        if _profile_keyword in item.keywords:
            item.add_marker(skip_profiling)


@pytest.fixture
def data(request):
    return os.path.realpath(request.config.getoption("--data"))
