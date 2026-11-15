"""1.01 — Variables, Types, Operators & Strings

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 1.01` from the course root to test your work.
"""


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit. Formula: F = C * 9/5 + 32.

    >>> celsius_to_fahrenheit(100)
    212.0
    """
    raise NotImplementedError


def is_even(n: int) -> bool:
    """Return True if n is even, otherwise False.

    >>> is_even(4)
    True
    """
    raise NotImplementedError


def split_bill(total: float, people: int) -> float:
    """Split a bill evenly and round to 2 decimal places.

    >>> split_bill(100, 3)
    33.33
    """
    raise NotImplementedError


def initials(full_name: str) -> str:
    """Return uppercase initials separated by dots, with a trailing dot.

    Ignore extra whitespace between names.

    >>> initials("ada lovelace")
    'A.L.'
    >>> initials("  grace   brewster  hopper ")
    'G.B.H.'
    """
    raise NotImplementedError


def is_palindrome(text: str) -> bool:
    """Return True if text reads the same forwards and backwards,
    ignoring case and spaces.

    >>> is_palindrome("Never odd or even")
    True
    """
    raise NotImplementedError


def format_receipt_line(item: str, qty: int, unit_price: float) -> str:
    """Return a receipt line made of three parts joined with no separator:
      1. item, left-aligned in 12 characters
      2. 'x' followed by qty left-aligned in 3 characters
      3. the line total (qty * unit_price), 2 decimals, right-aligned in 8 characters

    Hint: f"{value:<12}" left-aligns, f"{value:>8.2f}" right-aligns a float.

    >>> format_receipt_line("Coffee", 2, 3.5)
    'Coffee      x2      7.00'
    """
    raise NotImplementedError


def seconds_to_hms(seconds: int) -> str:
    """Convert a number of seconds into 'H:MM:SS'.

    Hint: use // and %.

    >>> seconds_to_hms(3725)
    '1:02:05'
    """
    raise NotImplementedError
