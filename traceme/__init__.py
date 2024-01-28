"""Traceme package."""
from ._version import __version__
from .traceme import TraceMe, log, trace


__all__ = ["TraceMe", "trace", "log", "__version__"]
