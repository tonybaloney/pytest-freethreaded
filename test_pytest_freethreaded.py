import pytest

@pytest.mark.freethreaded(threads=20, iterations=180)
def test_something():
    assert True


@pytest.mark.xfail
def test_a_failure():
    assert False
