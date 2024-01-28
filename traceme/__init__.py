"""Traceme package."""
from ._version import __version__
from .traceme import TraceContext, log, trace


__all__ = ["TraceContext", "trace", "log", "__version__"]
