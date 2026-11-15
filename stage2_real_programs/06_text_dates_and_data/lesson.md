# 2.06 — Text, Dates & Data Files

## Learning goals
- Match and extract text with regular expressions (`re`)
- Work with dates, times, durations and time zones (`datetime`, `zoneinfo`)
- Handle files and paths with `pathlib`
- Read and write JSON and CSV correctly

## 1. Regular expressions

Use **raw strings** (`r"..."`) so backslashes reach the regex engine untouched.

```python
import re

re.search(r"\d+", "order 66")           # first match anywhere -> Match object or None
re.match(r"\d+", "66 orders")           # must match at the START
re.fullmatch(r"\d{3}-\d{4}", "555-1234")# must match the WHOLE string
re.findall(r"\d+", "a1 b22 c333")       # ['1', '22', '333']
re.sub(r"\s+", " ", "a   b \n c")       # 'a b c'
re.split(r"[,;]\s*", "a, b;c")          # ['a', 'b', 'c']
```

| Pattern | Meaning |
|---|---|
| `.` | any character except newline |
| `\d` `\w` `\s` | digit, word char (letters, digits, `_`), whitespace (`\D \W \S` = opposite) |
| `[abc]` `[^abc]` `[a-z]` | character set / negated / range |
| `* + ?` | 0+, 1+, 0 or 1 (greedy; add `?` for lazy: `.*?`) |
| `{n}` `{n,m}` | exact / range repeat |
| `^` `$` | start / end of string (of line with `re.M`) |
| `\b` | word boundary |
| `(...)` `(?:...)` | capturing group / non-capturing |
| `a\|b` | alternation |

**Groups** pull out the parts you care about:

```python
LOG = re.compile(r"(?P<date>\d{4}-\d{2}-\d{2}) \[(?P<level>[A-Z]+)\] (?P<msg>.*)")
m = LOG.match("2024-03-15 [ERROR] disk full")
if m:                                   # always check for None!
    m.group("level")                    # 'ERROR'
    m.groupdict()                       # {'date': ..., 'level': ..., 'msg': ...}
```

Compile (`re.compile`) patterns used repeatedly. Flags: `re.I` ignore case, `re.M` multiline,
`re.X` verbose (allows comments/whitespace in the pattern). Regexes are for *text patterns*; don't
parse HTML or nested structures with them.

## 2. Dates and times

```python
from datetime import date, datetime, timedelta, timezone

d = date(2024, 3, 15)
d.weekday()                        # 0 = Monday ... 4 = Friday, 6 = Sunday
d + timedelta(days=30)             # date(2024, 4, 14)
date.fromisoformat("2024-03-15")   # parse ISO 8601
(date(2024, 3, 1) - date(2024, 2, 1)).days     # 29
datetime(2024, 3, 15, 9, 30).isoformat()       # '2024-03-15T09:30:00'
datetime.strptime("15/03/2024", "%d/%m/%Y")    # parse with a format
d.strftime("%A %d %B %Y")                      # 'Friday 15 March 2024'
```

Subtracting two dates/datetimes yields a `timedelta` (`.days`, `.total_seconds()`).
Months/years aren't fixed lengths, so `timedelta` has no months; use `calendar` or manual logic.

## 3. Time zones

A **naive** datetime has no zone; an **aware** one does. Never mix them (`TypeError`).

```python
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

ny = datetime(2024, 7, 15, 9, 0, tzinfo=ZoneInfo("America/New_York"))
ny.astimezone(timezone.utc)                 # 13:00 UTC (daylight time!)
datetime.now(timezone.utc)                  # current time, aware
```

Rules of thumb: store and compute in **UTC**; convert to local time only for display; always use
IANA names like `"Europe/Paris"`, never fixed offsets for places with DST. On Windows (or minimal
containers) install the data with `pip install tzdata`.

## 4. Files and paths with `pathlib`

```python
from pathlib import Path

p = Path("data") / "report.csv"        # `/` joins paths portably
p.name, p.stem, p.suffix, p.parent     # 'report.csv', 'report', '.csv', Path('data')
p.exists(), p.is_file(), p.is_dir()
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("hello\n", encoding="utf-8")
p.read_text(encoding="utf-8")
sorted(Path(".").glob("*.py"))         # this directory
sorted(Path(".").rglob("*.py"))        # recursive
p.relative_to("data"); p.as_posix(); p.with_suffix(".json")
```

Always pass `encoding="utf-8"` explicitly; use `with open(...)` for streaming large files line by line.

## 5. JSON

```python
import json

text = json.dumps({"b": 1, "a": [1, 2]}, indent=2, sort_keys=True)
data = json.loads(text)
Path("x.json").write_text(json.dumps(data), encoding="utf-8")
data = json.loads(Path("x.json").read_text(encoding="utf-8"))
```

JSON has only objects, arrays, strings, numbers, `true/false/null`. Python tuples become lists,
dict keys become strings, and `datetime`/`Path`/sets are **not** serialisable (convert them
first or pass `default=str`). Bad input raises `json.JSONDecodeError` (a `ValueError`).

## 6. CSV

Use the `csv` module — never `line.split(",")` (quoted fields can contain commas and newlines).

```python
import csv

with open("in.csv", newline="", encoding="utf-8") as f:     # newline="" is required
    for row in csv.DictReader(f):                            # each row is a dict of strings
        print(row["name"], int(row["age"]))

with open("out.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["name", "age"])
    w.writeheader()
    w.writerows([{"name": "Ann", "age": 30}])
```

Every cell read from CSV is a **string**: convert numbers and dates yourself. For
financial data prefer `decimal.Decimal` over `float`.

## Common mistakes

| Mistake | Fix |
|---|---|
| Regex without raw string: `"\d"` | `r"\d"` |
| Using the result of `re.match` without checking `None` | `if m:` first |
| Greedy `.*` swallowing too much | `.*?` or a tighter character class |
| `re.match` when you meant `re.search` | `match` anchors at the start |
| Naive `datetime.now()` in stored data | `datetime.now(timezone.utc)` |
| Adding hours across a DST change with naive math | Convert to UTC first |
| `strftime("%m")` vs `"%M"` | month vs minutes |
| Opening CSV without `newline=""` | Blank lines on Windows, broken quoted newlines |
| Forgetting CSV values are strings | `int(row["units"])` |
| `open(path)` without encoding | `encoding="utf-8"` |
| Building paths with string `+` | `Path(...) / "name"` |

## Practice

The exercises extract emails, parse log lines, do date arithmetic, convert time zones, walk a
directory tree, and round-trip JSON and CSV. File exercises receive a temporary directory
(`tmp_path`), so you can experiment without touching your own files.

```
python check.py 2.06
```
