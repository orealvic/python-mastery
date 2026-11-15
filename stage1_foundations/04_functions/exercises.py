"""1.04 — Functions

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 1.04` from the course root to test your work.

Pay close attention to the signatures: parameter names, defaults, and
keyword-only markers (`*`) are part of the specification.
"""


def greet(name: str, greeting: str = "Hello", punctuation: str = "!") -> str:
    """Return '<greeting>, <name><punctuation>'.

    >>> greet("Ada")
    'Hello, Ada!'
    >>> greet("Ada", "Hi", punctuation="?")
    'Hi, Ada?'
    """
    raise NotImplementedError


def add_item(item, items=None) -> list:
    """Append `item` to `items` and return the list.

    - If `items` is given, mutate that very list and return it.
    - If `items` is omitted, start a FRESH new list on every call.
      (Beware the mutable default argument pitfall!)

    >>> add_item(1)
    [1]
    >>> add_item(2)
    [2]
    >>> shared = [1]
    >>> add_item(2, shared) is shared
    True
    """
    raise NotImplementedError


def total(*numbers: float) -> float:
    """Return the sum of all positional arguments. With none, return 0.

    >>> total(1, 2, 3)
    6
    >>> total()
    0
    """
    raise NotImplementedError


def describe_options(**options) -> str:
    """Return the keyword arguments as 'key=value' pairs, sorted by key and
    joined by ', '. Values are formatted with str(). No options gives ''.

    >>> describe_options(size=3, color="red")
    'color=red, size=3'
    """
    raise NotImplementedError


def min_max(numbers: list[float]) -> tuple[float, float]:
    """Return (smallest, largest). Raise ValueError if `numbers` is empty.

    >>> min_max([3, 1, 4, 1, 5])
    (1, 5)
    """
    raise NotImplementedError


def format_price(amount: float, *, currency: str = "$", decimals: int = 2) -> str:
    """Format a price as currency followed by amount with `decimals` places
    and thousands separators. `currency` and `decimals` are keyword-only
    (keep the `*` in the signature!).

    >>> format_price(1234.5)
    '$1,234.50'
    >>> format_price(9.99, currency="EUR ", decimals=1)
    'EUR 10.0'
    """
    raise NotImplementedError


def make_multiplier(factor: float):
    """Return a function that multiplies its single argument by `factor`.

    >>> triple = make_multiplier(3)
    >>> triple(5)
    15
    """
    raise NotImplementedError


def make_counter(start: int = 0):
    """Return a function `tick()` that, on each call, adds 1 to a private
    counter and returns the new value. The first call returns start + 1.
    Separate counters must be independent. Hint: `nonlocal`.

    >>> c = make_counter()
    >>> c(), c(), c()
    (1, 2, 3)
    >>> make_counter(10)()
    11
    """
    raise NotImplementedError


def sort_words(words: list[str]) -> list[str]:
    """Return a NEW list of words sorted by length (shortest first), with
    words of equal length ordered alphabetically (case-sensitive, normal
    string ordering). Use sorted() with a key function.

    >>> sort_words(["pear", "fig", "banana", "apple", "kiwi"])
    ['fig', 'kiwi', 'pear', 'apple', 'banana']
    """
    raise NotImplementedError


def compose(*funcs):
    """Return a function that applies `funcs` right-to-left to its single
    argument: compose(f, g, h)(x) == f(g(h(x))).
    compose() with no functions returns a function that gives back its argument.

    >>> inc = lambda x: x + 1
    >>> dbl = lambda x: x * 2
    >>> compose(inc, dbl)(5)    # inc(dbl(5))
    11
    """
    raise NotImplementedError
