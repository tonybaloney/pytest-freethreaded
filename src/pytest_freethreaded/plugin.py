import pytest
import sys
from concurrent.futures import ThreadPoolExecutor
import threading

import logging

logger = logging.getLogger(__name__)


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--threads",
        action="store",
        default=10,
        type=int,
        help="Number of threads to run the rest on",
    )


@pytest.hookimpl
def pytest_sessionstart(session):
    # See https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_sessionstart
    assert not sys._is_gil_enabled()


@pytest.hookimpl
def pytest_sessionfinish(session):
    # See https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_sessionfinish
    ...


class ConcurrencyError(Exception):
    pass


def get_one_result(item: pytest.Item, barrier: threading.Barrier):
    try:
        barrier.wait()
        return item.runtest()
    except Exception as e:
        return e


@pytest.hookimpl()
def pytest_runtest_call(item: pytest.Item):
    # Try item.runtest()
    threads = item.config.option.threads
    iterations = 200
    assert iterations % threads == 0
    logger.debug("Running test %s", item.name)
    executor = ThreadPoolExecutor(max_workers=threads)
    barrier = threading.Barrier(threads)
    results = list(executor.map(get_one_result, [item] * iterations, [barrier] * iterations))
    exceptions = [isinstance(r, Exception) for r in results]
    if all(exceptions):
        raise results[0]
    if all(not e for e in exceptions):
        return results[0]
    raise ConcurrencyError() from next(r for r in results if isinstance(r, Exception))


# @pytest.hookimpl
# def pytest_pyfunc_call(pyfuncitem: pytest.Function):
#    logger.debug("Running function %s", pyfuncitem.name)
#    XXX: Fails on test functions that take arguments
#    return pyfuncitem.function()
