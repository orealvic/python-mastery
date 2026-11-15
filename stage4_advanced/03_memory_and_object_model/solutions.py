"""Reference solutions for 4.03. Try the exercises yourself first!"""
import copy
import sys
import types
import weakref


def make_grid(rows: int, cols: int, fill=0) -> list:
    return [[fill] * cols for _ in range(rows)]


def merge_defaults(config: dict, defaults: dict) -> dict:
    result = copy.deepcopy(defaults)
    for key, value in config.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_defaults(value, result[key])
        else:
            result[key] = copy.deepcopy(value)
    return result


def dedupe_strings(strings: list) -> list:
    return [sys.intern(s) for s in strings]


class Document:
    def __init__(self, title: str, pages: list):
        self.title = title
        self.pages = pages
        self.cache = {}

    def __copy__(self):
        return type(self)(self.title, self.pages)

    def __deepcopy__(self, memo):
        new = type(self).__new__(type(self))
        memo[id(self)] = new
        new.title = self.title
        new.pages = copy.deepcopy(self.pages, memo)
        new.cache = {}
        return new


def track_lifetime(obj, log: list, label: str):
    return weakref.finalize(obj, log.append, label)


class WeakCache:
    def __init__(self, factory):
        self._factory = factory
        self._data = weakref.WeakValueDictionary()
        self.misses = 0

    def get(self, key):
        obj = self._data.get(key)
        if obj is None:
            obj = self._factory(key)
            self._data[key] = obj
            self.misses += 1
        return obj

    def __len__(self) -> int:
        return len(self._data)

    def __contains__(self, key) -> bool:
        return self._data.get(key) is not None


def _reachable_containers(root) -> set:
    seen: set = set()
    found: set = set()
    stack = [root]
    while stack:
        obj = stack.pop()
        if id(obj) in seen:
            continue
        seen.add(id(obj))
        if isinstance(obj, (list, dict, set)):
            found.add(id(obj))
        if isinstance(obj, (list, tuple, set)):
            stack.extend(obj)
        elif isinstance(obj, dict):
            stack.extend(obj.values())
    return found


def find_shared_references(a, b) -> set:
    return _reachable_containers(a) & _reachable_containers(b)


def deep_getsizeof(obj) -> int:
    seen: set = set()
    total = 0
    stack = [obj]
    while stack:
        o = stack.pop()
        if id(o) in seen:
            continue
        seen.add(id(o))
        total += sys.getsizeof(o)
        if isinstance(o, dict):
            stack.extend(o.keys())
            stack.extend(o.values())
        elif isinstance(o, (list, tuple, set, frozenset)):
            stack.extend(o)
        elif not isinstance(o, (type, types.ModuleType)) and hasattr(o, "__dict__"):
            stack.append(vars(o))
    return total


def deep_copy(obj, _memo=None):
    memo = {} if _memo is None else _memo
    oid = id(obj)
    if oid in memo:
        return memo[oid]
    if isinstance(obj, list):
        new = memo[oid] = []
        new.extend(deep_copy(x, memo) for x in obj)
        return new
    if isinstance(obj, dict):
        new = memo[oid] = {}
        for k, v in obj.items():
            new[deep_copy(k, memo)] = deep_copy(v, memo)
        return new
    if isinstance(obj, set):
        new = memo[oid] = set()
        for x in obj:
            new.add(deep_copy(x, memo))
        return new
    if isinstance(obj, tuple):
        items = tuple(deep_copy(x, memo) for x in obj)
        if oid in memo:
            return memo[oid]
        memo[oid] = items
        return items
    return obj
