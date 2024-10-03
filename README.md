# pytest-freethreaded

A Pytest plugin for helping verify that your tests and libraries are thread-safe with the Python 3.13 experimental `freethreaded` mode.

## Why do I need this plugin?

Python 3.13 introduces a new mode called `freethreaded` that allows you to run Python code with the GIL disabled. This can be useful for running CPU-bound code in parallel, but it also means that your code must be thread-safe.

Some packages and libraries with good, mature test bases have marked their libraries as "compatible" with `freethreaded`, but they have only run the tests once and in a single-thread!

Pytest-xdist won't help you here, because it uses multiprocessing to parallelize tests, and the GIL is still enabled.

So we made this plugin to help you run your tests in a thread-pool with the GIL disabled, to help you identify if your tests are thread-safe.

And the first library we tested it on (which was marked as compatible) caused a segmentation fault in CPython! So you should give this a go if you're a package maintainer. 

## Installation

```bash
pip install pytest-freethreaded
```

## Usage

We recommend using this plugin in a phased approach to identify if your tests can be run in a thread-pool with the GIL disabled, before disabling the GIL.

### Phase 1: Your tests should pass without this plugin

First, your tests should be running, and you should have tests.

### Phase 2: Run your tests with the GIL enabled, but with concurrency

This plugin will run each multiple times, in parallel. By default, it will execute each test 10 times, then repeat that 20 times. This means each test will run 200 times. This is a lot, so we recommend only running this cycle once, or on a subset of tests. 

If a test fails on any of the runs, we will raise a special error called a `ConcurrencyError` that indicates the test partially failed, most likely due to a lack of thread-safety and/or a race condition.

#### Selecting specific tests

If, during this phase you decide to only run a subset of tests, you can use the `-k` flag to select tests by name. 

Alternatively, you can set the number of threads and the executions using a marker:

```python
import pytest

@pytest.mark.freethreaded(threads=10, executions=10)
def test_my_threaded_code():
    pass
```

Then on the command-line set the threads and executions to 1:

```bash
pytest --threads 1 --executions 1
```

### Phase 3: Run your tests with the GIL disabled

If you passed phase 3; congratulations! You can now run your tests with the GIL disabled.

We recommend using the `--require-gil-disabled` flag in Pytest for this phase so that if you accidentally run Python 3.13 with the GIL on, it will fail the tests.

```bash
pytest --require-gil-disabled
```

During this final phase, if you see any _new_ Concurrency Errors or even worse you see a crash in Python 3.13, you will need to debug it. 

## Development

Setup: 

```bash
python3.13t -m venv .venv
source .venv/bin/activate
python -m pip install flit
python -m flit install -s
```

### Testing

To run the tests

```bash
pytest -vvvv --log-level=DEBUG
```

## Credits

This extension was created at PyCon JP sprints with the following team members:

- Anthony Shaw @tonybaloney
- Mike Hommey @glandium
- Oliver Basset @obassett
- Maryanne Wachter @m-clare
- Toshihiko Yanase @toshihikoyanase
- Heejun Shin @abel9851
- Otake Katsuaki
- Rei Suyama @rhoboro