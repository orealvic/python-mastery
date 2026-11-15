"""Reference solutions for 1.01. Try the exercises yourself first!"""


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def is_even(n: int) -> bool:
    return n % 2 == 0


def split_bill(total: float, people: int) -> float:
    return round(total / people, 2)


def initials(full_name: str) -> str:
    return "".join(part[0].upper() + "." for part in full_name.split())


def is_palindrome(text: str) -> bool:
    cleaned = text.replace(" ", "").lower()
    return cleaned == cleaned[::-1]


def format_receipt_line(item: str, qty: int, unit_price: float) -> str:
    return f"{item:<12}x{qty:<3}{qty * unit_price:>8.2f}"


def seconds_to_hms(seconds: int) -> str:
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours}:{minutes:02}:{secs:02}"
