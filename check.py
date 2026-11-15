#!/usr/bin/env python3
"""Zero-dependency exercise checker for the Python Mastery course.

Usage:
    python check.py                       # list all modules and your progress
    python check.py 1.03                  # check stage 1, module 03
    python check.py stage1_foundations/03_data_structures
    python check.py 1.03 --solutions      # run the tests against the reference solutions
    python check.py --all                 # check every module
    python check.py --all --solutions     # verify the whole course (for maintainers)

Each module directory contains:
    lesson.md          - read this first
    exercises.py       - YOUR work goes here (stubs raise NotImplementedError)
    test_exercises.py  - the tests (also runnable with pytest once you install it)
    solutions.py       - reference solutions; peek only after a real attempt
"""
from __future__ import annotations

import asyncio
import importlib.util
import inspect
import os
import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GREEN, RED, YELLOW, DIM, BOLD, RESET = (
    ("\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m")
    if sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
    else ("",) * 6
)


def all_modules() -> list[Path]:
    return sorted(p.parent for p in ROOT.glob("stage*/*/test_exercises.py"))


def resolve(spec: str) -> Path:
    """Accept '1.03', '1.3', or a path to a module directory."""
    path = (ROOT / spec).resolve()
    if path.is_dir() and (path / "test_exercises.py").exists():
        return path
    if "." in spec:
        stage, mod = spec.split(".", 1)
        stage_dirs = sorted(ROOT.glob(f"stage{int(stage)}_*"))
        if stage_dirs:
            for m in sorted(stage_dirs[0].glob("*/")):
                if m.name.split("_", 1)[0].lstrip("0") == mod.lstrip("0"):
                    return m
    sys.exit(f"Could not find module '{spec}'. Run `python check.py` to list modules.")


class _TmpPath:
    """Minimal stand-in for pytest's tmp_path fixture."""

    def __enter__(self) -> Path:
        self._d = tempfile.TemporaryDirectory()
        return Path(self._d.name)

    def __exit__(self, *exc):
        self._d.cleanup()


def run_module(module_dir: Path, target: str, quiet: bool = False) -> tuple[int, int, int]:
    """Run test_exercises.py in module_dir against `target` (exercises|solutions).

    Returns (passed, failed, not_started).
    """
    os.environ["PM_TARGET"] = target
    sys.path.insert(0, str(module_dir))
    # Make sure each module gets fresh imports of its own exercises/solutions.
    for name in ("exercises", "solutions", "test_exercises"):
        sys.modules.pop(name, None)
    try:
        spec = importlib.util.spec_from_file_location("test_exercises", module_dir / "test_exercises.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception:
        print(f"{RED}Could not import tests/{target} for {module_dir.name}:{RESET}")
        traceback.print_exc()
        sys.path.remove(str(module_dir))
        return (0, 1, 0)

    tests = [(n, f) for n, f in vars(mod).items() if n.startswith("test_") and callable(f)]
    passed = failed = todo = 0
    for name, fn in tests:
        params = inspect.signature(fn).parameters
        try:
            if "tmp_path" in params:
                with _TmpPath() as tmp:
                    result = fn(tmp_path=tmp)
            else:
                result = fn()
            if inspect.iscoroutine(result):
                asyncio.run(result)
            passed += 1
            if not quiet:
                print(f"  {GREEN}PASS{RESET} {name}")
        except NotImplementedError:
            todo += 1
            if not quiet:
                print(f"  {YELLOW}TODO{RESET} {name}")
        except Exception as e:
            failed += 1
            if not quiet:
                print(f"  {RED}FAIL{RESET} {name}")
                tb = traceback.extract_tb(e.__traceback__)
                where = next((f for f in reversed(tb) if "check.py" not in f.filename), tb[-1])
                print(f"       {DIM}{Path(where.filename).name}:{where.lineno}{RESET}  {where.line}")
                print(f"       {type(e).__name__}: {e}" if str(e) else f"       {type(e).__name__}")
    sys.path.remove(str(module_dir))
    return passed, failed, todo


def label(module_dir: Path) -> str:
    return f"{module_dir.parent.name}/{module_dir.name}"


def main(argv: list[str]) -> int:
    target = "solutions" if "--solutions" in argv else "exercises"
    args = [a for a in argv if not a.startswith("--")]

    if "--all" in argv or not args:
        listing = not args and "--all" not in argv
        if listing:
            print(f"{BOLD}Python Mastery - progress ({target}){RESET}\n")
        total_fail = 0
        current_stage = None
        for m in all_modules():
            if m.parent.name != current_stage:
                current_stage = m.parent.name
                print(f"\n{BOLD}{current_stage}{RESET}")
            p, f, t = run_module(m, target, quiet=True)
            total = p + f + t
            total_fail += f + t
            mark = f"{GREEN}DONE{RESET}" if p == total else (f"{YELLOW}....{RESET}" if p else f"{DIM}----{RESET}")
            stage_num = int(m.parent.name[5])
            print(f"  [{mark}] {stage_num}.{m.name[:2]}  {m.name[3:]:<32} {p}/{total}")
        if listing:
            print(f"\nRun `python check.py <stage>.<module>` (e.g. `python check.py 1.01`) to see details.")
        return 1 if total_fail and target == "solutions" else 0

    module_dir = resolve(args[0])
    print(f"{BOLD}{label(module_dir)}{RESET}  {DIM}(testing {target}.py){RESET}")
    p, f, t = run_module(module_dir, target)
    total = p + f + t
    print()
    if p == total:
        print(f"{GREEN}{BOLD}All {total} tests passed!{RESET} On to the next module.")
        return 0
    print(f"{p}/{total} passed, {RED}{f} failing{RESET}, {YELLOW}{t} not started{RESET}.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
