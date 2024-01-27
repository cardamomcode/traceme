# import pytest
from traceme import log, trace


def test_trace_decorator_works():
    @trace
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_trace_decorator_parametrized_works():
    @trace(exit=True)
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_trace_string():
    a = log("hello world")
    assert a is None


def test_trace_with_params():
    a = 10
    a = log(a)
    assert a is None
