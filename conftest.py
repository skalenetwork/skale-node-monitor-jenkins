import pytest


def pytest_addoption(parser):
    """PyTest method for adding custom console parameters"""

    parser.addoption("--target", action="store", default=0, type=str,
                     help="Set additional value for target")


@pytest.fixture(scope="session")
def target(request):
    """Handler for --target parameter"""

    return request.config.getoption("--target")
