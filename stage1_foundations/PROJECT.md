# Stage 1 Capstone — Command-Line To-Do App

Build a small command-line task manager that saves its tasks to a JSON file. It pulls together
everything from Stage 1: variables and strings, control flow, lists/dicts, functions, file I/O,
JSON, and error handling.

Create your own folder (for example `stage1_foundations/todo/`) with a single file `todo.py` to
start. Standard library only.

## Example session

```text
$ python todo.py add "Buy milk"
Added task 1: Buy milk
$ python todo.py add "Write Stage 1 project" --priority high
Added task 2: Write Stage 1 project
$ python todo.py list
[ ]  1  Buy milk
[ ]  2  Write Stage 1 project  (high)
$ python todo.py done 1
Completed task 1: Buy milk
$ python todo.py list --all
[x]  1  Buy milk
[ ]  2  Write Stage 1 project  (high)
$ python todo.py remove 2
Removed task 2: Write Stage 1 project
$ python todo.py done 99
Error: no task with id 99
```

(The exact output format is up to you; the behavior is what matters.)

## Requirements

### Commands
1. `add <title> [--priority low|normal|high]` — create a task (default priority `normal`).
2. `list [--all]` — show open tasks; with `--all`, include completed ones. Say something friendly
   when there is nothing to show.
3. `done <id>` — mark a task complete.
4. `remove <id>` — delete a task.

### Data and storage
- Each task is a dict with at least: `id` (int), `title` (str), `done` (bool), `priority` (str).
- IDs are unique and never reused within a file, even after removals (hint: store the next id, or
  use `max(existing ids) + 1`, and think about which is safer).
- Tasks live in a JSON file (default `tasks.json` in the current directory). The file should be
  human-readable (use `indent`).
- A missing file means "no tasks yet", not a crash.

### Robustness
- Empty or whitespace-only titles are rejected with a clear message.
- Unknown ids, non-numeric ids, unknown commands, and bad priorities give a one-line error message
  and a non-zero exit code (`sys.exit(1)`), never a traceback.
- A corrupt JSON file is reported clearly and is **not** overwritten silently.
- Saving must not lose data if something goes wrong halfway (e.g. serialize to a string first, then write).

### Code quality
- Separate *logic* from *I/O*: write small functions such as `load_tasks(path)`,
  `save_tasks(path, tasks)`, `add_task(tasks, title, priority)`, `complete_task(tasks, task_id)`,
  `format_task(task)`. Functions that manipulate the list of tasks should not print or touch files,
  so they are easy to test.
- Every function has a docstring and, ideally, type hints.
- Use `if __name__ == "__main__":` to call a `main()` function.
- Parse arguments with the standard library `argparse` (look up `add_subparsers`), or with
  `sys.argv` by hand if you want extra practice first.

## Suggested milestones

1. **Data model on paper.** Decide the task dict and what a file with two tasks looks like. Write
   it out by hand as JSON.
2. **Pure functions.** Implement `add_task`, `complete_task`, `remove_task`, `format_task` operating
   on a list of dicts. Try them in the REPL.
3. **Persistence.** Implement `load_tasks` and `save_tasks` with `pathlib` and `json`. Handle a
   missing file (EAFP) and a corrupt file.
4. **CLI wiring.** Add `main()`: parse the arguments, call your functions, print results.
5. **Error handling pass.** Replace every possible traceback with a friendly error. Use your own
   exceptions or `ValueError` inside the logic, and catch them once in `main()`.
6. **Tests.** Write a `test_todo.py` using bare `assert` functions (the same style as the course
   tests). Test the pure functions and use a temporary directory for file tests.
7. **Polish.** Read your code top to bottom as if someone else wrote it. See the checklist below.

## Stretch goals
- `edit <id> <new title>` and `priority <id> <level>` commands.
- Optional due dates (`--due 2026-12-31`) using `datetime.date.fromisoformat`; show overdue tasks
  first or flagged.
- Sort `list` output by priority, then id.
- `list --search <text>` for case-insensitive title filtering.
- `clear-done` to delete all completed tasks.
- Tags (`--tag work`) stored as a list on each task, plus `list --tag work`.
- A `--file PATH` option and/or a `TODO_FILE` environment variable (`os.environ.get`).
- Atomic saves: write to a temporary file in the same folder, then `Path.replace()` it over the
  real file.
- Colored output using ANSI escape codes, disabled when output is not a terminal
  (`sys.stdout.isatty()`).

## Self-review checklist

Behavior
- [ ] Every command works on a brand-new (missing) tasks file.
- [ ] Adding, completing, and removing persist across separate runs of the program.
- [ ] Ids are never reused after a removal.
- [ ] Bad input (blank title, id `abc`, id `999`, bad priority) produces a clean error and exit code 1.
- [ ] A corrupt `tasks.json` does not crash with a traceback and is not wiped.

Code
- [ ] No function does more than one job; logic functions do not call `print` or `open`.
- [ ] No mutable default arguments, no bare `except:`, no `except Exception: pass`.
- [ ] Files are opened with `with` and `encoding="utf-8"`.
- [ ] Names are descriptive; no leftover debug prints or commented-out code.
- [ ] Every function has a docstring; type hints on public functions.
- [ ] There are no magic strings repeated in many places (e.g. priorities are defined once).

Testing
- [ ] Tests cover the happy path and at least three failure cases.
- [ ] File-based tests use a temporary directory and never touch real data.
- [ ] You can explain, line by line, what your `main()` does.

When all of the boxes are ticked, you have completed Stage 1.
