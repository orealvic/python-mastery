# Stage 2 Capstone — Data Fetcher & Report Generator

Build a command-line tool that pulls data from a public source on the internet, cleans it, stores
it, and produces a report. This is the first "real program" you'll write: several modules, classes,
logging, a proper CLI, and data that doesn't arrive in the shape you want.

It pulls together Stage 2: comprehensions, modules and packages, OOP, dunder methods and properties,
`collections`/`itertools`, text/dates/CSV/JSON, `argparse` and `logging`.

Create your own folder (for example `stage2_real_programs/report/`). Standard library only is the
default (`urllib.request`, `json`, `csv`, `sqlite3`). If you want, set up a virtual environment
and use `requests`. You practised that in module 2.02.

## Pick a data source

Choose something you're actually curious about. It should be free and need no API key, or only a
free one. Some options:

| Source | What you get |
|---|---|
| [Open-Meteo](https://open-meteo.com/) | Weather history and forecasts by latitude/longitude. No key needed. |
| [GitHub REST API](https://docs.github.com/en/rest) | Repos, issues, commits for any public project. No key needed for low volume. |
| [Hacker News API](https://github.com/HackerNews/API) | Top stories, comments, scores. |
| [REST Countries](https://restcountries.com/) | Population, area, languages, currencies. |
| A CSV export from your bank, fitness tracker, or a [data.gov](https://data.gov) dataset | Use a local file instead of an API if you'd rather avoid networking. |

Scraping HTML (`html.parser` from the standard library) is fine too. Check the site's terms and
`robots.txt` first, and keep your request rate polite.

## Example session (weather version)

```text
$ python -m report fetch --city Lisbon --days 30
INFO  fetched 30 daily records for Lisbon (38.72, -9.14)
INFO  saved 30 rows to data/weather.sqlite
$ python -m report summary --city Lisbon
Lisbon — last 30 days
  Avg high      21.4 °C
  Avg low       14.9 °C
  Rainy days    6
  Hottest day   2026-10-19 (27.8 °C)
$ python -m report export --city Lisbon --format csv -o lisbon.csv
Wrote 30 rows to lisbon.csv
$ python -m report fetch --city Atlantis
Error: city 'Atlantis' not found
```

## Requirements

### Structure
- A small package, not one giant file. For example:
  ```text
  report/
      __init__.py
      __main__.py      # makes `python -m report` work; just calls cli.main()
      cli.py           # argparse + wiring, nothing else
      client.py        # talks to the API / reads the source
      models.py        # your record class(es)
      storage.py       # SQLite or CSV/JSON persistence
      analysis.py      # summaries, grouping, statistics
  tests/
      test_models.py
      test_analysis.py
  ```
- At least one class that represents a record (e.g. `DailyWeather`, `Repo`, `Story`). Give it a
  useful `__repr__` and `__eq__`. Add a `@property` for at least one derived value, and a
  `@classmethod` constructor like `from_api(dict)` that does the parsing and validation.

### Fetching
- Network code lives in one place (`client.py`) and returns plain Python objects, not raw HTTP
  responses.
- Set a timeout on every request.
- Handle these failures with a clear message and a non-zero exit code: network errors, non-200
  responses, malformed JSON and "not found".
- Don't hammer the API. Add a short delay between paginated requests, or cache responses on disk.

### Processing and storage
- Convert dates and times to `datetime`/`date` objects at the boundary, and never pass date
  strings around inside your code.
- Store records in SQLite (`sqlite3`, using parameterized queries; never f-string SQL) **or** in
  CSV/JSON files. Re-fetching the same data must not create duplicates. SQLite users can rely on a
  `UNIQUE` constraint with `INSERT OR REPLACE`.
- At least three different summaries in `analysis.py` using `collections.Counter`, `defaultdict`,
  `itertools.groupby`, `statistics`, or comprehensions. All of them should be pure functions that
  take a list of records.

### CLI and logging
- `argparse` with subcommands (`fetch`, `summary`, `export`, or whatever fits your data).
- `logging`, not `print`, for progress and diagnostics. Use `-v/--verbose` to switch to DEBUG.
  Reserve `print` for the program's actual output.
- An `export` command that writes CSV with `csv.DictWriter`.

## Suggested milestones

1. **Explore the API in the REPL.** Fetch one response, `json.loads` it, and poke at the structure.
   Save one real response to `tests/fixtures/sample.json`. Your tests will use this file so they
   never touch the network.
2. **Model.** Write your record class and `from_api`. Test it against the fixture.
3. **Analysis.** Write the summary functions and test them with hand-built records.
4. **Storage.** Save and load; prove that loading what you saved gives equal objects.
5. **Client.** Do the real fetching, with timeouts and error handling.
6. **CLI.** Wire everything together in `cli.py`, and add logging.
7. **Polish.** Format with `ruff format`, and fix whatever `ruff check` reports.

## Stretch goals
- An on-disk cache: store raw responses keyed by URL with a timestamp, and reuse them if they're
  less than N minutes old.
- Retry with exponential backoff on 5xx errors and timeouts.
- `--since 2026-01-01` / `--until` date filtering.
- A plain-text bar chart in the terminal (`"█" * n`), or a Markdown or HTML report file.
- Compare two entities: two cities, two repos, two countries.
- A config file (`tomllib` for reading TOML) for defaults like the city and the database path.

## Self-review checklist

Behavior
- [ ] Every command works on a fresh checkout with no database file.
- [ ] Running `fetch` twice doesn't duplicate data.
- [ ] Unplugging the network (or using a bad URL) gives a one-line error, not a traceback.
- [ ] Exported CSV opens correctly in a spreadsheet.

Code
- [ ] `cli.py` contains no business logic; `analysis.py` contains no I/O.
- [ ] Network access happens only in `client.py`.
- [ ] SQL uses `?` placeholders everywhere.
- [ ] Dates are `datetime` objects everywhere except at the edges.
- [ ] Logging uses `logger = logging.getLogger(__name__)` per module, configured once in `main()`.

Testing
- [ ] Tests run without network access, using the saved fixture.
- [ ] Model parsing, at least two summaries, and the storage round-trip are tested.

When all of the boxes are ticked, you have completed Stage 2.
