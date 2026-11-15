# 4.04 — Threads & Processes

## Learning goals
- Explain the GIL, what it does and does not protect, and how free-threaded Python (3.13+/3.14) changes things
- Choose between threads, processes, and asyncio for I/O-bound vs CPU-bound work
- Use `threading` primitives correctly: `Lock`, `RLock`, `Event`, `Condition`, `Semaphore`, `Queue`
- Recognise race conditions and deadlocks and fix them
- Use `concurrent.futures` (`ThreadPoolExecutor`, `ProcessPoolExecutor`) and `multiprocessing` safely

## 1. Concurrency vs parallelism, I/O-bound vs CPU-bound

- **Concurrency**: many tasks in progress (interleaved). **Parallelism**: tasks literally running at the same instant.
- **I/O-bound** (network, disk, DB): most time is spent waiting -> threads or asyncio help, even with a GIL.
- **CPU-bound** (parsing, math, compression): needs real parallelism -> processes (or free-threaded threads, C extensions that
  release the GIL like NumPy, or a different algorithm).

| Workload | Best first choice | Why |
|---|---|---|
| Thousands of sockets | `asyncio` | tiny per-task cost |
| Dozens of blocking calls (legacy libs) | `ThreadPoolExecutor` | simple, GIL released while blocked |
| Heavy pure-Python computation | `ProcessPoolExecutor` | separate interpreters, no GIL sharing |
| Heavy computation, free-threaded build | threads *may* scale | measure first |
| Numeric arrays | NumPy etc. | C loops release the GIL |

## 2. The GIL

The Global Interpreter Lock lets only one thread execute Python bytecode at a time in a given interpreter.
- It protects CPython's *internal* state (reference counts, dict internals), **not your logic**.
- A thread releases it during blocking I/O, `time.sleep`, and in many C extensions; the interpreter also forces a switch
  every `sys.getswitchinterval()` (5 ms default).
- Consequence: CPU-bound pure-Python threads don't speed up; I/O-bound threads do.

**Free-threaded builds** (PEP 703): `python3.13t` / `python3.14t` can run without the GIL (officially supported in 3.14).
```python
import sys
sys._is_gil_enabled()     # False on a free-threaded build with the GIL disabled
import sysconfig; sysconfig.get_config_var("Py_GIL_DISABLED")   # 1 for free-threaded builds
```
Here threads can run Python code in parallel, so **data races that the GIL hid by luck now bite**. Built-in containers use
fine-grained locks (so `list.append` stays safe), but compound operations such as `counter += 1` or check-then-act are still races.
Code that is correct with explicit locks is correct on both builds.

## 3. Race conditions

```python
counter = 0
def work():
    global counter
    for _ in range(100_000):
        counter += 1        # LOAD, ADD, STORE: another thread can interleave between them
```
`counter += 1` is **not atomic**. Fix with a lock:

```python
lock = threading.Lock()
def work():
    global counter
    for _ in range(100_000):
        with lock:
            counter += 1
```
Rules of thumb: protect every shared mutable that is read-modify-written; keep critical sections short;
prefer sharing nothing (queues, immutable data, per-thread accumulators merged at the end).

## 4. Synchronisation primitives

| Primitive | Use |
|---|---|
| `Lock` | mutual exclusion; always use `with lock:` |
| `RLock` | re-entrant lock: same thread may acquire repeatedly (methods calling methods) |
| `Event` | one-shot/flag signalling: `set()`, `wait(timeout)`, `clear()` |
| `Condition` | wait for a state change: `with cv: while not ready: cv.wait()` then `notify` |
| `Semaphore(n)` / `BoundedSemaphore` | limit concurrent access to n resources |
| `Barrier(n)` | n threads wait for each other |
| `queue.Queue` | thread-safe FIFO; the best way to pass work/results |

```python
q = queue.Queue(maxsize=10)           # bounded -> back-pressure
def consumer():
    while (item := q.get()) is not SENTINEL:
        handle(item)
        q.task_done()
# producer: q.put(item) ...; q.put(SENTINEL) once per consumer; q.join() waits for task_done calls
```
Always re-check `Condition` predicates in a `while` loop (spurious wakeups, stolen notifications).
Use sentinels (or `queue.shutdown()` added in 3.13) to stop workers. Mark threads `daemon=True` only for
fire-and-forget helpers; otherwise `join()` them.

**Deadlock** = threads waiting for each other forever. Avoid by acquiring locks in a global order, using timeouts
(`lock.acquire(timeout=1)`), or holding at most one lock at a time.

## 5. `threading` basics
```python
t = threading.Thread(target=fn, args=(1,), name="worker-1")
t.start(); t.join()
threading.local()        # per-thread attributes
threading.current_thread().name
```
Exceptions in a thread don't propagate to the starter (they go to `threading.excepthook`). Executors capture them in futures.

## 6. `concurrent.futures`

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(fetch, urls))              # order preserved, exceptions raised on iteration
    futures = [pool.submit(fetch, u) for u in urls]
    for fut in as_completed(futures):                   # completion order
        print(fut.result())                             # re-raises the task's exception
```
- `Future`: `.result(timeout)`, `.exception()`, `.cancel()` (only if not started), `.add_done_callback(fn)`.
- `with` blocks wait for outstanding work on exit (`shutdown(wait=True)`).
- Submitting unboundedly creates unbounded queues; throttle with a semaphore for large streams.
- Pool size defaults: threads `min(32, cpu+4)`; processes `os.process_cpu_count()`.

## 7. Processes: `multiprocessing` and `ProcessPoolExecutor`

Each process has its own interpreter and memory: true parallelism, but arguments/results are **pickled** and shipped.
```python
def square(x): return x * x          # must be a module-level function (picklable)

if __name__ == "__main__":          # REQUIRED with spawn/forkserver start methods
    with ProcessPoolExecutor() as pool:
        print(list(pool.map(square, range(10), chunksize=4)))
```
- Start methods: `fork` (fast, unsafe with threads; was the Linux default until 3.13), `spawn` (default on macOS/Windows), `forkserver`
  (default on Linux from 3.14). Query with `multiprocessing.get_start_method()`.
- Lambdas, local functions and open sockets can't be pickled: use top-level functions.
- Overhead: process start (tens of ms) + pickling. Only worth it when each task does substantial work; batch small tasks with `chunksize`
  or split data into chunks.
- Share data with `multiprocessing.shared_memory`, `Value`/`Array`, or `Manager` (slow). Usually pass results back instead.
- Cross-process queue/pipe: `multiprocessing.Queue`, `Pipe`. `concurrent.futures` is nicer for most things.
- A worker killed abnormally raises `BrokenProcessPool`.

## 8. Practical patterns
- **Bounded worker pool**: semaphore released from a done-callback to limit in-flight tasks.
- **Rate limiting**: token bucket / sliding window around the call; inject the clock for testability.
- **Graceful shutdown**: `Event` as a stop flag checked in loops, `join(timeout)`.
- **Timeouts**: `future.result(timeout=...)`; note the task itself keeps running, threads cannot be killed.
- **Avoid shared state**: map-reduce with per-worker partial results.

## Common mistakes
- Assuming `x += 1` or "check then act" on shared data is atomic.
- Threads for CPU-bound work on a GIL build, then wondering about no speedup (and extra overhead).
- Lambdas / closures passed to `ProcessPoolExecutor`; forgetting the `if __name__ == "__main__":` guard.
- Not joining threads or not stopping consumers (hanging program at exit).
- Holding a lock while doing I/O or calling unknown callbacks (latency, deadlocks).
- Using `time.sleep` in tests to "wait until done": use events/joins.
- Sharing one DB connection/session between threads.
- `Condition.wait()` without a `while` loop on the predicate.

## Further reading
- `threading`, `queue`, `concurrent.futures`, `multiprocessing` docs
- PEP 703 (free-threading), docs *Python support for free threading*
- David Beazley: *Understanding the Python GIL*; Brett Slatkin, *Effective Python* (concurrency chapters)
- `py-spy dump` to see what every thread is doing in a live process

## Practice
Open `exercises.py`, implement each item, then run:

```bash
python check.py 4.04
```
