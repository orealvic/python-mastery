"""Reference solutions for 1.02. Try the exercises yourself first!"""


def fizzbuzz(n: int) -> list[str]:
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return out


def letter_grade(score: int) -> str:
    if not 0 <= score <= 100:
        raise ValueError(f"score out of range: {score}")
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"


def count_truthy(values: list) -> int:
    return sum(1 for v in values if v)


def running_totals(numbers: list[int]) -> list[int]:
    totals = []
    running = 0
    for n in numbers:
        running += n
        totals.append(running)
    return totals


def numbered(items: list[str]) -> list[str]:
    return [f"{i}. {item}" for i, item in enumerate(items, start=1)]


def pair_scores(names: list[str], scores: list[int]) -> dict[str, int]:
    return dict(zip(names, scores))


def first_repeated(items: list):
    seen = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None


def collatz_steps(n: int) -> int:
    if n < 1:
        raise ValueError("n must be >= 1")
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
    return steps


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, int(n ** 0.5) + 1):
        if n % d == 0:
            return False
    return True


def primes_up_to(limit: int) -> list[int]:
    return [n for n in range(2, limit + 1) if is_prime(n)]
