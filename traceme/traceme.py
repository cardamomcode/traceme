import logging
import threading
from collections.abc import Callable
from datetime import datetime, timedelta
from enum import IntEnum
from types import TracebackType
from typing import Any, ParamSpec, TypeVar, overload

import colorama
import structlog
from structlog.processors import CallsiteParameter
from structlog.typing import EventDict, WrappedLogger


_T = TypeVar("_T")
_P = ParamSpec("_P")

logger = structlog.get_logger()


class Direction(IntEnum):
    ENTER = 0
    EXIT = 1


class _Indentation(threading.local):
    indentation: int = 0


_indentation = _Indentation()


class TraceContext:
    def __init__(
        self,
        name: str,
        *args: Any,
        log_level: int = logging.INFO,
        log_exit: bool = False,
        timeit: bool = False,
        **kwargs: Any,
    ):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.log_exit = log_exit
        self.start: datetime | None = None
        self.log_level = log_level

    def __enter__(self) -> None:
        """Log the arguments and indentation."""
        self.start = datetime.now()
        logger.log(
            event=self.name,
            level=self.log_level,
            args=self.args,
            kwargs=self.kwargs,
            direction=Direction.ENTER,
            elapsed=None,
        )
        _indentation.indentation += 4

    def __exit__(
        self, exctype: type[BaseException] | None, excinst: BaseException | None, exctb: TracebackType | None
    ) -> None:
        """Exit and reset indentation."""
        _indentation.indentation -= 4
        elapsed = datetime.now() - self.start if self.start else None

        match self.log_exit, excinst:
            case True, None:
                logger.log(event=self.name, level=self.log_level, direction=Direction.EXIT, elapsed=elapsed)
            case True, exn:
                logger.log(
                    event=self.name, level=self.log_level, exc_info=exn, direction=Direction.EXIT, elapsed=elapsed
                )
            case _:
                pass


def _trace(log_level: int = logging.INFO) -> Callable[..., Any]:
    def _trace(
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        func_or_string = args[0] if args else None
        log_exit = kwargs.pop("log_exit", False)

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            # if func is an init method, use the class name instead of the method name
            if func.__name__ == "__init__":
                name = func.__qualname__.split(".")[0]
            else:
                name = func.__name__

            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with TraceContext(name, *args, log_exit=log_exit, log_level=log_level, **kwargs):
                    return func(*args, **kwargs)

            return wrapper

        match func_or_string:
            case None:
                return decorator
            case _:
                return decorator(func_or_string)

    return _trace


@overload
def info(func: Callable[_P, _T]) -> Callable[_P, _T]:
    ...


@overload
def info(log_exit: bool = False) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    ...


def info(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return _trace(log_level=logging.INFO)(*args, **kwargs)


@overload
def debug(func: Callable[_P, _T]) -> Callable[_P, _T]:
    ...


@overload
def debug(log_exit: bool = False) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    ...


def debug(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return _trace(log_level=logging.DEBUG)(*args, **kwargs)


@overload
def error(func: Callable[_P, _T]) -> Callable[_P, _T]:
    ...


@overload
def error(log_exit: bool = False) -> Callable[[Callable[_P, _T]], Callable[_P, _T]]:
    ...


def error(
    *args: Any,
    **kwargs: Any,
) -> Any:
    return _trace(log_level=logging.ERROR)(*args, **kwargs)


def stringify(arg: Any) -> str:
    max_length = 30
    match arg:
        case None:
            return "None"
        case True:
            return "True"
        case False:
            return "False"
        case str(arg):
            return arg
        case fn if callable(fn):
            name = fn.__name__.split(" at ")[0]
            # reduce length of function name with ... in the start if longer than 20 characters
            return f"...{fn.__name__[:max_length] if len(name) > max_length else name}()"
        case _:
            return str(arg)


# https://www.structlog.org/en/stable/processors.html
def indentation_processor(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """A structlog processor that uses the TraceContext."""
    event_dict["indentation"] = _indentation.indentation
    return event_dict


class IndentationFormatter:
    def __init__(self, style: str = "") -> None:
        self.color = style or colorama.Fore.LIGHTBLACK_EX

    def __call__(self, key: str, value: Any) -> str:
        return f"{self.color}{'│   ' * (value // 4)}│"


class DirectionFormatter:
    def __init__(self, style: str = "") -> None:
        self.color = style or colorama.Fore.LIGHTBLACK_EX

    def __call__(self, key: str, value: object | None) -> str:
        match value:
            case Direction.ENTER:
                return f"{self.color}▶"
            case Direction.EXIT:
                return f"{self.color}◀"
            case _:
                return ""


class ElapsedFormatter:
    def __init__(self, key_style: str = "", value_style: str = "") -> None:
        self.key_style = key_style or colorama.Fore.LIGHTBLACK_EX
        self.value_style = value_style or colorama.Fore.GREEN
        self.reset_style = colorama.Style.RESET_ALL

    def __call__(self, key: str, value: object) -> str:
        match value:
            case timedelta() if value.total_seconds() < 0.001:
                return (
                    f"{self.key_style}elapsed="
                    f"{self.value_style}{value.total_seconds() * 1_000_000:.0f} us"
                    f"{self.reset_style}"
                )
            case timedelta() if value.total_seconds() < 1:
                return (
                    f"{self.key_style}elapsed="
                    f"{self.value_style}{value.total_seconds() * 1000:.2f} ms"
                    f"{self.reset_style}"
                )
            case timedelta():
                return f"{self.key_style}elapsed={self.value_style}{value}{self.reset_style} secs"
            case _:
                return ""


indentation_column = structlog.dev.Column(
    "indentation",
    formatter=IndentationFormatter(style=colorama.Fore.LIGHTBLACK_EX),
)
direction_column = structlog.dev.Column(
    "direction",
    formatter=DirectionFormatter(style=colorama.Fore.LIGHTBLACK_EX),
)

columns = [
    structlog.dev.Column(
        "timestamp",
        structlog.dev.KeyValueColumnFormatter(
            key_style=None,
            value_style=colorama.Fore.YELLOW,
            reset_style=colorama.Style.RESET_ALL,
            value_repr=str,
        ),
    ),
    structlog.dev.Column(
        "level",
        structlog.dev.LogLevelColumnFormatter(
            level_styles={
                "critical": colorama.Style.BRIGHT + colorama.Fore.RED,
                "error": colorama.Fore.RED,
                "exception": colorama.Fore.RED,
                "warning": colorama.Fore.YELLOW,
                "info": colorama.Fore.GREEN,
                "debug": colorama.Fore.BLUE,
            },
            reset_style=colorama.Style.RESET_ALL,
        ),
    ),
    indentation_column,
    direction_column,
    structlog.dev.Column(
        "event",
        structlog.dev.KeyValueColumnFormatter(
            key_style=None,
            value_style=colorama.Style.BRIGHT + colorama.Fore.MAGENTA,
            reset_style=colorama.Style.RESET_ALL,
            value_repr=stringify,
        ),
    ),
    structlog.dev.Column(
        "elapsed",
        formatter=ElapsedFormatter(key_style=colorama.Fore.LIGHTBLACK_EX),
    ),
    structlog.dev.Column(
        "",
        structlog.dev.KeyValueColumnFormatter(
            key_style=colorama.Fore.CYAN,
            value_style=colorama.Fore.GREEN,
            reset_style=colorama.Style.RESET_ALL,
            value_repr=str,
        ),
    ),
]


def configure() -> None:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            indentation_processor,
            structlog.processors.CallsiteParameterAdder(
                parameters=[CallsiteParameter.MODULE],
                additional_ignores=[__name__],
            ),
            structlog.dev.ConsoleRenderer(columns=columns),
        ]
    )


__all__ = [
    "info",
    "debug",
    "error",
    "configure",
    "columns",
    "indentation_column",
    "direction_column",
]
