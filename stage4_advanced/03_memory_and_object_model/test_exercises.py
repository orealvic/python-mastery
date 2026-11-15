import copy
import gc
import importlib
import os
import sys

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


class Thing:
    """Weak-referenceable helper."""

    def __init__(self, key=None):
        self.key = key


def test_make_grid():
    g = ex.make_grid(2, 3)
    assert g == [[0, 0, 0], [0, 0, 0]]
    g[0][0] = 1
    assert g == [[1, 0, 0], [0, 0, 0]]
    assert g[0] is not g[1]
    assert ex.make_grid(0, 5) == []
    assert ex.make_grid(2, 2, "x") == [["x", "x"], ["x", "x"]]


def test_merge_defaults():
    d = {"tags": ["a"], "db": {"port": 1, "host": "x"}}
    c = {"db": {"port": 2}, "extra": [1]}
    d_snapshot, c_snapshot = copy.deepcopy(d), copy.deepcopy(c)
    r = ex.merge_defaults(c, d)
    assert r == {"tags": ["a"], "db": {"port": 2, "host": "x"}, "extra": [1]}
    assert d == d_snapshot and c == c_snapshot
    assert r["tags"] is not d["tags"]
    assert r["db"] is not d["db"] and r["db"] is not c["db"]
    assert r["extra"] is not c["extra"]
    r["tags"].append("b")
    r["db"]["host"] = "y"
    assert d == d_snapshot
    assert ex.merge_defaults({"a": 1}, {"a": {"b": 1}}) == {"a": 1}
    assert ex.merge_defaults({}, {}) == {}


def test_dedupe_strings():
    a = "".join(["he", "llo"])
    b = "".join(["hel", "lo"])
    c = "".join(["wor", "ld"])
    assert a is not b
    r = ex.dedupe_strings([a, c, b])
    assert r == ["hello", "world", "hello"]
    assert r[0] is r[2]
    assert ex.dedupe_strings([]) == []


def test_document_copy():
    doc = ex.Document("T", [["p1"], ["p2"]])
    doc.cache["k"] = 1
    sh = copy.copy(doc)
    assert sh is not doc and sh.title == "T"
    assert sh.pages is doc.pages
    assert sh.cache == {} and doc.cache == {"k": 1}
    dp = copy.deepcopy(doc)
    assert dp.pages == doc.pages and dp.pages is not doc.pages
    assert dp.pages[0] is not doc.pages[0]
    assert dp.cache == {}
    assert isinstance(dp, ex.Document)


def test_document_deepcopy_cycles_and_sharing():
    doc = ex.Document("T", [])
    doc.pages.append(doc)
    shared = ["s"]
    doc.pages.extend([shared, shared])
    dp = copy.deepcopy(doc)
    assert dp.pages[0] is dp
    assert dp.pages[1] is dp.pages[2] and dp.pages[1] is not shared
    # memo is respected across a container holding the doc twice
    pair = copy.deepcopy([doc, doc])
    assert pair[0] is pair[1] and pair[0] is not doc


def test_track_lifetime():
    log = []
    t = Thing()
    f = ex.track_lifetime(t, log, "t")
    assert f.alive and log == []
    del t
    gc.collect()
    assert log == ["t"]
    assert not f.alive
    u = Thing()
    g = ex.track_lifetime(u, log, "u")
    g.detach()
    del u
    gc.collect()
    assert log == ["t"]


def test_weak_cache():
    built = []

    def factory(key):
        built.append(key)
        return Thing(key)

    cache = ex.WeakCache(factory)
    a = cache.get("a")
    assert cache.get("a") is a
    assert cache.misses == 1 and built == ["a"]
    assert len(cache) == 1 and "a" in cache and "b" not in cache
    b = cache.get("b")
    assert len(cache) == 2
    del a
    gc.collect()
    assert "a" not in cache and len(cache) == 1
    a2 = cache.get("a")
    assert a2.key == "a" and cache.misses == 3 and built == ["a", "b", "a"]
    assert cache.get("b") is b


def test_find_shared_references():
    shared = [1]
    x = {"k": [shared, 2]}
    y = ([3], shared)
    assert ex.find_shared_references(x, y) == {id(shared)}
    assert ex.find_shared_references([1], [1]) == set()
    inner = {"a": []}
    outer = [inner]
    # everything reachable from `inner` is also reachable from `outer`
    assert ex.find_shared_references(outer, inner) == {id(inner), id(inner["a"])}
    assert id(inner) in ex.find_shared_references(outer, outer)


def test_find_shared_references_cycles():
    a = [1]
    a.append(a)
    b = [a]
    assert ex.find_shared_references(a, b) == {id(a)}
    c = {"me": None}
    c["me"] = c
    assert ex.find_shared_references(c, [c, ([],)]) == {id(c)}


def test_deep_getsizeof():
    s = "x" * 100
    lst = [s, s]
    assert ex.deep_getsizeof(lst) == sys.getsizeof(lst) + sys.getsizeof(s)
    d = {"a": 1}
    assert ex.deep_getsizeof(d) == sys.getsizeof(d) + sys.getsizeof("a") + sys.getsizeof(1)
    t = (s, [s])
    assert ex.deep_getsizeof(t) == sys.getsizeof(t) + sys.getsizeof(s) + sys.getsizeof([s])
    assert ex.deep_getsizeof("x" * 10_000) == sys.getsizeof("x" * 10_000)
    st = {1, 2, 3}
    assert ex.deep_getsizeof(frozenset(st)) >= sys.getsizeof(frozenset(st))
    big = [list(range(i * 1000, i * 1000 + 100)) for i in range(1, 11)]
    assert ex.deep_getsizeof(big) > ex.deep_getsizeof(big[0]) * 5


def test_deep_getsizeof_cycles_and_objects():
    a = []
    a.append(a)
    assert ex.deep_getsizeof(a) == sys.getsizeof(a)
    payload = list(range(1000, 1100))
    obj = Thing(payload)
    assert ex.deep_getsizeof(obj) >= sys.getsizeof(payload) + sys.getsizeof(obj)
    assert ex.deep_getsizeof(obj) > ex.deep_getsizeof(Thing(None))


def test_deep_copy_basic():
    orig = {"a": [1, 2, {"b": (3, [4])}], "s": {1, 2}}
    cp = ex.deep_copy(orig)
    assert cp == orig and cp is not orig
    assert cp["a"] is not orig["a"]
    assert cp["a"][2]["b"][1] is not orig["a"][2]["b"][1]
    assert cp["s"] is not orig["s"]
    cp["a"][2]["b"][1].append(5)
    assert orig["a"][2]["b"][1] == [4]
    assert ex.deep_copy(5) == 5 and ex.deep_copy("s") == "s" and ex.deep_copy(None) is None
    t = Thing()
    assert ex.deep_copy([t])[0] is t


def test_deep_copy_shared_and_cycles():
    x = [1]
    y = [x, x, {"k": x}]
    z = ex.deep_copy(y)
    assert z[0] is z[1] and z[0] is z[2]["k"] and z[0] is not x
    a = [1]
    a.append(a)
    b = ex.deep_copy(a)
    assert b is not a and b[0] == 1 and b[1] is b
    d = {}
    d["self"] = d
    e = ex.deep_copy(d)
    assert e["self"] is e and e is not d


def test_deep_copy_tuple_cycle():
    t = ([],)
    t[0].append(t)
    c = ex.deep_copy(t)
    assert c is not t and c[0] is not t[0]
    assert c[0][0] is c
