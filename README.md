# traceme

Is a library that helps you to debug and trace your code. It aims to
replace `print` debugging with a more powerful and permanent solution.

## Installation

```bash
pip install traceme
```

## Usage

```python
import math
from collections.abc import Callable

from traceme import log, trace


@trace(exit=True)
def add(a: int, b: int, cont: Callable[[int], None]) -> None:
    cont(a + b)


@trace(exit=True)
def square(a: int, cont: Callable[[int], None]) -> None:
    cont(a * a)


@trace(exit=True)
def sqrt(a: int, cont: Callable[[int], None]) -> None:
    cont(int(math.sqrt(a)))


@trace(exit=True)
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
    pythagoras(3, 4, lambda result: log("The result is", result))
```

This will output:

```bash
[17:56:32] │> pythagoras 3 4
           │< pythagoras
           │> then <function <lambda> at 0x100566c00>
           │   │> square 3
           │   │< square
           │   │> then <function pythagoras.<locals>.then.<locals>.<lambda> at 0x100ca8860>
           │   │   │> square 4
           │   │   │< square
           │   │   │> then <function pythagoras.<locals>.then.<locals>.<lambda>.<locals>.<lambda> at 0x100ca8b80>
           │   │   │   │> add 9 16
           │   │   │   │< add
           │   │   │   │> then <function pythagoras.<locals>.then.<locals>.<lambda>.<locals>.<lambda>.<locals>.<lambda> at 0x100ca8220>
           │   │   │   │   │> sqrt 25
           │   │   │   │   │< sqrt
           │   │   │   │   │> then <function <lambda> at 0x100566c00>
           │   │   │   │   │    The result is 5
           │   │   │   │   │< then
           │   │   │   │< then
           │   │   │< then
           │   │< then
           │< then
```
