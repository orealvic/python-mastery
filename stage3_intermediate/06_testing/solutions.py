"""Reference solutions for 3.06. Try the exercises yourself first!"""
import functools
import random
import re
import time
from collections.abc import Callable
from datetime import datetime


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def greeting(now: Callable[[], datetime] = datetime.now) -> str:
    hour = now().hour
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def roll_dice(count: int, rng: random.Random | None = None) -> list[int]:
    if count < 0:
        raise ValueError("count must be >= 0")
    rng = rng or random.Random()
    return [rng.randint(1, 6) for _ in range(count)]


def fetch_with_retry(fetch: Callable[[], object], retries: int = 3,
                     delay: float = 1.0,
                     sleep: Callable[[float], None] = time.sleep):
    for attempt in range(retries + 1):
        try:
            return fetch()
        except Exception:
            if attempt == retries:
                raise
            sleep(delay * 2 ** attempt)


def calls_summary(mock, name: str = "mock") -> list[str]:
    summaries = []
    for c in mock.call_args_list:
        parts = [repr(a) for a in c.args]
        parts += [f"{k}={v!r}" for k, v in c.kwargs.items()]
        summaries.append(f"{name}({', '.join(parts)})")
    return summaries


class FakeUserRepository:
    def __init__(self) -> None:
        self._users: dict[int, dict] = {}
        self.calls: list[tuple[str]] = []

    def save(self, user: dict) -> dict:
        self.calls.append(("save",))
        stored = dict(user)
        if "id" not in stored:
            stored["id"] = max(self._users, default=0) + 1
        self._users[stored["id"]] = stored
        return dict(stored)

    def get(self, user_id: int) -> dict | None:
        self.calls.append(("get",))
        user = self._users.get(user_id)
        return dict(user) if user is not None else None

    def delete(self, user_id: int) -> bool:
        self.calls.append(("delete",))
        return self._users.pop(user_id, None) is not None

    def all(self) -> list[dict]:
        self.calls.append(("all",))
        return [dict(self._users[k]) for k in sorted(self._users)]


def register_user(name: str, email: str, repo, mailer) -> dict:
    name = name.strip()
    if not name or "@" not in email:
        raise ValueError("invalid name or email")
    saved = repo.save({"name": name, "email": email})
    mailer.send(to=email, subject=f"Welcome, {name}!")
    return saved


def make_spy(func: Callable) -> Callable:
    @functools.wraps(func)
    def spy(*args, **kwargs):
        spy.calls.append((args, kwargs))
        spy.call_count += 1
        result = func(*args, **kwargs)
        spy.results.append(result)
        return result

    spy.calls = []
    spy.results = []
    spy.call_count = 0
    return spy


def parametrize(argnames: str, argvalues: list):
    names = [n.strip() for n in argnames.split(",")]

    def decorator(func):
        @functools.wraps(func)
        def runner():
            failures = []
            for i, case in enumerate(argvalues):
                values = [case] if len(names) == 1 else list(case)
                params = dict(zip(names, values, strict=True))
                try:
                    func(**params)
                except Exception as exc:
                    failures.append(f"case {i}: {params!r} -> {type(exc).__name__}: {exc}")
            if failures:
                raise AssertionError("\n".join(failures))

        runner.case_count = len(argvalues)
        return runner

    return decorator
