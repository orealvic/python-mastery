# 2.02 — Modules, Packages & Tooling

## Learning goals
- Import code correctly and understand what `import` actually does
- Structure a project as modules and packages, and use `if __name__ == "__main__"`
- Lay out a real project (src layout, `pyproject.toml`) and manage environments
- Use git, a linter/formatter, and the debugger as daily tools

## 1. Modules and imports

Any `.py` file is a **module**. Importing it runs it once and caches the result in `sys.modules`.

```python
import math                      # use as math.sqrt(2)
from math import sqrt, pi        # use as sqrt(2)
import numpy as np               # alias
from collections import (        # multi-line form
    Counter,
    defaultdict,
)
```

| Style | Pro | Con |
|---|---|---|
| `import x` | always clear where a name comes from | longer |
| `from x import y` | short | hides origin, can collide |
| `from x import *` | — | **avoid**: pollutes the namespace |

Convention (PEP 8): imports at the top, in three groups separated by blank lines:
standard library, third party, your own code.

Python searches `sys.path` (script directory, `PYTHONPATH`, installed packages) in order.
A file named `random.py` or `json.py` in your project **shadows** the standard library module!

## 2. Packages

A **package** is a directory of modules. It traditionally contains an `__init__.py`:

```
mypkg/
    __init__.py       # runs on `import mypkg`; can re-export names
    core.py
    utils/
        __init__.py
        io.py
```

```python
import mypkg.utils.io
from mypkg.utils import io
from mypkg import core
```

**Relative imports** work only inside packages. In `mypkg/utils/io.py`:

```python
from . import helpers          # mypkg.utils.helpers
from .helpers import clean     # same package
from .. import core            # mypkg.core  (one level up)
from ..core import run
```

One dot = "this package", two = "the parent". Prefer absolute imports unless the package is
likely to be renamed. Exercise `resolve_relative` makes you compute this by hand.

## 3. `if __name__ == "__main__"`

Every module has a `__name__`. It is `"__main__"` only when the file is run directly
(`python tool.py` or `python -m pkg.tool`) and the module's own name when imported.

```python
def main() -> int:
    print("working...")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

This keeps import side-effect free: tests can `import tool` without launching it.
`python -m pkg.tool` runs a module *inside its package* (so relative imports work);
for a package, put the entry point in `pkg/__main__.py` and run `python -m pkg`.

## 4. Project layout

The recommended **src layout**:

```
myproject/
    pyproject.toml
    README.md
    src/
        mypkg/
            __init__.py
            cli.py
    tests/
        test_cli.py
    .gitignore
```

Why `src/`? Your tests then import the *installed* package, not whatever happens to sit in the
current directory, so packaging mistakes show up early.

`pyproject.toml` is the single config file for modern projects:

```toml
[project]
name = "mypkg"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["requests>=2.31"]

[project.scripts]
mypkg = "mypkg.cli:main"      # creates a `mypkg` command

[tool.ruff]
line-length = 100

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Install your project in editable mode while developing: `pip install -e .`

## 5. Virtual environments and installing packages

A **virtual environment** is an isolated folder of installed packages, one per project.

```bash
python -m venv .venv              # create
source .venv/bin/activate         # activate (Windows: .venv\Scripts\activate)
python -m pip install requests    # install
python -m pip freeze > requirements.txt
python -m pip install -r requirements.txt
deactivate
```

`uv` is a much faster all-in-one alternative:

```bash
uv init myproject
uv add requests          # edits pyproject.toml and installs
uv run python main.py    # runs inside the project environment
```

Requirement lines look like `requests>=2.31`, `flask==3.0.0`, `numpy~=1.26` (compatible release).
Never install into your system Python; never commit `.venv/`.

## 6. git in five minutes

```bash
git init
git status
git add -A && git commit -m "Add CLI skeleton"
git switch -c feature/csv-export      # new branch
git log --oneline --graph
git diff                              # unstaged changes
```

Commit small, with messages that say *why*. A `.gitignore` for Python contains at least
`.venv/`, `__pycache__/`, `*.pyc`, `.env`, `dist/`.

## 7. Formatting and linting with ruff

```bash
ruff check .          # find problems (unused imports, undefined names, ...)
ruff check --fix .    # auto-fix the safe ones
ruff format .         # consistent formatting, like black
```

Configure it under `[tool.ruff]` in `pyproject.toml`. Run it before every commit.
Type hints plus a checker (`mypy` or `pyright`) catch another class of bugs.

## 8. Debugging

The built-in `print` works, but the debugger is better:

```python
def total(prices):
    result = 0
    for p in prices:
        breakpoint()      # drops into pdb right here
        result += p
    return result
```

| pdb command | Meaning |
|---|---|
| `n` | run the next line |
| `s` | step into a call |
| `c` | continue until next breakpoint |
| `p expr` / `pp expr` | print / pretty-print an expression |
| `l` | list source around here |
| `w` | show the call stack |
| `q` | quit |

Run `python -m pdb script.py` to start in the debugger, or `python -m pdb -c continue script.py`
to land in a **post-mortem** after an uncaught exception. Set `PYTHONBREAKPOINT=0` to disable all
`breakpoint()` calls. Read tracebacks from the **bottom** up: the last line is the error, the line
above it is where it happened.

## Common mistakes

| Mistake | Fix |
|---|---|
| Naming your file `test.py`, `random.py`, `json.py` | Choose names that do not shadow the stdlib |
| Circular imports (`a` imports `b` imports `a`) | Move shared code to a third module, or import inside the function |
| Code at module top level that does work | Put it in `main()` behind the `__main__` guard |
| `ModuleNotFoundError` for your own code | Install the project (`pip install -e .`) instead of fiddling with `sys.path` |
| Installing packages globally | Always activate a venv first; check with `which python` |
| Committing `.venv/` or secrets | Use `.gitignore`; keep secrets in environment variables |
| Leaving `breakpoint()` in committed code | Search for it before commit (ruff rule `T100`) |

## Practice

The exercises are small utilities of the kind real tooling uses: parse a requirements line,
a mini-TOML config, convert file paths to import paths, resolve relative imports, scan source
code for imports with `ast`.

Then, in a scratch folder, build a tiny src-layout project, make a venv, install it with
`pip install -e .`, and run it with `python -m`. Run `ruff` on it if you have it.

```
python check.py 2.02
```
