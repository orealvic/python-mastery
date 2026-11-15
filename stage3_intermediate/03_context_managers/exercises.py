"""3.03 — Context Managers

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 3.03` from the course root to test your work.
"""
from __future__ import annotations

from contextlib import contextmanager


class Timer:
    """Context manager measuring wall-clock time with time.perf_counter().

    `elapsed` is None before use. After the with-block exits (normally OR
    via an exception) `elapsed` is a float >= 0. Exceptions are NOT suppressed.
    `__enter__` returns the Timer itself.

    >>> with Timer() as t:
    ...     pass
    >>> t.elapsed >= 0
    True
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


@contextmanager
def temp_env_var(name: str, value: str):
    """Temporarily set os.environ[name] = value inside the block.

    On exit (even on exception) restore the previous state exactly: if the
    variable existed before, restore its old value; if not, remove it.
    Yields nothing.

    >>> with temp_env_var("MODE", "test"):
    ...     os.environ["MODE"]
    'test'
    """
    raise NotImplementedError
    yield  # pragma: no cover  (makes this a generator function; leave it)


@contextmanager
def changed_directory(path):
    """Temporarily os.chdir(path) inside the block, yielding the new current
    directory as a pathlib.Path (os.getcwd()). Always restore the previous
    working directory on exit, even on exception.

    (The stdlib has contextlib.chdir; write your own for practice.)
    """
    raise NotImplementedError
    yield  # pragma: no cover


class Transaction:
    """Wrap a dict: on a clean exit keep all changes; if the block raises,
    roll the dict back to its state at entry (same dict object, mutated in
    place) and let the exception propagate.

    `__enter__` returns the dict. Rollback must restore the exact earlier
    contents: removed keys come back, added keys vanish, changed values revert.
    Shallow copy semantics are fine.

    >>> d = {"a": 1}
    >>> try:
    ...     with Transaction(d) as t:
    ...         t["a"] = 2; t["b"] = 3; raise ValueError
    ... except ValueError: pass
    >>> d
    {'a': 1}
    """

    def __init__(self, data: dict) -> None:
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError


@contextmanager
def suppress_and_record(*exception_types):
    """Like contextlib.suppress, but remembers what it swallowed.

    Yields a list (initially empty). If the block raises an instance of one of
    `exception_types`, append that exception instance to the list and suppress
    it. Other exceptions propagate normally. With no types given, nothing is
    suppressed.

    >>> with suppress_and_record(KeyError) as errors:
    ...     {}["x"]
    >>> len(errors)
    1
    """
    raise NotImplementedError
    yield  # pragma: no cover


@contextmanager
def capture_output():
    """Capture everything printed to stdout inside the block.

    Yields an io.StringIO; after (or during) the block, `.getvalue()` has the
    text. stdout is restored afterwards. Use contextlib.redirect_stdout.

    >>> with capture_output() as out:
    ...     print("hi")
    >>> out.getvalue()
    'hi\\n'
    """
    raise NotImplementedError
    yield  # pragma: no cover


@contextmanager
def open_all(paths, mode: str = "r"):
    """Open every path in `paths` and yield a list of the open file objects
    (same order). On exit, close ALL files -- even if the block raised, and
    even if opening one of the later files fails (in which case the already
    opened files must be closed and the error propagated).

    Hint: contextlib.ExitStack and stack.enter_context().
    """
    raise NotImplementedError
    yield  # pragma: no cover


class Indenter:
    """A reusable, nestable context manager that tracks indentation depth and
    produces indented lines.

        ind = Indenter(" " * 2)      # indent unit (default 4 spaces)
        ind.line("root")             # 'root'
        with ind:
            ind.line("child")        # '  child'
            with ind:
                ind.line("leaf")     # '    leaf'
        ind.line("back")             # 'back'

    `line(text)` returns the string (it does not print). `depth` is an int
    attribute (0 initially). __enter__ increments depth and returns self;
    __exit__ decrements it (never suppresses exceptions).
    """

    def __init__(self, unit: str = "    ") -> None:
        raise NotImplementedError

    def line(self, text: str) -> str:
        raise NotImplementedError

    def __enter__(self):
        raise NotImplementedError

    def __exit__(self, exc_type, exc, tb):
        raise NotImplementedError
