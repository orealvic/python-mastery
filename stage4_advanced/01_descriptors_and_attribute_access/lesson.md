# 4.01 — Descriptors & Attribute Access

## Learning goals
- Explain the descriptor protocol (`__get__`, `__set__`, `__delete__`, `__set_name__`)
- Distinguish data from non-data descriptors and predict attribute lookup order
- Know when `__getattr__`, `__getattribute__`, and `__setattr__` run (and which to use)
- See that `property`, methods, `classmethod`, `staticmethod` and `__slots__` are all descriptors
- Build reusable validation / caching / logging descriptors

## 1. What `obj.attr` really does

Attribute access is not a dict lookup; it is a protocol implemented by `object.__getattribute__`.
For `obj.name` (with `cls = type(obj)`), CPython does roughly:

1. Look up `name` along `cls.__mro__` -> call it `attr`.
2. If `attr` is a **data descriptor** (its type defines `__set__` or `__delete__`), return `attr.__get__(obj, cls)`.
3. Else if `name` is in `obj.__dict__`, return that value.
4. Else if `attr` is a **non-data descriptor** (only `__get__`), return `attr.__get__(obj, cls)`.
5. Else if `attr` exists, return it as-is (plain class attribute).
6. Else raise `AttributeError` -> and **only then** is `__getattr__` called, if defined.

```python
class Demo:
    def method(self): ...          # function = non-data descriptor
    @property
    def prop(self): return 1       # property = data descriptor (has __set__ even without a setter)
    cls_attr = 10

d = Demo()
d.__dict__["method"] = "shadowed"   # instance dict wins over non-data descriptor
d.__dict__["prop"] = "ignored"      # ...but NOT over a data descriptor
print(d.method, d.prop)             # shadowed 1
```

| Kind | Defines | Beats instance `__dict__`? | Examples |
|---|---|---|---|
| Data descriptor | `__get__` + `__set__`/`__delete__` | yes | `property`, `__slots__` members |
| Non-data descriptor | `__get__` only | no (instance dict wins) | functions/methods, `classmethod`, `functools.cached_property` |
| Plain attribute | nothing | no | ints, strs, lists on the class |

## 2. The descriptor protocol

```python
class Descriptor:
    def __set_name__(self, owner, name): ...        # called once at class creation (3.6+)
    def __get__(self, obj, objtype=None): ...       # obj is None for Class.attr
    def __set__(self, obj, value): ...
    def __delete__(self, obj): ...
```

Descriptors only work when stored **on a class** (not on an instance, not in a module).

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = name                    # "age" - no more repeating strings!

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                     # Class.attr returns the descriptor itself
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be positive")
        obj.__dict__[self.name] = value

class Person:
    age = Positive()
    def __init__(self, age):
        self.age = age                      # routed through Positive.__set__

p = Person(30)
p.age = -1     # ValueError
```

### Where to store the value?
The descriptor object is **shared by all instances**, so never store per-instance data on `self`
of the descriptor (a classic bug). Options:

- `obj.__dict__[self.name]` (fine because a data descriptor wins over the instance dict, so
  there is no recursion). Best default.
- A `WeakKeyDictionary` keyed by instance (works with `__slots__`, requires hashable + weakref-able).
- A private name like `"_" + name` with `setattr`/`getattr`.

## 3. `property` is just a descriptor

This pure-Python equivalent is close to the real thing:

```python
class my_property:
    def __init__(self, fget=None, fset=None, doc=None):
        self.fget, self.fset, self.__doc__ = fget, fset, doc or getattr(fget, "__doc__", None)
    def __set_name__(self, owner, name): self.name = name
    def __get__(self, obj, objtype=None):
        if obj is None: return self
        if self.fget is None: raise AttributeError(f"unreadable attribute {self.name}")
        return self.fget(obj)
    def __set__(self, obj, value):
        if self.fset is None: raise AttributeError(f"can't set attribute {self.name}")
        self.fset(obj, value)
    def setter(self, fset):
        return type(self)(self.fget, fset, self.__doc__)
```

Methods work through the same machinery: `function.__get__(obj, cls)` returns a *bound method*.

```python
class A:
    def f(self): return 1
a = A()
A.f.__get__(a, A)()      # same as a.f()
```

## 4. `functools.cached_property` — a non-data descriptor on purpose

```python
class Report:
    @cached_property
    def total(self):
        print("computing")
        return sum(range(10**6))
```

On first access it computes and stores the result in `obj.__dict__["total"]`. Because it has no
`__set__`, later reads find the instance dict entry first (step 3) and never call the descriptor
again: caching with zero overhead. Delete the entry (`del r.total`) to invalidate.

## 5. `__getattr__` vs `__getattribute__`

| Hook | Called when | Typical use |
|---|---|---|
| `__getattribute__(self, name)` | **every** attribute read | tracing, security (rare, dangerous) |
| `__getattr__(self, name)` | only after normal lookup **fails** | proxies, lazy attributes, delegation |
| `__setattr__(self, name, value)` | every attribute assignment | validation, immutability, observers |
| `__delattr__(self, name)` | every `del obj.x` | mirror of `__setattr__` |

```python
class Proxy:
    def __init__(self, target):
        object.__setattr__(self, "_target", target)   # bypass our own __setattr__
    def __getattr__(self, name):                      # only for names Proxy lacks
        return getattr(self._target, name)
    def __setattr__(self, name, value):
        setattr(self._target, name, value)
```

Pitfalls:
- In `__getattribute__` / `__setattr__`, use `object.__getattribute__(self, n)` /
  `object.__setattr__(self, n, v)` or `super()`; touching `self.x` recurses forever.
- `__getattr__` must raise `AttributeError` (not `KeyError`) for missing names, or `hasattr`,
  `copy`, and `pickle` break. Be careful with dunder names like `__deepcopy__`.
- Implicit special-method lookups (`len(x)`, `x + y`, `with x:`) bypass `__getattr__`
  and `__getattribute__` entirely; they look on the **type**.

## 6. `__slots__`

```python
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y): self.x, self.y = x, y
```

Each slot is a data descriptor (`Point.x` is a `member_descriptor`); there is no per-instance
`__dict__` or `__weakref__` (add `"__weakref__"` to the slots if you need weak references).
Benefits: lower memory (often 30-50% for many small objects) and typo protection
(`p.z = 1` raises `AttributeError`). Costs: no dynamic attributes, and inheritance gotchas
(a subclass without `__slots__` gets a `__dict__` again; multiple inheritance with non-empty slots
in several bases fails with a layout conflict).

## 7. Class-level vs instance-level, and `vars`/`dir`

```python
vars(obj)            # obj.__dict__ (instance attributes only)
dir(obj)             # names from instance + class + bases
inspect.getattr_static(obj, "x")   # lookup WITHOUT triggering descriptors or __getattr__
type(obj).__mro__    # the order step 1 searches
```

`inspect.getattr_static` is the right tool for introspection that must not run user code.

## 8. Practical descriptor patterns

- **Validation** (`Typed`, `Range`, `NonEmpty`): reuse across many classes, the heart of dataclass-like
  libraries and ORMs (Django fields, SQLAlchemy columns are descriptors).
- **Lazy / cached values**: `cached_property`.
- **Access logging / auditing / observable attributes.**
- **Computed class-level behaviour**: `classmethod`, `staticmethod` are descriptors too.

## Common mistakes
- Storing the value on the descriptor (`self.value = v`): all instances share it.
- Forgetting `if obj is None: return self` -> `Class.attr` crashes or returns garbage.
- Using `getattr(obj, self.name)` inside `__get__` for a data descriptor that has the same name: infinite recursion.
- Defining `__set__` on `cached_property`-like descriptors, which turns them into data descriptors and defeats the cache.
- `__getattr__` that raises `KeyError` or returns `None` for unknown names.
- Assigning in `__setattr__` with `self.x = v` (infinite recursion).
- Putting a descriptor on an instance (`obj.d = Descriptor()`): it is never invoked.

## Further reading
- Python docs: *Descriptor HowTo Guide* (docs.python.org/3/howto/descriptor.html), the canonical reference
- Data model: *Customizing attribute access* and *Implementing descriptors*
- `functools.cached_property` source in `Lib/functools.py`
- Raymond Hettinger's talks on descriptors

## Practice
Open `exercises.py`, implement each item, then run:

```bash
python check.py 4.01
```
