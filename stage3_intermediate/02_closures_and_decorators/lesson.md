# 3.02 — Closures & Decorators

## Learning goals
- Treat functions as values: pass them, return them, store them
- Explain closures and use `nonlocal`
- Write decorators, with and without arguments, function-based and class-based
- Preserve metadata with `functools.wraps`
- Stack decorators and predict their order of application

## 1. Functions are first-class objects

```python
def shout(s): return s.upper() + "!"

f = shout                       # no parentheses: the function object itself
f("hi")                         # 'HI!'
handlers = {"shout": shout, "len": len}
handlers["len"]("abc")          # 3
sorted(["b", "A", "c"], key=str.lower)   # functions as arguments
```

A function that takes or returns a function is a **higher-order function**
(`map`, `filter`, `sorted(key=...)`, `functools.reduce`...).

## 2. Closures

A function defined inside another can *remember* variables from the enclosing scope, even after
the outer function has returned:

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor      # `factor` is a free variable captured from outside
    return multiply

double = make_multiplier(2)
double(21)                     # 42
double.__closure__[0].cell_contents   # 2  (peek at the captured cell)
```

Each call to `make_multiplier` creates a fresh scope, so `double` and `triple` don't interfere.

### `nonlocal`

Assigning to a name makes it *local* by default. To rebind an enclosing variable use `nonlocal`:

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count         # without this: UnboundLocalError
        count += 1
        return count
    return increment

c = make_counter()
c(), c(), c()                  # (1, 2, 3)
```

(Mutating a captured list/dict needs no `nonlocal` — only *rebinding* does.)

### Late binding gotcha

Closures capture *variables*, not values:

```python
funcs = [lambda: i for i in range(3)]
[f() for f in funcs]           # [2, 2, 2]  — all see the final i
funcs = [lambda i=i: i for i in range(3)]   # bind now via a default
[f() for f in funcs]           # [0, 1, 2]
```

## 3. Your first decorator

A decorator is a callable that takes a function and returns a replacement:

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}{args}")
        result = func(*args, **kwargs)
        print(f"-> {result!r}")
        return result
    return wrapper

@log_calls
def add(a, b):
    return a + b

# exactly equivalent to:  add = log_calls(add)
add(2, 3)
```

Always accept `*args, **kwargs` and **return the result** so the wrapper is transparent.

## 4. `functools.wraps`

Without it, the wrapper hides the original's identity:

```python
add.__name__    # 'wrapper'   — bad for debugging, help(), introspection, pickling
```

Fix it:

```python
import functools

def log_calls(func):
    @functools.wraps(func)          # copies __name__, __doc__, __module__, __wrapped__...
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

`wraps` also sets `wrapper.__wrapped__ = func`, which `inspect.signature` follows, and lets
you bypass a decorator in tests (`add.__wrapped__(1, 2)`).

## 5. Decorators with arguments

`@retry(3)` means "call `retry(3)`, and apply *the result* as the decorator" — so you need
**three** nested levels:

```python
def repeat(times):                       # 1. the factory: takes the arguments
    def decorator(func):                 # 2. the decorator: takes the function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):    # 3. the wrapper: runs on each call
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def hello(): print("hi")
```

## 6. Decorators that keep state

State can live in a closure (`nonlocal`), in a mutable default, or as an attribute on the wrapper:

```python
def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper
```

Memoization is the classic example (and `functools.cache` / `lru_cache` are the stdlib versions):

```python
def memoize(func):
    cache = {}
    @functools.wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper
```

## 7. Class-based decorators

Any object with `__call__` can be a decorator. A class is handy when state is substantial:

```python
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)   # class-based version of @wraps
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

@CountCalls
def f(): ...
f(); f()
f.calls    # 2
```

Caveat: instances are not functions, so they don't bind as methods unless you also implement
`__get__`. Prefer function decorators for decorating methods.

## 8. Stacking decorators

```python
@a
@b
def f(): ...
# same as: f = a(b(f))
```

Decoration happens bottom-up (`b` first), but at call time the outermost (`a`'s wrapper) runs first.

## 9. Useful stdlib decorators

| Decorator | Purpose |
|---|---|
| `functools.wraps` | preserve metadata in your wrappers |
| `functools.cache`, `lru_cache(maxsize=...)` | memoization |
| `functools.singledispatch` | overload by first-argument type |
| `functools.cached_property` | compute-once attribute |
| `functools.partial` | pre-fill arguments (not a decorator, but related) |
| `@staticmethod`, `@classmethod`, `@property` | method kinds |
| `contextlib.contextmanager` | see 3.03 |

## 10. Registering decorators

A decorator need not wrap anything — it can just record the function and return it unchanged.
This is the basis of plugin systems, routing (`@app.route("/")`), and CLI frameworks:

```python
COMMANDS = {}

def command(name):
    def register(func):
        COMMANDS[name] = func
        return func          # return the ORIGINAL function
    return register

@command("hello")
def hello(): ...
```

## Common mistakes
- **Forgetting `return result`** in the wrapper (every call returns `None`).
- **Forgetting `@functools.wraps`**, then wondering why every function is named `wrapper`.
- **`@retry` vs `@retry()`**: with an argument-taking decorator you must write the parentheses.
- **Forgetting `nonlocal`** when rebinding a captured variable.
- **Late-binding closures in loops** (see section 2).
- **Unhashable arguments** in a naive memoize (`dict`/`list` args can't be dict keys).
- **Applying order mistakes**: `@login_required` should usually be *outside* (above) `@cache`.

## Practice
Open `exercises.py`, implement each function/decorator, then run:

```bash
python check.py 3.02
```
