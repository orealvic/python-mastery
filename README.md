# Python Mastery

A hands-on course that takes you from first steps in Python to advanced, professional-level work.
Every module has a **lesson**, a set of **exercises**, **automated tests** that check your work, and **reference solutions**.
Each stage ends with a **capstone project**.

## Quick start

```bash
cd python-mastery
python3 check.py          # see all modules and your progress
python3 check.py 1.01     # test your work on Stage 1, Module 01
```

You don't need to install anything. The checker uses only the standard library and needs Python 3.13 or newer (3.14 is recommended).
Once you reach Stage 3 you'll install `pytest`, and the same test files will run under it too.
Run it from inside a module directory: `cd stage3_intermediate/01_iterators_and_generators && python -m pytest`.

## How to work through a module

1. **Read** `lesson.md`. Type the examples into the REPL (`python3`). Don't just read them.
2. **Implement** the stubs in `exercises.py`. Each docstring is the specification.
3. **Check** your work with `python3 check.py <stage>.<module>`. Results show `PASS`, `FAIL` (with the failing line) or `TODO`.
4. **Compare** your code with `solutions.py` **only after** all tests pass, or after you've been stuck for 30 minutes or more. Look for idioms you didn't know.
5. **Commit** your progress with git. Start this habit on day one.

> Tip: `python3 check.py 1.01 --solutions` runs the tests against the reference solution, which shows you what passing looks like.

## Curriculum

| Stage | Focus | Time* | Capstone |
|---|---|---|---|
| **1 · Foundations** — `stage1_foundations/` | syntax, control flow, data structures, functions, files and errors | 3–4 wks | CLI to-do app with JSON storage |
| **2 · Real Programs** — `stage2_real_programs/` | comprehensions, modules and tooling, OOP, dunder methods, stdlib, CLI and logging | 4–6 wks | API client or scraper that produces a CSV/SQLite report |
| **3 · Intermediate** — `stage3_intermediate/` | generators, decorators, context managers, type hints, dataclasses, testing, pattern matching | 6–8 wks | Installable, typed, tested package |
| **4 · Advanced Internals** — `stage4_advanced/` | descriptors, metaclasses, memory, threads and processes, asyncio, performance, bytecode and AST | 6–8 wks | Profiled async crawler |
| **5 · Specialize** — `stage5_specialize/` | choose a track: web, data, ML/AI, automation, scientific | ongoing | Track capstone |
| **6 · Mastery** — `stage6_mastery/` | read great code, contribute to open source, design, packaging, teaching | ongoing | Published package and an OSS contribution |

*At roughly 1–2 hours a day.

## Weekly rhythm (suggested)

| Day | Activity |
|---|---|
| Mon–Thu | One module, or half of one: lesson, then exercises |
| Fri | Re-do yesterday's hardest exercise from scratch without looking |
| Sat | Work on the stage capstone project |
| Sun | Rest, or do 2–3 [Exercism](https://exercism.org/tracks/python) or [Advent of Code](https://adventofcode.com) puzzles |

## Rules that make this work

- **Code more than you read.** Aim for 70% writing code and 30% reading.
- **Read the whole traceback** before you search for help.
- **Don't skip the capstones.** The modules teach you the parts; the projects teach you how to put them together.
- **Revisit old code** every couple of months and refactor it with what you've learned since.
