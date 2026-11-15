"""Reference solutions for 2.07. Try the exercises yourself first!"""
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
    parser = argparse.ArgumentParser(prog="greet", description="Greet someone.")
    parser.add_argument("name", help="who to greet")
    parser.add_argument("-s", "--shout", action="store_true", help="UPPERCASE the greeting")
    parser.add_argument("-n", "--times", type=int, default=1, help="how many times")
    parser.add_argument("-g", "--greeting", default="Hello", help="greeting word")
    return parser


def greet_lines(args: argparse.Namespace) -> list[str]:
    """Return the greeting lines for parsed `args` (a Namespace from `build_parser`).

    Each line is "<greeting>, <name>!", uppercased when `args.shout`, and the
    list has `args.times` identical lines (0 times -> empty list).

    >>> greet_lines(build_parser().parse_args(["Ada", "-g", "Hi"]))
    ['Hi, Ada!']
    """
    line = f"{args.greeting}, {args.name}!"
    if args.shout:
        line = line.upper()
    return [line] * args.times


def main(argv: Sequence[str] | None = None) -> int:
    """Run the greet program and return the process exit code.

    - Parse `argv` with `build_parser()` (None means `sys.argv[1:]`).
    - If `times` is less than 1: write "error: --times must be >= 1" plus a
      newline to **stderr**, print nothing to stdout, and return 2.
    - Otherwise print each line from `greet_lines` to stdout and return 0.
    - Do NOT call `sys.exit` yourself.
    """
    args = build_parser().parse_args(argv)
    if args.times < 1:
        print("error: --times must be >= 1", file=sys.stderr)
        return 2
    for line in greet_lines(args):
        print(line)
    return 0


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
    parser = argparse.ArgumentParser(prog="calc")
    parser.add_argument("--precision", type=int, default=2)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("add", "mul"):
        p = sub.add_parser(name, help=f"{name} the numbers")
        p.add_argument("numbers", nargs="+", type=float)
    return parser


def run_calc(argv: Sequence[str]) -> str:
    """Parse `argv` with `build_calc_parser`, compute, and return the formatted result.

    "add" sums the numbers, "mul" multiplies them. The result is formatted with
    `precision` decimals (fixed-point), e.g. "3.50".

    >>> run_calc(["add", "1", "2.5"])
    '3.50'
    >>> run_calc(["--precision", "0", "mul", "2", "3"])
    '6'
    """
    args = build_calc_parser().parse_args(argv)
    if args.command == "add":
        result = sum(args.numbers)
    else:
        result = 1.0
        for n in args.numbers:
            result *= n
    return f"{result:.{args.precision}f}"


def configure_logger(name: str, level: int, handler: logging.Handler) -> logging.Logger:
    """Return a logger named `name` set up to send records only to `handler`.

    - Set the logger's level to `level`.
    - Remove any handlers already attached to the logger (so calling this
      twice does not duplicate output).
    - Give `handler` a Formatter with the format
      "%(levelname)s:%(name)s:%(message)s" and attach it.
    - Set `propagate` to False so records do not also reach the root logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers.clear()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


class ListHandler(logging.Handler):
    """A logging handler that stores records in memory (handy for tests).

    - `records`: list of the LogRecord objects received, in order.
    - `messages()`: list of `record.getMessage()` for each stored record.
    - `levels()`: list of `record.levelname` for each stored record.
    Implement `emit(self, record)`; remember to call `super().__init__()`.
    """

    def __init__(self, level: int = logging.NOTSET):
        super().__init__(level)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)

    def messages(self) -> list[str]:
        return [r.getMessage() for r in self.records]

    def levels(self) -> list[str]:
        return [r.levelname for r in self.records]


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
    total = 0
    for item in items:
        if not isinstance(item, int):
            logger.error("bad item: %r", item)
        elif item < 0:
            logger.warning("negative item: %d", item)
        else:
            logger.debug("ok item: %d", item)
            total += item
    return total


def exit_code_for(exc: BaseException | None) -> int:
    """Map an exception (or None) to a conventional process exit code.

    - None -> 0
    - KeyboardInterrupt -> 130
    - ValueError -> 2
    - any other OSError (FileNotFoundError, PermissionError, ...) -> 74
    - anything else -> 1
    """
    if exc is None:
        return 0
    if isinstance(exc, KeyboardInterrupt):
        return 130
    if isinstance(exc, ValueError):
        return 2
    if isinstance(exc, OSError):
        return 74
    return 1


def run_cli(func: Callable[[Sequence[str]], int | None], argv: Sequence[str]) -> int:
    """Run `func(argv)` the way a well-behaved CLI entry point should.

    - If `func` returns an int, return it; if it returns None, return 0.
    - `KeyboardInterrupt`: write "interrupted" + newline to stderr, return 130.
    - Any other `Exception`: write "error: <message>" + newline to stderr
      (message is `str(exc)`) and return `exit_code_for(exc)`.
    - `SystemExit` (e.g. from argparse) is NOT caught; let it propagate.
    """
    try:
        result = func(argv)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return exit_code_for(KeyboardInterrupt())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exit_code_for(exc)
    return 0 if result is None else result
