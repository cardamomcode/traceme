# import pytest
from traceme import trace


def test_trace_decorator_works():
    @trace
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3
