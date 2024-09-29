import pytest


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


def test_counter(counter):
    value = counter.value()
    counter.increment()
    counter.decrement()
    value_after = counter.value()
    assert value == value_after, f"{value} != {value_after}"


@pytest.mark.freethreaded(threads=20, iterations=180)
def test_counter_with_markers(counter):
    value = counter.value()
    counter.increment()
    counter.decrement()
    value_after = counter.value()
    assert value == value_after, f"{value} != {value_after}"


@pytest.mark.freethreaded(iterations=180)
def test_counter_with_markers_no_threads(counter):
    value = counter.value()
    counter.increment()
    counter.decrement()
    value_after = counter.value()
    assert value == value_after, f"{value} != {value_after}"
