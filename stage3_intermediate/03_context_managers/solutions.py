"""Reference solutions for 3.03. Try the exercises yourself first!"""
from __future__ import annotations

import io
import os
import time
from contextlib import ExitStack, contextmanager, redirect_stdout
from pathlib import Path


class Timer:
    def __init__(self) -> None:
        self.elapsed: float | None = None
        self._start = 0.0

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self._start
        return False


@contextmanager
def temp_env_var(name: str, value: str):
    missing = object()
    old = os.environ.get(name, missing)
    os.environ[name] = value
    try:
        yield
    finally:
        if old is missing:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old  # type: ignore[assignment]


@contextmanager
def changed_directory(path):
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield Path(os.getcwd())
    finally:
        os.chdir(previous)


class Transaction:
    def __init__(self, data: dict) -> None:
        self.data = data
        self._snapshot: dict = {}

    def __enter__(self):
        self._snapshot = dict(self.data)
        return self.data

    def __exit__(self, exc_type, exc, tb):
        if exc_type is not None:
            self.data.clear()
            self.data.update(self._snapshot)
        return False


@contextmanager
def suppress_and_record(*exception_types):
    errors: list = []
    try:
        yield errors
    except exception_types as exc:
        errors.append(exc)


@contextmanager
def capture_output():
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        yield buffer


@contextmanager
def open_all(paths, mode: str = "r"):
    with ExitStack() as stack:
        yield [stack.enter_context(open(p, mode)) for p in paths]


class Indenter:
    def __init__(self, unit: str = "    ") -> None:
        self.unit = unit
        self.depth = 0

    def line(self, text: str) -> str:
        return self.unit * self.depth + text

    def __enter__(self):
        self.depth += 1
        return self

    def __exit__(self, exc_type, exc, tb):
        self.depth -= 1
        return False
