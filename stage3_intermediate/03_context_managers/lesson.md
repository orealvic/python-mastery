# 3.03 — Context Managers

## Learning goals
- Use `with` to guarantee cleanup
- Write context managers as classes (`__enter__` / `__exit__`) and as generators (`@contextmanager`)
- Understand how `__exit__` can suppress or observe exceptions
- Use `contextlib` tools: `suppress`, `ExitStack`, `redirect_stdout`, `closing`, `nullcontext`

## 1. The problem `with` solves

```python
f = open("data.txt")
data = f.read()      # if this raises, f is never closed
f.close()
```

`try/finally` fixes it, but `with` is shorter and impossible to forget:

```python
with open("data.txt") as f:
    data = f.read()
# f is closed here, even if read() raised
```

Typical uses: files, locks (`with lock:`), database transactions, temporary state changes
(cwd, env vars, decimal precision), timers, mocks, network connections.

## 2. The protocol

```python
with EXPR as NAME:
    BODY
```

behaves roughly like:

```python
mgr = EXPR
NAME = mgr.__enter__()
try:
    BODY
except BaseException as exc:
    if not mgr.__exit__(type(exc), exc, exc.__traceback__):
        raise                   # exit returned falsy: re-raise
else:
    mgr.__exit__(None, None, None)
```

- `__enter__` runs first; its return value is bound to `NAME`.
- `__exit__(exc_type, exc, tb)` **always** runs. If the body succeeded all three are `None`.
- If `__exit__` returns a **truthy** value, the exception is *suppressed*. Otherwise it propagates.

## 3. A class-based context manager

```python
import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self                      # what `as t` receives

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self.start
        return False                     # do not suppress exceptions

with Timer() as t:
    sum(range(1_000_000))
print(t.elapsed)
```

Return `False`/`None` from `__exit__` unless you *deliberately* want to swallow the error.
Never raise a new exception from `__exit__` unless the cleanup itself failed.

### Suppressing

```python
class Ignore:
    def __init__(self, *types): self.types = types
    def __exit__(self, exc_type, exc, tb):
        return exc_type is not None and issubclass(exc_type, self.types)
    def __enter__(self): return self
```

## 4. Generator-based: `@contextlib.contextmanager`

Far less boilerplate. Everything before `yield` is `__enter__`; the yielded value is the `as` target;
everything after is `__exit__`:

```python
from contextlib import contextmanager
import os

@contextmanager
def temp_env(name, value):
    old = os.environ.get(name)
    os.environ[name] = value
    try:
        yield                       # body of the with-block runs here
    finally:                        # ALWAYS use try/finally around the yield
        if old is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = old
```

If the body raises, the exception is re-raised **at the `yield`**. If you don't catch it, it
propagates; if you catch it and don't re-raise, it is suppressed. Without `try/finally`, cleanup
is skipped on error — the most common bug with `@contextmanager`.

`@contextmanager` objects can also be used as decorators (`@temp_env("A", "1")`) since 3.2.

## 5. `contextlib` toolbox

| Tool | Purpose |
|---|---|
| `suppress(*excs)` | `with suppress(FileNotFoundError): os.remove(p)` |
| `redirect_stdout(f)` / `redirect_stderr(f)` | capture printed output into a `StringIO` |
| `closing(obj)` | call `obj.close()` on exit |
| `nullcontext(value)` | a do-nothing `with` target (optional context managers) |
| `ExitStack()` | manage a *dynamic* number of context managers / callbacks |
| `chdir(path)` | (3.11+) temporarily change directory — stdlib version of an exercise here |
| `aclosing`, `AsyncExitStack` | async versions |

```python
import io
from contextlib import redirect_stdout, suppress

buf = io.StringIO()
with redirect_stdout(buf):
    print("hidden")
buf.getvalue()           # 'hidden\n'

with suppress(KeyError):
    {}["missing"]        # silently ignored
```

## 6. `ExitStack`: many managers, unknown count

```python
from contextlib import ExitStack

with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]   # any number of files
    stack.callback(print, "cleanup done")                   # arbitrary callbacks
    ...
# all files closed in reverse order, callback invoked; even if one open() failed midway
```

`stack.pop_all()` transfers ownership so nothing closes at the end of the block — useful in
constructors that must release resources only on failure.

## 7. Multiple managers in one `with`

```python
with open("in.txt") as src, open("out.txt", "w") as dst:
    dst.write(src.read())

with (
    open("a") as a,
    open("b") as b,        # parenthesized form: 3.10+
):
    ...
```

They enter left-to-right and exit right-to-left.

## 8. Patterns worth knowing

**Transaction / rollback** — snapshot state on enter, restore on exception:

```python
@contextmanager
def transaction(data):
    snapshot = dict(data)
    try:
        yield data
    except BaseException:
        data.clear(); data.update(snapshot)
        raise
```

**Reentrancy:** a single-use manager (like a generator-based one) can't be entered twice;
class-based ones can if you design them so. `threading.Lock` is not reentrant; `RLock` is.

**Exceptions inside cleanup:** if both the body and `__exit__` raise, the later exception
replaces the earlier (the earlier is kept as `__context__`).

## Common mistakes
- **No `try/finally` around `yield`** in `@contextmanager` — cleanup is skipped on errors.
- **Returning `True` from `__exit__` by accident** (e.g. `return self.close()`) — silently swallows errors.
- **Yielding twice** in a `@contextmanager` function: `RuntimeError`.
- **Using the `as` target after the block** when it was cleaned up (closed file, closed connection).
- **Not returning `self`** from `__enter__` and then getting `None` from `as`.
- **Catching `Exception` at the `yield`** and forgetting to re-raise — hides bugs.

## Practice
Open `exercises.py`, implement each, then run:

```bash
python check.py 3.03
```
