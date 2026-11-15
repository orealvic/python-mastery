"""2.06 — Text, Dates & Data Files

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 2.06` from the course root to test your work.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
_LOG_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2}:\d{2}) "
    r"\[(?P<level>[A-Z]+)\] (?P<message>.*)$"
)


def extract_emails(text: str) -> list[str]:
    """Return every email address found in `text`, in order of appearance.

    An address is: one or more of letters/digits/underscore/dot/plus/hyphen,
    an `@`, then a domain of two or more dot-separated labels (letters,
    digits, underscore, hyphen). A dot at the very end of a sentence is not
    part of the address.

    >>> extract_emails("Mail ann@example.com or bob.smith+x@mail.co.uk.")
    ['ann@example.com', 'bob.smith+x@mail.co.uk']
    """
    raise NotImplementedError


def parse_log_line(line: str) -> dict[str, str] | None:
    """Parse "YYYY-MM-DD HH:MM:SS [LEVEL] message" into a dict.

    The result has keys `date`, `time`, `level`, `message` (all strings; the
    message is everything after the single space following `]`). LEVEL is
    uppercase letters. A line that does not match returns None.
    Hint: named groups `(?P<name>...)` and `match.groupdict()`.

    >>> parse_log_line("2024-03-15 10:30:45 [ERROR] disk full")
    {'date': '2024-03-15', 'time': '10:30:45', 'level': 'ERROR', 'message': 'disk full'}
    >>> parse_log_line("garbage") is None
    True
    """
    raise NotImplementedError


def days_between(start: str, end: str) -> int:
    """Return the number of days from `start` to `end` (ISO `YYYY-MM-DD` strings).

    Negative if `end` is before `start`. Invalid dates raise ValueError.

    >>> days_between("2024-02-28", "2024-03-01")
    2
    """
    raise NotImplementedError


def add_business_days(start: date, n: int) -> date:
    """Return the date `n` business days (Mon-Fri) after `start`. `n >= 0`.

    Weekends never count. If `n` is 0 return `start` unchanged (even on a
    weekend). `n < 0` raises ValueError.

    >>> add_business_days(date(2024, 3, 15), 1)   # Friday -> Monday
    datetime.date(2024, 3, 18)
    """
    raise NotImplementedError


def to_utc_iso(local: str, tz_name: str) -> str:
    """Convert a local wall-clock time to a UTC ISO-8601 string.

    `local` is "YYYY-MM-DD HH:MM" (or with ":SS") in the IANA time zone
    `tz_name` (e.g. "America/New_York"). Return `datetime.isoformat()` of the
    equivalent UTC moment, i.e. ending in "+00:00". Daylight saving time must
    be respected. Hint: `zoneinfo.ZoneInfo`, `.replace(tzinfo=...)`, `.astimezone`.

    >>> to_utc_iso("2024-01-15 09:00", "America/New_York")
    '2024-01-15T14:00:00+00:00'
    """
    raise NotImplementedError


def list_py_files(root: Path) -> list[str]:
    """List all `.py` files under directory `root`, recursively.

    Return paths relative to `root`, as forward-slash strings, sorted
    alphabetically. Skip any file that has a path component starting with `.`
    (hidden dirs like `.venv`) or equal to `__pycache__`.
    Hint: `Path.rglob`, `Path.relative_to`, `Path.as_posix`.

    >>> # root/a.py, root/pkg/b.py, root/.venv/c.py  ->  ['a.py', 'pkg/b.py']
    """
    raise NotImplementedError


def save_json(path: Path, data: object) -> None:
    """Write `data` to `path` as pretty JSON.

    Format: 2-space indent, keys sorted, non-ASCII characters kept as-is
    (not escaped), UTF-8 encoding, and exactly one trailing newline.
    """
    raise NotImplementedError


def load_json_with_defaults(path: Path, defaults: dict) -> dict:
    """Load a JSON settings file and merge it over `defaults`.

    - If the file does not exist, return a copy of `defaults`.
    - Otherwise return `{**defaults, **loaded}` (shallow merge; file wins).
    - Invalid JSON propagates `json.JSONDecodeError` (a ValueError).
    - If the JSON top level is not an object, raise ValueError.
    - Never modify the `defaults` argument.
    """
    raise NotImplementedError


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> int:
    """Write dict rows to a CSV file with a header; return the number of rows written.

    - Columns are in the order of `fieldnames`; a key missing from a row
      becomes an empty cell; a key not in `fieldnames` raises ValueError.
    - Use "\\n" as the line terminator, UTF-8 encoding, and open the file with
      `newline=""` (as the csv docs require).
    - Cells containing commas/quotes are quoted by the csv module's defaults.
    Hint: `csv.DictWriter`.
    """
    raise NotImplementedError


def sales_by_region(path: Path) -> dict[str, float]:
    """Read a CSV with header `region,units,price` and total revenue per region.

    Revenue of a row is `int(units) * float(price)`. Return a dict mapping
    region -> sum of revenues rounded to 2 decimals. Hint: `csv.DictReader`.

    >>> # region,units,price / north,2,1.50 / north,1,2.00 / south,3,1.00
    >>> # -> {'north': 5.0, 'south': 3.0}
    """
    raise NotImplementedError
