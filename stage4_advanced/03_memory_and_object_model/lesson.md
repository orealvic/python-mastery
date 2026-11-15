# 4.03 — Memory & the Object Model

## Learning goals
- Separate identity (`is`, `id`) from equality (`==`) and know when each is right
- Explain references, reference counting, and the cyclic garbage collector
- Recognise and fix aliasing bugs from mutability
- Use `copy.copy` / `copy.deepcopy` and customise them with `__copy__` / `__deepcopy__`
- Use `weakref` (`ref`, `WeakValueDictionary`, `finalize`) to avoid leaks
- Measure object sizes and understand interning

## 1. Everything is an object; names are references

```python
a = [1, 2, 3]
b = a            # no copy: two names, ONE object
b.append(4)
print(a)         # [1, 2, 3, 4]
```

Each object has an **identity** (`id(x)`, its address in CPython, unique while it lives), a **type**,
and a **value**. `a is b` compares identities; `a == b` calls `a.__eq__(b)`.

```python
x = [1]; y = [1]
x == y, x is y        # (True, False)
```

Use `is` only for singletons: `None`, `True`/`False`, sentinels (`_MISSING = object()`).
Never `is` with numbers or strings: it "works" for small ints/interned strings by accident of the implementation.

## 2. Mutability and aliasing bugs

Immutable: `int float str bytes tuple frozenset bool None`. Mutable: `list dict set bytearray` and most user objects.
Hazards:

```python
grid = [[0] * 3] * 3          # three references to ONE row
grid[0][0] = 1                # every row changes!
grid = [[0] * 3 for _ in range(3)]   # fix: build each row separately

def add(item, bucket=[]):     # default evaluated ONCE at def time
    bucket.append(item); return bucket
def add(item, bucket=None):   # fix
    if bucket is None: bucket = []
    bucket.append(item); return bucket

defaults = {"tags": []}
cfg = dict(defaults)          # shallow copy: cfg["tags"] IS defaults["tags"]
```

Other classic sources: `list * n`, `dict.fromkeys(keys, [])`, returning an internal list from a getter,
mutating an argument you were passed, and `+=` on a list (in-place, unlike `+`).

A tuple is immutable but can *contain* mutables: `t = ([],); t[0].append(1)` is fine,
and `t[0] += [2]` raises **and** mutates (classic puzzle).

## 3. Reference counting

CPython frees an object the instant its reference count hits zero (deterministic; `__del__` runs then).

```python
import sys
a = object()
sys.getrefcount(a)     # 2: the name `a` + the temporary argument
b = a; sys.getrefcount(a)   # 3
del b
```
- References come from names, container slots, closures, frames, arguments...
- Since 3.12, some objects are *immortal* (small ints, `None`, interned strings): their count is meaningless.
- Free-threaded builds (3.13t/3.14t) use biased/deferred reference counting; same semantics, different internals.
- Other implementations (PyPy) do not refcount: never rely on `__del__` timing. Use context managers.

## 4. Cycles and the garbage collector

Refcounting cannot free cycles:

```python
a = []; a.append(a)       # refers to itself
del a                     # refcount stays 1 -> leaked until the cyclic GC runs
```
The `gc` module detects unreachable cycles among *container* objects. Python 3.12+ GC runs on allocation
thresholds (3.14 uses an incremental collector for the old generation).

```python
import gc
gc.collect()              # force a full collection, returns number of unreachable objects
gc.get_threshold(); gc.get_count(); gc.get_referrers(obj)
gc.disable()              # for short latency-critical sections / benchmarks only
```
Since 3.4, objects with `__del__` in cycles are collectable too, but avoid `__del__`.
Typical cycle makers: parent <-> child pointers, callbacks storing `self`, exceptions holding tracebacks that hold frames
(`except E as e` deletes `e` at block end to avoid this).

## 5. `copy` — shallow vs deep

```python
import copy
orig = {"tags": ["a"], "n": 1}
sh = copy.copy(orig)        # new dict, SAME inner list
dp = copy.deepcopy(orig)    # everything duplicated
sh["tags"].append("b")      # also changes orig
```
`deepcopy` keeps a **memo** (`id -> copy`) so shared references stay shared and cycles terminate:

```python
a = [1]; a.append(a)
b = copy.deepcopy(a)
b[1] is b          # True: the cycle was reproduced, not recursed forever
```
Customise per class:

```python
class Doc:
    def __copy__(self): ...                 # return a new shallow copy
    def __deepcopy__(self, memo):           # register new object in memo BEFORE copying children
        new = type(self).__new__(type(self)); memo[id(self)] = new
        new.pages = copy.deepcopy(self.pages, memo)
        return new
```
Shortcuts for common shallow copies: `list(x)`, `x[:]`, `x.copy()`, `dict(x)`.
Immutable atoms (ints, strs, functions, classes) are not copied by either.

## 6. `weakref` — references that don't keep objects alive

```python
import weakref
class Img: ...
img = Img()
r = weakref.ref(img)
r() is img          # True
del img
r()                 # None (collected)
```
- `WeakValueDictionary`: cache whose entries vanish once nobody else holds the value.
- `WeakKeyDictionary` / `WeakSet`: attach metadata to objects without owning them.
- `weakref.finalize(obj, func, *args)`: robust cleanup callback; runs when `obj` dies or at interpreter exit
  (`.detach()` cancels it). Prefer over `__del__`.
- Not every type supports weak references: `int`, `str`, `list`, `dict`, `tuple` do not (subclasses do);
  `__slots__` classes need `"__weakref__"` in the slots.
- A bound method `obj.method` creates a new object on each access; use `weakref.WeakMethod`.

```python
cache = weakref.WeakValueDictionary()
def load(key):
    obj = cache.get(key)
    if obj is None:
        obj = cache[key] = expensive(key)
    return obj
```
Pattern: never write `if key in cache: return cache[key]` (the entry can die between the two lines); use `.get`.

## 7. Interning and small-object caches

```python
a = "hello"; b = "hel" + "lo"      # compile-time constant folding -> usually same object
c = "".join(["hel", "lo"])          # runtime string: a different object, == but not `is`
import sys
sys.intern(c) is sys.intern("hello")   # True
```
- Identifier-like string literals are interned; `sys.intern` forces it (saves memory & makes dict lookups faster when many duplicates).
- Small ints -5..256 are cached singletons. Don't depend on it.

## 8. How big is an object?

```python
sys.getsizeof([])           # 56 (bytes, shallow, platform dependent)
sys.getsizeof([1, 2, 3])    # includes the pointer array only, NOT the ints
```
`getsizeof` is shallow: a real estimate walks containers and counts each `id` once (shared objects count once).
Other tools: `tracemalloc` (module 4.06), `__slots__` for many small objects, `array`/`numpy` for numeric data,
`memoryview` for zero-copy slices, generators instead of lists, `sys.getallocatedblocks()`,
`gc.get_objects()` for leak hunting, and `objgraph`/`pympler` (third-party).

## 9. Why this matters for leaks
Python "leaks" are almost always *unintended references*: module-level caches that grow, closures capturing big
objects, `lru_cache` holding arguments (including `self`), registries of callbacks, exceptions with
tracebacks stored in globals, and thread-local/context state. Fix by weak references, bounded caches,
and clearer ownership.

## Common mistakes
- Comparing with `is` for value equality (`if x is 1000`, `if s is "yes"`).
- Mutable default arguments; `[[0]*n]*m` grids; `dict.fromkeys(keys, [])`.
- Using shallow copy on nested data then mutating inner objects.
- Writing `__deepcopy__` that doesn't pass `memo` down (breaks shared refs and cycles).
- Relying on `__del__` for cleanup, or on refcount-driven timing in portable code.
- Checking `if k in weak_dict: weak_dict[k]` (race with GC): use `.get`.
- Trusting `sys.getsizeof` as the total memory of a structure.

## Further reading
- Data model, *Objects, values and types* (docs.python.org/3/reference/datamodel.html)
- `gc`, `copy`, `weakref`, `sys` module docs; *Design of CPython's Garbage Collector* (devguide)
- PEP 683 (immortal objects), PEP 703 (free-threading)
- Ned Batchelder, *Facts and myths about Python names and values*

## Practice
Open `exercises.py`, implement each item, then run:

```bash
python check.py 4.03
```
