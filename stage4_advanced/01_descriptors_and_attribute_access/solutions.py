"""Reference solutions for 4.01. Try the exercises yourself first!"""


def attribute_source(obj, name: str) -> str:
    attr = missing = object()
    for klass in type(obj).__mro__:
        if name in vars(klass):
            attr = vars(klass)[name]
            break
    found = attr is not missing
    attr_type = type(attr)
    if found and (hasattr(attr_type, "__set__") or hasattr(attr_type, "__delete__")):
        return "data descriptor"
    try:
        if name in vars(obj):
            return "instance"
    except TypeError:
        pass
    if found and hasattr(attr_type, "__get__"):
        return "non-data descriptor"
    if found:
        return "class"
    return "missing"


class Typed:
    def __init__(self, expected_type):
        self.expected_type = expected_type
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name) from None

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{self.name} must be {self.expected_type}, got {type(value).__name__}")
        obj.__dict__[self.name] = value


class Bounded:
    def __init__(self, low, high):
        self.low, self.high = low, high
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            return obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name) from None

    def __set__(self, obj, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{self.name} must be a number")
        if not self.low <= value <= self.high:
            raise ValueError(f"{self.name} must be in [{self.low}, {self.high}]")
        obj.__dict__[self.name] = value

    def __delete__(self, obj):
        try:
            del obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name) from None


class cached_property:
    def __init__(self, func):
        self.func = func
        self.name = None
        self.__doc__ = func.__doc__

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        obj.__dict__[self.name] = value
        return value


class LoggedAttribute:
    def __init__(self, log: list):
        self.log = log
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        try:
            value = obj.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name) from None
        self.log.append(("get", self.name, value))
        return value

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value
        self.log.append(("set", self.name, value))


class Proxy:
    def __init__(self, target):
        object.__setattr__(self, "_target", target)

    def __getattr__(self, name):
        return getattr(object.__getattribute__(self, "_target"), name)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, "_target"), name, value)

    def __delattr__(self, name):
        delattr(object.__getattribute__(self, "_target"), name)

    def __repr__(self):
        return f"Proxy({object.__getattribute__(self, '_target')!r})"


class AttrDict(dict):
    def __getattr__(self, name):
        try:
            value = self[name]
        except KeyError:
            raise AttributeError(name) from None
        if type(value) is dict:
            value = AttrDict(value)
            self[name] = value
        return value

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name) from None


class Frozen:
    _FLAG = "_frozen"

    def __init__(self, **fields):
        for key, value in fields.items():
            object.__setattr__(self, key, value)
        object.__setattr__(self, self._FLAG, True)

    def __setattr__(self, name, value):
        if self.__dict__.get(self._FLAG):
            raise AttributeError(f"{type(self).__name__} is frozen")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if self.__dict__.get(self._FLAG):
            raise AttributeError(f"{type(self).__name__} is frozen")
        object.__delattr__(self, name)

    def _fields(self):
        return {k: v for k, v in self.__dict__.items() if k != self._FLAG}

    def replace(self, **changes):
        fields = self._fields()
        for key in changes:
            if key not in fields:
                raise AttributeError(key)
        fields.update(changes)
        return type(self)(**fields)

    def __repr__(self):
        body = ", ".join(f"{k}={v!r}" for k, v in self._fields().items())
        return f"{type(self).__name__}({body})"
