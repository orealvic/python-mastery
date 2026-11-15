import importlib
import math
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def test_make_class():
    Point = ex.make_class("Point", ["x", "y"], {"norm1": lambda self: abs(self.x) + abs(self.y)})
    p = Point(3, -4)
    assert type(p) is Point and Point.__name__ == "Point"
    assert (p.x, p.y) == (3, -4)
    assert repr(p) == "Point(x=3, y=-4)"
    assert p.norm1() == 7
    assert Point._fields == ("x", "y")
    assert raises(TypeError, Point, 1)
    assert raises(TypeError, Point, 1, 2, 3)


def test_make_class_bases_and_override():
    class Base:
        def hello(self):
            return "base"

    C = ex.make_class("C", ("a",), {"__repr__": lambda self: "custom"}, bases=(Base,))
    c = C(1)
    assert isinstance(c, Base) and c.hello() == "base"
    assert repr(c) == "custom"
    E = ex.make_class("Empty", [])
    assert repr(E()) == "Empty()"


def test_auto_repr():
    @ex.auto_repr
    class P:
        def __init__(self):
            self.a = 1
            self._hidden = 2
            self.b = "x"

    assert repr(P()) == "P(a=1, b='x')"

    @ex.auto_repr
    class Q:
        def __repr__(self):
            return "old"

    assert repr(Q()) == "Q()"
    assert isinstance(Q(), Q)


def test_shapes():
    r = ex.Rectangle(3, 4)
    assert r.area() == 12 and r.perimeter() == 14
    assert r.describe() == "Rectangle: area=12.00, perimeter=14.00"
    c = ex.Circle(1)
    assert abs(c.area() - math.pi) < 1e-12
    assert abs(c.perimeter() - 2 * math.pi) < 1e-12
    assert c.describe() == "Circle: area=3.14, perimeter=6.28"
    assert isinstance(r, ex.Shape)
    assert raises(TypeError, ex.Shape)

    class Half(ex.Shape):
        def area(self):
            return 1

    assert raises(TypeError, Half)
    assert ex.Shape.__abstractmethods__ == frozenset({"area", "perimeter"})


def test_plugin_registry():
    class Loader(ex.PluginBase):
        def __init__(self, path="?"):
            self.path = path

    class Csv(Loader, key="csv"):
        pass

    class Json(Loader):
        pass

    class SubJson(Json, key="sub"):
        pass

    assert sorted(Loader.registry) == ["csv", "json", "sub"]
    assert Loader.registry["csv"] is Csv
    obj = Loader.create("json", path="a.json")
    assert type(obj) is Json and obj.path == "a.json"
    assert type(Json.create("sub")) is SubJson
    assert raises(KeyError, Loader.create, "nope")


def test_plugin_registry_isolation_and_duplicates():
    class A(ex.PluginBase):
        pass

    class B(ex.PluginBase):
        pass

    class X(A):
        pass

    class Y(B, key="x"):
        pass

    assert list(A.registry) == ["x"] and list(B.registry) == ["x"]
    assert A.registry is not B.registry
    assert A.registry["x"] is X and B.registry["x"] is Y
    assert "a" not in A.registry

    def define_dup():
        class X2(A, key="x"):
            pass

    assert raises(ValueError, define_dup)
    assert A.registry["x"] is X


def test_singleton_meta():
    calls = []

    class Config(metaclass=ex.SingletonMeta):
        def __init__(self, value=0):
            calls.append(value)
            self.value = value

    a = Config(5)
    b = Config(99)
    assert a is b and a.value == 5
    assert calls == [5]

    class Other(metaclass=ex.SingletonMeta):
        pass

    class Sub(Config):
        pass

    assert Other() is Other()
    assert Other() is not Config()
    s = Sub(1)
    assert s is not a and s is Sub(2) and isinstance(s, Config)


def test_enforced_meta():
    class Closeable(metaclass=ex.EnforcedMeta):
        required_methods = ("close", "flush")

    class Good(Closeable):
        def close(self):
            pass

        def flush(self):
            pass

    class AlsoGood(Good):
        pass

    def define(body_names):
        ns = {n: (lambda self: None) for n in body_names}
        return ex.EnforcedMeta("Bad", (Closeable,), ns)

    try:
        define(["close"])
    except TypeError as e:
        assert str(e) == "Bad must implement: flush"
    else:
        assert False, "expected TypeError"
    try:
        define([])
    except TypeError as e:
        assert str(e) == "Bad must implement: close, flush"
    else:
        assert False, "expected TypeError"
    assert define(["close", "flush"]).__name__ == "Bad"

    # non-callable attribute does not count
    def define_noncallable():
        class Bad2(Closeable):
            close = 1
            flush = 2

    assert raises(TypeError, define_noncallable)

    class Plain(metaclass=ex.EnforcedMeta):
        pass

    assert Plain() is not None


def test_no_dup_meta():
    class Fine(metaclass=ex.NoDupMeta):
        x = 1

        def f(self):
            return 1

        def g(self):
            return 2

    assert Fine().f() == 1 and Fine.x == 1

    class Child(Fine):
        def f(self):
            return 10

    assert Child().f() == 10

    def bad_method():
        class Bad(metaclass=ex.NoDupMeta):
            def f(self):
                return 1

            def f(self):  # noqa: F811
                return 2

    def bad_attr():
        class Bad(metaclass=ex.NoDupMeta):
            a = 1
            a = 2

    for fn in (bad_method, bad_attr):
        try:
            fn()
        except TypeError as e:
            assert "duplicate definition of" in str(e)
        else:
            assert False, "expected TypeError"
