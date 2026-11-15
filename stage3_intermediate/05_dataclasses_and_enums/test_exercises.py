import dataclasses
import importlib
import os
from enum import Enum, IntEnum, StrEnum

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_point_frozen_ordered_hashable():
    p = ex.Point(1, 2)
    assert dataclasses.is_dataclass(p)
    assert repr(p) == "Point(x=1, y=2)"
    assert p == ex.Point(1, 2)
    assert hash(p) == hash(ex.Point(1, 2))
    assert len({p, ex.Point(1, 2), ex.Point(2, 1)}) == 2
    assert sorted([ex.Point(2, 1), ex.Point(1, 5), ex.Point(1, 3)]) == [
        ex.Point(1, 3), ex.Point(1, 5), ex.Point(2, 1)]
    try:
        p.x = 10
        assert False, "should be frozen"
    except dataclasses.FrozenInstanceError:
        pass


def test_point_distance():
    assert ex.Point(0, 0).distance_to(ex.Point(3, 4)) == 5.0
    assert ex.Point(1, 1).distance_to(ex.Point(1, 1)) == 0.0


def test_product():
    p = ex.Product("  Pen ", 1.5)
    assert p.name == "Pen"
    assert repr(p) == "Product(name='Pen', price=1.5, tags=[])"
    a, b = ex.Product("a", 1), ex.Product("b", 2)
    a.tags.append("x")
    assert b.tags == []  # default_factory, not shared
    assert ex.Product("a", 1, ["t"]).tags == ["t"]
    assert ex.Product("a", 1) == ex.Product("a", 1)


def test_product_validation():
    for args in [("   ", 1), ("", 1), ("x", -0.01)]:
        try:
            ex.Product(*args)
            assert False, f"expected ValueError for {args}"
        except ValueError:
            pass
    assert ex.Product("free", 0).price == 0


def test_server_config():
    c = ex.ServerConfig(host="localhost")
    assert (c.host, c.port, c.debug) == ("localhost", 8080, False)
    assert repr(c) == "ServerConfig(host='localhost', port=8080, debug=False)"
    assert ex.ServerConfig(host="h", port=1, debug=True).debug is True
    try:
        ex.ServerConfig("localhost")
        assert False, "should be keyword-only"
    except TypeError:
        pass


def test_server_config_slots_and_validation():
    c = ex.ServerConfig(host="h")
    assert not hasattr(c, "__dict__")
    try:
        c.nope = 1
        assert False, "slots should block new attributes"
    except AttributeError:
        pass
    for bad in (0, 65536, -1):
        try:
            ex.ServerConfig(host="h", port=bad)
            assert False, f"port {bad} should fail"
        except ValueError:
            pass
    assert ex.ServerConfig(host="h", port=65535).port == 65535


def test_rectangle():
    r = ex.Rectangle(2, 3)
    assert r.area == 6
    assert repr(r) == "Rectangle(width=2, height=3)"
    assert r == ex.Rectangle(2, 3)
    names = [f.name for f in dataclasses.fields(r)]
    assert names == ["width", "height", "area"]
    init_field = [f for f in dataclasses.fields(r) if f.name == "area"][0]
    assert init_field.init is False
    for bad in [(0, 1), (1, -2)]:
        try:
            ex.Rectangle(*bad)
            assert False, "expected ValueError"
        except ValueError:
            pass


def test_with_changes():
    p = ex.Point(1, 2)
    q = ex.with_changes(p, y=9)
    assert q == ex.Point(1, 9)
    assert p == ex.Point(1, 2)
    assert q is not p
    try:
        ex.with_changes({"x": 1}, x=2)
        assert False, "expected TypeError"
    except TypeError:
        pass
    try:
        ex.with_changes(ex.Point, x=2)
        assert False, "expected TypeError"
    except TypeError:
        pass


def test_non_default_fields():
    c = ex.ServerConfig(host="h", port=9000)
    assert ex.non_default_fields(c) == {"host": "h", "port": 9000}
    assert ex.non_default_fields(ex.ServerConfig(host="h")) == {"host": "h"}
    p = ex.Product("pen", 2.0, ["a"])
    assert ex.non_default_fields(p) == {"name": "pen", "price": 2.0, "tags": ["a"]}
    assert ex.non_default_fields(ex.Product("pen", 2.0)) == {"name": "pen", "price": 2.0}


def test_is_weekend():
    assert ex.is_weekend(ex.Weekday.SATURDAY) is True
    assert ex.is_weekend(ex.Weekday.SUNDAY) is True
    assert ex.is_weekend(ex.Weekday.MONDAY) is False
    assert ex.is_weekend(ex.Weekday.FRIDAY) is False


def test_parse_weekday():
    assert ex.parse_weekday("friday") is ex.Weekday.FRIDAY
    assert ex.parse_weekday("  SUNDAY ") is ex.Weekday.SUNDAY
    assert ex.parse_weekday("3") is ex.Weekday.WEDNESDAY
    for bad in ["funday", "", "8", "0"]:
        try:
            ex.parse_weekday(bad)
            assert False, f"expected ValueError for {bad!r}"
        except ValueError:
            pass


def test_describe_permissions():
    P = ex.Permission
    assert ex.describe_permissions(P.READ | P.EXECUTE) == "READ|EXECUTE"
    assert ex.describe_permissions(P.WRITE) == "WRITE"
    assert ex.describe_permissions(P(0)) == "NONE"
    assert ex.describe_permissions(P.READ | P.WRITE | P.EXECUTE) == "READ|WRITE|EXECUTE"


def test_make_level_enum():
    Level = ex.make_level_enum()
    assert issubclass(Level, StrEnum)
    assert Level.__name__ == "Level"
    assert [m.name for m in Level] == ["LOW", "MEDIUM", "HIGH"]
    assert Level.LOW == "low" and Level.HIGH.value == "high"
    assert Level("medium") is Level.MEDIUM
    assert isinstance(Level.LOW, str)


def test_make_priority_enum():
    Priority = ex.make_priority_enum()
    assert issubclass(Priority, IntEnum)
    assert Priority.__name__ == "Priority"
    assert [(m.name, m.value) for m in Priority] == [("LOW", 1), ("MEDIUM", 2), ("HIGH", 3)]
    assert Priority.HIGH > Priority.LOW
    assert sorted([Priority.HIGH, Priority.LOW, Priority.MEDIUM])[0] is Priority.LOW
