# 4.05 — asyncio

## Learning goals
- Explain the event loop, coroutines, tasks and futures, and what `await` really does
- Run many things concurrently with `gather`, `TaskGroup`, `wait`, and `as_completed`
- Apply timeouts (`asyncio.timeout`), cancellation, and cleanup correctly
- Limit concurrency with `Semaphore`, pass work with `asyncio.Queue`
- Write async generators and async context managers
- Bridge to blocking code with `asyncio.to_thread` and avoid blocking the loop

## 1. The model: cooperative multitasking on one thread

An **event loop** runs tasks one at a time on a single thread. A task runs until it hits an `await` on something that is
not ready; then it *yields control* and the loop runs another ready task. Nothing is ever pre-empted, so:

- Great for **many I/O-bound** jobs (sockets, HTTP, DB with async drivers).
- A single CPU-heavy or blocking call (`time.sleep`, `requests.get`, a big loop) **freezes everything**.
- No data races between awaits (a block of code with no `await` is atomic with respect to other tasks), but
  races across `await` points still exist.

```python
import asyncio

async def fetch(name, delay):              # `async def` -> calling it returns a coroutine object, running nothing
    await asyncio.sleep(delay)             # suspension point
    return f"{name} done"

async def main():
    print(await fetch("a", 0.1))           # runs sequentially: 0.1s
    r = await asyncio.gather(fetch("a", 0.1), fetch("b", 0.1))   # concurrently: ~0.1s total

asyncio.run(main())                        # creates a loop, runs main, closes the loop
```

## 2. Coroutines, Tasks, Futures

| Thing | What it is |
|---|---|
| coroutine object | result of calling `async def`; does nothing until awaited or wrapped in a task |
| `Task` | a coroutine scheduled on the loop (`asyncio.create_task(coro)`); starts running at the next loop iteration |
| `Future` | low-level placeholder for a result set later (callbacks, thread bridges) |
| awaitable | anything usable with `await`: coroutine, Task, Future |

`await coro` runs it inline (no concurrency by itself). `create_task` is what creates concurrency.
**Keep a reference** to tasks you create; the loop holds only weak references, so a dropped task can be garbage collected mid-flight.
Never forget to await a coroutine: "coroutine ... was never awaited" is the warning.

## 3. Structured concurrency: `TaskGroup` (3.11+)

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch("a", 0.1))
        t2 = tg.create_task(fetch("b", 0.2))
    print(t1.result(), t2.result())        # the block exits only when all tasks are done
```
If any task fails, the group **cancels the siblings** and raises an `ExceptionGroup` (handle with `except*`):
```python
try:
    async with asyncio.TaskGroup() as tg: ...
except* ValueError as eg:
    print(eg.exceptions)
```
`asyncio.gather(*aws, return_exceptions=False)` is the older tool: returns results in order; on the first exception it raises
but does **not** cancel the others (they keep running!). Prefer `TaskGroup` for new code.

Other tools: `asyncio.wait(tasks, return_when=FIRST_COMPLETED)` -> `(done, pending)`; `as_completed(aws)` yields in completion order.

## 4. Timeouts and cancellation

```python
try:
    async with asyncio.timeout(1.0):       # 3.11+; replaces wait_for in most code
        await slow()
except TimeoutError:
    ...
```
- `task.cancel()` schedules `CancelledError` to be raised at the task's current `await`.
- **Cancellation is an exception**: clean up with `try/finally`; if you catch `CancelledError` you must re-raise it
  (unless you really intend to swallow it). `CancelledError` derives from `BaseException`, so `except Exception` won't catch it.
- After `task.cancel()`, `await` the task (or gather with `return_exceptions=True`) to be sure it finished unwinding.
- `asyncio.shield(aw)` protects an inner task from the outer cancellation (use sparingly).
- `asyncio.timeout(...)` cancels the enclosed block and converts to `TimeoutError`; `cm.expired()` tells you if it fired.

## 5. Limiting concurrency and passing work

```python
sem = asyncio.Semaphore(10)
async def limited(coro):
    async with sem:
        return await coro
```
```python
q = asyncio.Queue(maxsize=100)               # back-pressure: put() waits when full
async def worker():
    while True:
        item = await q.get()
        try: await handle(item)
        finally: q.task_done()
# producer: await q.put(x); await q.join() waits until every item has had task_done()
# stop workers: cancel them after join(), or put sentinels, or q.shutdown() (3.13+)
```
Other primitives: `Lock`, `Event`, `Condition`, `Barrier` (3.11). All are *not thread-safe*: use them only inside the loop's thread.

## 6. Async iteration and context managers

```python
async def ticker(n, delay):                 # async generator
    for i in range(n):
        await asyncio.sleep(delay)
        yield i

async for i in ticker(3, 0.1): ...
values = [i async for i in ticker(3, 0.1)]       # async comprehension
```
Close async generators deterministically (`aclose()` or `contextlib.aclosing`) if you may exit early.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def connection(url):
    conn = await open_conn(url)
    try:
        yield conn
    finally:
        await conn.close()

async with connection(url) as c: ...
```
A class-based version defines `__aenter__` / `__aexit__`; async iterators define `__aiter__` / `__anext__`.

## 7. Blocking code and the loop

```python
data = await asyncio.to_thread(blocking_read, path)          # runs in the default thread pool, copies contextvars
loop = asyncio.get_running_loop()
res = await loop.run_in_executor(process_pool, cpu_job, arg)  # CPU-bound: use a ProcessPoolExecutor
```
Debug slow callbacks with `asyncio.run(main(), debug=True)` (logs callbacks taking >100 ms) or `PYTHONASYNCIODEBUG=1`.
From other threads use `asyncio.run_coroutine_threadsafe(coro, loop)` / `loop.call_soon_threadsafe`.

## 8. Patterns

- **Fan-out with a limit**: semaphore + `TaskGroup`/`gather`.
- **Retry with backoff**: loop, `await asyncio.sleep(delay * 2**attempt)`, re-raise the last error. Add jitter in production.
- **First wins / hedged requests**: `asyncio.wait(..., FIRST_COMPLETED)`, then cancel and await the rest.
- **Deadline for a whole operation**: wrap in `asyncio.timeout`; inner code just needs to be cancel-safe.
- **Rate limiting**: sliding window / token bucket guarded by a lock; inject clock and sleep for tests.
- **Testing**: write `async def` tests, run with `asyncio.run`; use tiny sleeps or fake clocks, never rely on wall-clock precision.

## Common mistakes
- Calling blocking functions (`time.sleep`, `requests`, heavy loops, file I/O at scale) inside `async def`.
- Forgetting `await` (you get a coroutine object, not the result) or `create_task` (no concurrency).
- Fire-and-forget `create_task` without storing the reference; exceptions then vanish ("Task exception was never retrieved").
- Swallowing `CancelledError` (`except BaseException`, or `except asyncio.CancelledError: pass`).
- `gather` leaving sibling tasks running after one fails; unbounded `gather` over 100k items without a semaphore.
- Creating a new event loop per call or calling `asyncio.run` from inside a running loop.
- Sharing asyncio primitives across threads.
- Using `asyncio.sleep(0)` as a "fix" for ordering problems.

## Further reading
- `asyncio` docs: *Coroutines and Tasks*, *Runners*, *Synchronization Primitives*, *Developing with asyncio*
- PEP 492 (async/await), PEP 525 (async generators), PEP 654 (ExceptionGroup/`except*`), `asyncio.TaskGroup` / `timeout` (3.11)
- Łukasz Langa, *asyncio* tutorials; `anyio` and `trio` for structured-concurrency design ideas

## Practice
Open `exercises.py`, implement each item, then run:

```bash
python check.py 4.05
```
