# make a debug enter and exit context manager that prints the arguments similar to icecream

# import inspect
import threading
from collections.abc import Callable
from datetime import datetime
from types import TracebackType
from typing import Any, ParamSpec, TypeVar, overload

import structlog
from structlog.typing import EventDict, WrappedLogger


_T = TypeVar("_T")
_P = ParamSpec("_P")

# console = Console(width=200, color_system="auto", force_terminal=True, log_path=False)
logger = structlog.get_logger()


class _Indentation(threading.local):
    indentation: int = 0


_indentation = _Indentation()


class TraceContext:
    def __init__(self, name: str, *args: Any, exit: bool = False, timeit: bool = False, **kwargs: Any):
        self.name = name
        self.args = args
        self.kwargs = kwargs
        self.exit = exit
        self.start: datetime | None = None

    def __enter__(self) -> None:
        """Log the arguments and indentation."""
        self.start = datetime.now()
        logger.info(self.name, args=self.args, kwargs=self.kwargs, indentation=_indentation.indentation, direction=">")
        _indentation.indentation += 4

    def __exit__(
        self, exctype: type[BaseException] | None, excinst: BaseException | None, exctb: TracebackType | None
    ) -> None:
        """Exit and reset indentation."""
        _indentation.indentation -= 4
        elapsed = datetime.now() - self.start if self.start else None

        match self.exit, excinst:
            case True, None:
                logger.info(self.name, indentation=_indentation.indentation, direction="<", elapsed=elapsed)
            case True, exn:
                logger.error(
                    self.name, exc_info=exn, indentation=_indentation.indentation, direction="<", elapsed=elapsed
                )
            case _:
                pass

    @classmethod
    def trace(cls, msg: str, *args: Any, **kwargs: Any) -> None:
        """Print the arguments with indentation."""
        logger.info(msg, args=args, kwargs=kwargs, indentation=_indentation.indentation)


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


def log(msg: str, *args: Any, **kwargs: Any) -> None:
    """Print the arguments with indentation."""
    # TODO: print variable_name = value for each arg
    TraceContext.trace(msg, *args, **kwargs)


def stringify(arg: Any) -> str:
    match arg:
        case None:
            return "None"
        case True:
            return "True"
        case False:
            return "False"
        case fn if callable(fn):
            # reduce length of function name with ... in the start if longer than 20 characters
            return f"{fn.__name__[:20] + '...' if len(fn.__name__) > 20 else fn.__name__}()"
        case _:
            return str(arg)


# make a structlog processor that uses the TraceContext
# https://www.structlog.org/en/stable/processors.html
def structlog_processor(logger: WrappedLogger, method_name: str, event_dict: EventDict) -> EventDict:
    """A structlog processor that uses the TraceContext."""
    # print(f"logger: {logger}, method_name: {method_name}, event_dict: {event_dict}")
    # indent event in each event_dict
    indent = event_dict.get("indentation", 0)
    num_bars = indent // 4
    remaining_spaces = indent % 4
    indentation = "│   " * num_bars + " " * remaining_spaces
    event = event_dict.get("event", "")
    direction = event_dict.get("direction", "")
    elapsed = event_dict.get("elapsed", "")
    args = ", ".join(stringify(arg) for arg in event_dict.get("args", []))

    event_dict["event"] = f"{indentation} {direction} {event}({args}) elapsed={elapsed}"
    del event_dict["indentation"]
    if "direction" in event_dict:
        del event_dict["direction"]
    if "elapsed" in event_dict:
        del event_dict["elapsed"]
    return event_dict


structlog.configure(processors=[structlog_processor, structlog.dev.ConsoleRenderer()])
