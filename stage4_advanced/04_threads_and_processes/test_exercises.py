import importlib
import os
import threading

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def run_threads(n, target):
    threads = [threading.Thread(target=target) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(30)
    assert not any(t.is_alive() for t in threads)


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


def test_thread_safe_counter():
    c = ex.ThreadSafeCounter()
    assert c.value == 0
    assert c.increment() == 1
    assert c.increment(5) == 6
    c2 = ex.ThreadSafeCounter(100)
    assert c2.value == 100

    c3 = ex.ThreadSafeCounter()
    seen, lock = [], threading.Lock()

    def work():
        local = [c3.increment() for _ in range(2000)]
        with lock:
            seen.extend(local)

    run_threads(8, work)
    assert c3.value == 16000
    assert len(seen) == 16000 and len(set(seen)) == 16000
    assert sorted(seen) == list(range(1, 16001))


def test_parallel_map_order():
    import time

    def slow_first(x):
        time.sleep(0.05 if x == 0 else 0)
        return x * 10

    assert ex.parallel_map(slow_first, range(6), max_workers=3) == [0, 10, 20, 30, 40, 50]
    assert ex.parallel_map(str, []) == []
    assert ex.parallel_map(lambda x: x + 1, iter([1, 2, 3])) == [2, 3, 4]


def test_parallel_map_concurrency_and_errors():
    barrier = threading.Barrier(3, timeout=10)

    def meet(x):
        barrier.wait()  # only passes if 3 calls run at the same time
        return x

    assert ex.parallel_map(meet, [1, 2, 3], max_workers=3) == [1, 2, 3]

    def boom(x):
        if x == 2:
            raise ValueError("two")
        return x

    try:
        ex.parallel_map(boom, [1, 2, 3])
    except ValueError as e:
        assert str(e) == "two"
    else:
        assert False, "expected ValueError"
    try:
        ex.parallel_map(str, [1], max_workers=0)
    except ValueError:
        pass
    else:
        assert False, "expected ValueError"


def test_split_chunks():
    assert ex.split_chunks([1, 2, 3, 4, 5], 2) == [[1, 2, 3], [4, 5]]
    assert ex.split_chunks([1, 2], 3) == [[1], [2], []]
    assert ex.split_chunks([], 2) == [[], []]
    assert ex.split_chunks(range(10), 5) == [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]
    chunks = ex.split_chunks(range(103), 7)
    assert len(chunks) == 7
    assert [x for c in chunks for x in c] == list(range(103))
    sizes = [len(c) for c in chunks]
    assert max(sizes) - min(sizes) <= 1 and sizes == sorted(sizes, reverse=True)
    try:
        ex.split_chunks([1], 0)
    except ValueError:
        pass
    else:
        assert False


def test_producer_consumer():
    before = threading.active_count()
    out = ex.producer_consumer(range(100), lambda x: x * x, n_consumers=4)
    assert sorted(out) == [x * x for x in range(100)]
    assert threading.active_count() == before
    assert ex.producer_consumer(list(range(30)), lambda x: -x, n_consumers=1) == [-x for x in range(30)]
    assert ex.producer_consumer([], lambda x: x) == []


def test_producer_consumer_uses_multiple_threads():
    names, lock = set(), threading.Lock()
    barrier = threading.Barrier(3, timeout=10)

    def transform(x):
        barrier.wait()
        with lock:
            names.add(threading.current_thread().name)
        return x

    out = ex.producer_consumer([1, 2, 3], transform, n_consumers=3)
    assert sorted(out) == [1, 2, 3]
    assert len(names) == 3


def test_bounded_executor_results_and_limits():
    lock = threading.Lock()
    state = {"running": 0, "peak": 0}

    def task(x):
        with lock:
            state["running"] += 1
            state["peak"] = max(state["peak"], state["running"])
        total = sum(range(2000))
        with lock:
            state["running"] -= 1
        return x + total * 0

    with ex.BoundedExecutor(max_workers=3, max_pending=5) as pool:
        futures = [pool.submit(task, i) for i in range(40)]
    assert [f.result() for f in futures] == list(range(40))
    assert state["peak"] <= 3
    with ex.BoundedExecutor(1, 1) as pool:
        assert pool.submit(pow, 2, 5).result() == 32
        assert pool.submit(lambda a, b=0: a - b, 5, b=2).result() == 3
        f = pool.submit(lambda: 1 / 0)
        try:
            f.result()
        except ZeroDivisionError:
            pass
        else:
            assert False


def test_bounded_executor_blocks_submit():
    gate = threading.Event()
    third_done = threading.Event()
    box = {}
    pool = ex.BoundedExecutor(max_workers=1, max_pending=2)
    try:
        f1 = pool.submit(gate.wait, 10)
        f2 = pool.submit(lambda: 2)

        def third():
            box["f3"] = pool.submit(lambda: 3)
            third_done.set()

        t = threading.Thread(target=third)
        t.start()
        assert not third_done.wait(0.3), "submit should block while 2 tasks are outstanding"
        gate.set()
        assert third_done.wait(10), "submit should unblock once a task finishes"
        t.join(10)
        assert f1.result(10) is True and f2.result(10) == 2 and box["f3"].result(10) == 3
    finally:
        gate.set()
        pool.shutdown()


def test_rate_limiter_with_fake_clock():
    clock = FakeClock()
    rl = ex.RateLimiter(2, 1.0, clock=clock, sleep=clock.sleep)
    times = []
    for _ in range(5):
        rl.acquire()
        times.append(clock.now)
    assert times == [0.0, 0.0, 1.0, 1.0, 2.0]
    clock.now += 10
    rl.acquire()
    rl.acquire()
    assert clock.now == 12.0
    assert clock.sleeps == [1.0, 1.0]


def test_rate_limiter_partial_window():
    clock = FakeClock()
    rl = ex.RateLimiter(3, 10.0, clock=clock, sleep=clock.sleep)
    rl.acquire()
    clock.now = 4.0
    rl.acquire()
    clock.now = 5.0
    rl.acquire()
    rl.acquire()  # must wait until the first stamp (t=0) expires at t=10
    assert clock.now == 10.0


def test_rate_limiter_real_clock_default():
    rl = ex.RateLimiter(1000, 1.0)
    for _ in range(10):
        rl.acquire()


def test_fetch_all_limited():
    clock = FakeClock()
    rl = ex.RateLimiter(2, 1.0, clock=clock, sleep=clock.sleep)
    urls = [f"u{i}" for i in range(5)]
    called = []
    out = ex.fetch_all_limited(urls, lambda u: called.append(u) or u.upper(), rl, max_workers=3)
    assert out == ["U0", "U1", "U2", "U3", "U4"]
    assert sorted(called) == urls
    assert clock.now == 2.0
    assert ex.fetch_all_limited([], str, ex.RateLimiter(1, 1.0)) == []


def test_count_primes_and_processes():
    assert ex.count_primes(2) == 0
    assert ex.count_primes(10) == 4
    assert ex.count_primes(100) == 25
    assert ex.count_primes(1000) == 168
    assert ex.parallel_prime_counts([10, 100, 1000, 2]) == [4, 25, 168, 0]
    assert ex.parallel_prime_counts([], workers=1) == []
