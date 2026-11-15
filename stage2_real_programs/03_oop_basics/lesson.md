# 2.03 — Object-Oriented Basics

## Learning goals
- Define classes with `__init__`, attributes and methods
- Distinguish instance attributes from class attributes
- Reuse behaviour with inheritance and `super()`, and override methods
- Choose between inheritance ("is a") and composition ("has a")

## 1. Classes and instances

A **class** is a blueprint; an **instance** is one object built from it.

```python
class Dog:
    def __init__(self, name: str):      # runs when you call Dog("Rex")
        self.name = name                 # instance attribute

    def speak(self) -> str:              # method: first parameter is the instance
        return f"{self.name} says Woof"

rex = Dog("Rex")
rex.speak()          # 'Rex says Woof'   (Python passes `rex` as `self`)
Dog.speak(rex)       # the same call, spelled out
```

`self` is just a convention for the first parameter — but always use it. Attributes are created
by assignment (usually in `__init__`) and live in the instance's `__dict__`.

## 2. Instance vs class attributes

```python
class Ticket:
    next_id = 1                 # class attribute: ONE copy shared by all instances

    def __init__(self, title):
        self.id = Ticket.next_id    # reading it via the class name
        Ticket.next_id += 1         # modifying the shared value
        self.title = title          # instance attribute: one per object
```

Lookup order for `obj.attr`: the instance first, then its class, then parent classes.

**Danger:** `self.next_id += 1` would *create an instance attribute* that shadows the class one.
Assign through the class name (`Ticket.next_id += 1`) when you mean the shared value.

**Bigger danger:** never use a mutable default in the class body when you want per-instance data:

```python
class Bad:
    items = []                  # shared by every instance!
class Good:
    def __init__(self):
        self.items = []         # fresh list per instance
```

## 3. Methods and encapsulation

Methods are functions that receive the instance. Python has no `private` keyword; it uses
conventions:

| Name | Meaning |
|---|---|
| `name` | public API |
| `_name` | internal — "please don't touch" |
| `__name` | name-mangled to `_Class__name` (avoids clashes in subclasses; not real security) |

Validate in methods and raise exceptions for misuse:

```python
def withdraw(self, amount):
    if amount > self.balance:
        raise ValueError("insufficient funds")
    self.balance -= amount
    return self.balance
```

Methods that change state usually return `None` (like `list.append`) *or* the new value — pick
one convention per class and document it. Exercises here say which.

## 4. Inheritance

A subclass gets all attributes and methods of its parent and can **override** them.

```python
class Animal:
    def __init__(self, name):
        self.name = name
    def speak(self):
        return "..."
    def intro(self):
        return f"{self.name} says {self.speak()}"

class Dog(Animal):             # Dog "is an" Animal
    def speak(self):           # override
        return "Woof"

Dog("Rex").intro()             # 'Rex says Woof' -- intro() is inherited, but it calls
                               # self.speak(), which resolves to Dog.speak
```

That last point is **polymorphism**: code written against the parent works with any subclass.

## 5. `super()`

`super()` gives access to the parent's version of a method. Use it to extend rather than replace:

```python
class SavingsAccount(BankAccount):
    def __init__(self, owner, balance=0, rate=0.02):
        super().__init__(owner, balance)     # let the parent set up its part
        self.rate = rate                     # then add ours

class Puppy(Dog):
    def speak(self):
        return super().speak() + "!"
```

If you override `__init__` and forget `super().__init__()`, the parent's attributes never exist.
With multiple inheritance, `super()` follows the **MRO** (`Cls.__mro__`), not just "the parent".

Useful introspection: `isinstance(x, Dog)`, `issubclass(Puppy, Animal)`, `type(x).__name__`.

## 6. Abstract-ish base classes

A base class can define an interface that subclasses must fill in:

```python
class Shape:
    def area(self):
        raise NotImplementedError
    def describe(self):
        return f"{type(self).__name__} with area {self.area():.2f}"
```

For enforced interfaces use `abc.ABC` and `@abstractmethod` (instantiating the base then fails).
The "template method" pattern above — shared logic in the base calling hooks in subclasses —
is the main payoff of inheritance.

## 7. Composition vs inheritance

| Inheritance ("is a") | Composition ("has a") |
|---|---|
| `Square(Rectangle)` | `Car` has an `Engine` |
| Tight coupling to the parent | Parts can be swapped freely |
| Good for true specialisations | Good for assembling behaviour |

```python
class Car:
    def __init__(self, make, engine):
        self.make = make
        self.engine = engine          # a Car HAS an Engine
    def start(self):
        self.engine.start()           # delegate
```

Rule of thumb: **prefer composition**; use inheritance only for a genuine "is a" relationship and
when the subclass can be used anywhere the parent is. (A classic trap: `Square(Rectangle)` breaks if
`Rectangle` lets you set width and height independently.) Don't inherit just to reuse a few methods.
Inheriting from built-ins such as `list` or `dict` is rarely worth it.

## Common mistakes

| Mistake | Fix |
|---|---|
| Forgetting `self` in a method signature or call | `def m(self, ...)`; `self.other()` |
| Forgetting `self.` when reading/writing an attribute | `self.balance`, not `balance` |
| Mutable class attribute meant per instance | Create it in `__init__` |
| Overriding `__init__` without `super().__init__()` | Call it (usually first) |
| Hard-coding the parent's behaviour in the child | Use `super()` |
| Deep inheritance trees | Flatten; use composition |
| Comparing types with `type(x) == Dog` | `isinstance(x, Dog)` |

## Practice

You will build a ticket counter (class attributes), a bank account with a savings subclass, an
animal and a shape hierarchy, an inventory, and a car composed of an engine. Read each docstring
for the exact rules — error cases matter.

```
python check.py 2.03
```
