# 4.06 — Performance & Profiling

## Learning goals
- Measure before optimising: `timeit`, `time.perf_counter`, and why one run proves nothing
- Find hot spots with `cProfile` + `pstats`, and memory hogs with `tracemalloc`
- Know the cost of common operations (membership, string building, attribute lookups, comprehensions)
- Reason about algorithmic complexity and fix accidental O(n^2) code
- Use `functools.lru_cache` / `cache`, `__slots__`, generators, `bisect` and `heapq`
- Know when to leave pure Python (NumPy, C extensions, PyPy)

## 1. Measure first

"Premature optimisation is the root of all evil": guessing where time goes is usually wrong.

```python
import time
t0 = time.perf_counter()          # monotonic, highest-resolution clock
result = sum(range(1_000_000))
print(time.perf_counter() - t0)   # seconds, as a float
```

One run is noisy (caches, other processes, GC). Use `timeit`, which repeats and disables GC while timing:

```python
import timeit
timeit.timeit("sum(range(1000))", number=10_000)            # total seconds for 10_000 runs
times = timeit.repeat("sum(range(1000))", repeat=5, number=1000)
min(times) / 1000        # per-call estimate: take the MIN, not the mean
```
The minimum is the least-disturbed run; higher values are noise from the machine, not from your code.
In IPython/Jupyter: `%timeit expr`. For tests, **inject the clock** (`clock=time.perf_counter`) so a fake clock
makes timing code deterministic. Never assert "A is 3x faster than B" in a test; it will flake.

## 2. `cProfile` and `pstats`: where does the time go?

```python
import cProfile, pstats
with cProfile.Profile() as pr:
    main()
stats = pstats.Stats(pr).sort_stats("cumulative")   # or "tottime", "calls"
stats.print_stats(10)                               # top 10 rows
```
From the shell: `python -m cProfile -s cumulative script.py`.

- `ncalls`: number of calls. `tottime`: time inside the function itself (excluding callees).
- `cumtime`: including callees. Sort by `cumulative` to find the slow *path*, by `tottime` to find the slow *line of work*.
- `stats.print_callers("name")` shows who calls a hot function; `stats.fcn_list` holds the sorted keys
  `(filename, lineno, funcname)`.
- Profiling slows code down and distorts tiny functions; trust relative ordering, not absolute numbers.
  Sampling profilers (`py-spy`, Python 3.15's `profiling.sampling`) have less overhead.

## 3. `tracemalloc`: where does the memory go?

```python
import tracemalloc
tracemalloc.start()
data = [str(i) for i in range(100_000)]
current, peak = tracemalloc.get_traced_memory()     # bytes
snap = tracemalloc.take_snapshot()
for stat in snap.statistics("lineno")[:3]:
    print(stat)                                     # file:line, size, count
tracemalloc.stop()
```
`peak` is the high-water mark, which is what decides whether you run out of RAM. Compare two snapshots with
`snap2.compare_to(snap1, "lineno")` to hunt leaks. Tracing costs time and memory; use it in debugging only.

## 4. The cost of common operations

```python
x in some_list      # O(n): scans
x in some_set       # O(1) average: hash lookup
d[k]                # O(1)
lst.insert(0, v)    # O(n): shifts everything; use collections.deque for queues
lst.pop(0)          # O(n); deque.popleft() is O(1)
```
- **String building**: `s += piece` in a loop *can* be quadratic (CPython sometimes optimises it, PyPy does not).
  Collect pieces and `"".join(pieces)`.
- **Comprehensions** are usually a bit faster than the equivalent `for` + `append` (no repeated method lookup).
  Built-ins implemented in C (`sum`, `min`, `any`, `sorted`, `str.join`) beat hand-written loops.
- **Attribute and global lookups** cost a dict lookup each time (3.11+ specialises many of them, so gains are smaller
  than they once were). In a hot loop, bind to a local:

```python
def f(items):
    append = out.append          # local name: fast
    for x in items:
        append(x * 2)
```
- Function calls are comparatively expensive in Python; inlining a tiny function inside the hottest loop can help.
  Measure first: readability usually matters more than 10%.

## 5. Algorithmic complexity beats micro-tuning

Big-O describes how cost grows with input size `n`. Doubling `n` makes O(n) twice as slow, O(n^2) four times.

```python
def common(a, b):                         # O(len(a) * len(b))
    return [x for x in a if x in b]       # `x in b` scans the list each time

def common(a, b):                         # O(len(a) + len(b))
    bs = set(b)
    return [x for x in a if x in bs]
```
Typical wins: lists -> sets/dicts for lookup, sort once instead of searching repeatedly, `Counter` instead of nested
counting loops, precomputing (prefix sums), and avoiding work inside loops that does not depend on the loop.
Deterministic way to check complexity in a test: **count operations** (comparisons, calls), not seconds.

## 6. Caching: `functools.lru_cache` and `cache`

```python
from functools import lru_cache, cache

@lru_cache(maxsize=256)       # keeps the 256 most recently used results
def fib(n): return n if n < 2 else fib(n - 1) + fib(n - 2)

fib(80)
fib.cache_info()    # CacheInfo(hits=78, misses=81, maxsize=256, currsize=81)
fib.cache_clear()

@cache                        # unbounded, same as lru_cache(maxsize=None)
```
- Arguments must be hashable; the function must be pure (same inputs, same output).
- Caches hold references: on methods, `self` is part of the key and stays alive (a classic leak, see 4.03).
- Bound the size unless the key space is known to be small.

## 7. Memory: `__slots__` and generators

```python
class P:
    __slots__ = ("x", "y")        # no per-instance __dict__
    def __init__(self, x, y): self.x, self.y = x, y
```
Millions of small objects shrink substantially (no dict per instance), attribute access gets slightly faster, and typos
like `p.z = 1` raise `AttributeError`. Costs: no arbitrary attributes, and `"__weakref__"` must be listed to allow
weak references. `dataclass(slots=True)` does this for you.

Generators produce values lazily, keeping memory flat:

```python
sum([i * i for i in range(10_000_000)])   # builds a 10M-element list first (hundreds of MB)
sum(i * i for i in range(10_000_000))     # constant memory
```
Also: iterate a file line by line instead of `.read()`; `array.array` / `bytes` / `memoryview` for compact data.

## 8. `bisect` and `heapq`

```python
import bisect, heapq
scores = [10, 20, 30, 40]                 # must be SORTED
bisect.bisect_left(scores, 25)            # 2: insertion point, O(log n)
bisect.insort(scores, 25)                 # insert keeping order (the insert itself is O(n))
breaks, grades = [60, 70, 80, 90], "FDCBA"
grades[bisect.bisect(breaks, 85)]         # 'B'

heapq.nlargest(3, data)                   # O(n log k), better than sorted(data)[-3:] for small k
heapq.nsmallest(3, data, key=len)
heap = []; heapq.heappush(heap, 5); heapq.heappop(heap)    # priority queue, smallest first
```
`sorted()` costs O(n log n) and needs all the data in memory; a heap of size `k` handles streams of any length.

## 9. When Python itself is the limit

- **NumPy / pandas**: vectorised operations run in compiled loops. Replace Python loops over numbers with array ops.
- **C extensions / Cython / Rust (PyO3) / `ctypes` / `cffi`**: move the hot inner loop to compiled code.
- **PyPy**: a JIT that often speeds up long-running pure-Python loops several times, with some C-extension limits.
- **`multiprocessing` / free-threaded Python 3.13t+/3.14t**: for CPU-bound parallelism (see 4.04).
- CPython 3.13+ has an experimental JIT; 3.11+ has the specialising adaptive interpreter. Upgrading Python is free speed.
- `asyncio` helps I/O-bound work, never CPU-bound work (see 4.05).

## Common mistakes
- Optimising without profiling, or profiling with a toy input that doesn't resemble production.
- Timing one run; averaging instead of taking the minimum with `timeit.repeat`.
- Timing with `time.time()` (not monotonic) instead of `perf_counter`.
- `x in list` inside a loop, `list.pop(0)`, and string `+=` in loops.
- `lru_cache` on a method with a growing key space (unbounded memory) or on impure functions.
- Leaving `tracemalloc` or `cProfile` on in production.
- Micro-optimising (local-variable tricks) while an O(n^2) algorithm remains.
- Asserting speed ratios in unit tests; count operations or use an injected clock instead.

## Further reading
- `timeit`, `cProfile`, `pstats`, `tracemalloc`, `functools`, `bisect`, `heapq` module docs
- Python wiki: *TimeComplexity*, the docs' *Python Speed* and *Performance Tips* pages
- Brendan Gregg, *Flame Graphs*; `py-spy`, `scalene`, `snakeviz` (third-party tools)
- *High Performance Python*, Gorelick & Ozsvald

## Practice
Open `exercises.py`, implement each item, then run:

```bash
python check.py 4.06
```
