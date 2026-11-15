# 2.07 — Command-Line Programs & Logging

## Learning goals
- Build command-line interfaces with `argparse` (options, flags, sub-commands)
- Structure a program as a testable `main(argv)` with proper exit codes
- Replace `print` debugging with the `logging` module: levels, handlers, formatters
- Test CLI and logging code without touching the terminal

## 1. `argparse` basics

```python
import argparse

parser = argparse.ArgumentParser(prog="greet", description="Greet someone.")
parser.add_argument("name")                                   # positional, required
parser.add_argument("-n", "--times", type=int, default=1)     # option with a value
parser.add_argument("-s", "--shout", action="store_true")     # flag: present -> True
args = parser.parse_args()          # reads sys.argv[1:]; prints usage and exits(2) on error
print(args.name, args.times, args.shout)
```

You get `--help`, usage text and error messages for free. Pass a list to parse something else:
`parser.parse_args(["Ada", "-n", "3"])` — this is how you **test** a parser.

| `add_argument` option | Effect |
|---|---|
| `type=int` / `float` / `Path` / any callable | convert (and validate) the text |
| `default=...` | value when absent |
| `choices=["a", "b"]` | restrict values |
| `nargs="+"` / `"*"` / `"?"` / `3` | one-or-more / zero-or-more / optional / exactly 3 |
| `action="store_true"` / `"store_false"` / `"count"` / `"append"` | flags, `-vvv`, repeated options |
| `required=True` | make an option mandatory |
| `help="..."` / `metavar="FILE"` | documentation in `--help` |

Dashes in option names become underscores in the namespace: `--dry-run` -> `args.dry_run`.

## 2. Sub-commands

Tools like `git commit` / `git push` use sub-parsers:

```python
parser = argparse.ArgumentParser(prog="calc")
parser.add_argument("--precision", type=int, default=2)       # before the sub-command
sub = parser.add_subparsers(dest="command", required=True)
add = sub.add_parser("add")
add.add_argument("numbers", nargs="+", type=float)

args = parser.parse_args(["--precision", "3", "add", "1", "2"])
args.command, args.numbers      # 'add', [1.0, 2.0]
```

Options belong to the parser level where they are defined: `calc --precision 3 add ...`,
not `calc add --precision 3 ...`.

## 3. A testable `main`

```python
import sys

def main(argv=None) -> int:
    args = build_parser().parse_args(argv)     # argv=None -> sys.argv[1:]
    ...
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

- Separate **building the parser**, **doing the work** and **printing** so each is unit-testable.
- `main` *returns* a code; only the bottom of the file calls `sys.exit`.
- Errors and diagnostics go to **stderr**, results to **stdout**:
  `print("error: ...", file=sys.stderr)` so that `tool > out.txt` and pipes keep working.

To test output, use `contextlib.redirect_stdout(io.StringIO())` (or pytest's `capsys`).

## 4. Exit codes

| Code | Convention |
|---|---|
| `0` | success |
| `1` | generic failure |
| `2` | usage error (argparse uses this) |
| `130` | interrupted by Ctrl-C (128 + SIGINT 2) |

Shells and CI use the code: `tool && echo ok`. `sys.exit("message")` prints the message to
stderr and exits 1. Catch `KeyboardInterrupt` at the top level so Ctrl-C ends cleanly,
and let `SystemExit` pass through untouched.

## 5. Why `logging` and not `print`

`logging` gives severity levels, timestamps, destinations (console, file, network) and the ability
for a *user* of your library to turn the noise up or down — without changing your code.

```python
import logging

log = logging.getLogger(__name__)      # one logger per module, named after it

log.debug("details: %s", data)
log.info("started")
log.warning("disk at %d%%", 91)
log.error("could not open %s", path)
log.exception("failed")                 # error + traceback; only inside `except:`
log.critical("shutting down")
```

| Level | Number | When |
|---|---|---|
| `DEBUG` | 10 | diagnostic detail |
| `INFO` | 20 | normal milestones |
| `WARNING` | 30 | something unexpected, still working (the default threshold) |
| `ERROR` | 40 | an operation failed |
| `CRITICAL` | 50 | the program may not continue |

Pass values as **arguments** (`log.info("got %s", x)`), not an f-string: formatting is skipped if
the level is disabled, and tools can group identical messages.

## 6. Loggers, handlers, formatters

- A **Logger** has a name (`"app.db"`) and a level. Names form a hierarchy by dots; records
  **propagate** up to the parent loggers' handlers, ending at the root.
- A **Handler** decides where records go (`StreamHandler`, `FileHandler`, `RotatingFileHandler`)
  and has its own level.
- A **Formatter** decides how they look.

```python
handler = logging.StreamHandler()                                # stderr by default
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
```

A record is emitted only if it passes the logger's level **and** then each handler's level.
For a quick script: `logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")`.

Library code should only call `getLogger(__name__)` — **only the application** configures
handlers. A common CLI feature: `-v` / `-vv` flags (`action="count"`) mapping to `WARNING`, `INFO`,
`DEBUG`.

## 7. Testing logging

Write a tiny handler that stores records, attach it, and assert on levels and messages:

```python
class ListHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []
    def emit(self, record):
        self.records.append(record)
```

(pytest has `caplog` and the standard library has `unittest.TestCase.assertLogs`.)
Beware of leftover handlers: calling a setup function twice adds a second handler and
duplicates every line.

## Common mistakes

| Mistake | Fix |
|---|---|
| `sys.exit()` deep inside functions | Raise exceptions; convert to exit codes in one place |
| Parsing `sys.argv` by hand | `argparse` (or `typer`/`click` for bigger tools) |
| Reading `sys.argv` inside the parser builder | Accept `argv` as a parameter so tests can pass a list |
| Errors printed to stdout | `file=sys.stderr` |
| f-strings in log calls | `log.info("x=%s", x)` |
| `logging.info(...)` on the root logger in libraries | `logging.getLogger(__name__)` |
| Configuring handlers at import time in a library | Let the application do it |
| Duplicate log lines | Handlers added twice, or propagation to the root as well |
| Nothing shows up for `info()` | Default level is WARNING; set the level |
| `log.exception` outside an `except` block | Use `log.error(..., exc_info=True)` or call it within the handler |

## Practice

Build a greeter CLI and a calculator with sub-commands, wrap them in an exit-code-aware
`run_cli`, then configure loggers and write your own `ListHandler`. All tests call functions
with explicit argument lists, so nothing reads your real command line.

```
python check.py 2.07
```
