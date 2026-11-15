# 3.01 — Iterators & Generators

## Learning goals
- Explain the difference between an *iterable* and an *iterator*
- Write your own iterator class with `__iter__` / `__next__`
- Write generator functions with `yield`, `yield from`, and generator expressions
- Build lazy, memory-efficient pipelines and infinite sequences
- Know when (and why) `send()` exists

## 1. What `for` really does

```python
for x in [1, 2, 3]:
    print(x)
```

is roughly:

```python
it = iter([1, 2, 3])          # calls [1, 2, 3].__iter__()
while True:
    try:
        x = next(it)          # calls it.__next__()
    except StopIteration:
        break
    print(x)
```

| Term | Has | Example |
|---|---|---|
| **Iterable** | `__iter__()` returning an iterator | `list`, `str`, `dict`, `range`, files |
| **Iterator** | `__next__()` *and* `__iter__()` returning `self` | `iter([1])`, generators, `open(...)` |

Key facts:
- Iterators are **single-use**: once exhausted they stay exhausted.
- Iterables (like lists) can hand out many independent iterators.
- `next(it)` raises `StopIteration` when done; `next(it, default)` returns a default instead.

```python
it = iter("ab")
next(it)         # 'a'
next(it)         # 'b'
next(it, None)   # None  (exhausted)
list(it)         # []    (still exhausted!)
```

## 2. Writing an iterator class

```python
class Countup:
    def __init__(self, stop):
        self.current = 0
        self.stop = stop

    def __iter__(self):
        return self                  # an iterator is its own iterator

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

list(Countup(3))   # [0, 1, 2]
```

If you want a *re-iterable* container, keep the state out of the object and return a **fresh** iterator
from `__iter__`:

```python
class Repeat:
    def __init__(self, value, times):
        self.value, self.times = value, times
    def __iter__(self):
        for _ in range(self.times):    # __iter__ may itself be a generator!
            yield self.value
```

## 3. Generator functions

Any function containing `yield` is a **generator function**. Calling it runs *nothing*; it returns a
generator object (an iterator). Code runs only as you ask for values, pausing at each `yield`.

```python
def countup(stop):
    n = 0
    while n < stop:
        yield n        # pause here, hand out n
        n += 1         # resume here on the next next()

g = countup(2)
next(g)   # 0
next(g)   # 1
next(g)   # raises StopIteration
```

A generator is the shortest way to write an iterator: Python builds `__iter__`, `__next__`, and
saves local variables between pauses for you. A bare `return` (or falling off the end) raises
`StopIteration`.

### Generator expressions

```python
squares = (n * n for n in range(10))     # lazy; uses O(1) memory
sum(n * n for n in range(1_000_000))     # no intermediate list
```

Use `[...]` when you need a list; use `(...)` when you only iterate once.

## 4. Laziness and infinite sequences

Because values are produced on demand, a generator can represent an *infinite* stream:

```python
def naturals():
    n = 0
    while True:
        yield n
        n += 1

from itertools import islice
list(islice(naturals(), 5))    # [0, 1, 2, 3, 4]
```

Never call `list()` on an infinite generator. Use `itertools.islice`, `takewhile`, or `break`.

## 5. Pipelines

Chain generators; each stage pulls one item at a time from the previous one:

```python
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip("\n")

def grep(lines, word):
    return (l for l in lines if word in l)

def first_n(it, n):
    return list(islice(it, n))

first_n(grep(read_lines("huge.log"), "ERROR"), 10)
```

This reads only as much of `huge.log` as needed to find 10 errors. Memory stays flat no matter how
large the file is.

## 6. `yield from`

Delegates to a sub-iterator, passing every value through:

```python
def flatten(nested):
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)     # recursion made easy
        else:
            yield item

list(flatten([1, [2, [3, 4]], 5]))       # [1, 2, 3, 4, 5]
```

`yield from` also forwards `send()`/`throw()` and captures the sub-generator's `return` value:

```python
def inner():
    yield 1
    return "done"

def outer():
    result = yield from inner()
    print(result)        # "done"
```

## 7. `send()`, `throw()`, `close()` (briefly)

`yield` is actually an *expression*. `send(value)` resumes the generator and makes the paused
`yield` evaluate to `value`:

```python
def running_average():
    total = count = 0
    average = None
    while True:
        x = yield average
        total += x
        count += 1
        average = total / count

avg = running_average()
next(avg)          # "prime" it: run to the first yield
avg.send(10)       # 10.0
avg.send(20)       # 15.0
avg.close()        # raises GeneratorExit inside at the yield
```

Coroutines like this have mostly been superseded by `async`/`await` (Stage 4), but the mechanism is
good to understand.

## 8. Handy tools

| Tool | What it does |
|---|---|
| `itertools.islice(it, n)` | first n items (slicing for iterators) |
| `itertools.chain(a, b)` | concatenate iterables lazily |
| `itertools.count()`, `cycle()`, `repeat()` | infinite sources |
| `itertools.takewhile / dropwhile` | stop/skip by predicate |
| `itertools.batched(it, n)` | chunks as tuples (3.12+) |
| `itertools.pairwise(it)` | overlapping pairs (3.10+) |
| `itertools.tee(it, n)` | n independent copies of an iterator |
| `zip`, `enumerate`, `map`, `filter`, `reversed` | built-in lazy helpers |
| `collections.deque(maxlen=n)` | great for sliding windows |

## Common mistakes
- **Reusing an exhausted iterator.** `g = (x for x in data); list(g); list(g)` — second is `[]`.
- **Calling `list()` on an infinite generator** — hangs and eats memory.
- **Forgetting that generator bodies don't run until iterated.** Errors (and side effects) inside
  appear late, at the first `next()`.
- **Raising `StopIteration` inside a generator** — since Python 3.7 this becomes `RuntimeError`.
  Just `return`.
- **Mutating a list while iterating over it.** Iterate over a copy or build a new list.
- **Returning a list from `__iter__`.** It must return an *iterator*: `return iter(self.items)`.

## Practice
Open `exercises.py`, implement each function/class, then run:

```bash
python check.py 3.01
```
