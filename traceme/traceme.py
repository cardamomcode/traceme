# make a debug enter and exit context manager that prints the arguments similar to icecream

# import inspect
import threading
from collections.abc import Callable
from datetime import datetime
from types import TracebackType
from typing import Any, ParamSpec, TypeVar, overload

# from rich import print
from rich.console import Console


_T = TypeVar("_T")
_P = ParamSpec("_P")

console = Console(width=200, color_system="auto", force_terminal=True, log_path=False)


class _Indentation(threading.local):
    indentation: int = 0


_indentation = _Indentation()

# Store the code for a full width vertical line. Codes at https://rich.readthedocs.io/en/stable/appendix/colors.html
bar: str = "[grey23]│[/grey23]"
func_color: str = "deep_sky_blue4"


class TraceContext:
    def __init__(self, name: str, *args: Any, exit: bool = False, timeit: bool = False, **kwargs: Any):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.exit = exit
        self.start: datetime | None = None
        # inspect arguments similar to icecream
        # frame = inspect.currentframe().f_back
        # line = inspect.getframeinfo(frame).code_context[0]
        # variable_name = line[line.index("(") + 1 : line.index(")")].strip()
        # debug("*** variable_name", variable_name)

    @staticmethod
    def indent() -> str:
        num_bars = _indentation.indentation // 4
        remaining_spaces = _indentation.indentation % 4
        indentation = f"{bar}   " * num_bars + " " * remaining_spaces
        return indentation

    def __enter__(self) -> None:
        """Print the arguments with indentation."""
        self.start = datetime.now()
        indentation = self.indent()
        console.log(f"{indentation}{bar}> [{func_color}]{self.name}[/]", *self.args, **self.kwargs)
        _indentation.indentation += 4

    def __exit__(
        self, exctype: type[BaseException] | None, excinst: BaseException | None, exctb: TracebackType | None
    ) -> None:
        """Exit and reset indentation."""
        _indentation.indentation -= 4
        indentation = self.indent()

        match self.exit, excinst:
            case True, None:
                console.log(f"{indentation}{bar}< [{func_color}]{self.name}[/]")
            case True, exn:
                console.log(f"{indentation}{bar}< [{func_color}]{self.name}[/] [red]{exn!r}[/]")
            case _:
                pass

    @classmethod
    def trace(cls, *args: Any, **kwargs: Any) -> None:
        """Print the arguments with indentation."""
        indentation = cls.indent()
        console.log(indentation, *args, **kwargs)


@overload
def trace(func: Callable[_P, _T]) -> Callable[_P, _T]:
    ...


@overload
def trace(exit: bool = False) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    ...


def trace(
    *args: Any,
    **kwargs: Any,
) -> Any:
    func_or_string = args[0] if args else None
    exit = kwargs.pop("exit", False)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with TraceContext(func.__name__, *args, exit=exit, **kwargs):
                return func(*args, **kwargs)

        return wrapper

    match func_or_string:
        case None:
            return decorator
        case _:
            return decorator(func_or_string)


def log(*args: Any, **kwargs: Any) -> None:
    """Print the arguments with indentation."""
    # TODO: print variable_name = value for each arg
    TraceContext.trace(*args, **kwargs)
