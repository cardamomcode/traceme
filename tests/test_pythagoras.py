# write pytaogoras test cases here using continusations instead of return

import math
from collections.abc import Callable

import structlog

import traceme


logger = structlog.get_logger(__name__)


@traceme.debug
def add(a: int, b: int, cont: Callable[[int], None]) -> None:
    cont(a + b)


@traceme.info(log_exit=True)
def square(a: int, cont: Callable[[int], None]) -> None:
    cont(a * a)


@traceme.info(log_exit=True)
def sqrt(a: int, cont: Callable[[int], None]) -> None:
    # raise Exception("Not implemented")
    cont(int(math.sqrt(a)))


@traceme.info(log_exit=True)
def pythagoras(a: int, b: int, cont: Callable[[int], None]) -> None:
    square(
        a,
        lambda a2: square(
            b,
            lambda b2: add(
                a2,
                b2,
                lambda a2b2: sqrt(
                    a2b2,
                    cont,
                ),
            ),
        ),
    )


if __name__ == "__main__":
    traceme.configure()
    pythagoras(3, 4, lambda result: logger.debug("The result is", result=result))
