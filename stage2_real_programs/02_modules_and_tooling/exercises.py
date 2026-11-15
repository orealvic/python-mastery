"""2.02 — Modules, Packages & Tooling

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 2.02` from the course root to test your work.
"""
from __future__ import annotations

import ast
import re
from pathlib import PurePosixPath

_REQ_RE = re.compile(r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(==|>=|<=|~=|!=|>|<)?\s*(\S+)?$")


def parse_requirement(line: str) -> tuple[str, str, str] | None:
    """Parse one line of a requirements.txt file into (name, operator, version).

    Rules:
    - Anything after a `#` is a comment and is ignored.
    - Surrounding whitespace is ignored.
    - A blank (or comment-only) line returns None.
    - Supported operators: ==, >=, <=, ~=, !=, >, <
    - Whitespace around the operator is allowed.
    - A bare name has operator "" and version "".
    - The name is returned exactly as written (no case change).
    - A line that does not look like a requirement raises ValueError.

    >>> parse_requirement("requests>=2.31")
    ('requests', '>=', '2.31')
    >>> parse_requirement("  Flask == 3.0.0   # web framework")
    ('Flask', '==', '3.0.0')
    >>> parse_requirement("pytest")
    ('pytest', '', '')
    >>> parse_requirement("# just a comment") is None
    True
    """
    raise NotImplementedError


def normalize_requirements(lines: list[str]) -> list[str]:
    """Return the sorted, de-duplicated, normalised package names in `lines`.

    Normalisation: lowercase, and every run of `-`, `_` or `.` becomes a single `-`.
    Blank and comment-only lines are skipped. Use `parse_requirement`.

    >>> normalize_requirements(["Flask==3", "# hi", "requests", "typing_extensions", "flask"])
    ['flask', 'requests', 'typing-extensions']
    """
    raise NotImplementedError


def parse_config(text: str) -> dict[str, dict[str, object]]:
    """Parse a tiny TOML/INI-like config into {section: {key: value}}.

    Rules:
    - A line `[name]` starts section `name`.
    - A line `key = value` sets a key in the current section. Split on the FIRST `=`.
    - Keys and values are stripped of surrounding whitespace.
    - Keys that appear before any section header go in the section named "".
      (That section only exists if there is at least one such key.)
    - Blank lines and lines starting with `#` are ignored.
    - Values: `"text"` (double-quoted) -> str without the quotes;
      `true` / `false` -> bool; an optionally negative run of digits -> int;
      anything else -> the stripped raw string.
    - No inline comments, no multi-line values.
    - A later duplicate key overwrites the earlier one.

    >>> parse_config('name = "demo"\\n[tool]\\nline = 88\\nfast = true')
    {'': {'name': 'demo'}, 'tool': {'line': 88, 'fast': True}}
    """
    raise NotImplementedError


def _parse_value(value: str) -> object:
    raise NotImplementedError


def module_path_to_dotted(path: str, root: str = "src") -> str:
    """Convert a source file path into the dotted name used to import it.

    - Paths use forward slashes.
    - If the path starts with the directory `root`, that directory is removed first.
    - The `.py` suffix is dropped; a final `__init__` is dropped too
      (a package is imported by its directory name).
    - A path that does not end in `.py` raises ValueError.

    >>> module_path_to_dotted("src/mypkg/utils/io.py")
    'mypkg.utils.io'
    >>> module_path_to_dotted("src/mypkg/__init__.py")
    'mypkg'
    >>> module_path_to_dotted("tools/build.py")
    'tools.build'
    """
    raise NotImplementedError


def resolve_relative(current: str, name: str, is_package: bool = False) -> str:
    """Resolve a (possibly relative) import `name` seen inside module `current`.

    - A name that does not start with `.` is already absolute: return it unchanged.
    - `current` is the dotted name of the module doing the import. If
      `is_package` is True, `current` is a package (its `__init__.py`), and one
      dot refers to `current` itself; otherwise one dot refers to the package
      containing `current`.
    - Each extra leading dot goes one package further up.
    - Going above the top-level package (or using a relative import in a
      top-level module) raises ValueError.

    >>> resolve_relative("pkg.sub.mod", ".sibling")
    'pkg.sub.sibling'
    >>> resolve_relative("pkg.sub.mod", "..other.thing")
    'pkg.other.thing'
    >>> resolve_relative("pkg.sub", ".child", is_package=True)
    'pkg.sub.child'
    >>> resolve_relative("pkg.mod", ".")
    'pkg'
    """
    raise NotImplementedError


def build_pyproject(name: str, version: str, dependencies: list[str]) -> str:
    """Build the text of a minimal pyproject.toml `[project]` table.

    The output has exactly this shape (4-space indent, trailing comma on each
    dependency, final newline):

        [project]
        name = "demo"
        version = "0.1.0"
        dependencies = [
            "requests>=2",
            "rich",
        ]

    With no dependencies the last line is `dependencies = []`.

    >>> print(build_pyproject("demo", "0.1.0", []), end="")
    [project]
    name = "demo"
    version = "0.1.0"
    dependencies = []
    """
    raise NotImplementedError


def find_missing_imports(source: str, installed: set[str]) -> list[str]:
    """Return the sorted top-level modules imported by `source` that are not in `installed`.

    Use the `ast` module (do not use regexes). Rules:
    - `import a.b.c` and `from a.b import c` both contribute the top-level name `a`.
    - Relative imports (`from . import x`, `from .m import y`) are ignored.
    - Imports anywhere in the file count (including inside functions).
    - Each missing name appears once.

    >>> find_missing_imports("import os\\nimport requests.adapters\\nfrom rich import print", {"os"})
    ['requests', 'rich']
    """
    raise NotImplementedError


def entry_message(module_name: str) -> str:
    """Describe how a module is being used, given its `__name__`.

    Return "running as script" when `module_name == "__main__"`, otherwise
    "imported as <module_name>".

    >>> entry_message("__main__")
    'running as script'
    >>> entry_message("mypkg.tools")
    'imported as mypkg.tools'
    """
    raise NotImplementedError
