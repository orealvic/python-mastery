"""Reference solutions for 4.05. Try the exercises yourself first!"""
import asyncio
import time


async def run_all(coros) -> list:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(c) for c in coros]
    return [t.result() for t in tasks]


async def gather_with_limit(limit: int, coros) -> list:
    if limit < 1:
        raise ValueError("limit must be >= 1")
    sem = asyncio.Semaphore(limit)

    async def run(coro):
        async with sem:
            return await coro

    return list(await asyncio.gather(*(run(c) for c in coros)))


async def first_completed(coros):
    tasks = [asyncio.ensure_future(c) for c in coros]
    if not tasks:
        raise ValueError("no coroutines given")
    try:
        done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        winner = next(t for t in tasks if t in done)
    finally:
        pending = [t for t in tasks if not t.done()]
        for t in pending:
            t.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
    return winner.result()


async def retry_async(func, retries: int = 3, delay: float = 0.0, backoff: float = 1.0,
                      exceptions: tuple = (Exception,)):
    attempt = 0
    while True:
        try:
            return await func()
        except exceptions:
            if attempt >= retries:
                raise
            await asyncio.sleep(delay * backoff**attempt)
            attempt += 1


async def with_timeout(coro, timeout: float, default=None):
    try:
        async with asyncio.timeout(timeout) as cm:
            return await coro
    except TimeoutError:
        if cm.expired():
            return default
        raise


async def run_blocking(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)


async def async_producer_consumer(items, handler, n_workers: int = 3) -> list:
    items = list(items)
    results: list = [None] * len(items)
    queue: asyncio.Queue = asyncio.Queue(maxsize=2 * n_workers)

    async def worker():
        while True:
            job = await queue.get()
            if job is None:
                return
            index, item = job
            results[index] = await handler(item)

    async with asyncio.TaskGroup() as tg:
        for _ in range(n_workers):
            tg.create_task(worker())
        for pair in enumerate(items):
            await queue.put(pair)
        for _ in range(n_workers):
            await queue.put(None)
    return results


class AsyncRateLimiter:
    def __init__(self, max_calls: int, period: float, clock=time.monotonic, sleep=asyncio.sleep):
        self._max_calls = max_calls
        self._period = period
        self._clock = clock
        self._sleep = sleep
        self._stamps: list = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            while True:
                now = self._clock()
                self._stamps = [s for s in self._stamps if s > now - self._period]
                if len(self._stamps) < self._max_calls:
                    self._stamps.append(now)
                    return
                await self._sleep(self._stamps[0] + self._period - now)

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


async def abatch(aiterable, size: int):
    if size < 1:
        raise ValueError("size must be >= 1")
    batch = []
    async for item in aiterable:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch
