"""Reference solutions for 4.04. Try the exercises yourself first!"""
import queue
import threading
import time
from collections import deque
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor


class ThreadSafeCounter:
    def __init__(self, start: int = 0):
        self._value = start
        self._lock = threading.Lock()

    def increment(self, n: int = 1) -> int:
        with self._lock:
            self._value += n
            return self._value

    @property
    def value(self) -> int:
        with self._lock:
            return self._value


def parallel_map(func, items, max_workers: int = 4) -> list:
    if max_workers < 1:
        raise ValueError("max_workers must be >= 1")
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(func, items))


def split_chunks(seq, n: int) -> list:
    if n < 1:
        raise ValueError("n must be >= 1")
    items = list(seq)
    size, extra = divmod(len(items), n)
    chunks, start = [], 0
    for i in range(n):
        end = start + size + (1 if i < extra else 0)
        chunks.append(items[start:end])
        start = end
    return chunks


def producer_consumer(items, transform, n_consumers: int = 3) -> list:
    q: queue.Queue = queue.Queue(maxsize=10)
    sentinel = object()
    results: list = []
    lock = threading.Lock()

    def consumer():
        while True:
            item = q.get()
            if item is sentinel:
                return
            result = transform(item)
            with lock:
                results.append(result)

    threads = [threading.Thread(target=consumer) for _ in range(n_consumers)]
    for t in threads:
        t.start()
    for item in items:
        q.put(item)
    for _ in threads:
        q.put(sentinel)
    for t in threads:
        t.join()
    return results


class BoundedExecutor:
    def __init__(self, max_workers: int, max_pending: int):
        self._pool = ThreadPoolExecutor(max_workers=max_workers)
        self._slots = threading.BoundedSemaphore(max_pending)

    def submit(self, fn, /, *args, **kwargs) -> Future:
        self._slots.acquire()
        try:
            future = self._pool.submit(fn, *args, **kwargs)
        except BaseException:
            self._slots.release()
            raise
        future.add_done_callback(lambda _f: self._slots.release())
        return future

    def shutdown(self, wait: bool = True) -> None:
        self._pool.shutdown(wait=wait)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.shutdown(wait=True)
        return False


class RateLimiter:
    def __init__(self, max_calls: int, period: float, clock=time.monotonic, sleep=time.sleep):
        self._max_calls = max_calls
        self._period = period
        self._clock = clock
        self._sleep = sleep
        self._stamps: deque = deque()
        self._lock = threading.Lock()

    def acquire(self) -> None:
        with self._lock:
            while True:
                now = self._clock()
                while self._stamps and self._stamps[0] <= now - self._period:
                    self._stamps.popleft()
                if len(self._stamps) < self._max_calls:
                    self._stamps.append(now)
                    return
                self._sleep(self._stamps[0] + self._period - now)


def fetch_all_limited(urls, fetch, limiter: RateLimiter, max_workers: int = 4) -> list:
    def task(url):
        limiter.acquire()
        return fetch(url)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(task, urls))


def count_primes(limit: int) -> int:
    if limit < 3:
        return 0
    sieve = bytearray([1]) * limit
    sieve[0:2] = b"\x00\x00"
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(range(i * i, limit, i)))
    return sum(sieve)


def parallel_prime_counts(limits, workers: int = 2) -> list:
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(count_primes, limits))
