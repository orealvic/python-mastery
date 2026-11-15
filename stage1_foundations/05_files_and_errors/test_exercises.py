import importlib
import json
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def test_safe_int():
    assert ex.safe_int("42") == 42
    assert ex.safe_int(" -7 ") == -7
    assert ex.safe_int("4x2", default=-1) == -1
    assert ex.safe_int("abc") is None
    assert ex.safe_int("") is None
    assert ex.safe_int("3.5", default=0) == 0


def test_parse_age():
    assert ex.parse_age("30") == 30
    assert ex.parse_age("0") == 0
    assert ex.parse_age("150") == 150
    assert raises(ValueError, ex.parse_age, "abc")
    assert raises(ValueError, ex.parse_age, "")
    assert raises(ValueError, ex.parse_age, "-1")
    assert raises(ValueError, ex.parse_age, "151")


def test_write_lines(tmp_path):
    p = tmp_path / "out.txt"
    assert ex.write_lines(p, ["a", "b"]) == 2
    assert p.read_text(encoding="utf-8") == "a\nb\n"
    assert ex.write_lines(str(p), ["only"]) == 1  # replaces content, accepts str
    assert p.read_text(encoding="utf-8") == "only\n"
    assert ex.write_lines(p, []) == 0
    assert p.read_text(encoding="utf-8") == ""


def test_read_lines(tmp_path):
    p = tmp_path / "in.txt"
    p.write_text("a\n\nb\n", encoding="utf-8")
    assert ex.read_lines(p) == ["a", "", "b"]
    p.write_text("no newline at end", encoding="utf-8")
    assert ex.read_lines(str(p)) == ["no newline at end"]
    p.write_text("", encoding="utf-8")
    assert ex.read_lines(p) == []
    assert raises(FileNotFoundError, ex.read_lines, tmp_path / "missing.txt")


def test_append_log(tmp_path):
    p = tmp_path / "log.txt"
    assert ex.append_log(p, "started") is None
    ex.append_log(p, "stopped")
    assert p.read_text(encoding="utf-8") == "started\nstopped\n"
    p2 = tmp_path / "pre.txt"
    p2.write_text("existing\n", encoding="utf-8")
    ex.append_log(p2, "more")
    assert p2.read_text(encoding="utf-8") == "existing\nmore\n"


def test_count_words_in_file(tmp_path):
    p = tmp_path / "words.txt"
    p.write_text("one two\n  three\n\nfour  five\n", encoding="utf-8")
    assert ex.count_words_in_file(p) == 5
    p.write_text("", encoding="utf-8")
    assert ex.count_words_in_file(p) == 0
    assert ex.count_words_in_file(tmp_path / "missing.txt") == 0


def test_save_json(tmp_path):
    p = tmp_path / "data.json"
    data = {"name": "Ada", "langs": ["python", "c"], "n": 3, "ok": True, "x": None}
    assert ex.save_json(p, data) is None
    assert json.loads(p.read_text(encoding="utf-8")) == data
    assert "\n" in p.read_text(encoding="utf-8")  # pretty-printed
    ex.save_json(str(p), [1, 2])
    assert json.loads(p.read_text(encoding="utf-8")) == [1, 2]
    assert raises(TypeError, ex.save_json, tmp_path / "bad.json", {"s": {1, 2}})


def test_load_json(tmp_path):
    p = tmp_path / "data.json"
    p.write_text('{"a": [1, 2, {"b": null}]}', encoding="utf-8")
    assert ex.load_json(p) == {"a": [1, 2, {"b": None}]}
    assert ex.load_json(tmp_path / "missing.json") is None
    assert ex.load_json(tmp_path / "missing.json", default=[]) == []
    p.write_text("{not json", encoding="utf-8")
    assert raises(ValueError, ex.load_json, p)


def test_json_roundtrip(tmp_path):
    p = tmp_path / "rt.json"
    tasks = [{"id": 1, "title": "write tests", "done": False}]
    ex.save_json(p, tasks)
    assert ex.load_json(p) == tasks


def test_read_config(tmp_path):
    p = tmp_path / "app.cfg"
    p.write_text(
        "host = localhost\n"
        "# a comment\n"
        "\n"
        "   \n"
        "  # indented comment\n"
        "url=a=b\n"
        "port=80\n"
        "port = 8080\n"
        "empty=\n",
        encoding="utf-8",
    )
    assert ex.read_config(p) == {
        "host": "localhost",
        "url": "a=b",
        "port": "8080",
        "empty": "",
    }
    p.write_text("", encoding="utf-8")
    assert ex.read_config(p) == {}


def test_read_config_bad_line(tmp_path):
    p = tmp_path / "bad.cfg"
    p.write_text("ok=1\nthis is wrong\n", encoding="utf-8")
    assert raises(ValueError, ex.read_config, p)


def test_sum_ints_in_file(tmp_path):
    p = tmp_path / "nums.txt"
    p.write_text("1\n2\nx\n\n4\n", encoding="utf-8")
    assert ex.sum_ints_in_file(p) == (7, 1)
    p.write_text("", encoding="utf-8")
    assert ex.sum_ints_in_file(p) == (0, 0)
    p.write_text(" 5 \n-3\n1.5\nabc\n", encoding="utf-8")
    assert ex.sum_ints_in_file(p) == (2, 2)


def test_divide_with_log():
    log = []
    assert ex.divide_with_log(6, 3, log) == 2.0
    assert log == ["ok", "done"]
    log = []
    assert ex.divide_with_log(1, 0, log) is None
    assert log == ["zero", "done"]


def test_divide_with_log_other_errors_propagate():
    log = []
    try:
        ex.divide_with_log("a", 2, log)
    except TypeError:
        pass
    else:
        raise AssertionError("TypeError should propagate")
    assert log == ["done"]
