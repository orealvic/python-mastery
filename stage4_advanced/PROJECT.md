# Stage 4 Capstone — A Profiled Async Web Crawler

Build a concurrent web crawler with `asyncio`, then *measure* it and make it faster using evidence
instead of guesses. Write a short performance report on what you found.

It pulls together Stage 4: descriptors and class machinery (for configuration), the object model
and memory, threads and processes, asyncio, performance and profiling, and (optionally) the AST.

## Ground rules: crawl politely

You will build something that can send many requests quickly, so:
- **Develop against a local site.** The milestones below show how to generate one and serve it with
  `python -m http.server`. Run every benchmark against it.
- When crawling real sites, obey `robots.txt` (`urllib.robotparser`), limit requests per host, set a
  descriptive `User-Agent`, and stay on one domain. Never point it at sites you don't own at high
  concurrency.

## What it does

```text
$ python -m crawler http://localhost:8000/ --max-pages 500 --concurrency 20 --per-host 5
crawled 500 pages in 3.42 s (146.2 pages/s)
  200: 481   404: 12   timeout: 4   other errors: 3
  broken links: 12 (see report.json)
  slowest: /big/page-0193.html  (0.81 s)
  deepest: depth 9
```

- Start from a seed URL. Fetch the page, extract the `<a href>` links, resolve them with
  `urllib.parse.urljoin`, and normalize them (drop `#fragments`, lowercase the host).
- Stay on the seed's domain by default. Never fetch the same URL twice.
- Stop at `--max-pages` or `--max-depth`.
- Write `report.json` containing every URL, its status, size, elapsed time, depth, the page that
  linked to it, and the list of broken links.

## Requirements

### Concurrency
- Use `asyncio` with a **worker-pool** design: an `asyncio.Queue` of URLs and N worker tasks inside
  a `TaskGroup`, like `async_producer_consumer` from 4.05.
- Enforce a global concurrency limit **and** a per-host limit (a `Semaphore` per host).
- Every request has a timeout. One bad page must never crash or hang the crawl.
- `Ctrl-C` stops cleanly. Cancel the workers and still write a partial report.
- The HTTP client is up to you. `aiohttp` or `httpx` are the usual choices. To stay stdlib-only,
  run `urllib.request` calls in threads with `asyncio.to_thread`, and compare the two approaches in
  your report.

### Parsing
- Extract links with `html.parser.HTMLParser`, or with `lxml`/`selectolax` if you install one of
  them.
- Parsing is CPU work. Measure whether it blocks the event loop. If it does, try moving it to a
  `ProcessPoolExecutor` with `loop.run_in_executor`, and *measure again*.

### Design
- A `CrawlConfig` class whose fields are validated, using descriptors from 4.01 (e.g. a
  `PositiveInt` descriptor) or a frozen dataclass with checks in `__post_init__`.
- A `PageResult` record that uses `__slots__` (or `@dataclass(slots=True)`), because you will
  create thousands of them. Measure the memory difference with `tracemalloc`.
- Inject the fetch function so tests can use a fake "web" built from a dict, without any network
  access.

### Measurement: the main point of this capstone
1. **Baseline.** Crawl the local site with `--concurrency 1` and record the pages per second.
2. **Scale.** Run again at concurrency 5, 10, 20, 50 and 100. Plot or tabulate the results. Where
   does throughput stop improving, and why?
3. **Profile.** Run `python -m cProfile -o crawl.prof -m crawler ...`, and look at the result with
   `pstats` (sort by `cumulative`, then by `tottime`). What are the top five functions? Is the time
   spent in your code, in parsing, or in waiting?
4. **Memory.** Use `tracemalloc` to find peak memory for a 5,000-page crawl. What is using it?
5. **Optimize** the single biggest cost you found, then **re-measure**. Keep a change only if the
   numbers improve.

Write up the results in `PERFORMANCE.md`: the method, a table of numbers, what you changed, and what
didn't help. Negative results count too.

## Suggested milestones

1. **A local test site.** Write `make_site.py`. It should generate 2,000 or more HTML pages in a
   `site/` folder with random links between them, including some broken links, some deep chains and
   some large pages. Serve it with `python -m http.server -d site 8000`.
2. **Sequential crawler.** Get the logic right with no concurrency: fetch, parse, normalize, dedupe,
   and enforce depth and page limits. Test it against a fake fetcher.
3. **Async workers.** Add the queue, workers, `TaskGroup` and the global semaphore.
4. **Robustness.** Add timeouts, per-host limits, error categories and clean Ctrl-C handling.
5. **Report.** Write `report.json` and print the summary.
6. **Measure and optimize** using the steps above, then write `PERFORMANCE.md`.

## Stretch goals
- Respect `robots.txt` and `Crawl-delay` per host.
- Resume an interrupted crawl from a saved frontier (store the queue and the seen set in SQLite).
- A live progress line updated in place (`\r`), showing pages per second, queue size and errors.
- Compare against a `ThreadPoolExecutor` version of the same crawler, and explain the difference.
- Use `sys.getsizeof` with a recursive walk, or `tracemalloc` snapshots, to show how much memory the
  `seen` set uses. Try storing URL hashes instead.
- Use the `ast` module to write a tiny check that fails your CI if anyone calls `time.sleep` or
  `requests.get` inside an `async def`.

## Self-review checklist

Correctness
- [ ] No URL is fetched twice, and the crawl never leaves the seed domain (unless a flag allows it).
- [ ] A page that hangs forever doesn't hang the crawl.
- [ ] Ctrl-C produces a partial report, not a traceback.
- [ ] Tests run against a fake web with no network access, and cover dedupe, depth limits and error
      handling.

Concurrency
- [ ] Nothing blocking runs on the event loop. Check with `PYTHONASYNCIODEBUG=1`, which warns about
      slow callbacks.
- [ ] Global and per-host limits are both enforced. Prove it with a test that counts peak
      concurrency.

Performance
- [ ] `PERFORMANCE.md` contains real numbers from your own machine, before and after.
- [ ] You can explain *why* throughput stops improving past some concurrency level.
- [ ] Every optimization you kept is backed by a measurement.

When all of the boxes are ticked, you have completed Stage 4.
