# Stage 3 Capstone — An Installable, Typed, Tested Package

Turn code you've written into a proper Python package: installable with `pip`, fully type-hinted
and checked by mypy, tested with pytest, linted with ruff, and documented. This is what the
difference between "a script" and "software" looks like.

It pulls together Stage 3: generators, decorators, context managers, type hints, dataclasses and
enums, testing, and pattern matching.

## Pick what to package

Choose **one**:

1. **Promote your Stage 2 project.** Refactor it into the structure below. This is the most
   realistic option, because real packaging work usually happens to existing code.
2. **`tinyschema` — a small validation library.** Describe the shape of a dict and validate data
   against it:
   ```python
   from tinyschema import Schema, Str, Int, ListOf, Optional

   User = Schema({"name": Str(min_len=1), "age": Int(ge=0), "tags": ListOf(Str()),
                  "email": Optional(Str())})
   User.validate({"name": "Ada", "age": 36, "tags": []})          # returns the cleaned dict
   User.validate({"name": "", "age": -1, "tags": [3]})            # raises ValidationError
   # ValidationError: 3 errors
   #   name: shorter than 1 character
   #   age: must be >= 0
   #   tags[0]: expected str, got int
   ```
3. **`logslice` — a log-file analysis tool.** It streams huge log files with generators, parses
   lines into dataclasses, filters with `match` on parsed records, and prints summaries. It must
   work on a multi-gigabyte file without loading it into memory.

## Required layout

```text
mypackage/
    pyproject.toml
    README.md
    LICENSE
    src/
        mypackage/
            __init__.py      # public API + __all__ + __version__
            py.typed         # empty marker: "this package ships type hints"
            core.py
            ...
            __main__.py      # if it has a CLI
    tests/
        conftest.py
        test_core.py
        ...
```

The `src/` layout forces your tests to run against the *installed* package rather than a stray
local import. Install it in editable mode while you develop:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

A minimal `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mypackage"
version = "0.1.0"
description = "One line about what it does"
readme = "README.md"
requires-python = ">=3.13"
dependencies = []

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "mypy", "ruff"]

[project.scripts]
mypackage = "mypackage.cli:main"    # only if you have a CLI

[tool.mypy]
strict = true

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]

[tool.pytest.ini_options]
addopts = "--strict-markers"
```

## Requirements

### Features (whichever option you choose)
- At least one **generator pipeline**: lazy processing, with `yield` and generator expressions.
- At least one **decorator** you wrote, using `functools.wraps`, that does something useful (timing,
  retry, caching, validation, registering plugins and so on).
- At least one **context manager**, written either as a class or with `@contextmanager`.
- **Dataclasses** for your data and **enums** for fixed sets of values. No magic strings.
- At least one **`match` statement** where it genuinely reads better than `if`/`elif`.
- **Custom exceptions** in a hierarchy (`class MyPackageError(Exception)`, with subclasses).

### Types
- `mypy --strict src/` passes with **zero** errors and no `# type: ignore` (or, at most, one that
  has a comment explaining why).
- Use `Protocol`, generics (`def first[T](xs: Iterable[T]) -> T | None`), `TypedDict`, or
  `Literal` where they fit, not just `str` and `int`.

### Tests
- `pytest` passes, and `pytest --cov=mypackage` shows **≥ 90 %** line coverage.
- Use fixtures (`conftest.py`), `@pytest.mark.parametrize`, `pytest.raises(..., match=...)`, and
  `tmp_path`.
- At least one test uses `monkeypatch` or `unittest.mock` to isolate something like the clock, the
  network or the environment.
- Tests document behavior. A reader should learn how to use the package from reading them.

### Quality
- `ruff check` and `ruff format --check` are clean.
- Every public function, class and module has a docstring.
- The README has an install section, a 10-line usage example that actually works, and a
  "Development" section explaining how to run the tests.

## Suggested milestones

1. **Skeleton.** Create the layout and `pyproject.toml`. Run `pip install -e ".[dev]"` and add one
   trivial test so `pytest` passes. Commit.
2. **Tooling.** Get `mypy --strict`, `ruff` and `pytest` all green on the skeleton. From now on, keep
   them green with every commit.
3. **Core.** Write the main functionality test-first: write a failing test, make it pass, then
   refactor.
4. **Public API.** Decide what users import. Re-export it from `__init__.py` and list it in
   `__all__`. Everything else counts as private.
5. **Errors.** Go through every failure path and check that users get your exception with a helpful
   message.
6. **CLI (optional).** Add `[project.scripts]` so `mypackage --help` works after installing.
7. **Build.** Run `pip install build && python -m build`. Then install the wheel from `dist/` into a
   *fresh* venv and use it. Something will probably be missing the first time.

## Stretch goals
- A GitHub Actions workflow that runs ruff, mypy and pytest on Python 3.13 and 3.14.
- A `pre-commit` config that runs ruff on each commit.
- Property-based tests with [Hypothesis](https://hypothesis.readthedocs.io/).
- Docs with MkDocs, plus `mkdocstrings` to generate an API reference from your docstrings.
- Publish to [TestPyPI](https://test.pypi.org/) and install the package from there.

## Self-review checklist

Packaging
- [ ] `pip install .` into a fresh venv works, and `import mypackage` succeeds.
- [ ] The built wheel contains `py.typed` and does not contain your tests.
- [ ] `mypackage.__version__` matches the version in `pyproject.toml`.

Quality gates (all green)
- [ ] `ruff check .` and `ruff format --check .`
- [ ] `mypy --strict src/`
- [ ] `pytest --cov=mypackage` at 90 % or more

Design
- [ ] The public API is small and listed in `__all__`.
- [ ] No function is longer than about 40 lines; the nesting depth is ≤ 3.
- [ ] Errors are specific exception types with useful messages, and nothing is silently swallowed.
- [ ] A stranger could use the package from the README alone.

When all of the boxes are ticked, you have completed Stage 3.
