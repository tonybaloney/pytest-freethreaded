import pytest
import sys

import logging

logger = logging.getLogger(__name__)

@pytest.hookimpl
def pytest_sessionstart(session):
    # See https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_sessionstart
    assert not sys._is_gil_enabled()


@pytest.hookimpl
def pytest_sessionfinish(session):
    # See https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_sessionfinish
    ...

@pytest.hookimpl
def pytest_runtest_call(item: pytest.Item):
    # Try item.runtest()
    logger.debug("Running test %s", item.name)
    return item.runtest()
    ...

@pytest.hookimpl
def pytest_pyfunc_call(pyfuncitem: pytest.Function):
    logger.debug("Running function %s", pyfuncitem.name)
    return pyfuncitem.function()
