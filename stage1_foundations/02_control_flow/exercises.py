"""1.02 — Control Flow

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 1.02` from the course root to test your work.
"""


def fizzbuzz(n: int) -> list[str]:
    """Return a list of strings for the numbers 1..n (inclusive).

    - multiples of 3 -> 'Fizz'
    - multiples of 5 -> 'Buzz'
    - multiples of both -> 'FizzBuzz'
    - otherwise the number itself as a string

    fizzbuzz(0) returns an empty list.

    >>> fizzbuzz(5)
    ['1', '2', 'Fizz', '4', 'Buzz']
    """
    raise NotImplementedError


def letter_grade(score: int) -> str:
    """Convert a numeric score to a letter grade.

    90-100 -> 'A', 80-89 -> 'B', 70-79 -> 'C', 60-69 -> 'D', 0-59 -> 'F'.
    Scores below 0 or above 100 raise ValueError.

    >>> letter_grade(85)
    'B'
    >>> letter_grade(100)
    'A'
    """
    raise NotImplementedError


def count_truthy(values: list) -> int:
    """Return how many items in `values` are truthy.

    >>> count_truthy([0, 1, "", "a", None, [], [0]])
    3
    """
    raise NotImplementedError


def running_totals(numbers: list[int]) -> list[int]:
    """Return the running (cumulative) totals of `numbers`.

    The input must not be modified. An empty list gives an empty list.

    >>> running_totals([1, 2, 3, 4])
    [1, 3, 6, 10]
    """
    raise NotImplementedError


def numbered(items: list[str]) -> list[str]:
    """Return each item prefixed with its 1-based position, as '<n>. <item>'.

    Hint: enumerate(items, start=1)

    >>> numbered(["eggs", "milk"])
    ['1. eggs', '2. milk']
    """
    raise NotImplementedError


def pair_scores(names: list[str], scores: list[int]) -> dict[str, int]:
    """Return a dict mapping each name to the score at the same position.

    If the lists have different lengths, ignore the extra items of the longer one.

    >>> pair_scores(["ann", "bob", "cy"], [90, 72])
    {'ann': 90, 'bob': 72}
    """
    raise NotImplementedError


def first_repeated(items: list):
    """Return the first item whose second occurrence appears earliest while
    scanning left to right, i.e. the first item that you see for the second time.
    Return None if all items are unique. Items are hashable.

    >>> first_repeated([3, 1, 4, 1, 5, 3])
    1
    >>> first_repeated([1, 2, 3]) is None
    True
    """
    raise NotImplementedError


def collatz_steps(n: int) -> int:
    """Return the number of steps for n to reach 1 in the Collatz process:
    if n is even, n = n // 2; otherwise n = 3 * n + 1. Count each application.

    collatz_steps(1) == 0. Raise ValueError if n < 1.

    >>> collatz_steps(6)   # 6 -> 3 -> 10 -> 5 -> 16 -> 8 -> 4 -> 2 -> 1
    8
    """
    raise NotImplementedError


def is_prime(n: int) -> bool:
    """Return True if n is a prime number. Numbers below 2 are not prime.

    Hint: you only need to test divisors up to the square root of n.
    The loop `else` clause is a nice fit here.

    >>> is_prime(13)
    True
    >>> is_prime(15)
    False
    """
    raise NotImplementedError


def primes_up_to(limit: int) -> list[int]:
    """Return all primes p with 2 <= p <= limit, in ascending order.

    >>> primes_up_to(20)
    [2, 3, 5, 7, 11, 13, 17, 19]
    """
    raise NotImplementedError
