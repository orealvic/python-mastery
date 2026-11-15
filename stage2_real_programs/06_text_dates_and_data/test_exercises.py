import importlib
import json
import os
from datetime import date

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def test_extract_emails():
    assert ex.extract_emails("Mail ann@example.com or bob.smith+x@mail.co.uk.") == [
        "ann@example.com", "bob.smith+x@mail.co.uk"]
    assert ex.extract_emails("no emails here") == []
    assert ex.extract_emails("") == []
    assert ex.extract_emails("a@b.c,d@e.fg") == ["a@b.c", "d@e.fg"]
    assert ex.extract_emails("not@valid and @x.com") == []
    assert ex.extract_emails("<jo-e_1@my-site.org>") == ["jo-e_1@my-site.org"]


def test_parse_log_line():
    assert ex.parse_log_line("2024-03-15 10:30:45 [ERROR] disk full") == {
        "date": "2024-03-15", "time": "10:30:45", "level": "ERROR", "message": "disk full"}
    r = ex.parse_log_line("2024-01-01 00:00:00 [INFO] a [b] c: d")
    assert r["level"] == "INFO" and r["message"] == "a [b] c: d"
    assert ex.parse_log_line("garbage") is None
    assert ex.parse_log_line("") is None
    assert ex.parse_log_line("2024-03-15 10:30:45 [error] lower") is None
    assert ex.parse_log_line("2024-3-15 10:30:45 [INFO] short date") is None
    assert ex.parse_log_line("2024-03-15 10:30:45 [INFO] ")["message"] == ""


def test_days_between():
    assert ex.days_between("2024-02-28", "2024-03-01") == 2  # leap year
    assert ex.days_between("2023-02-28", "2023-03-01") == 1
    assert ex.days_between("2024-01-01", "2024-01-01") == 0
    assert ex.days_between("2024-03-01", "2024-02-28") == -2
    assert ex.days_between("2023-12-31", "2024-12-31") == 366
    assert raises(ValueError, ex.days_between, "2024-13-01", "2024-01-01")
    assert raises(ValueError, ex.days_between, "nope", "2024-01-01")


def test_add_business_days():
    f = ex.add_business_days
    assert f(date(2024, 3, 15), 1) == date(2024, 3, 18)  # Fri -> Mon
    assert f(date(2024, 3, 11), 4) == date(2024, 3, 15)  # Mon -> Fri
    assert f(date(2024, 3, 11), 5) == date(2024, 3, 18)
    assert f(date(2024, 3, 16), 1) == date(2024, 3, 18)  # Sat -> Mon
    assert f(date(2024, 3, 16), 0) == date(2024, 3, 16)
    assert f(date(2024, 3, 11), 10) == date(2024, 3, 25)
    assert raises(ValueError, f, date(2024, 3, 11), -1)


def test_to_utc_iso():
    f = ex.to_utc_iso
    assert f("2024-01-15 09:00", "America/New_York") == "2024-01-15T14:00:00+00:00"
    assert f("2024-07-15 09:00", "America/New_York") == "2024-07-15T13:00:00+00:00"  # DST
    assert f("2024-07-01 12:30:15", "Europe/Paris") == "2024-07-01T10:30:15+00:00"
    assert f("2024-01-01 00:00", "UTC") == "2024-01-01T00:00:00+00:00"
    assert f("2024-01-01 08:00", "Asia/Tokyo") == "2023-12-31T23:00:00+00:00"
    assert raises(Exception, f, "2024-01-01 08:00", "Not/AZone")


def test_list_py_files(tmp_path):
    (tmp_path / "pkg" / "sub").mkdir(parents=True)
    (tmp_path / ".venv" / "lib").mkdir(parents=True)
    (tmp_path / "pkg" / "__pycache__").mkdir()
    (tmp_path / "b.py").write_text("")
    (tmp_path / "a.py").write_text("")
    (tmp_path / "notes.txt").write_text("")
    (tmp_path / "pkg" / "__init__.py").write_text("")
    (tmp_path / "pkg" / "sub" / "deep.py").write_text("")
    (tmp_path / ".venv" / "lib" / "x.py").write_text("")
    (tmp_path / "pkg" / "__pycache__" / "c.py").write_text("")
    assert ex.list_py_files(tmp_path) == ["a.py", "b.py", "pkg/__init__.py", "pkg/sub/deep.py"]


def test_list_py_files_empty(tmp_path):
    assert ex.list_py_files(tmp_path) == []


def test_save_json(tmp_path):
    p = tmp_path / "out.json"
    ex.save_json(p, {"b": 1, "a": [1, 2], "name": "café"})
    text = p.read_text(encoding="utf-8")
    assert text == '{\n  "a": [\n    1,\n    2\n  ],\n  "b": 1,\n  "name": "café"\n}\n'
    assert json.loads(text) == {"a": [1, 2], "b": 1, "name": "café"}
    ex.save_json(p, [])
    assert p.read_text() == "[]\n"


def test_load_json_with_defaults(tmp_path):
    defaults = {"theme": "light", "size": 10}
    p = tmp_path / "settings.json"
    assert ex.load_json_with_defaults(p, defaults) == defaults
    result = ex.load_json_with_defaults(p, defaults)
    result["theme"] = "x"
    assert defaults["theme"] == "light"  # a copy was returned
    p.write_text('{"size": 12, "extra": true}')
    assert ex.load_json_with_defaults(p, defaults) == {"theme": "light", "size": 12, "extra": True}
    assert defaults == {"theme": "light", "size": 10}
    p.write_text("[1, 2]")
    assert raises(ValueError, ex.load_json_with_defaults, p, defaults)
    p.write_text("{not json")
    assert raises(ValueError, ex.load_json_with_defaults, p, defaults)


def test_write_csv(tmp_path):
    p = tmp_path / "out.csv"
    n = ex.write_csv(p, [{"name": "Ann", "age": 30}, {"name": "Bob, Jr.", "age": 5}], ["name", "age"])
    assert n == 2
    assert p.read_text(encoding="utf-8") == 'name,age\nAnn,30\n"Bob, Jr.",5\n'


def test_write_csv_edge_cases(tmp_path):
    p = tmp_path / "out.csv"
    assert ex.write_csv(p, [{"a": 1}], ["a", "b"]) == 1
    assert p.read_text() == "a,b\n1,\n"
    assert ex.write_csv(p, [], ["x", "y"]) == 0
    assert p.read_text() == "x,y\n"
    assert raises(ValueError, ex.write_csv, p, [{"zzz": 1}], ["a"])
    ex.write_csv(p, [{"t": "é"}], ["t"])
    assert p.read_bytes() == "t\né\n".encode("utf-8")


def test_sales_by_region(tmp_path):
    p = tmp_path / "sales.csv"
    p.write_text("region,units,price\nnorth,2,1.50\nnorth,1,2.00\nsouth,3,1.00\n")
    assert ex.sales_by_region(p) == {"north": 5.0, "south": 3.0}
    p.write_text("region,units,price\neast,3,0.10\neast,3,0.10\n")
    assert ex.sales_by_region(p) == {"east": 0.6}  # 0.30000000000000004 * 2 must be rounded
    p.write_text("region,units,price\n")
    assert ex.sales_by_region(p) == {}
