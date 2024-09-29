import pytest
import sys
from concurrent.futures import ThreadPoolExecutor

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

def get_one_result(item: pytest.Item):
    try:
        return item.runtest()
    except Exception as e:
        return e


@pytest.hookimpl
def pytest_runtest_call(item: pytest.Item):
    # Try item.runtest()
    logger.debug("Running test %s", item.name)
    executor = ThreadPoolExecutor(max_workers=20)
    results = list(executor.map(get_one_result, [item] * 200))
    exceptions = [isinstance(r, Exception) for r in results]
    if all(exceptions):
       raise results[0]
    if all(not e for e in exceptions):
       return results[0]
    raise Exception("Result discrepancy") from next(r for r in results if isinstance(r, Exception))

#@pytest.hookimpl
#def pytest_pyfunc_call(pyfuncitem: pytest.Function):
#    logger.debug("Running function %s", pyfuncitem.name)
#    XXX: Fails on test functions that take arguments
#    return pyfuncitem.function()
