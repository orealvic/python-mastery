"""4.05 — asyncio

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 4.05` from the course root to test your work.

All tests use tiny delays or fake clocks, so they run fast.
"""
import asyncio
import time


async def run_all(coros) -> list:
    """Run all coroutines concurrently using `asyncio.TaskGroup` and return
    their results as a list in input order.

    If any coroutine raises, the other (still running) coroutines are cancelled
    and the TaskGroup's ExceptionGroup propagates (do not catch it).

    >>> await run_all([asyncio.sleep(0, "a"), asyncio.sleep(0, "b")])
    ['a', 'b']
    """
    raise NotImplementedError


async def gather_with_limit(limit: int, coros) -> list:
    """Await all `coros` concurrently but with at most `limit` running at the
    same time (use an asyncio.Semaphore). Return results in input order.
    `limit < 1` raises ValueError.

    >>> await gather_with_limit(2, [asyncio.sleep(0, i) for i in range(5)])
    [0, 1, 2, 3, 4]
    """
    raise NotImplementedError


async def first_completed(coros):
    """Run the coroutines concurrently; return the result of the FIRST one to
    finish and CANCEL all the others, awaiting their cancellation so they have
    fully unwound (their `finally` blocks have run) before you return.

    - If the first to finish raised an exception, propagate it (still cancel
      the others first).
    - If the awaiting call itself is cancelled, cancel all children too.
    - Empty input raises ValueError.
    - On a tie (several already done), prefer the earliest in input order.
    """
    raise NotImplementedError


async def retry_async(func, retries: int = 3, delay: float = 0.0, backoff: float = 1.0,
                      exceptions: tuple = (Exception,)):
    """Call `await func()` (a zero-argument async callable) until it succeeds.

    - On an exception that matches `exceptions`, wait `delay * backoff**attempt`
      seconds (attempt = 0 for the first failure) and try again.
    - At most `retries` RETRIES, i.e. up to retries + 1 calls in total. When the
      last attempt fails, re-raise that last exception.
    - Exceptions not in `exceptions` propagate immediately (no retry).
    - Return the successful result.

    >>> # func fails twice then returns "ok": retry_async(func, retries=2) -> "ok"
    """
    raise NotImplementedError


async def with_timeout(coro, timeout: float, default=None):
    """Await `coro`; if it takes longer than `timeout` seconds, cancel it and
    return `default` instead. Use `asyncio.timeout`.

    - A TimeoutError raised *by the coroutine itself* (not by our deadline)
      should still propagate: use the context manager's `.expired()`.
    - Other exceptions propagate.

    >>> await with_timeout(asyncio.sleep(10, "x"), 0.01, default="late")
    'late'
    """
    raise NotImplementedError


async def run_blocking(func, *args, **kwargs):
    """Run the BLOCKING callable `func(*args, **kwargs)` in a worker thread
    (asyncio.to_thread) and return its result, so the event loop stays free
    to run other tasks meanwhile.
    """
    raise NotImplementedError


async def async_producer_consumer(items, handler, n_workers: int = 3) -> list:
    """Process `items` through `await handler(item)` using an asyncio.Queue and
    `n_workers` worker tasks. Return the handler results in INPUT order.

    - The caller enqueues `(index, item)` pairs on a bounded queue
      (maxsize = 2 * n_workers), then one stop sentinel per worker.
    - At most n_workers handlers run at once.
    - Use a TaskGroup (or otherwise ensure all workers have finished and that
      errors in a handler propagate).
    - Empty `items` returns [].
    """
    raise NotImplementedError


class AsyncRateLimiter:
    """Async sliding-window rate limiter: at most `max_calls` acquisitions in
    any window of `period` seconds.

        limiter = AsyncRateLimiter(2, 1.0)
        async with limiter:      # or: await limiter.acquire()
            await do_request()

    - `clock` (default time.monotonic) returns now; `sleep` (default
      asyncio.sleep) is an async function used to wait. Both injectable.
    - `acquire()`: under an asyncio.Lock, drop timestamps `<= now - period`;
      if fewer than `max_calls` remain, record `now` and return; otherwise
      `await sleep(oldest + period - now)` (holding the lock) and re-check.
    - `async with limiter` calls `acquire()` on entry; exit does nothing.

    With max_calls=2, period=1.0 and a fake clock starting at 0, five acquires
    complete at times 0, 0, 1, 1, 2.
    """

    def __init__(self, max_calls: int, period: float, clock=time.monotonic, sleep=asyncio.sleep):
        raise NotImplementedError

    async def acquire(self) -> None:
        raise NotImplementedError

    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, exc_type, exc, tb):
        raise NotImplementedError


async def abatch(aiterable, size: int):
    """Async generator: consume an async iterable and yield lists ("batches") of
    up to `size` items; the final batch may be shorter. No empty batches.
    `size < 1` raises ValueError when iteration starts.

    >>> [b async for b in abatch(agen(range(5)), 2)]
    [[0, 1], [2, 3], [4]]
    """
    raise NotImplementedError
    yield  # pragma: no cover - makes this an async generator
