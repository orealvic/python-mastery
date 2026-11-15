"""1.05 — Files & Errors

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 1.05` from the course root to test your work.

Functions taking `path` accept either a str or a pathlib.Path.
Always read and write text with encoding="utf-8".
"""


def safe_int(text: str, default: int | None = None) -> int | None:
    """Convert `text` to an int, returning `default` if it is not a valid
    integer string. Surrounding whitespace is allowed.

    >>> safe_int("42")
    42
    >>> safe_int("4x2", default=-1)
    -1
    >>> safe_int("abc") is None
    True
    """
    raise NotImplementedError


def parse_age(text: str) -> int:
    """Parse `text` as an age and return it as an int.

    Raise ValueError if the text is not an integer, or if the age is
    outside 0..150 (inclusive).

    >>> parse_age("30")
    30
    """
    raise NotImplementedError


def write_lines(path, lines: list[str]) -> int:
    """Write each string in `lines` to the file at `path`, one per line (each
    followed by '\\n'), replacing any existing content. Return the number of
    lines written. An empty list creates an empty file.

    >>> # write_lines("out.txt", ["a", "b"]) -> 2, file contains 'a\\nb\\n'
    """
    raise NotImplementedError


def read_lines(path) -> list[str]:
    """Return the lines of the file at `path` without their trailing newline
    characters. Blank lines are kept. An empty file gives []. Let
    FileNotFoundError propagate if the file does not exist.

    >>> # file contains 'a\\n\\nb\\n' -> ['a', '', 'b']
    """
    raise NotImplementedError


def append_log(path, message: str) -> None:
    """Append `message` plus a newline to the file at `path`, creating the file
    if it does not exist. Existing content must be preserved.

    >>> # append_log("log.txt", "started"); append_log("log.txt", "stopped")
    >>> # file contains 'started\\nstopped\\n'
    """
    raise NotImplementedError


def count_words_in_file(path) -> int:
    """Return the number of whitespace-separated words in the file at `path`.
    If the file does not exist, return 0 (use EAFP: try/except, don't check first).
    """
    raise NotImplementedError


def save_json(path, data) -> None:
    """Write `data` as JSON to `path`, pretty-printed with indent=2,
    replacing any existing content. Non-serializable data raises TypeError.
    """
    raise NotImplementedError


def load_json(path, default=None):
    """Load and return JSON from `path`.

    - If the file does not exist, return `default`.
    - If the file exists but holds invalid JSON, let the error propagate
      (json.JSONDecodeError is a ValueError).
    """
    raise NotImplementedError


def read_config(path) -> dict[str, str]:
    """Parse a simple config file into a dict.

    Each non-blank line is 'key=value'. Rules:
    - Lines that are blank (or only whitespace) are ignored.
    - Lines whose first non-space character is '#' are comments; ignore them.
    - Keys and values are stripped of surrounding whitespace.
    - Split on the FIRST '=' only, so values may contain '='.
    - A non-blank, non-comment line without '=' raises ValueError.
    - Later duplicates of a key override earlier ones.

    >>> # 'host = localhost\\n# note\\nurl=a=b\\n' -> {'host': 'localhost', 'url': 'a=b'}
    """
    raise NotImplementedError


def sum_ints_in_file(path) -> tuple[int, int]:
    """Read a file with one value per line. Return (total, bad) where `total`
    is the sum of the lines that are valid integers and `bad` is how many
    non-blank lines were NOT valid integers. Blank lines are ignored entirely.

    >>> # file '1\\n2\\nx\\n\\n4\\n' -> (7, 1)
    """
    raise NotImplementedError


def divide_with_log(a, b, log: list[str]):
    """Divide a by b using try/except/else/finally, recording what happened by
    appending to the list `log`:

    - success: append 'ok' and return a / b
    - ZeroDivisionError: append 'zero' and return None
    - always (even if some other exception such as TypeError is raised and
      propagates): append 'done' LAST

    So a success logs ['ok', 'done'] and a zero division logs ['zero', 'done'].

    >>> log = []
    >>> divide_with_log(6, 3, log), log
    (2.0, ['ok', 'done'])
    """
    raise NotImplementedError
