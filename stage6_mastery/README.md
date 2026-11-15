# Stage 6 — Mastery

Mastery isn't a finish line. It's a set of habits. This stage is a series of open-ended **assignments**.
Do them in any order, and keep coming back to them.

---

## 6.1 Read great code

Reading high-quality code is the fastest way to absorb idioms you'd never find on your own.

**Method for each codebase:**
1. Clone it, install it in editable mode, and get the tests passing.
2. Pick **one** feature and trace it end to end with a debugger. Set a breakpoint at the public entry point and step through.
3. Write a one-page note: architecture, 3 idioms you learned, 1 thing you'd do differently, and why they probably didn't do it that way.

| Codebase | What to study |
|---|---|
| stdlib `collections/__init__.py`, `functools.py` | `namedtuple` code generation, `lru_cache`, `singledispatch` |
| stdlib `dataclasses.py` | generating methods with `exec`, `__set_name__`, field handling |
| [`httpx`](https://github.com/encode/httpx) | a sync and async API sharing one design, transport abstraction |
| [`rich`](https://github.com/Textualize/rich) | the renderable protocol, `__rich_console__`, measurement |
| [`click`](https://github.com/pallets/click) | decorators that build an object model, context passing |
| [`attrs`](https://github.com/python-attrs/attrs) / [`pydantic`](https://github.com/pydantic/pydantic) | class creation, validation design |
| [`FastAPI`](https://github.com/fastapi/fastapi) | dependency injection built on `inspect.signature` and type hints |

**Done when:** you've written notes on at least 4 codebases.

---

## 6.2 Contribute to open source

1. Pick a project **you already use**. That gives you context and motivation.
2. Read `CONTRIBUTING.md`, set up the dev environment and run the test suite.
3. Start small: a doc fix, a failing test that reproduces a bug, then a "good first issue".
4. Before writing code, comment on the issue with your plan. Keep PRs small and focused, and follow the project's style.
5. Respond to review with grace. Reviews are free mentorship.

**Done when:** you've had 3 merged PRs, and at least one changes behavior with a test (not only docs).

---

## 6.3 Design & architecture

- **Read:** *Architecture Patterns with Python* (free at cosmicpython.com): repository, unit of work, service layer, events.
- **Read:** *Fluent Python* again. On a second read you'll take in different things.
- **Study:** SOLID, adapted for Python. Prefer composition, protocols (structural typing) over deep hierarchies, functions over classes when there's no state, and "make illegal states unrepresentable" with types and enums.
- **Assignment:** refactor one of your earlier capstones using the ports-and-adapters pattern. Swap its storage (for example JSON to SQLite) without changing business logic, and prove that with tests.

**Done when:** the swap touches only the adapter layer and the tests didn't change.

---

## 6.4 Packaging & releasing

- **Learn:** `pyproject.toml` in depth, build backends (hatchling, uv_build), versioning (SemVer and dynamic versions), wheels and sdists, trusted publishing to PyPI, changelogs, documentation (MkDocs Material + mkdocstrings).
- **Assignment:** publish a genuinely useful small library to PyPI, with docs hosted online, CI, type hints (`py.typed`) and a test matrix across supported Python versions.

**Done when:** `pip install your-package` works for a stranger, and the docs explain how to use it.

---

## 6.5 Teach

Explaining something reveals the gaps in your own understanding.

- Write 4 blog posts, one on each of: a concept that confused you (descriptors? async?), a bug you hunted, a library you read, and your capstone.
- Answer 10 Python questions on Stack Overflow, Reddit's r/learnpython, or the Python Discord.
- Pair with or mentor someone at an earlier stage of this course.

---

## 6.6 Stay sharp

- Follow "What's New in Python 3.x" for each release, and try the new features.
- Read PEPs that affect you (for example PEP 703 on free threading, PEP 695 on type parameter syntax, PEP 750 on template strings).
- Solve Advent of Code each December, in idiomatic Python.
- Watch talks: PyCon, Raymond Hettinger's classics, David Beazley on generators and concurrency.

---

## Mastery self-assessment

You're there when you can do all of these **without looking anything up**:

- [ ] Explain attribute lookup order, including descriptors and `__getattr__`.
- [ ] Explain when to use threads, processes or asyncio, and why.
- [ ] Profile a slow program and fix the real bottleneck.
- [ ] Write a decorator, a context manager, a generator pipeline and a descriptor from scratch.
- [ ] Design a package API that others find pleasant to use.
- [ ] Review someone else's Python and give feedback that makes it clearly better.
- [ ] Read an unfamiliar large codebase and make a correct change within a day.
