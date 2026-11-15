"""4.03 — Memory & the Object Model

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 4.03` from the course root to test your work.
"""


def make_grid(rows: int, cols: int, fill=0) -> list:
    """Return a rows x cols list of lists where every row is a DIFFERENT list
    (fixing the `[[fill] * cols] * rows` aliasing bug). `fill` itself is placed
    in each cell as-is (not copied).

    >>> g = make_grid(2, 3); g[0][0] = 1; g
    [[1, 0, 0], [0, 0, 0]]
    """
    raise NotImplementedError


def merge_defaults(config: dict, defaults: dict) -> dict:
    """Return a NEW dict: `defaults` overlaid with `config`.

    - Nested dicts present on both sides are merged recursively (config wins).
    - Otherwise a key from `config` replaces the default.
    - Neither input may be mutated, and the result must share NO mutable
      object (list/dict/set) with either input: mutating the result later must
      never affect `config` or `defaults`.

    >>> d = {"tags": ["a"], "db": {"port": 1, "host": "x"}}
    >>> r = merge_defaults({"db": {"port": 2}}, d)
    >>> r
    {'tags': ['a'], 'db': {'port': 2, 'host': 'x'}}
    >>> r["tags"] is d["tags"]
    False
    """
    raise NotImplementedError


def dedupe_strings(strings: list) -> list:
    """Return a new list with the same strings in the same order, but where
    equal strings are the SAME object (`result[i] is result[j]` whenever
    `strings[i] == strings[j]`). Use `sys.intern`.

    >>> a, b = "".join(["he", "llo"]), "".join(["hel", "lo"])
    >>> r = dedupe_strings([a, b]); r[0] is r[1]
    True
    """
    raise NotImplementedError


class Document:
    """A document with custom copy behaviour.

    - `Document(title, pages)` stores `title`, `pages` (a list) and an empty
      dict `cache` (derived data that must never be shared between copies).
    - `copy.copy(doc)` (implement `__copy__`) returns a new Document that SHARES
      the same `pages` list object and has its own fresh empty `cache`.
    - `copy.deepcopy(doc)` (implement `__deepcopy__(memo)`) returns a new
      Document with a deep-copied `pages` and a fresh empty `cache`. It must
      register the new object in `memo` BEFORE copying children, and pass `memo`
      to the inner deepcopy, so cycles (a page referencing the document) and
      shared references work.
    """

    def __init__(self, title: str, pages: list):
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError

    def __deepcopy__(self, memo):
        raise NotImplementedError


def track_lifetime(obj, log: list, label: str):
    """Arrange for `label` to be appended to `log` when `obj` is garbage collected.

    Must NOT keep `obj` alive (no strong reference to it). Return the
    `weakref.finalize` object (so callers can `.detach()` it or check `.alive`).

    >>> log = []
    >>> class T: pass
    >>> t = T(); f = track_lifetime(t, log, "t"); del t
    >>> log
    ['t']
    """
    raise NotImplementedError


class WeakCache:
    """Cache of expensive-to-build objects that doesn't keep them alive.

    - `WeakCache(factory)`; `factory(key)` builds a new (weak-referenceable) object.
    - `get(key)` returns the cached object if it is still alive, otherwise
      calls `factory(key)`, caches it WEAKLY (WeakValueDictionary) and returns it.
    - `misses` is the number of times the factory has been called.
    - `len(cache)` is the number of live cached entries; `key in cache` is True
      only if the entry is alive.
    - Use `.get()` on the weak dict rather than `in` followed by `[]`.
    """

    def __init__(self, factory):
        raise NotImplementedError

    def get(self, key):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def __contains__(self, key) -> bool:
        raise NotImplementedError


def find_shared_references(a, b) -> set:
    """Return the set of `id()`s of mutable containers (list, dict, set) that are
    reachable from BOTH `a` and `b` (including `a` or `b` themselves).

    Traverse list items, tuple items, dict VALUES and set items (dict keys and
    set items are hashable so ignore them as traversal targets). Only ids of
    list/dict/set objects are reported. Must handle cycles.

    >>> shared = [1]
    >>> x = {"k": [shared, 2]}; y = ([3], shared)
    >>> find_shared_references(x, y) == {id(shared)}
    True
    """
    raise NotImplementedError


def deep_getsizeof(obj) -> int:
    """Estimate total bytes used by `obj` and everything it references.

    Sum `sys.getsizeof` over every distinct object (by `id`) reachable from obj;
    an object reachable by several paths is counted ONCE. Descend into:
      - list, tuple, set, frozenset items
      - dict keys AND values
      - for any other object that has an instance `__dict__` (and is not a class
        or module): that `__dict__` object and its contents.
    Must terminate on cycles.

    >>> s = "x" * 100
    >>> deep_getsizeof([s, s]) == sys.getsizeof([s, s]) + sys.getsizeof(s)   # doctest: +SKIP
    True
    """
    raise NotImplementedError


def deep_copy(obj, _memo=None):
    """Deep-copy nested list / dict / set / tuple structures (no `copy` module!).

    - list, dict (values AND keys are copied via deep_copy), set and tuple are
      rebuilt; every other object (ints, strs, None, custom objects...) is
      returned as is.
    - Shared references are preserved: if the same inner list appears twice in
      the input, it appears as the same (new) list twice in the output.
    - Cycles are reproduced, not recursed into forever. This includes a cycle
      that passes through a tuple, e.g. `t = ([],); t[0].append(t)`.
    - Hint: keep a memo dict {id(original): copy}. Register lists/dicts/sets in
      the memo BEFORE filling them; for tuples build the items first, then check
      the memo again (a nested container may already have produced the copy).
    - `_memo` is the internal memo for recursion.

    >>> a = [1]; a.append(a); b = deep_copy(a); b[1] is b
    True
    """
    raise NotImplementedError
