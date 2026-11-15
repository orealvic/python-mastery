# 1.02 — Control Flow

## Learning goals
- Make decisions with `if` / `elif` / `else`
- Repeat work with `for` and `while`, and pick the right one
- Use `range`, `enumerate`, and `zip` instead of manual index juggling
- Control loops with `break`, `continue`, and the loop `else` clause
- Understand truthiness and write idiomatic conditions

## 1. Decisions: `if` / `elif` / `else`

Python uses **indentation** (4 spaces) to define blocks. A colon starts the block.

```python
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C or below"
print(grade)   # B
```

Conditions are checked top to bottom; the **first** true branch runs and the rest are skipped.
That is why you order range checks from most to least restrictive (`>= 90` before `>= 80`).

Chained comparisons read like math:

```python
age = 25
if 18 <= age < 65:
    print("working age")
```

Combine conditions with `and`, `or`, `not`. They **short-circuit**: `a and b` does not evaluate `b`
if `a` is falsy.

```python
items = []
if items and items[0] == "x":   # safe: items[0] is never evaluated when items is empty
    ...
```

### Conditional expression (ternary)

```python
label = "even" if n % 2 == 0 else "odd"
```

Use it for simple either/or values; use a regular `if` once it gets complicated.

## 2. Truthiness

Any object can be used in a condition. These are **falsy**; everything else is truthy:

| Falsy | Truthy examples |
|---|---|
| `False`, `None` | `True` |
| `0`, `0.0` | `-1`, `0.1` |
| `""` | `"0"`, `" "`, `"False"` |
| `[]`, `()`, `{}`, `set()` | `[0]`, `[None]` |

```python
names = []
if not names:          # idiomatic "is empty" check
    print("no names")
```

Prefer `if items:` over `if len(items) > 0:`. Use `is None` (not `== None`) to test for `None`,
because `0` and `""` are falsy but are *not* `None`.

`or` and `and` return one of their operands, not necessarily a bool:

```python
name = "" or "anonymous"     # 'anonymous'
"hi" and "there"             # 'there'
```

## 3. `for` loops

`for` iterates over anything iterable: lists, strings, dicts, ranges, files...

```python
for ch in "abc":
    print(ch)

total = 0
for n in [3, 1, 4]:
    total += n
```

### `range`

```python
list(range(5))          # [0, 1, 2, 3, 4]       stop is exclusive
list(range(2, 6))       # [2, 3, 4, 5]
list(range(10, 0, -3))  # [10, 7, 4, 1]         step may be negative
```

### `enumerate` — when you need the index too

```python
for i, name in enumerate(["ann", "bob"], start=1):
    print(i, name)      # 1 ann / 2 bob
```

Avoid `for i in range(len(xs)): xs[i]` — `enumerate` is clearer and less error-prone.

### `zip` — walk several sequences in step

```python
for name, score in zip(["ann", "bob", "cy"], [90, 72]):
    print(name, score)  # stops at the SHORTEST input: cy is dropped
```

`dict(zip(keys, values))` builds a dictionary in one line.

## 4. `while` loops

Use `while` when you do not know in advance how many iterations you need.

```python
n = 27
steps = 0
while n != 1:
    n = n // 2 if n % 2 == 0 else 3 * n + 1
    steps += 1
```

Make sure something inside the loop moves you toward the condition becoming false, otherwise
you get an infinite loop (Ctrl+C stops it). `while True:` with a `break` is a common pattern.

## 5. `break`, `continue`, and loop `else`

```python
for n in [1, 3, 8, 5]:
    if n % 2 == 0:
        print("first even:", n)
        break               # leave the loop immediately
else:
    print("no even number") # runs only if the loop was NOT ended by break
```

`continue` skips to the next iteration:

```python
for n in range(10):
    if n % 3 != 0:
        continue
    print(n)                # 0 3 6 9
```

The loop `else` is perfect for search loops ("did I find it?"):

```python
def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            break
    else:
        return True
    return False
```

## 6. Common loop patterns

```python
# accumulate
total = 0
for x in xs: total += x

# running totals
running, out = 0, []
for x in xs:
    running += x
    out.append(running)

# find first match (return early, or None if nothing matches)
for x in xs:
    if x < 0:
        return x
return None

# count matches
count = sum(1 for x in xs if x > 0)      # a generator expression; more in later lessons
```

## Common mistakes
- Forgetting the colon, or mixing tabs and spaces.
- Off-by-one with `range`: `range(1, n)` stops at `n - 1`; use `range(1, n + 1)` to include `n`.
- Modifying a list while looping over it — build a new list instead.
- Writing `if x == True:`; just write `if x:`.
- Using `is` for value comparison (`x is 5`); use `==`. Reserve `is` for `None`/`True`/`False`.
- Assuming loop `else` means "if the loop was empty" — it means "no `break` happened".
- Infinite `while` loops where the loop variable is never updated.

## Practice
Open `exercises.py`, implement each function, then run:

```bash
python check.py 1.02
```
