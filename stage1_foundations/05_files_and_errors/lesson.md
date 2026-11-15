# 1.05 — Files & Errors

## Learning goals
- Read and write text files safely with `with open(...)`
- Use `pathlib.Path` for file paths
- Store and load structured data with the `json` module
- Handle errors with `try` / `except` / `else` / `finally`
- Raise your own exceptions and choose EAFP vs LBYL appropriately

## 1. Reading and writing text files

Always use a `with` block: it closes the file for you, even if an error occurs.

```python
with open("notes.txt", "w", encoding="utf-8") as f:   # "w" truncates/creates
    f.write("first line\n")                           # write() does NOT add newlines
    f.writelines(["second\n", "third\n"])

with open("notes.txt", encoding="utf-8") as f:        # default mode is "r"
    text = f.read()          # whole file as one string
```

| Mode | Meaning |
|---|---|
| `"r"` | read (default); error if file is missing |
| `"w"` | write; **erases** existing content |
| `"a"` | append to the end; creates if missing |
| `"x"` | create; error if the file already exists |
| add `"b"` | binary mode (`"rb"`, `"wb"`), bytes instead of str |

Ways to read:

```python
with open("notes.txt", encoding="utf-8") as f:
    for line in f:                 # best for big files: one line at a time
        print(line.rstrip("\n"))

with open("notes.txt", encoding="utf-8") as f:
    lines = f.read().splitlines()  # list of lines without newline characters
```

Always pass `encoding="utf-8"` for text so behavior is the same on every OS.

### `pathlib`

```python
from pathlib import Path

p = Path("data") / "notes.txt"      # / joins path parts
p.exists(), p.is_file(), p.suffix, p.name, p.parent
p.parent.mkdir(parents=True, exist_ok=True)
p.write_text("hello\n", encoding="utf-8")
p.read_text(encoding="utf-8")
open(p)                             # open() accepts Path objects too
```

## 2. JSON

JSON is the standard text format for structured data.

| Python | JSON |
|---|---|
| `dict` | object |
| `list`, `tuple` | array |
| `str` | string |
| `int`, `float` | number |
| `True`/`False`/`None` | `true`/`false`/`null` |

```python
import json

data = {"name": "Ada", "langs": ["python"], "active": True}

text = json.dumps(data, indent=2)     # object -> str
back = json.loads(text)               # str -> object

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)      # object -> file
with open("data.json", encoding="utf-8") as f:
    loaded = json.load(f)             # file -> object
```

Gotchas: dict keys become strings (`{1: "a"}` round-trips as `{"1": "a"}`), tuples come back as lists,
and things like `set` or `datetime` are not serializable (`TypeError`). Invalid JSON raises
`json.JSONDecodeError`, which is a subclass of `ValueError`.

## 3. Exceptions

An error at runtime raises an exception, which unwinds the call stack until something catches it.

```python
try:
    n = int(text)
except ValueError:
    n = 0
```

Full form:

```python
try:
    f = open(path, encoding="utf-8")
except FileNotFoundError:
    print("no such file")
except (PermissionError, IsADirectoryError) as e:    # several types; bind the exception
    print("cannot open:", e)
else:
    # runs only if the try block raised nothing
    with f:
        data = f.read()
finally:
    # ALWAYS runs: cleanup, logging, even after return/raise
    print("done")
```

Common built-in exceptions:

| Exception | Typical cause |
|---|---|
| `ValueError` | right type, bad value (`int("abc")`) |
| `TypeError` | wrong type (`"a" + 1`) |
| `KeyError` | missing dict key |
| `IndexError` | list index out of range |
| `FileNotFoundError` | file doesn't exist (subclass of `OSError`) |
| `ZeroDivisionError` | `x / 0` |
| `AttributeError` | object lacks that attribute |

Hierarchy matters: `except OSError` also catches `FileNotFoundError`. Put specific handlers first.

### Catch narrowly

```python
try:
    ...
except Exception:      # too broad: hides bugs
    pass               # swallowing errors silently is worse
```

Catch only what you can actually handle, and keep the `try` body small.

### Raising

```python
def set_age(age):
    if not 0 <= age <= 150:
        raise ValueError(f"age out of range: {age}")
    ...
```

Re-raise with a bare `raise` inside `except`. Chain a new error with `raise NewError(...) from err`.
Define your own types by subclassing: `class ConfigError(Exception): pass`.

## 4. EAFP vs LBYL

- **LBYL** — "Look Before You Leap": check first.
  ```python
  if os.path.exists(path):
      data = open(path).read()      # but the file could vanish between the check and the open!
  ```
- **EAFP** — "Easier to Ask Forgiveness than Permission": just try it.
  ```python
  try:
      data = open(path).read()
  except FileNotFoundError:
      data = ""
  ```

Python style favors EAFP: it is race-free and often shorter. LBYL is still fine for cheap,
clear validation (`if not items:`), especially when failure is common rather than exceptional.

## Common mistakes
- Forgetting `"\n"` when using `write()`.
- Opening with `"w"` when you meant `"a"` and wiping the file.
- Not using `with`, leaving files unflushed or open.
- Bare `except:` or `except Exception: pass` hiding real bugs.
- Putting a lot of code in `try` so you can't tell which line failed.
- Expecting JSON to preserve tuples, int keys, or sets.
- Reading a huge file with `.read()` when line iteration would do.

## Practice
Open `exercises.py`, implement each function, then run:

```bash
python check.py 1.05
```
