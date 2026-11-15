"""3.02 — Closures & Decorators

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 3.02` from the course root to test your work.

All decorators must preserve the wrapped function's metadata
(use functools.wraps) and pass through arguments and return values.
"""
import functools


def make_counter(start: int = 0, step: int = 1):
    """Return a function `counter()` that, each time it is called, returns the
    next value in the sequence start, start+step, start+2*step, ...
    Each call to make_counter creates an independent counter.

    >>> c = make_counter()
    >>> c(), c(), c()
    (0, 1, 2)
    >>> d = make_counter(10, 5)
    >>> d(), d()
    (10, 15)

    Hint: closure + nonlocal.
    """
    raise NotImplementedError


def memoize(func):
    """Decorator: cache results keyed by the positional arguments.

    Only positional arguments need to be supported (all hashable).
    The wrapper must expose `cache_info()` returning a dict
    {"hits": int, "misses": int} and `cache_clear()` which empties the cache
    and resets both counters.

    >>> @memoize
    ... def sq(x): return x * x
    >>> sq(4), sq(4)
    (16, 16)
    >>> sq.cache_info()
    {'hits': 1, 'misses': 1}
    """
    raise NotImplementedError


def retry(times: int, exceptions: tuple = (Exception,)):
    """Decorator factory: call the function up to `times` times in total.

    If the call raises one of `exceptions`, try again. If every attempt fails,
    re-raise the LAST exception. Exceptions not in `exceptions` propagate
    immediately without retrying. On success return the result.

    >>> @retry(3, (ValueError,))
    ... def flaky(): ...

    Hint: three nested functions.
    """
    raise NotImplementedError


def timer(func):
    """Decorator: measure how long each call takes, using time.perf_counter.

    After each call, `wrapper.elapsed` holds the duration (float seconds) of
    the most recent call, and `wrapper.history` is a list of the durations of
    all calls so far. Before any call: elapsed is None and history == [].
    The elapsed time must still be recorded if the function raises
    (and the exception must propagate).
    """
    raise NotImplementedError


def validate_types(func):
    """Decorator: check arguments against the function's type annotations at
    call time and raise TypeError on a mismatch.

    Rules (keep it simple):
      * Only check parameters whose annotation is a plain class
        (e.g. int, str, list). Skip unannotated ones (beware: the
        'no annotation' marker inspect.Parameter.empty is itself a class!) and anything else.
      * Use isinstance. bool counts as int (normal isinstance behaviour).
      * Check both positional and keyword arguments (use inspect.signature
        and sig.bind). Do not check default values that weren't passed.
      * The TypeError message must contain the parameter name.
      * Do not check the return value.

    >>> @validate_types
    ... def repeat(s: str, n: int): return s * n
    >>> repeat("a", 3)
    'aaa'
    >>> repeat("a", "3")   # TypeError mentioning 'n'
    """
    raise NotImplementedError


def limit_calls(max_calls: int):
    """Decorator factory: allow the function to be called at most `max_calls`
    times. Further calls raise RuntimeError (and do NOT call the function).
    The wrapper exposes `calls_made` (int) and `reset()` which sets it to 0.

    >>> @limit_calls(2)
    ... def ping(): return "pong"
    >>> ping(), ping()
    ('pong', 'pong')
    >>> ping()   # RuntimeError
    """
    raise NotImplementedError


REGISTRY: dict[str, object] = {}


def register(name: str | None = None):
    """Decorator factory that records the function in the module-level
    REGISTRY dict and returns the ORIGINAL function unchanged (same object).

    The key is `name` if given, else the function's __name__. Registering a
    key that already exists raises ValueError (and leaves REGISTRY unchanged).
    Must work as `@register()` and `@register("custom")`.

    >>> @register("hi")
    ... def hello(): return "hello"
    >>> REGISTRY["hi"] is hello
    True
    """
    raise NotImplementedError


def compose_decorators(*decorators):
    """Return a single decorator equivalent to stacking the given decorators
    in the order written, as if you had put them one above the other:

        @compose_decorators(a, b, c)
        def f(): ...
    is the same as
        @a
        @b
        @c
        def f(): ...
    (i.e. f = a(b(c(f)))). With no decorators it returns the function unchanged.
    """
    raise NotImplementedError


class CountCalls:
    """Class-based decorator that counts how many times the function is called.

    Usage:
        @CountCalls
        def f(x): return x + 1
        f(1); f(2)
        f.count   # 2
        f.__name__   # 'f' (preserved via functools.update_wrapper)

    Instances are callable and pass through args/returns. `count` is an int
    starting at 0; failed calls (exceptions) still count.
    Hint: implement __init__ and __call__; use functools.update_wrapper(self, func).
    """

    def __init__(self, func) -> None:
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        raise NotImplementedError
