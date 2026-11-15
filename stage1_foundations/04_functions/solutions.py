"""Reference solutions for 1.04. Try the exercises yourself first!"""


def greet(name: str, greeting: str = "Hello", punctuation: str = "!") -> str:
    return f"{greeting}, {name}{punctuation}"


def add_item(item, items=None) -> list:
    if items is None:
        items = []
    items.append(item)
    return items


def total(*numbers: float) -> float:
    return sum(numbers)


def describe_options(**options) -> str:
    return ", ".join(f"{key}={value}" for key, value in sorted(options.items()))


def min_max(numbers: list[float]) -> tuple[float, float]:
    if not numbers:
        raise ValueError("min_max() requires a non-empty list")
    return min(numbers), max(numbers)


def format_price(amount: float, *, currency: str = "$", decimals: int = 2) -> str:
    return f"{currency}{amount:,.{decimals}f}"


def make_multiplier(factor: float):
    def multiply(x):
        return x * factor
    return multiply


def make_counter(start: int = 0):
    count = start

    def tick() -> int:
        nonlocal count
        count += 1
        return count

    return tick


def sort_words(words: list[str]) -> list[str]:
    return sorted(words, key=lambda w: (len(w), w))


def compose(*funcs):
    def composed(x):
        for f in reversed(funcs):
            x = f(x)
        return x
    return composed
