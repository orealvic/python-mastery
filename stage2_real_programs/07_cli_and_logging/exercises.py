"""2.07 — Command-Line Programs & Logging

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 2.07` from the course root to test your work.
"""
from __future__ import annotations

import argparse
import logging
import sys
from typing import Callable, Sequence


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for a tiny `greet` program.

    `prog` is "greet". Arguments:
    - positional `name` (str)
    - `-s` / `--shout`: flag, stores True (default False)
    - `-n` / `--times`: int, default 1
    - `-g` / `--greeting`: str, default "Hello"

    >>> args = build_parser().parse_args(["Ada", "-n", "2", "--shout"])
    >>> (args.name, args.times, args.shout, args.greeting)
    ('Ada', 2, True, 'Hello')

    Invalid input (missing name, `--times abc`) makes argparse exit with
    status 2 -- you get that for free.
    """
    raise NotImplementedError


def greet_lines(args: argparse.Namespace) -> list[str]:
    """Return the greeting lines for parsed `args` (a Namespace from `build_parser`).

    Each line is "<greeting>, <name>!", uppercased when `args.shout`, and the
    list has `args.times` identical lines (0 times -> empty list).

    >>> greet_lines(build_parser().parse_args(["Ada", "-g", "Hi"]))
    ['Hi, Ada!']
    """
    raise NotImplementedError


def main(argv: Sequence[str] | None = None) -> int:
    """Run the greet program and return the process exit code.

    - Parse `argv` with `build_parser()` (None means `sys.argv[1:]`).
    - If `times` is less than 1: write "error: --times must be >= 1" plus a
      newline to **stderr**, print nothing to stdout, and return 2.
    - Otherwise print each line from `greet_lines` to stdout and return 0.
    - Do NOT call `sys.exit` yourself.
    """
    raise NotImplementedError


def build_calc_parser() -> argparse.ArgumentParser:
    """Build a parser with sub-commands for a `calc` program.

    - `prog` is "calc".
    - Top-level option `--precision` (int, default 2); it goes BEFORE the sub-command.
    - Required sub-command stored in `args.command`: "add" or "mul".
    - Each sub-command takes one or more positional `numbers` (floats).

    >>> a = build_calc_parser().parse_args(["--precision", "3", "add", "1", "2.5"])
    >>> (a.command, a.numbers, a.precision)
    ('add', [1.0, 2.5], 3)
    """
    raise NotImplementedError


def run_calc(argv: Sequence[str]) -> str:
    """Parse `argv` with `build_calc_parser`, compute, and return the formatted result.

    "add" sums the numbers, "mul" multiplies them. The result is formatted with
    `precision` decimals (fixed-point), e.g. "3.50".

    >>> run_calc(["add", "1", "2.5"])
    '3.50'
    >>> run_calc(["--precision", "0", "mul", "2", "3"])
    '6'
    """
    raise NotImplementedError


def configure_logger(name: str, level: int, handler: logging.Handler) -> logging.Logger:
    """Return a logger named `name` set up to send records only to `handler`.

    - Set the logger's level to `level`.
    - Remove any handlers already attached to the logger (so calling this
      twice does not duplicate output).
    - Give `handler` a Formatter with the format
      "%(levelname)s:%(name)s:%(message)s" and attach it.
    - Set `propagate` to False so records do not also reach the root logger.
    """
    raise NotImplementedError


class ListHandler(logging.Handler):
    """A logging handler that stores records in memory (handy for tests).

    - `records`: list of the LogRecord objects received, in order.
    - `messages()`: list of `record.getMessage()` for each stored record.
    - `levels()`: list of `record.levelname` for each stored record.
    Implement `emit(self, record)`; remember to call `super().__init__()`.
    """

    def __init__(self, level: int = logging.NOTSET):
        raise NotImplementedError

    def emit(self, record: logging.LogRecord) -> None:
        raise NotImplementedError

    def messages(self) -> list[str]:
        raise NotImplementedError

    def levels(self) -> list[str]:
        raise NotImplementedError


def process_items(items: Sequence[object], logger: logging.Logger) -> int:
    """Sum the valid items, logging what happens to each one.

    For every item, in order:
    - not an `int` -> `logger.error("bad item: %r", item)`; skipped.
    - a negative int -> `logger.warning("negative item: %d", item)`; skipped.
    - otherwise -> `logger.debug("ok item: %d", item)`; added to the total.
    Return the total. Use %-style lazy arguments (NOT f-strings) so the
    record's `args` hold the item.

    >>> process_items([1, -2, "x", 3], logging.getLogger("demo"))
    4
    """
    raise NotImplementedError


def exit_code_for(exc: BaseException | None) -> int:
    """Map an exception (or None) to a conventional process exit code.

    - None -> 0
    - KeyboardInterrupt -> 130
    - ValueError -> 2
    - any other OSError (FileNotFoundError, PermissionError, ...) -> 74
    - anything else -> 1
    """
    raise NotImplementedError


def run_cli(func: Callable[[Sequence[str]], int | None], argv: Sequence[str]) -> int:
    """Run `func(argv)` the way a well-behaved CLI entry point should.

    - If `func` returns an int, return it; if it returns None, return 0.
    - `KeyboardInterrupt`: write "interrupted" + newline to stderr, return 130.
    - Any other `Exception`: write "error: <message>" + newline to stderr
      (message is `str(exc)`) and return `exit_code_for(exc)`.
    - `SystemExit` (e.g. from argparse) is NOT caught; let it propagate.
    """
    raise NotImplementedError
