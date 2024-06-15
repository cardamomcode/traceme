# import pytest
import structlog

import traceme


logger = structlog.get_logger()


def test_trace_decorator_works():
    @traceme.info
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_trace_decorator_parametrized_works():
    @traceme.info(log_exit=True)
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_trace_string():
    a = logger.info("hello world")
    assert a is None


def test_trace_with_params():
    a = 10
    a = logger.info(a)
    assert a is None


def test_recursive():
    @traceme.info(log_exit=True)
    def factorial(n: int) -> int:
        if n == 0:
            return 1
        return n * factorial(n - 1)

    assert factorial(5) == 120


if __name__ == "__main__":
    traceme.configure(traceme.Environment.DEVELOPMENT)
    test_recursive()
