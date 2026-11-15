# 1.04 — Functions

## Learning goals
- Define functions with parameters, return values, and docstrings
- Use default, keyword, `*args`, `**kwargs`, and keyword-only arguments
- Avoid the mutable-default-argument pitfall
- Understand scope (LEGB), closures, `global`, and `nonlocal`
- Treat functions as values: pass them around, return them, use `lambda` and `key=`

## 1. Defining and calling

```python
def area(width, height):
    """Return the area of a rectangle."""
    return width * height

area(3, 4)                    # positional
area(height=4, width=3)       # keyword - order doesn't matter
```

- A function with no `return` (or a bare `return`) returns `None`.
- `return` ends the function immediately.
- The first string in the body is the **docstring**; `help(area)` shows it. Write one for every
  public function: what it does, what it returns, what it raises.

### Returning multiple values

You are really returning one tuple, which callers unpack:

```python
def min_max(xs):
    return min(xs), max(xs)

lo, hi = min_max([3, 1, 4])
```

## 2. Parameters in depth

### Defaults

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

greet("Ada")             # 'Hello, Ada!'
greet("Ada", "Hi")       # 'Hi, Ada!'
```

Parameters with defaults must come after those without.

### The mutable default pitfall

Defaults are evaluated **once**, when `def` runs - not on every call.

```python
def add(item, bucket=[]):      # BUG
    bucket.append(item)
    return bucket

add(1)   # [1]
add(2)   # [1, 2]  <- the same list is reused!
```

The fix is the `None` sentinel:

```python
def add(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

### `*args` and `**kwargs`

```python
def total(*numbers):          # numbers is a tuple
    return sum(numbers)

total(1, 2, 3)                # 6

def show(**options):          # options is a dict
    return options

show(color="red", size=3)     # {'color': 'red', 'size': 3}
```

The same stars *unpack* at the call site:

```python
nums = [1, 2, 3]
total(*nums)                  # same as total(1, 2, 3)
opts = {"color": "red"}
show(**opts)
```

### Keyword-only (and positional-only) parameters

Everything after a bare `*` must be passed by keyword. Great for flags that would be
unreadable positionally:

```python
def connect(host, *, timeout=10, retries=3):
    ...

connect("example.com", timeout=5)     # ok
connect("example.com", 5)             # TypeError
```

Everything before a `/` is positional-only: `def f(a, b, /, c): ...`.

Full order: `def f(pos, /, normal, *args, kw_only, **kwargs)`.

## 3. Scope: LEGB

Python looks up a name in this order: **L**ocal, **E**nclosing function, **G**lobal, **B**uilt-in.

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        print(x)       # finds 'enclosing' (E)
    inner()
```

Assigning to a name inside a function makes it local for the *whole* function. To rebind an
outer variable you must say so:

```python
count = 0
def bump():
    global count        # rebinds the module-level name
    count += 1

def make_counter():
    n = 0
    def tick():
        nonlocal n      # rebinds the enclosing function's variable
        n += 1
        return n
    return tick
```

Prefer returning values over `global`. `make_counter` is a **closure**: `tick` remembers `n`
after `make_counter` has returned.

## 4. Functions are values

Functions are objects: assign them, store them in lists/dicts, pass them as arguments, return them.

```python
def apply_twice(f, x):
    return f(f(x))

apply_twice(str.upper, "a")            # 'A'

ops = {"add": lambda a, b: a + b, "mul": lambda a, b: a * b}
ops["mul"](3, 4)                       # 12

def make_multiplier(k):
    return lambda x: x * k             # returns a new function

double = make_multiplier(2)
double(21)                             # 42
```

### `lambda`

A lambda is an anonymous single-expression function: `lambda args: expression`. Use it for short
throwaway functions, mostly as a `key=`. If you need to name it or it spans logic, use `def`.

### `sorted`, `min`, `max` with `key=`

```python
words = ["pear", "fig", "banana"]
sorted(words)                          # alphabetical
sorted(words, key=len)                 # ['fig', 'pear', 'banana']
sorted(words, key=lambda w: (len(w), w))   # tie-break alphabetically
sorted(words, reverse=True)
max(words, key=len)                    # 'banana'
```

`key` is called once per item and items are compared by the key. Python's sort is **stable**:
equal keys keep their original relative order.

## 5. Good function design
- Do one thing; name it with a verb (`parse_line`, not `line`).
- Prefer returning results over printing them (callers can then test and reuse).
- Don't mutate arguments unless the name/docstring says so.
- Add type hints for readability: `def area(w: float, h: float) -> float:`. They are not enforced
  at runtime; tools like mypy use them.

## Common mistakes
- Mutable default arguments (`def f(x=[])`).
- Forgetting `return` and getting `None` back.
- Calling `f` instead of `f()` - without parentheses you have the function object, not its result.
- Using `lst = lst.sort()`-style patterns on functions that return `None`.
- Modifying a global without `global`, which raises `UnboundLocalError`.
- Overusing `lambda` for complex logic.
- Late binding in closures: `[lambda: i for i in range(3)]` all see the final `i`; use
  `lambda i=i: i` or a factory function.

## Practice
Open `exercises.py`, implement each function, then run:

```bash
python check.py 1.04
```
