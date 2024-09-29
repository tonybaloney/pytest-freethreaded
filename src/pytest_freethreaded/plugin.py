import pytest
import sys
from concurrent.futures import ThreadPoolExecutor
import threading
from itertools import repeat

import logging

logger = logging.getLogger(__name__)


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--threads",
        action="store",
        default=10,
        type=int,
        help="Number of threads to run the tests on",
    )
    parser.addoption(
        "--iterations",
        action="store",
        default=200,
        type=int,
        help="Number of iterations to run the tests for",
    )


def pytest_configure(config: pytest.Config):
    config.addinivalue_line(
        name="markers",
        line="freethreaded(threads=n, iterations=m): Run test (m) times, in a threadpool of (n) threads",
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
    def __init__(self, iterations: int, failures: int, threads: int):
        self.iterations = iterations
        self.failures = failures
        self.threads = threads

    def __str__(self):
        return f"{self.failures} failures in {self.iterations} iterations across {self.threads} threads"


def get_one_result(item: pytest.Item, barrier: threading.Barrier):
    try:
        barrier.wait()
        return item.runtest()
    except Exception as e:
        return e


@pytest.hookimpl()
def pytest_runtest_call(item: pytest.Item):
    # Try item.runtest()
    config_threads = item.config.option.threads
    config_iterations = item.config.option.iterations
    freethreaded_mark = item.get_closest_marker(name="freethreaded")

    if freethreaded_mark:
        threads = freethreaded_mark.kwargs.get("threads", config_threads)
        iterations = freethreaded_mark.kwargs.get("iterations", config_iterations)
    else:
        iterations = config_iterations
        threads = config_threads

    logger.debug("Running test %s", item.name)
    executor = ThreadPoolExecutor(max_workers=threads)
    barrier = threading.Barrier(threads)
    results = list(
        executor.map(
            get_one_result, repeat(item, iterations), repeat(barrier, iterations)
        )
    )
    exceptions = [r for r in results if isinstance(r, Exception)]
    if not exceptions:
        return results[0]
    if len(exceptions) == len(results):
        raise results[0]
    raise ConcurrencyError(
        iterations=iterations, failures=len(exceptions), threads=threads
    ) from exceptions[0]


# @pytest.hookimpl
# def pytest_pyfunc_call(pyfuncitem: pytest.Function):
#    logger.debug("Running function %s", pyfuncitem.name)
#    XXX: Fails on test functions that take arguments
#    return pyfuncitem.function()
