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
```

```toml
2024-05-25T09:50:03.709926Z [info     ] │ ▶ pythagoras args=(3, 4, <function <lambda> at 0x1073581f0>) kwargs={} module=test_pythagoras
2024-05-25T09:50:03.737203Z [info     ] │   │ ▶ square args=(3, <function pythagoras.<locals>.<lambda> at 0x10735b490>) kwargs={} module=test_pythagoras
2024-05-25T09:50:03.737427Z [info     ] │   │   │ ▶ square args=(4, <function pythagoras.<locals>.<lambda>.<locals>.<lambda> at 0x10735b370>) kwargs={} module=test_pythagoras
2024-05-25T09:50:03.737633Z [debug    ] │   │   │   │ ▶ add args=(9, 16, <function pythagoras.<locals>.<lambda>.<locals>.<lambda>.<locals>.<lambda> at 0x10735b5b0>) kwargs={} module=test_pythagoras
2024-05-25T09:50:03.737842Z [info     ] │   │   │   │   │ ▶ sqrt args=(25, <function <lambda> at 0x1073581f0>) kwargs={} module=test_pythagoras
2024-05-25T09:50:03.738029Z [debug    ] │   │   │   │   │   │ The result is module=test_pythagoras result=5
2024-05-25T09:50:03.738199Z [info     ] │   │   │   │   │ ◀ sqrt elapsed=361 us module=test_pythagoras
2024-05-25T09:50:03.738391Z [info     ] │   │   │ ◀ square elapsed=968 us module=test_pythagoras
2024-05-25T09:50:03.738569Z [info     ] │   │ ◀ square elapsed=1.38 ms module=test_pythagoras
2024-05-25T09:50:03.738739Z [info     ] │ ◀ pythagoras elapsed=28.84 ms module=test_pythagoras
```

Switching `traceme` to `PRODUCTION` will remove all the indentation.

```python
traceme.configure(Environment.PRODUCTION)
```

```json
{"event": "pythagoras", "timestamp": "2024-05-25T09:49:09.802510Z", "level": "info"}
{"event": "square", "timestamp": "2024-05-25T09:49:09.802929Z", "level": "info"}
{"event": "square", "timestamp": "2024-05-25T09:49:09.802991Z", "level": "info"}
{"event": "add", "timestamp": "2024-05-25T09:49:09.803050Z", "level": "debug"}
{"event": "sqrt", "timestamp": "2024-05-25T09:49:09.803101Z", "level": "info"}
{"result": 5, "event": "The result is", "timestamp": "2024-05-25T09:49:09.803147Z", "level": "debug"}
{"event": "sqrt", "timestamp": "2024-05-25T09:49:09.803200Z", "level": "info"}
{"event": "square", "timestamp": "2024-05-25T09:49:09.803248Z", "level": "info"}
{"event": "square", "timestamp": "2024-05-25T09:49:09.803291Z", "level": "info"}
{"event": "pythagoras", "timestamp": "2024-05-25T09:49:09.803335Z", "level": "info"}
```
