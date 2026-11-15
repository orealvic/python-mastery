import asyncio
import importlib
import os
import threading

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    async def sleep(self, seconds):
        self.now += seconds


async def agen(iterable, delay=0.0):
    for x in iterable:
        await asyncio.sleep(delay)
        yield x


async def test_run_all():
    async def job(x, d):
        await asyncio.sleep(d)
        return x

    assert await ex.run_all([job("a", 0.02), job("b", 0.0), job("c", 0.01)]) == ["a", "b", "c"]
    assert await ex.run_all([]) == []


async def test_run_all_failure_cancels_siblings():
    cancelled = []

    async def slow():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancelled.append("slow")
            raise

    async def bad():
        await asyncio.sleep(0.01)
        raise ValueError("bad")

    try:
        await ex.run_all([slow(), bad()])
    except ExceptionGroup as eg:
        assert any(isinstance(e, ValueError) for e in eg.exceptions)
    else:
        assert False, "expected ExceptionGroup"
    assert cancelled == ["slow"]


async def test_gather_with_limit():
    state = {"now": 0, "peak": 0}

    async def job(i):
        state["now"] += 1
        state["peak"] = max(state["peak"], state["now"])
        await asyncio.sleep(0.005)
        state["now"] -= 1
        return i * 2

    out = await ex.gather_with_limit(3, [job(i) for i in range(10)])
    assert out == [i * 2 for i in range(10)]
    assert state["peak"] == 3
    assert await ex.gather_with_limit(5, []) == []
    try:
        await ex.gather_with_limit(0, [])
    except ValueError:
        pass
    else:
        assert False


async def test_first_completed():
    cancelled = []

    async def job(name, delay):
        try:
            await asyncio.sleep(delay)
            return name
        except asyncio.CancelledError:
            cancelled.append(name)
            raise

    result = await ex.first_completed([job("slow", 10), job("fast", 0.01), job("mid", 5)])
    assert result == "fast"
    assert sorted(cancelled) == ["mid", "slow"]


async def test_first_completed_errors_and_empty():
    cancelled = []

    async def slow():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancelled.append(1)
            raise

    async def bad():
        await asyncio.sleep(0.01)
        raise KeyError("k")

    try:
        await ex.first_completed([slow(), bad()])
    except KeyError:
        pass
    else:
        assert False, "expected KeyError"
    assert cancelled == [1]
    try:
        await ex.first_completed([])
    except ValueError:
        pass
    else:
        assert False


async def test_first_completed_outer_cancel():
    cancelled = []

    async def slow(n):
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancelled.append(n)
            raise

    task = asyncio.ensure_future(ex.first_completed([slow(1), slow(2)]))
    await asyncio.sleep(0.01)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    assert sorted(cancelled) == [1, 2]


async def test_retry_async():
    calls = []

    def flaky(fail_times):
        async def func():
            calls.append(1)
            if len(calls) <= fail_times:
                raise ConnectionError(f"fail {len(calls)}")
            return "ok"

        return func

    assert await ex.retry_async(flaky(2), retries=2) == "ok"
    assert len(calls) == 3
    calls.clear()
    try:
        await ex.retry_async(flaky(10), retries=2)
    except ConnectionError as e:
        assert str(e) == "fail 3"
    else:
        assert False
    assert len(calls) == 3
    calls.clear()
    try:
        await ex.retry_async(flaky(5), retries=0)
    except ConnectionError:
        pass
    assert len(calls) == 1


async def test_retry_async_exceptions_and_backoff():
    calls = []

    async def wrong():
        calls.append(1)
        raise KeyError("nope")

    try:
        await ex.retry_async(wrong, retries=5, exceptions=(ValueError,))
    except KeyError:
        pass
    else:
        assert False
    assert len(calls) == 1

    n = []

    async def twice():
        n.append(1)
        if len(n) < 3:
            raise ValueError
        return len(n)

    loop = asyncio.get_running_loop()
    start = loop.time()
    assert await ex.retry_async(twice, retries=2, delay=0.02, backoff=2.0, exceptions=(ValueError,)) == 3
    assert loop.time() - start >= 0.05  # 0.02 + 0.04 (minus slack)


async def test_with_timeout():
    assert await ex.with_timeout(asyncio.sleep(10, "x"), 0.01, default="late") == "late"
    assert await ex.with_timeout(asyncio.sleep(0, "x"), 5, default="late") == "x"
    assert await ex.with_timeout(asyncio.sleep(10), 0.01) is None

    cancelled = []

    async def slow():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cancelled.append(1)
            raise

    await ex.with_timeout(slow(), 0.01)
    assert cancelled == [1]


async def test_with_timeout_inner_errors_propagate():
    async def inner_timeout():
        raise TimeoutError("inner")

    async def boom():
        raise ValueError("v")

    for coro, exc in ((inner_timeout(), TimeoutError), (boom(), ValueError)):
        try:
            await ex.with_timeout(coro, 5, default="d")
        except exc:
            pass
        else:
            assert False, f"expected {exc}"


async def test_run_blocking():
    gate = threading.Event()
    main_thread = threading.get_ident()

    def blocking(a, b=0):
        ok = gate.wait(10)  # needs the loop to stay responsive to be set
        return (a + b, ok, threading.get_ident())

    async def opener():
        await asyncio.sleep(0.01)
        gate.set()

    opener_task = asyncio.ensure_future(opener())
    total, ok, tid = await ex.run_blocking(blocking, 2, b=3)
    await opener_task
    assert total == 5 and ok is True
    assert tid != main_thread


async def test_async_producer_consumer():
    state = {"now": 0, "peak": 0}

    async def handler(x):
        state["now"] += 1
        state["peak"] = max(state["peak"], state["now"])
        await asyncio.sleep(0.005 if x % 2 else 0.001)
        state["now"] -= 1
        return x * x

    out = await ex.async_producer_consumer(list(range(20)), handler, n_workers=3)
    assert out == [x * x for x in range(20)]
    assert 2 <= state["peak"] <= 3
    assert await ex.async_producer_consumer([], handler) == []
    assert await ex.async_producer_consumer(iter([3]), handler, n_workers=5) == [9]


async def test_async_producer_consumer_error_propagates():
    async def handler(x):
        await asyncio.sleep(0)
        if x == 3:
            raise ValueError("three")
        return x

    # A TaskGroup wraps the error in an ExceptionGroup; accept either form.
    try:
        await ex.async_producer_consumer(range(10), handler, n_workers=2)
    except ValueError:
        pass
    except ExceptionGroup as eg:
        assert eg.subgroup(ValueError) is not None, f"unexpected errors: {eg!r}"
    else:
        assert False, "expected an error"


async def test_async_rate_limiter():
    clock = FakeClock()
    rl = ex.AsyncRateLimiter(2, 1.0, clock=clock, sleep=clock.sleep)
    times = []
    for _ in range(5):
        await rl.acquire()
        times.append(clock.now)
    assert times == [0.0, 0.0, 1.0, 1.0, 2.0]


async def test_async_rate_limiter_context_and_concurrency():
    clock = FakeClock()
    rl = ex.AsyncRateLimiter(3, 10.0, clock=clock, sleep=clock.sleep)
    times = []

    async def use():
        async with rl:
            times.append(clock.now)

    await asyncio.gather(*(use() for _ in range(7)))
    assert sorted(times) == [0.0, 0.0, 0.0, 10.0, 10.0, 10.0, 20.0]

    rl2 = ex.AsyncRateLimiter(100, 1.0)  # real clock / real asyncio.sleep
    for _ in range(5):
        await rl2.acquire()


async def test_abatch():
    assert [b async for b in ex.abatch(agen(range(5)), 2)] == [[0, 1], [2, 3], [4]]
    assert [b async for b in ex.abatch(agen(range(4), 0.001), 2)] == [[0, 1], [2, 3]]
    assert [b async for b in ex.abatch(agen([]), 3)] == []
    assert [b async for b in ex.abatch(agen("abc"), 10)] == [["a", "b", "c"]]
    try:
        async for _ in ex.abatch(agen([1]), 0):
            pass
    except ValueError:
        pass
    else:
        assert False
