import pytest
from pytest_freethreaded.plugin import ConcurrencyError


class Counter:
    VALUE = 0

    def increment(self):
        self.VALUE += 1

    def decrement(self):
        self.VALUE -= 1

    def value(self):
        return self.VALUE


@pytest.fixture
def counter():
    return Counter()


def common_test_counter(counter):
    value = counter.value()
    counter.increment()
    counter.decrement()
    value_after = counter.value()
    assert value == value_after, f"{value} != {value_after}"


@pytest.mark.xfail(raises=ConcurrencyError)
def test_counter(counter):
    common_test_counter(counter)


@pytest.mark.freethreaded(threads=20, iterations=180)
@pytest.mark.xfail(raises=ConcurrencyError)
def test_counter_with_markers(counter):
    common_test_counter(counter)


@pytest.mark.freethreaded(iterations=100)
@pytest.mark.xfail(raises=ConcurrencyError)
def test_counter_with_markers_no_threads(counter):
    common_test_counter(counter)


@pytest.mark.freethreaded(threads=1, iterations=100)
def test_counter_with_markers_single_thread(counter):
    common_test_counter(counter)
