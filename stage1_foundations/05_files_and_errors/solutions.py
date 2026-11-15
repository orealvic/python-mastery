"""Reference solutions for 1.05. Try the exercises yourself first!"""
import json
from pathlib import Path


def safe_int(text: str, default: int | None = None) -> int | None:
    try:
        return int(text)
    except ValueError:
        return default


def parse_age(text: str) -> int:
    age = int(text)  # raises ValueError for non-integers
    if not 0 <= age <= 150:
        raise ValueError(f"age out of range: {age}")
    return age


def write_lines(path, lines: list[str]) -> int:
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
    return len(lines)


def read_lines(path) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def append_log(path, message: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def count_words_in_file(path) -> int:
    try:
        with open(path, encoding="utf-8") as f:
            return len(f.read().split())
    except FileNotFoundError:
        return 0


def save_json(path, data) -> None:
    text = json.dumps(data, indent=2)  # serialize first: don't truncate the file on error
    Path(path).write_text(text + "\n", encoding="utf-8")


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def read_config(path) -> dict[str, str]:
    config: dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if not sep:
                raise ValueError(f"invalid config line: {line!r}")
            config[key.strip()] = value.strip()
    return config


def sum_ints_in_file(path) -> tuple[int, int]:
    total = bad = 0
    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue
            try:
                total += int(line)
            except ValueError:
                bad += 1
    return total, bad


def divide_with_log(a, b, log: list[str]):
    try:
        result = a / b
    except ZeroDivisionError:
        log.append("zero")
        return None
    else:
        log.append("ok")
        return result
    finally:
        log.append("done")
