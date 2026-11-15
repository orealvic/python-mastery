"""Reference solutions for 3.02. Try the exercises yourself first!"""
import functools
import inspect
import time


def make_counter(start: int = 0, step: int = 1):
    value = start - step

    def counter():
        nonlocal value
        value += step
        return value

    return counter


def memoize(func):
    cache: dict = {}
    stats = {"hits": 0, "misses": 0}

    @functools.wraps(func)
    def wrapper(*args):
        if args in cache:
            stats["hits"] += 1
        else:
            stats["misses"] += 1
            cache[args] = func(*args)
        return cache[args]

    def cache_info():
        return dict(stats)

    def cache_clear():
        cache.clear()
        stats["hits"] = stats["misses"] = 0

    wrapper.cache_info = cache_info
    wrapper.cache_clear = cache_clear
    return wrapper


def retry(times: int, exceptions: tuple = (Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last: BaseException | None = None
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last = exc
            assert last is not None
            raise last

        return wrapper

    return decorator


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            wrapper.elapsed = time.perf_counter() - start
            wrapper.history.append(wrapper.elapsed)

    wrapper.elapsed = None
    wrapper.history = []
    return wrapper


def validate_types(func):
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        for name, value in bound.arguments.items():
            annotation = sig.parameters[name].annotation
            if (isinstance(annotation, type) and annotation is not inspect.Parameter.empty
                    and not isinstance(value, annotation)):
                raise TypeError(
                    f"argument {name!r} must be {annotation.__name__}, "
                    f"got {type(value).__name__}"
                )
        return func(*args, **kwargs)

    return wrapper


def limit_calls(max_calls: int):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if wrapper.calls_made >= max_calls:
                raise RuntimeError(f"{func.__name__} limited to {max_calls} calls")
            wrapper.calls_made += 1
            return func(*args, **kwargs)

        def reset():
            wrapper.calls_made = 0

        wrapper.calls_made = 0
        wrapper.reset = reset
        return wrapper

    return decorator


REGISTRY: dict[str, object] = {}


def register(name: str | None = None):
    def decorator(func):
        key = name if name is not None else func.__name__
        if key in REGISTRY:
            raise ValueError(f"{key!r} already registered")
        REGISTRY[key] = func
        return func

    return decorator


def compose_decorators(*decorators):
    def decorator(func):
        for dec in reversed(decorators):
            func = dec(func)
        return func

    return decorator


class CountCalls:
    def __init__(self, func) -> None:
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)
