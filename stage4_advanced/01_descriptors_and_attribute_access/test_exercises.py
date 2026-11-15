import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def test_attribute_source():
    class A:
        x = 1
        __slots__ = ()

        def m(self):
            pass

        p = property(lambda self: 1)

    class B:
        x = 1

        def m(self):
            pass

        p = property(lambda self: 1)

        def __getattr__(self, name):
            return 42

    b = B()
    b.y = 2
    b.__dict__["m"] = "shadow"
    b.__dict__["p"] = "ignored"
    assert ex.attribute_source(b, "p") == "data descriptor"
    assert ex.attribute_source(b, "y") == "instance"
    assert ex.attribute_source(b, "m") == "instance"
    assert ex.attribute_source(b, "x") == "class"
    assert ex.attribute_source(b, "dynamic") == "missing"
    a = A()
    assert ex.attribute_source(a, "m") == "non-data descriptor"
    assert ex.attribute_source(a, "q") == "missing"
    assert ex.attribute_source(B(), "m") == "non-data descriptor"

    class Slotted:
        __slots__ = ("s",)

    assert ex.attribute_source(Slotted(), "s") == "data descriptor"


def test_typed():
    class Person:
        name = ex.Typed(str)
        age = ex.Typed((int, float))

    p = Person()
    p.name = "Ada"
    p.age = 36
    assert (p.name, p.age) == ("Ada", 36)
    assert raises(TypeError, setattr, p, "name", 5)
    assert p.name == "Ada"
    assert raises(AttributeError, getattr, Person(), "name")
    assert isinstance(Person.name, ex.Typed)
    q = Person()
    q.name = "Bob"
    assert p.name == "Ada" and q.name == "Bob"
    assert "name" in p.__dict__
    try:
        p.age = "x"
    except TypeError as e:
        assert "age" in str(e)
    else:
        assert False


def test_bounded():
    class Player:
        health = ex.Bounded(0, 100)
        speed = ex.Bounded(-1.5, 1.5)

    a, b = Player(), Player()
    a.health = 50
    b.health = 100
    a.speed = -1.5
    assert (a.health, b.health, a.speed) == (50, 100, -1.5)
    assert raises(ValueError, setattr, a, "health", 101)
    assert raises(ValueError, setattr, a, "health", -1)
    assert raises(TypeError, setattr, a, "health", "5")
    assert a.health == 50
    assert raises(AttributeError, getattr, Player(), "health")
    del a.health
    assert raises(AttributeError, getattr, a, "health")
    assert b.health == 100
    assert isinstance(Player.health, ex.Bounded)


def test_cached_property():
    calls = []

    class C:
        @ex.cached_property
        def value(self):
            calls.append(1)
            return len(calls) * 10

    c, d = C(), C()
    assert c.value == 10
    assert c.value == 10
    assert len(calls) == 1
    assert d.value == 20
    assert "value" in c.__dict__
    del c.value
    assert c.value == 30
    c.value = 99
    assert c.value == 99
    assert isinstance(C.value, ex.cached_property)
    assert not hasattr(ex.cached_property, "__set__")


def test_cached_property_error_not_cached():
    state = {"n": 0}

    class C:
        @ex.cached_property
        def v(self):
            state["n"] += 1
            if state["n"] == 1:
                raise RuntimeError("boom")
            return "ok"

    c = C()
    assert raises(RuntimeError, getattr, c, "v")
    assert c.v == "ok"
    assert c.v == "ok"
    assert state["n"] == 2


def test_logged_attribute():
    log = []

    class Account:
        balance = ex.LoggedAttribute(log)

    a = Account()
    assert raises(AttributeError, getattr, a, "balance")
    assert log == []
    a.balance = 10
    assert a.balance == 10
    a.balance = 20
    assert log == [("set", "balance", 10), ("get", "balance", 10), ("set", "balance", 20)]
    n = len(log)
    Account.balance
    assert len(log) == n
    b = Account()
    b.balance = 1
    assert a.balance == 20


def test_proxy():
    target = [1, 2]
    p = ex.Proxy(target)
    p.append(3)
    assert target == [1, 2, 3]
    assert p.count(3) == 1
    assert repr(p) == "Proxy([1, 2, 3])"
    assert raises(AttributeError, getattr, p, "nope")

    class Obj:
        pass

    o = Obj()
    q = ex.Proxy(o)
    q.color = "red"
    assert o.color == "red"
    assert q.color == "red"
    assert "color" not in vars(q)
    del q.color
    assert not hasattr(o, "color")
    assert raises(AttributeError, getattr, q, "color")


def test_attrdict():
    d = ex.AttrDict({"a": 1, "inner": {"b": 2}})
    assert d.a == 1
    assert d.inner.b == 2
    assert isinstance(d.inner, ex.AttrDict)
    assert d.inner is d.inner
    d.inner.b = 5
    assert d["inner"]["b"] == 5
    d.c = 3
    assert d["c"] == 3
    del d.a
    assert "a" not in d
    assert raises(AttributeError, getattr, d, "a")
    assert raises(AttributeError, delattr, d, "zzz")
    assert isinstance(d, dict)
    d["keys"] = 1
    assert callable(d.keys)
    assert sorted(d.keys()) == ["c", "inner", "keys"]
    assert not hasattr(d, "missing")


def test_frozen():
    class Point(ex.Frozen):
        pass

    p = Point(x=1, y=2)
    assert (p.x, p.y) == (1, 2)
    assert raises(AttributeError, setattr, p, "x", 5)
    assert raises(AttributeError, setattr, p, "z", 5)
    assert raises(AttributeError, delattr, p, "x")
    assert p.x == 1
    assert repr(p) == "Point(x=1, y=2)"
    q = p.replace(x=10)
    assert isinstance(q, Point) and (q.x, q.y) == (10, 2)
    assert p.x == 1
    assert raises(AttributeError, lambda: p.replace(z=1))
    try:
        p.x = 3
    except AttributeError as e:
        assert "Point" in str(e)
