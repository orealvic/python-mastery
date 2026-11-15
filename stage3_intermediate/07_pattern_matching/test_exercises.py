import importlib
import math
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_classify_literals_and_types():
    c = ex.classify
    assert c(None) == "none"
    assert c(True) == "bool" and c(False) == "bool"
    assert c(0) == "zero" and c(0.0) == "zero"
    assert c(7) == "int" and c(-3) == "int"
    assert c(2.5) == "float"
    assert c("") == "empty string"
    assert c("hi") == "string"


def test_classify_containers():
    c = ex.classify
    assert c([]) == "empty sequence" and c(()) == "empty sequence"
    assert c([1]) == "sequence" and c((1, 2)) == "sequence"
    assert c({}) == "dict" and c({"a": 1}) == "dict"
    assert c(b"x") == "other" and c(set()) == "other"


def test_parse_command_simple():
    p = ex.parse_command
    assert p("") == ("noop",)
    assert p("   ") == ("noop",)
    assert p("quit") == ("quit",)
    assert p("exit") == ("quit",)
    assert p("go north") == ("move", "north")
    assert p("  go   west ") == ("move", "west")


def test_parse_command_variadic():
    p = ex.parse_command
    assert p("take lamp") == ("take", ["lamp"])
    assert p("take lamp  sword") == ("take", ["lamp", "sword"])
    assert p("say hello   there world") == ("say", "hello there world")


def test_parse_command_unknown():
    p = ex.parse_command
    assert p("go up") == ("unknown", "go up")
    assert p("go") == ("unknown", "go")
    assert p("take") == ("unknown", "take")
    assert p("say") == ("unknown", "say")
    assert p("quit now") == ("unknown", "quit now")
    assert p("dance now") == ("unknown", "dance now")


def test_summarize_seq():
    s = ex.summarize_seq
    assert s([]) == ("empty",)
    assert s(()) == ("empty",)
    assert s([9]) == ("one", 9)
    assert s((1, 2)) == ("pair", 1, 2)
    assert s([1, 2, 3]) == ("many", 1, 3, 1)
    assert s([1, 2, 3, 4, 5]) == ("many", 1, 5, 3)
    assert s("abc") == ("not a sequence",)
    assert s(42) == ("not a sequence",)
    assert s({"a": 1}) == ("not a sequence",)


def test_area():
    assert ex.area(ex.Rect(3, 4)) == 12
    assert ex.area(ex.Triangle(6, 5)) == 15
    assert abs(ex.area(ex.Circle(2)) - 4 * math.pi) < 1e-9


def test_area_unknown_type():
    for bad in (42, "circle", None, (1, 2)):
        try:
            ex.area(bad)
        except TypeError:
            pass
        else:
            assert False, f"expected TypeError for {bad!r}"


def test_shape_name():
    n = ex.shape_name
    assert n(ex.Circle(1)) == "circle"
    assert n(ex.Rect(2, 2)) == "square"
    assert n(ex.Rect(2, 3)) == "rectangle"
    assert n(ex.Triangle(1, 1)) == "triangle"
    assert n("blob") == "unknown"


def test_handle_event_click():
    h = ex.handle_event
    assert h({"type": "click", "pos": (3, 4)}) == "click at 3,4"
    assert h({"type": "click", "pos": [3, 4], "button": 1}) == "click at 3,4"
    assert h({"type": "click", "pos": [1, 2, 3]}) == "ignored"
    assert h({"type": "click"}) == "ignored"


def test_handle_event_key():
    h = ex.handle_event
    assert h({"type": "key", "key": "k"}) == "key k"
    assert h({"type": "key", "key": "k", "mods": []}) == "key k"
    assert h({"type": "key", "key": "k", "mods": ["ctrl"]}) == "ctrl+k"
    assert h({"type": "key", "key": "k", "mods": ["ctrl", "shift"]}) == "ctrl+shift+k"


def test_handle_event_error_and_other():
    h = ex.handle_event
    assert h({"type": "error"}) == "error with 0 detail(s)"
    assert h({"type": "error", "code": 500}) == "error with 1 detail(s)"
    assert h({"type": "error", "code": 500, "msg": "boom"}) == "error with 2 detail(s)"
    assert h({"type": "scroll"}) == "ignored"
    assert h("click") == "ignored"
    assert h(None) == "ignored"
    assert h([("type", "click")]) == "ignored"


def test_parse_config_valid():
    p = ex.parse_config
    assert p({"mode": "tcp", "host": "localhost", "port": 8080}) == ("tcp", "localhost", 8080)
    assert p({"mode": "tcp", "host": "h", "port": 65535, "x": 1}) == ("tcp", "h", 65535)
    assert p({"mode": "unix", "path": "/tmp/s.sock", "debug": True}) == ("unix", "/tmp/s.sock")


def test_parse_config_invalid():
    bad = [
        {"mode": "tcp", "host": "h", "port": 0},
        {"mode": "tcp", "host": "h", "port": 65536},
        {"mode": "tcp", "host": "h", "port": "80"},
        {"mode": "tcp", "host": "h"},
        {"mode": "tcp", "port": 80},
        {"mode": "tcp", "host": 5, "port": 80},
        {"mode": "unix"},
        {"mode": "unix", "path": 3},
        {"mode": "udp", "host": "h", "port": 1},
        {},
        [],
        None,
        "tcp",
    ]
    for cfg in bad:
        try:
            ex.parse_config(cfg)
        except ValueError:
            pass
        else:
            assert False, f"expected ValueError for {cfg!r}"


def test_evaluate():
    e = ex.evaluate
    assert e(ex.Num(3)) == 3
    assert e(ex.Neg(ex.Num(5))) == -5
    tree = ex.Add(ex.Num(1), ex.Mul(ex.Num(2), ex.Var("x")))
    assert e(tree, {"x": 10}) == 21
    assert e(ex.Mul(ex.Add(ex.Num(1), ex.Num(2)), ex.Neg(ex.Var("y"))), {"y": 4}) == -12


def test_evaluate_errors():
    try:
        ex.evaluate(ex.Var("missing"), {"x": 1})
    except KeyError:
        pass
    else:
        assert False, "expected KeyError"
    try:
        ex.evaluate(ex.Var("x"))
    except KeyError:
        pass
    else:
        assert False, "expected KeyError with no env"
    for bad in ("1 + 2", 5, ex.Add(ex.Num(1), "oops")):
        try:
            ex.evaluate(bad)
        except TypeError:
            pass
        else:
            assert False, f"expected TypeError for {bad!r}"


def test_simplify_identities():
    s, N, V = ex.simplify, ex.Num, ex.Var
    x = V("x")
    assert s(ex.Add(N(0), x)) == x
    assert s(ex.Add(x, N(0))) == x
    assert s(ex.Mul(N(1), x)) == x
    assert s(ex.Mul(x, N(1))) == x
    assert s(ex.Mul(N(0), x)) == N(0)
    assert s(ex.Mul(x, N(0))) == N(0)


def test_simplify_constants_and_neg():
    s, N, V = ex.simplify, ex.Num, ex.Var
    assert s(ex.Add(N(2), N(3))) == N(5)
    assert s(ex.Mul(N(2), N(3))) == N(6)
    assert s(ex.Neg(N(4))) == N(-4)
    assert s(ex.Neg(ex.Neg(V("x")))) == V("x")
    assert s(ex.Neg(V("x"))) == ex.Neg(V("x"))


def test_simplify_nested_and_unchanged():
    s, N, V = ex.simplify, ex.Num, ex.Var
    assert s(ex.Add(N(0), ex.Mul(N(1), V("x")))) == V("x")
    assert s(ex.Mul(V("y"), ex.Add(N(2), N(-2)))) == N(0)
    assert s(ex.Add(ex.Add(N(1), N(2)), V("z"))) == ex.Add(N(3), V("z"))
    assert s(ex.Add(V("a"), V("b"))) == ex.Add(V("a"), V("b"))
    assert s(ex.Mul(V("a"), N(2))) == ex.Mul(V("a"), N(2))
    assert s(N(7)) == N(7) and s(V("q")) == V("q")


def test_simplify_does_not_mutate():
    tree = ex.Add(ex.Num(0), ex.Var("x"))
    before = repr(tree)
    ex.simplify(tree)
    assert repr(tree) == before


def test_next_light():
    L = ex.Light
    assert ex.next_light(L.RED) is L.GREEN
    assert ex.next_light(L.GREEN) is L.YELLOW
    assert ex.next_light(L.YELLOW) is L.RED
    assert ex.next_light(L.FLASHING) is L.FLASHING
    for bad in ("RED", 1, None):
        try:
            ex.next_light(bad)
        except ValueError:
            pass
        else:
            assert False, f"expected ValueError for {bad!r}"


def test_flatten():
    f = ex.flatten
    assert f([1, [2, (3, "ab")], {"a": 4, "b": [5]}]) == [1, 2, 3, "ab", 4, 5]
    assert f("hi") == ["hi"]
    assert f(b"hi") == [b"hi"]
    assert f(7) == [7]
    assert f(None) == [None]
    assert f([]) == []
    assert f({}) == []
    assert f([[], [[]], ()]) == []
    assert f({"a": {"b": ["x", ["y"]]}}) == ["x", "y"]


def test_vec_class():
    v = ex.Vec(1, 2)
    assert (v.x, v.y) == (1, 2)
    assert ex.Vec.__match_args__ == ("x", "y")
    assert repr(v) == "Vec(1, 2)"
    import dataclasses
    assert not dataclasses.is_dataclass(v)


def test_vec_works_in_match():
    match ex.Vec(5, 6):
        case ex.Vec(a, b):
            assert (a, b) == (5, 6)
        case _:
            assert False, "positional class pattern should match"


def test_quadrant_vec_and_tuple():
    q, V = ex.quadrant, ex.Vec
    assert q(V(0, 0)) == "origin" and q((0, 0)) == "origin"
    assert q(V(3, 0)) == "x-axis" and q((-3, 0)) == "x-axis"
    assert q(V(0, 2)) == "y-axis" and q((0, -2)) == "y-axis"
    assert q(V(1, 1)) == "I" and q((2, 5)) == "I"
    assert q(V(-1, 1)) == "II" and q((-2, 5)) == "II"
    assert q(V(-1, -1)) == "III" and q((-2, -5)) == "III"
    assert q(V(3, -1)) == "IV" and q((2, -5)) == "IV"


def test_quadrant_invalid():
    for bad in (5, "ab", (1, 2, 3), None):
        try:
            ex.quadrant(bad)
        except ValueError:
            pass
        else:
            assert False, f"expected ValueError for {bad!r}"
