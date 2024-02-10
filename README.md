# traceme

Is a `structlog` helper library that helps you to debug and trace your
code. It aims to replace `print` debugging with a more powerful and
permanent solution.

## Installation

```bash
pip install traceme
```

## Usage

```python
import math
from collections.abc import Callable

import structlog

import traceme


logger = structlog.get_logger()

@traceme.info(exit=True)
def add(a: int, b: int, cont: Callable[[int], None]) -> None:
    cont(a + b)


@traceme.info(exit=True)
def square(a: int, cont: Callable[[int], None]) -> None:
    cont(a * a)


@traceme.info(exit=True)
def sqrt(a: int, cont: Callable[[int], None]) -> None:
    cont(int(math.sqrt(a)))


@traceme.info(exit=True)
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

    pythagoras(3, 4, lambda result: logger.info("The result is", result=result))
```

This will output:

```bash
❯ poetry run python tests/test_pythagoras.py
2024-02-10T15:52:19.284431Z [info     ] │ ▶ pythagoras args=(3, 4, <function <lambda> at 0x1040c2840>) kwargs={} module=test_pythagoras
2024-02-10T15:52:19.313361Z [info     ] │   │ ▶ square args=(3, <function pythagoras.<locals>.<lambda> at 0x1040c2ac0>) kwargs={} module=test_pythagoras
2024-02-10T15:52:19.313621Z [info     ] │   │   │ ▶ square args=(4, <function pythagoras.<locals>.<lambda>.<locals>.<lambda> at 0x1040c2c00>) kwargs={} module=test_pythagoras
2024-02-10T15:52:19.314165Z [debug    ] │   │   │   │ ▶ add args=(9, 16, <function pythagoras.<locals>.<lambda>.<locals>.<lambda>.<locals>.<lambda> at 0x1040c2ca0>) kwargs={} module=test_pythagoras
2024-02-10T15:52:19.314407Z [info     ] │   │   │   │   │ ▶ sqrt args=(25, <function <lambda> at 0x1040c2840>) kwargs={} module=test_pythagoras
2024-02-10T15:52:19.314616Z [debug    ] │   │   │   │   │   │ The result is module=test_pythagoras result=5
2024-02-10T15:52:19.314806Z [info     ] │   │   │   │   │ ◀ sqrt elapsed=399 us module=test_pythagoras
2024-02-10T15:52:19.315301Z [info     ] │   │   │ ◀ square elapsed=1.68 ms module=test_pythagoras
2024-02-10T15:52:19.315493Z [info     ] │   │ ◀ square elapsed=2.15 ms module=test_pythagoras
2024-02-10T15:52:19.315676Z [info     ] │ ◀ pythagoras elapsed=31.27 ms module=test_pythagoras
```
