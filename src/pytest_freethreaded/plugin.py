import pytest
import sys
import base
from concurrent.futures import ThreadPoolExecutor

import logging

logger = logging.getLogger(__name__)

nogil_unsupported_modules = []



class ModuleNeedsGIL(Exception):
    """Exception raised when an imported module has not declared noGIL compatibility."""

    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"

@pytest.hookimpl
def pytest_sessionstart(session):
    # See https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_sessionstart
    assert not sys._is_gil_enabled()

@pytest.hookimpl
def pytest_sessionfinish(session):
    # See https://docs.pytest.org/en/7.1.x/reference/reference.html#pytest.hookspec.pytest_sessionfinish
    if nogil_unsupported_modules:
        raise ModuleNeedsGIL(nogil_unsupported_modules[0].message)

def get_one_result(item: pytest.Item):
    try:
        return item.runtest()
    except Exception as e:
        return e

def pytest_warning_recorded(w, *args, **kwargs):
    runtime_err_val = "The global interpreter lock (GIL) has been enabled to load module"
    if issubclass(w.category, RuntimeWarning) and runtime_err_val in str(w.message):
        logger.warning(w.message)
        nogil_unsupported_modules.append(w)

def pytest_warning_captured(w, *args, **kwargs):
    # Support version of pytest older than 7.0.0
    pytest_warning_recorded(w, *args, **kwargs)

#@pytest.hookimpl
#def pytest_pyfunc_call(pyfuncitem: pytest.Function):
#    logger.debug("Running function %s", pyfuncitem.name)
#    XXX: Fails on test functions that take arguments
#    return pyfuncitem.function()
