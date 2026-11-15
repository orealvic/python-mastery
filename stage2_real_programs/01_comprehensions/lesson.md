# 2.01 — Comprehensions & Generator Expressions

## Learning goals
- Build lists, dicts and sets with comprehensions instead of manual loops
- Add filters and nested loops, and read them without getting lost
- Use generator expressions with `sum`, `any`, `all`, `max`, `min`
- Know when a plain `for` loop is the better tool

## 1. The idea

A comprehension is a loop that *builds a collection* in a single expression.

```python
# the loop version
squares = []
for n in range(5):
    squares.append(n * n)

# the comprehension version
squares = [n * n for n in range(5)]      # [0, 1, 4, 9, 16]
```

Read it left to right as: "give me `n * n` **for** each `n` **in** `range(5)`".
The shape is always `[ expression  for  name  in  iterable ]`.

## 2. Filtering with `if`

An `if` at the **end** keeps only items that pass:

```python
evens = [n for n in range(10) if n % 2 == 0]     # [0, 2, 4, 6, 8]
longish = [w for w in ["a", "abc", "hello"] if len(w) > 2]
```

## 3. Choosing between two values: the conditional expression

An `if/else` at the **front** is part of the *expression*, not a filter:

```python
labels = ["even" if n % 2 == 0 else "odd" for n in range(4)]
# ['even', 'odd', 'even', 'odd']
```

| Position | Syntax | Effect |
|---|---|---|
| after the `for` | `[x for x in xs if cond]` | **drops** items |
| before the `for` | `[a if cond else b for x in xs]` | **transforms** every item |

You can combine both: `[x.upper() if x else "?" for x in xs if x is not None]`.

## 4. Dict and set comprehensions

```python
lengths = {w: len(w) for w in ["a", "abc"]}      # {'a': 1, 'abc': 3}
letters = {w[0] for w in ["apple", "avocado"]}   # {'a'}  (a set)
swapped = {v: k for k, v in lengths.items()}     # {1: 'a', 3: 'abc'}
```

Note `{}` with a `key: value` pair is a dict; `{x for ...}` with a single
expression is a set. There is **no tuple comprehension** — `(x for x in xs)`
is a generator expression (section 6).

## 5. Nested loops

Several `for` clauses read in the **same order** as nested loops:

```python
pairs = [(x, y) for x in range(3) for y in range(3) if x < y]
# equivalent to:
# for x in range(3):
#     for y in range(3):
#         if x < y: pairs.append((x, y))
# [(0, 1), (0, 2), (1, 2)]

flat = [x for row in [[1, 2], [3]] for x in row]     # [1, 2, 3]
```

A comprehension can also be the *expression* of another one (building a matrix):

```python
grid = [[r * c for c in range(1, 4)] for r in range(1, 4)]
# [[1, 2, 3], [2, 4, 6], [3, 6, 9]]

transposed = [[row[i] for row in grid] for i in range(3)]
```

Rule of thumb: **two levels is the limit** for readability.

## 6. Generator expressions

Replace the brackets with parentheses and you get something *lazy*:

```python
squares = (n * n for n in range(1_000_000))   # nothing computed yet
next(squares)                                  # 0
```

It produces one item at a time, so memory use is constant. It is single-use:
once consumed, it is empty.

When a generator expression is the **only argument** of a call, drop the extra parens:

```python
total = sum(n * n for n in range(10))
has_neg = any(n < 0 for n in numbers)
all_ok = all(s.isdigit() for s in ids)
longest = max((len(w) for w in words), default=0)
count = sum(1 for w in words if w.startswith("a"))   # counting idiom
```

`any` and `all` **short-circuit**: they stop at the first decisive item. They
are also correct on empty input: `any([])` is `False`, `all([])` is `True`.

## 7. Comprehension scope

The loop variable lives inside the comprehension and does not leak:

```python
[i for i in range(3)]
print(i)          # NameError
```

Python 3.12+ inlines comprehensions for speed, but the scoping rule stays.

## 8. Walrus operator (`:=`) in comprehensions

Avoid computing something twice by naming it inside the filter:

```python
results = [y for x in data if (y := expensive(x)) > 0]
```

Use sparingly — if it feels clever, use a loop.

## 9. When NOT to use a comprehension

- **For side effects.** `[print(x) for x in xs]` builds a throwaway list. Use a `for` loop.
- **When it needs more than ~2 clauses or a long expression.** Break it up or use a loop.
- **When you need `break`, `continue`, `try/except`, or multiple statements.** Comprehensions are expressions only.
- **When a built-in already does it.** `list(xs)` beats `[x for x in xs]`; `sorted(set(xs))`, `sum(xs)`, `"".join(...)`.
- **When you only iterate once.** `sum([x for x in xs])` builds a pointless list; use `sum(x for x in xs)`.

```python
# Too clever
result = [f(x) for row in data for x in row if x and (g(x) or h(x)) and not k(x)]

# Better
result = []
for row in data:
    for x in row:
        if not x or k(x):
            continue
        if g(x) or h(x):
            result.append(f(x))
```

## Common mistakes

| Mistake | Fix |
|---|---|
| `[x for x in xs else 0]` (else on a filter) | `[x if cond else 0 for x in xs]` — conditional goes in front |
| `[x for x in xs if cond else 0]` | same as above |
| Wrong order of nested `for` clauses | Write the nested loops out first, then flatten top-to-bottom |
| Reusing a generator expression twice | It is exhausted after one pass; make a list or a new generator |
| `{}` expecting an empty set | `{}` is an empty dict; use `set()` |
| Using a list comp for side effects | Use a plain `for` loop |
| `any([...])` with square brackets | Drop the brackets so it short-circuits and stays lazy |

## Practice

Open `exercises.py` and work through the functions from top to bottom.
Try to write each as a **single expression** — except where the docstring says otherwise.

When you are ready:

```
python check.py 2.01
```
