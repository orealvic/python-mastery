"""3.06 — Testing: testable design & unittest.mock

pytest isn't installed, so these exercises practise the *ideas*: dependency
injection, fakes, spies, mocks, and a tiny parametrize decorator.
Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 3.06` from the course root to test your work.
"""
import random
import time
from collections.abc import Callable
from datetime import datetime


def slugify(text: str) -> str:
    """Turn text into a URL slug (write it TDD-style from the examples).

    Lowercase; every run of characters that are not ASCII letters or digits
    becomes a single "-"; no leading or trailing "-".

    >>> slugify("Hello, World!")
    'hello-world'
    >>> slugify("  spaces   everywhere  ")
    'spaces-everywhere'
    >>> slugify("a--b__c")
    'a-b-c'
    >>> slugify("!!!")
    ''
    """
    raise NotImplementedError


def greeting(now: Callable[[], datetime] = datetime.now) -> str:
    """Return a greeting based on the hour of `now()` (dependency injection
    of the clock):

        hour < 12   -> "Good morning"
        hour < 18   -> "Good afternoon"
        otherwise   -> "Good evening"

    >>> greeting(lambda: datetime(2024, 1, 1, 9, 30))
    'Good morning'
    """
    raise NotImplementedError


def roll_dice(count: int, rng: random.Random | None = None) -> list[int]:
    """Roll `count` six-sided dice and return the results.

    Use `rng.randint(1, 6)` for each roll, calling it exactly `count` times
    in order. If `rng` is None, use a new `random.Random()`.
    Raise ValueError if count < 0.

    Injecting the generator makes the function deterministic in tests:
    roll_dice(3, random.Random(42)) always returns the same list.
    """
    raise NotImplementedError


def fetch_with_retry(fetch: Callable[[], object], retries: int = 3,
                     delay: float = 1.0,
                     sleep: Callable[[float], None] = time.sleep):
    """Call `fetch()`; if it raises an Exception, wait and try again.

    * Total attempts = retries + 1.
    * Before retry number k (k = 1, 2, ...) call `sleep(delay * 2 ** (k - 1))`
      (exponential backoff: delay, 2*delay, 4*delay, ...).
    * Never sleep after the final failed attempt; re-raise that last exception.
    * Return fetch()'s result on the first success.
    * Only `Exception` is retried (not KeyboardInterrupt etc.).

    `sleep` is injected so tests don't actually wait.
    """
    raise NotImplementedError


def calls_summary(mock, name: str = "mock") -> list[str]:
    """Summarise every call recorded on a unittest.mock.Mock as strings.

    Format: "<name>(<args>, <kwargs>)" where args are repr()'d and joined by
    ", " followed by keyword args rendered "key=repr(value)" in call order.

    >>> m = Mock(); m(1, "a", x=3); m()
    >>> calls_summary(m, "f")
    ["f(1, 'a', x=3)", 'f()']

    Hint: mock.call_args_list; each entry has .args and .kwargs.
    """
    raise NotImplementedError


class FakeUserRepository:
    """An in-memory fake of a user repository (a *fake* is a small working
    implementation used in place of a database).

    Users are plain dicts. Methods:

      save(user: dict) -> dict
          Store a COPY. If "id" is missing assign the next integer id
          (1, 2, 3, ...; ids already used by explicit ids are never reused:
          next id = max existing id + 1, or 1 if empty). Return a copy of
          what was stored (including the id). Saving an existing id replaces it.
      get(user_id: int) -> dict | None
          Return a COPY of the stored user, or None.
      delete(user_id: int) -> bool
          Remove it; return True if it existed.
      all() -> list[dict]
          Copies of all users sorted by id.

    It also records every call as `self.calls`: a list of (method_name,)
    tuples in order, e.g. [("save",), ("get",)].
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def save(self, user: dict) -> dict:
        raise NotImplementedError

    def get(self, user_id: int) -> dict | None:
        raise NotImplementedError

    def delete(self, user_id: int) -> bool:
        raise NotImplementedError

    def all(self) -> list[dict]:
        raise NotImplementedError


def register_user(name: str, email: str, repo, mailer) -> dict:
    """A service function with injected collaborators.

      1. Raise ValueError if `email` does not contain "@" or `name` is blank
         (nothing must be saved or sent in that case).
      2. Save {"name": name.strip(), "email": email} with `repo.save(...)`.
      3. Send a welcome message: `mailer.send(to=email, subject=f"Welcome, {name}!")`
         (keyword arguments; `name` stripped).
      4. Return what `repo.save` returned.

    Tests pass in a Mock mailer and a fake repo.
    """
    raise NotImplementedError


def make_spy(func: Callable) -> Callable:
    """Wrap `func` in a *spy*: it still calls and returns the real function,
    but records how it was used on the wrapper:

      spy.calls    -> list of (args_tuple, kwargs_dict) per call, in order
      spy.results  -> list of return values (only successful calls)
      spy.call_count -> int

    A call that raises is still recorded in `calls`/`call_count` (but adds no
    result) and the exception propagates. Preserve func's __name__.
    """
    raise NotImplementedError


def parametrize(argnames: str, argvalues: list):
    """A tiny version of pytest.mark.parametrize.

    `argnames` is a comma-separated string such as "a, b" (or just "x").
    `argvalues` is a list of cases: for multiple names each case is a
    tuple/list of the same length; for a single name each case is the value.

        @parametrize("a, b, expected", [(1, 2, 3), (2, 2, 4)])
        def test_add(a, b, expected):
            assert a + b == expected

        test_add()      # runs the body once per case, with keyword arguments

    The decorated function becomes a zero-argument runner that:
      * runs ALL cases (a failing case does not stop the others);
      * if any case raised, raises ONE AssertionError after running all cases
        whose message contains, for each failing case, its index and its
        parameters, e.g. "case 1: {'a': 2, 'b': 2, 'expected': 5}";
      * returns None when every case passes;
      * exposes `runner.case_count` (number of cases) and preserves __name__.
    """
    raise NotImplementedError
