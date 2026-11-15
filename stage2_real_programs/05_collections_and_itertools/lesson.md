# 2.05 — Collections & itertools

## Learning goals
- Pick the right container from `collections` for counting, grouping, queues and records
- Compose lazy pipelines with `itertools`
- Use `functools.reduce` (and know when not to)

The standard library already solved most of the "boring" data problems. Knowing it well is the
difference between 5 lines and 30.

## 1. `Counter` — counting things

```python
from collections import Counter

c = Counter("mississippi")          # Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
c["s"]                              # 4
c["zzz"]                            # 0  (missing keys count as 0, no KeyError)
c.most_common(2)                    # [('i', 4), ('s', 4)]  (ties: first seen first)
c.update("miss")                    # adds counts
Counter("abc") + Counter("cd")      # arithmetic on counts
sum(c.values()); c.total()          # total number of items
```

## 2. `defaultdict` — grouping without `if key in d`

```python
from collections import defaultdict

groups = defaultdict(list)          # missing key -> new empty list
for word in ["tea", "eat", "bat"]:
    groups[tuple(sorted(word))].append(word)

totals = defaultdict(int)           # missing key -> 0
for ch in "hello":
    totals[ch] += 1
```

Reading a missing key *creates* it; use `key in d` (or `.get`) when you only want to look.
Convert with `dict(d)` or `list(d.values())` at the end.

## 3. `deque` — fast at both ends

`list.pop(0)` is O(n); a `deque` pops/pushes on either side in O(1).

```python
from collections import deque

q = deque([1, 2, 3])
q.append(4); q.appendleft(0)        # deque([0, 1, 2, 3, 4])
q.popleft()                         # 0
q.rotate(1)                         # rotate right by 1
last3 = deque(maxlen=3)             # bounded: old items fall off automatically
for i in range(10): last3.append(i) # deque([7, 8, 9])
```

Use it for queues (BFS), sliding windows and "last N" buffers. Indexing in the middle is O(n).

## 4. `namedtuple` (and friends) — lightweight records

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
p.x, p[1]                           # 3, 4
x, y = p                            # still a tuple: unpackable, hashable, immutable
p._replace(x=10)                    # Point(x=10, y=4) (new object)
p._asdict()                         # {'x': 3, 'y': 4}
```

Alternatives: `typing.NamedTuple` (class syntax with type hints) and `@dataclass`
(mutable, more features). Use a namedtuple for small immutable records.

## 5. `OrderedDict` — still useful

Plain dicts keep insertion order. `OrderedDict` adds order-aware operations, notably
`move_to_end(key)` and `popitem(last=False)`, which make an LRU cache trivial:

```python
from collections import OrderedDict
d = OrderedDict(a=1, b=2, c=3)
d.move_to_end("a")                  # order: b, c, a
d.popitem(last=False)               # removes ('b', 2) -- the oldest
```

(`OrderedDict ==` also compares order, unlike `dict ==`.) Also see `ChainMap` for layered config.

## 6. `itertools` — lazy building blocks

Everything here returns **iterators**: wrap in `list()` to see results, and remember they are single-use.

| Function | What it does | Example |
|---|---|---|
| `chain(a, b)` / `chain.from_iterable(xs)` | concatenate iterables | `list(chain([1], [2, 3]))` -> `[1, 2, 3]` |
| `islice(it, stop)` / `islice(it, start, stop, step)` | slice any iterator | `list(islice(count(), 3))` -> `[0, 1, 2]` |
| `count(start=0, step=1)` | infinite counter | |
| `cycle(xs)` / `repeat(x, n)` | repeat forever / n times | |
| `accumulate(xs, func=add)` | running totals | `[1, 3, 6]` from `[1, 2, 3]` |
| `groupby(xs, key=None)` | group **consecutive** equal keys | see below |
| `product(a, b)` | cartesian product (nested loops) | `product("ab", [1, 2])` |
| `permutations(xs, r)` | ordered arrangements | |
| `combinations(xs, r)` | unordered selections, no repeats | `combinations("abc", 2)` -> `ab ac bc` |
| `pairwise(xs)` | overlapping neighbours (3.10+) | `[(1,2),(2,3)]` |
| `batched(xs, n)` | chunks of n (3.12+) | `[(1,2),(3,4),(5,)]` |
| `zip_longest(a, b, fillvalue=)` | zip padding the shorter | |
| `takewhile` / `dropwhile` | cut by a predicate | |

### `groupby` needs sorted input

```python
from itertools import groupby

words = ["apple", "avocado", "banana", "blueberry", "cherry"]
for letter, group in groupby(words, key=lambda w: w[0]):
    print(letter, list(group))          # a [...], b [...], c [...]
```

`groupby` only merges **adjacent** items. To group everything, sort by the same key first.
Each `group` is a lazy view: consume it (e.g. `list(group)`) before moving on.

### Pipelines

```python
from itertools import islice, count

evens_squared = (n * n for n in count() if n % 2 == 0)
first5 = list(islice(evens_squared, 5))      # [0, 4, 16, 36, 64]
```

## 7. `functools.reduce`

`reduce(f, items, initial)` folds a sequence into one value by repeatedly applying `f`:

```python
from functools import reduce
reduce(lambda acc, x: acc * x, [2, 3, 4], 1)    # 24
```

Always pass the initial value (it makes empty input safe). If a built-in exists
(`sum`, `math.prod`, `max`, `"".join`, `any`, `all`), use it instead; reserve `reduce` for custom
folds such as merging a list of dicts with `|`.

Related: `functools.lru_cache` / `functools.cache` memoise pure functions.

## Choosing a container

| Need | Use |
|---|---|
| Count occurrences | `Counter` |
| Group items by key | `defaultdict(list)` |
| Queue / sliding window / last-N | `deque` |
| Small immutable record | `namedtuple` / `NamedTuple` |
| Order-sensitive operations (LRU) | `OrderedDict` |
| Unique items, fast membership | `set` |

## Common mistakes

| Mistake | Fix |
|---|---|
| `groupby` on unsorted data | `sorted(xs, key=k)` first, with the same key |
| Iterating an itertools object twice | It is exhausted; recreate it or `list()` it |
| `defaultdict` lookup that accidentally creates keys | Use `in` / `.get()` to peek |
| `list.pop(0)` in a loop | Use `deque.popleft()` |
| `reduce` without initial value on a possibly-empty list | Provide the initial value |
| Consuming a `groupby` group after advancing | Materialise with `list(group)` first |
| Expecting `Counter.most_common()` ties in alphabetical order | Ties keep first-seen order |

## Practice

Ten tasks cover each tool. For every one, first ask "which standard-library tool does
this?" — most solutions are one or two lines. Finally build an `LRUCache` from an `OrderedDict`.

```
python check.py 2.05
```
