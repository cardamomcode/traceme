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

<img width="977" alt="Screenshot 2024-05-25 at 12 02 27" src="https://github.com/dbrattli/traceme/assets/849479/9a435fe0-fd73-4c62-b55b-e84983402b86">


Switching `traceme` to `Environment.PRODUCTION` will remove all the indentation.

```python
from traceme import Environment

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
