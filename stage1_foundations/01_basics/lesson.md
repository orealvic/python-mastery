# 1.01 — Variables, Types, Operators & Strings

## Learning goals
- Create variables and understand Python's core types
- Use arithmetic, comparison, and boolean operators
- Format strings with f-strings and use common string methods

## 1. Variables are names, not boxes

```python
age = 30          # int
price = 19.99     # float
name = "Ada"      # str
active = True     # bool
nothing = None    # NoneType
```

A variable is a *name bound to an object*. `type(x)` tells you the object's type:

```python
>>> type(age)
<class 'int'>
```

Python is **dynamically typed** (names can be rebound to any type) but **strongly typed**
(`"3" + 4` is an error — no silent conversion).

```python
int("42")      # 42
float("3.5")   # 3.5
str(10)        # '10'
bool("")       # False   (empty things are "falsy")
```

**Falsy values:** `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`. Everything else is truthy.

## 2. Operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+ - *` | add, subtract, multiply | `7 * 3` | `21` |
| `/` | true division (always float) | `7 / 2` | `3.5` |
| `//` | floor division | `7 // 2` | `3` |
| `%` | remainder (modulo) | `7 % 2` | `1` |
| `**` | power | `2 ** 10` | `1024` |
| `== != < <= > >=` | comparison | `3 < 5` | `True` |
| `and or not` | boolean logic | `True and not False` | `True` |

Comparisons chain: `0 <= x < 10` works as you'd hope.

> ⚠️ Floats are approximate: `0.1 + 0.2 == 0.3` is `False`. Use `round()` or `math.isclose()`.

## 3. Strings

Strings are **immutable** sequences of characters.

```python
s = "Hello, World"
len(s)            # 12
s[0]              # 'H'
s[-1]             # 'd'
s[0:5]            # 'Hello'   (slice: start inclusive, end exclusive)
s[::-1]           # 'dlroW ,olleH'  (reversed)
s.lower()         # 'hello, world'
s.upper()         # 'HELLO, WORLD'
s.replace("World", "Python")
s.split(", ")     # ['Hello', 'World']
"-".join(["a", "b", "c"])   # 'a-b-c'
"  pad  ".strip()  # 'pad'
s.startswith("He") # True
"World" in s       # True
s.count("l")       # 3
```

### f-strings

```python
name, score = "Ada", 93.456
f"{name} scored {score:.1f}"     # 'Ada scored 93.5'
f"{1234567:,}"                   # '1,234,567'
f"{name!r}"                      # "'Ada'"
f"{score=}"                      # 'score=93.456'  (great for debugging)
f"{'hi':>6}"                     # '    hi'  (right-align in 6 chars)
```

## 4. Input & output

```python
print("a", "b", sep="-", end="!\n")   # a-b!
answer = input("Your name? ")          # always returns a str
```

## Common mistakes
- Using `=` (assignment) when you mean `==` (comparison).
- Forgetting that `input()` returns a string: `int(input())` to get a number.
- Expecting `s.upper()` to change `s` — strings are immutable; methods return **new** strings.

## Practice
Open `exercises.py`, implement each function, then run:

```bash
python check.py 1.01
```
