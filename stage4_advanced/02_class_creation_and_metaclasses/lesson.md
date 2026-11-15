# 4.02 — Class Creation & Metaclasses

## Learning goals
- Describe exactly what happens when a `class` statement executes
- Create classes dynamically with `type(name, bases, namespace)`
- Use `__init_subclass__`, `__set_name__`, and class decorators (and know why they usually beat metaclasses)
- Write metaclasses using `__prepare__`, `__new__`, `__init__`, and `__call__`
- Build registries, singletons, and enforce interfaces; use `abc` correctly

## 1. Classes are objects, and `type` makes them

```python
class Point:
    z = 0
    def hello(self): return "hi"
```
is (approximately) sugar for:

```python
def hello(self): return "hi"
Point = type("Point", (object,), {"z": 0, "hello": hello})
```

`type` has two jobs: `type(x)` returns the class of `x`; `type(name, bases, ns)` builds a new class.
Every class is an *instance of its metaclass*; the default metaclass is `type` itself
(`type(type) is type`).

```python
print(type(3), type(int), type(type))   # <class 'int'> <class 'type'> <class 'type'>
```

## 2. What the `class` statement does

1. Resolve the metaclass: explicit `metaclass=` keyword, else the metaclass of the most derived base, else `type`.
   (If bases have *unrelated* metaclasses you get "metaclass conflict".)
2. Call `meta.__prepare__(name, bases, **kwds)` -> returns the namespace mapping (default: a fresh `dict`).
3. **Execute the class body** as a function whose local namespace is that mapping. Yes, code in the body
   runs at class-definition time: `print`, loops, conditionals all work.
4. Call `meta(name, bases, namespace, **kwds)` -> `meta.__call__` -> `meta.__new__` then `meta.__init__`.
5. During `type.__new__`: every value with `__set_name__` gets `value.__set_name__(cls, attr_name)`, then
   the parent's `__init_subclass__(**kwds)` is called.
6. Class decorators run last, and the result is bound to the name.

```python
class Meta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kw):
        print("prepare", name); return {}
    def __new__(mcls, name, bases, ns, **kw):
        print("new", name); return super().__new__(mcls, name, bases, ns)
    def __init__(cls, name, bases, ns, **kw):
        print("init", name); super().__init__(name, bases, ns)

class A(metaclass=Meta):
    print("body runs")
# prepare A / body runs / new A / init A
```

## 3. Prefer the lighter hooks

Metaclasses are the heaviest tool. Reach for them in this order:

| Need | Tool |
|---|---|
| Modify/register a class after creation | **class decorator** |
| React to subclassing (registry, validation) | **`__init_subclass__`** |
| Descriptor needs to know its attribute name | **`__set_name__`** |
| Control class namespace (`__prepare__`), change instantiation (`__call__`), change how class objects behave | metaclass |

### `__init_subclass__`
```python
class Plugin:
    registry = {}
    def __init_subclass__(cls, /, name=None, **kw):
        super().__init_subclass__(**kw)       # always cooperate
        Plugin.registry[name or cls.__name__.lower()] = cls

class CsvLoader(Plugin, name="csv"): ...
Plugin.registry   # {'csv': <class CsvLoader>}
```
It is called on the **parent** each time a subclass is created (not for the class defining it).
Extra class keyword arguments are forwarded to it.

### Class decorators
```python
def add_repr(cls):
    def __repr__(self):
        items = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{cls.__name__}({items})"
    cls.__repr__ = __repr__
    return cls
```
`@dataclass` and `@functools.total_ordering` work this way. They don't affect subclasses automatically.

## 4. Writing metaclasses

### `__new__` / `__init__` : customize the class
```python
class Validated(type):
    def __new__(mcls, name, bases, ns):
        for attr, value in ns.items():
            if attr.startswith("test") and not callable(value):
                raise TypeError(f"{attr} must be callable")
        return super().__new__(mcls, name, bases, ns)
```
Use `__new__` when you need to change `bases`/`ns` before the class exists; use `__init__` to act
on the finished class.

### `__call__` : customize instantiation
`Cls(...)` is `type(Cls).__call__(Cls, ...)`, which normally runs `Cls.__new__` then `Cls.__init__`.
Overriding it on a metaclass allows singletons, instance pooling, or post-init hooks:

```python
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in Singleton._instances:
            Singleton._instances[cls] = super().__call__(*args, **kwargs)
        return Singleton._instances[cls]
```
(Thread safety: guard with a lock if singletons may be created concurrently. Often a module-level
instance is simpler and better than a singleton.)

### `__prepare__` : customize the namespace
```python
class StrictNS(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise TypeError(f"duplicate {key!r}")
        super().__setitem__(key, value)

class NoDup(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kw):
        return StrictNS()
```
Caveat: the `@x.setter` property idiom *re-binds* `x` and would trip this check; real code must allow it.

## 5. Dynamic class creation

```python
def make_point(*fields):
    def __init__(self, *args):
        for f, a in zip(fields, args): setattr(self, f, a)
    return type("Point", (), {"__init__": __init__, "__slots__": fields})
```
Use `types.new_class` when you need metaclass resolution and `__prepare__` to run properly, and
`collections.namedtuple` / `dataclasses.make_dataclass` for the common cases.

## 6. Abstract base classes (`abc`)

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self): ...
    def describe(self): return f"{type(self).__name__} area={self.area():.2f}"

Shape()               # TypeError: Can't instantiate abstract class Shape ...
class Sq(Shape):
    def __init__(self, s): self.s = s
    def area(self): return self.s ** 2     # now concrete
```
- `ABCMeta` is a metaclass; it computes `__abstractmethods__` at class creation and `object.__new__`
  refuses to instantiate when it is non-empty.
- `ABC.register(cls)` declares *virtual subclasses* (no inheritance, `isinstance` works).
- `__subclasshook__` lets `isinstance` check structure (`collections.abc.Sized` does this via `__len__`).
- For static duck typing prefer `typing.Protocol`.

## 7. Descriptors meet class creation: `__set_name__`

```python
class Field:
    def __set_name__(self, owner, name):
        self.name = name; owner._fields = getattr(owner, "_fields", []) + [name]

class Model:
    id = Field()
    title = Field()
# Model._fields == ['id', 'title']
```

## 8. When *not* to use a metaclass
- If a decorator or `__init_subclass__` works, use it. Metaclasses don't compose (metaclass conflicts).
- Django models, SQLAlchemy declarative, `enum.Enum`, `ABCMeta`, and `typing.NamedTuple` use them; your app code rarely should.
- "Metaclasses are deeper magic than 99% of users should ever worry about." (Tim Peters)

## Common mistakes
- Forgetting `super().__init_subclass__(**kwargs)` in cooperative hierarchies.
- Doing `__call__` work in `__new__` of the metaclass (they run at different times: class creation vs instantiation).
- Overriding `__new__` of a metaclass without passing `ns` through to `super().__new__`.
- Creating metaclass conflicts by mixing `ABC` with a custom metaclass; derive yours from `ABCMeta`.
- Registering abstract/intermediate classes in plugin registries by accident.
- Assuming a class decorator also applies to subclasses.
- Singleton `__call__` without handling subclass separation (key the cache by `cls`).

## Further reading
- Data model: *Customizing class creation* (docs.python.org/3/reference/datamodel.html)
- PEP 487 (`__init_subclass__`, `__set_name__`), PEP 3115 (`__prepare__`), PEP 3119 (ABCs)
- `types.new_class`, `types.DynamicClassAttribute`, `abc` module docs
- David Beazley: *Python 3 Metaprogramming*

## Practice
Open `exercises.py`, implement each item, then run:

```bash
python check.py 4.02
```
