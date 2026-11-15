import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def test_vector_repr_str_eq_hash():
    v = ex.Vector(1, 2)
    assert repr(v) == "Vector(1, 2)"
    assert str(v) == "(1, 2)"
    assert repr(ex.Vector(1.5, -2)) == "Vector(1.5, -2)"
    assert v == ex.Vector(1, 2)
    assert v != ex.Vector(2, 1)
    assert (v == (1, 2)) is False
    assert hash(v) == hash(ex.Vector(1, 2))
    assert len({ex.Vector(1, 2), ex.Vector(1, 2), ex.Vector(0, 0)}) == 2
    assert {ex.Vector(1, 2): "a"}[ex.Vector(1, 2)] == "a"


def test_vector_arithmetic():
    v = ex.Vector(3, 4)
    assert v + ex.Vector(1, 1) == ex.Vector(4, 5)
    assert v - ex.Vector(1, 1) == ex.Vector(2, 3)
    assert -v == ex.Vector(-3, -4)
    assert v * 2 == ex.Vector(6, 8)
    assert 2 * v == ex.Vector(6, 8)
    assert 0.5 * v == ex.Vector(1.5, 2.0)
    assert v == ex.Vector(3, 4)  # originals unchanged
    assert raises(TypeError, lambda: v + 1)
    assert raises(TypeError, lambda: v * "a")


def test_vector_misc():
    assert abs(ex.Vector(3, 4)) == 5.0
    assert abs(ex.Vector(0, 0)) == 0
    assert not ex.Vector(0, 0)
    assert ex.Vector(0, 1)
    x, y = ex.Vector(7, 8)
    assert (x, y) == (7, 8)
    assert list(ex.Vector(1, 2)) == [1, 2]


def test_money_basics():
    assert str(ex.Money(1234)) == "12.34 USD"
    assert str(ex.Money(5)) == "0.05 USD"
    assert str(ex.Money(-550, "EUR")) == "-5.50 EUR"
    assert str(ex.Money(-5)) == "-0.05 USD"
    assert repr(ex.Money(1234)) == "Money(1234, 'USD')"
    assert ex.Money(100) == ex.Money(100, "USD")
    assert ex.Money(100) != ex.Money(100, "EUR")
    assert hash(ex.Money(100)) == hash(ex.Money(100))
    assert len({ex.Money(1), ex.Money(1), ex.Money(2)}) == 2


def test_money_parse():
    assert ex.Money.parse("12.34") == ex.Money(1234)
    assert ex.Money.parse("5.5 EUR") == ex.Money(550, "EUR")
    assert ex.Money.parse("5") == ex.Money(500)
    assert ex.Money.parse("-0.05 GBP") == ex.Money(-5, "GBP")
    assert ex.Money.parse("0.1") == ex.Money(10)
    assert ex.Money.parse("19.99") == ex.Money(1999)  # no float rounding errors
    assert ex.Money.parse("1.15") == ex.Money(115)
    for bad in ["", "abc", "1.234", "1.2.3", "1 USD extra", "--1", "$5"]:
        assert raises(ValueError, ex.Money.parse, bad), bad


def test_money_arithmetic():
    assert ex.Money(100) + ex.Money(250) == ex.Money(350)
    assert ex.Money(100) - ex.Money(250) == ex.Money(-150)
    assert ex.Money(100) * 3 == ex.Money(300)
    assert 3 * ex.Money(100) == ex.Money(300)
    assert raises(ValueError, lambda: ex.Money(1, "USD") + ex.Money(1, "EUR"))
    assert raises(ValueError, lambda: ex.Money(1, "USD") - ex.Money(1, "EUR"))
    assert sum([ex.Money(100), ex.Money(250), ex.Money(5)]) == ex.Money(355)
    assert raises(TypeError, lambda: ex.Money(1) + 5)


def test_money_ordering():
    assert ex.Money(100) < ex.Money(200)
    assert ex.Money(200) > ex.Money(100)
    assert ex.Money(100) <= ex.Money(100)
    assert ex.Money(100) >= ex.Money(100)
    assert sorted([ex.Money(300), ex.Money(100), ex.Money(200)]) == [ex.Money(100), ex.Money(200), ex.Money(300)]
    assert max(ex.Money(1), ex.Money(9)) == ex.Money(9)
    assert raises(ValueError, lambda: ex.Money(1, "USD") < ex.Money(2, "EUR"))


def test_playlist_sequence_protocol():
    songs = ["a", "b", "c"]
    p = ex.Playlist("Mix", songs)
    songs.append("zzz")  # must not leak into the playlist
    assert len(p) == 3
    assert p[0] == "a" and p[-1] == "c"
    assert p[1:] == ["b", "c"]
    assert list(p) == ["a", "b", "c"]
    assert list(p) == ["a", "b", "c"]  # re-iterable
    assert "b" in p and "z" not in p
    assert bool(p) is True and bool(ex.Playlist("e")) is False
    assert len(ex.Playlist("e")) == 0
    assert raises(IndexError, lambda: p[10])


def test_playlist_mutation_and_combining():
    p = ex.Playlist("Mix", ["a"])
    assert p.add("b") is None
    assert list(p) == ["a", "b"]
    q = ex.Playlist("Other", ["c"])
    r = p + q
    assert r.name == "Mix" and list(r) == ["a", "b", "c"]
    assert list(p) == ["a", "b"] and list(q) == ["c"]
    assert raises(TypeError, lambda: p + ["x"])


def test_playlist_eq_repr():
    assert ex.Playlist("A", ["x"]) == ex.Playlist("A", ["x"])
    assert ex.Playlist("A", ["x"]) != ex.Playlist("B", ["x"])
    assert ex.Playlist("A", ["x"]) != ex.Playlist("A", ["y"])
    assert (ex.Playlist("A") == ["x"]) is False
    assert repr(ex.Playlist("Road Trip", ["a", "b", "c"])) == "Playlist('Road Trip', 3 songs)"
    assert repr(ex.Playlist("E")) == "Playlist('E', 0 songs)"


def test_temperature_properties():
    t = ex.Temperature(100)
    assert t.celsius == 100
    assert t.fahrenheit == 212.0
    assert abs(t.kelvin - 373.15) < 1e-9
    t.fahrenheit = 32
    assert abs(t.celsius) < 1e-9
    t.celsius = 37
    assert abs(t.fahrenheit - 98.6) < 1e-9
    assert repr(ex.Temperature(25)) == "Temperature(25)"


def test_temperature_validation():
    assert raises(ValueError, ex.Temperature, -300)
    ex.Temperature(-273.15)  # allowed
    t = ex.Temperature(0)
    def set_c():
        t.celsius = -273.16
    assert raises(ValueError, set_c)
    def set_f():
        t.fahrenheit = -1000
    assert raises(ValueError, set_f)
    assert t.celsius == 0  # unchanged after failed assignment


def test_temperature_readonly_and_constructors():
    t = ex.Temperature(0)
    def set_k():
        t.kelvin = 5
    assert raises(AttributeError, set_k)
    assert abs(ex.Temperature.from_fahrenheit(212).celsius - 100) < 1e-9
    assert isinstance(ex.Temperature.from_fahrenheit(32), ex.Temperature)
    assert ex.Temperature.c_to_f(100) == 212
    assert ex.Temperature.c_to_f(-40) == -40


def test_version_parse_and_str():
    v = ex.Version.parse("1.2.3")
    assert (v.major, v.minor, v.patch) == (1, 2, 3)
    assert str(v) == "1.2.3"
    assert repr(v) == "Version(1, 2, 3)"
    assert ex.Version(0, 0, 1) == ex.Version.parse("0.0.1")
    for bad in ["1.2", "1.2.3.4", "a.b.c", "1..3", "", "-1.0.0", "1.2.x"]:
        assert raises(ValueError, ex.Version.parse, bad), bad


def test_version_is_valid():
    assert ex.Version.is_valid("1.2.3") is True
    assert ex.Version.is_valid("10.0.0") is True
    assert ex.Version.is_valid("1.2") is False
    assert ex.Version.is_valid("x") is False


def test_version_ordering_and_hash():
    p = ex.Version.parse
    assert p("1.10.0") > p("1.9.0")
    assert p("2.0.0") > p("1.99.99")
    assert p("1.0.0") <= p("1.0.0") and p("1.0.0") >= p("1.0.0")
    assert p("1.0.1") > p("1.0.0")
    assert sorted([p("1.10.0"), p("1.2.0"), p("1.9.5")]) == [p("1.2.0"), p("1.9.5"), p("1.10.0")]
    assert len({p("1.0.0"), p("1.0.0"), p("1.0.1")}) == 2
    assert (ex.Version(1, 0, 0) == "1.0.0") is False
    assert max([p("0.9.0"), p("0.10.0")]) == p("0.10.0")
