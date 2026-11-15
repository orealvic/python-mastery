# 1.03 — Data Structures: lists, tuples, dicts, sets

## Learning goals
- Use the four core built-in containers and know when to pick each
- Slice sequences and understand mutability and aliasing
- Use the essential methods of lists, dicts, and sets
- Build and navigate nested structures
- Write simple comprehensions

## 1. Overview: which container?

| Type | Literal | Ordered | Mutable | Duplicates | Use it for |
|---|---|---|---|---|---|
| `list` | `[1, 2]` | yes | yes | yes | a sequence you grow/change |
| `tuple` | `(1, 2)` | yes | no | yes | fixed-size records, dict keys, multiple returns |
| `dict` | `{"a": 1}` | yes (insertion order) | yes | keys unique | lookup by key |
| `set` | `{1, 2}` | no | yes | no | membership tests, uniqueness, set math |

Note: `{}` is an empty **dict**; an empty set is `set()`. A one-item tuple needs a comma: `(1,)`.

## 2. Lists

```python
xs = [10, 20, 30]
xs.append(40)          # [10, 20, 30, 40]
xs.extend([50, 60])    # add many
xs.insert(0, 5)        # insert at index
xs.pop()               # remove & return last (xs.pop(0) removes first - slow for big lists)
xs.remove(20)          # remove first occurrence of a value (ValueError if absent)
xs.index(30)           # position of a value
xs.sort()              # in place, returns None!
sorted(xs, reverse=True)  # new list
len(xs), min(xs), max(xs), sum(xs)
30 in xs               # membership: O(n) for lists
```

### Slicing

`seq[start:stop:step]` — `start` inclusive, `stop` exclusive, all optional, negatives count from the end.

```python
s = [0, 1, 2, 3, 4, 5]
s[1:4]     # [1, 2, 3]
s[:2]      # [0, 1]
s[-2:]     # [4, 5]
s[::2]     # [0, 2, 4]
s[::-1]    # [5, 4, 3, 2, 1, 0]   reversed copy
s[:]       # shallow copy
```

Slicing never raises `IndexError` for out-of-range bounds; indexing (`s[99]`) does.
Slices work the same on strings and tuples.

## 3. Mutability and aliasing

```python
a = [1, 2, 3]
b = a            # NOT a copy: two names, one list
b.append(4)
print(a)         # [1, 2, 3, 4]

c = a.copy()     # or list(a) or a[:]  -> independent (shallow) copy
```

A *shallow* copy copies the outer container but shares inner objects:

```python
grid = [[0, 0], [0, 0]]
shallow = grid.copy()
shallow[0][0] = 9
print(grid[0][0])   # 9 - inner list is shared!
```

Use `copy.deepcopy` when you need a fully independent nested copy.

Classic trap: `[[0] * 3] * 3` creates three references to the **same** row. Use
`[[0] * 3 for _ in range(3)]`.

Strings and tuples are immutable: you cannot assign `t[0] = 1`; you create new objects.

## 4. Tuples and unpacking

```python
point = (3, 4)
x, y = point
first, *rest = [1, 2, 3, 4]    # first=1, rest=[2, 3, 4]
a, b = b, a                    # swap without a temp variable
for name, score in [("ann", 9), ("bob", 7)]:
    ...
```

## 5. Dictionaries

```python
d = {"apple": 3, "pear": 5}
d["kiwi"] = 7              # add / update
d["apple"]                 # 3   (KeyError if missing)
d.get("fig")               # None
d.get("fig", 0)            # 0   default
"pear" in d                # True (checks keys)
del d["pear"]
d.pop("kiwi", None)        # remove with default
d.setdefault("fig", 0)     # insert default if missing, return value
d.update({"apple": 10})    # merge in another dict
for k in d: ...            # iterate keys
for k, v in d.items(): ... # keys and values
list(d.keys()), list(d.values())
merged = {**d1, **d2}      # or d1 | d2 (later wins)
```

Keys must be **hashable** (immutable): strings, numbers, tuples of hashables. Lists are not.

Counting pattern:

```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
```

Grouping pattern:

```python
groups = {}
for w in words:
    groups.setdefault(w[0], []).append(w)
```

(`collections.Counter` and `defaultdict` do these even more neatly; you'll meet them in Stage 2.)

## 6. Sets

```python
s = {1, 2, 3}
s.add(4); s.discard(10)         # discard doesn't raise if missing
a, b = {1, 2, 3}, {2, 3, 4}
a | b      # union         {1, 2, 3, 4}
a & b      # intersection  {2, 3}
a - b      # difference    {1}
a ^ b      # symmetric difference {1, 4}
a <= b     # subset test
```

Membership in a set or dict is O(1) on average, vs O(n) for a list — convert to a set for
repeated lookups. Sets are unordered, so wrap in `sorted(...)` when you need a stable order.

Deduplicating while **preserving order** needs a loop with a `seen` set (or `dict.fromkeys(items)`),
because `set(items)` loses ordering.

## 7. Nested structures

```python
people = [
    {"name": "Ann", "langs": ["python", "c"]},
    {"name": "Bob", "langs": ["go"]},
]
people[0]["langs"][1]          # 'c'
all_langs = [lang for p in people for lang in p["langs"]]   # flatten
matrix = [[1, 2, 3], [4, 5, 6]]
matrix[1][2]                   # 6
```

## 8. Comprehensions (a first look)

```python
squares = [n * n for n in range(5)]            # [0, 1, 4, 9, 16]
evens   = [n for n in range(10) if n % 2 == 0]
lengths = {w: len(w) for w in ["a", "bb"]}     # dict comprehension
unique  = {c for c in "hello"}                 # set comprehension
```

Keep them readable; if it needs more than one `for` and one `if`, use a loop.

## Common mistakes
- `xs = xs.sort()` sets `xs` to `None` — `sort()` returns `None`.
- Assuming `b = a` copies a list.
- Mutating a list while iterating over it.
- Mutable default values and `[[0]*3]*3` aliasing.
- `d[key]` on a missing key (use `.get` or `in` when absence is normal).
- Writing `{}` and expecting an empty set.
- Using a list as a dict key (unhashable) — use a tuple.

## Practice
Open `exercises.py`, implement each function, then run:

```bash
python check.py 1.03
```
