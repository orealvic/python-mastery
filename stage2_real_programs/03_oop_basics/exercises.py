"""2.03 — Object-Oriented Basics

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 2.03` from the course root to test your work.
"""
from __future__ import annotations


class Ticket:
    """A support ticket with an automatically assigned id.

    The class attribute `next_id` starts at 1. Every new Ticket takes the
    current value as its `id` and then increments `next_id` (on the class,
    shared by all instances).

    Attributes: `id` (int), `title` (str), `done` (bool, starts False).
    Methods: `close()` sets `done` to True.

    >>> Ticket.next_id = 1
    >>> a, b = Ticket("login bug"), Ticket("typo")
    >>> (a.id, b.id, Ticket.next_id)
    (1, 2, 3)
    """

    next_id = 1

    def __init__(self, title: str):
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError


class BankAccount:
    """A simple bank account.

    - `BankAccount(owner, balance=0)` stores `owner` and `balance`.
    - `deposit(amount)`: amount must be > 0, else ValueError. Adds to balance.
    - `withdraw(amount)`: amount must be > 0 (ValueError) and <= balance
      (ValueError, balance unchanged). Subtracts from balance.
    - Both methods return the new balance.
    - `transactions` is a list of `(kind, amount)` tuples, `kind` being
      "deposit" or "withdraw", recorded only for successful operations.
      The opening balance is NOT a transaction.

    >>> acct = BankAccount("Ada", 100)
    >>> acct.deposit(50)
    150
    >>> acct.withdraw(30)
    120
    >>> acct.transactions
    [('deposit', 50), ('withdraw', 30)]
    """

    def __init__(self, owner: str, balance: float = 0):
        raise NotImplementedError

    def deposit(self, amount: float) -> float:
        raise NotImplementedError

    def withdraw(self, amount: float) -> float:
        raise NotImplementedError


class SavingsAccount(BankAccount):
    """A BankAccount that earns interest. Subclass BankAccount.

    - `SavingsAccount(owner, balance=0, rate=0.02)` -- call `super().__init__`.
      `rate` is stored as `self.rate`.
    - `add_interest()` deposits `balance * rate` (using the inherited
      `deposit`, so it appears in `transactions`) and returns the new balance.
      If the interest would be 0, do nothing and just return the balance
      (no transaction recorded).
    - `withdraw` is inherited unchanged.

    >>> s = SavingsAccount("Ada", 1000, rate=0.05)
    >>> s.add_interest()
    1050.0
    """

    def __init__(self, owner: str, balance: float = 0, rate: float = 0.02):
        raise NotImplementedError

    def add_interest(self) -> float:
        raise NotImplementedError


class Animal:
    """Base class for animals.

    - `Animal(name)` stores `self.name`.
    - `speak()` returns "..." .
    - `intro()` returns "<name> says <speak()>" -- it must call `self.speak()`
      so that subclasses automatically change what `intro` says.

    >>> Animal("Generic").intro()
    'Generic says ...'
    """

    def __init__(self, name: str):
        raise NotImplementedError

    def speak(self) -> str:
        raise NotImplementedError

    def intro(self) -> str:
        raise NotImplementedError


class Dog(Animal):
    """An Animal whose `speak()` returns "Woof"."""

    def speak(self) -> str:
        raise NotImplementedError


class Puppy(Dog):
    """A Dog whose `speak()` is the Dog's sound followed by "!" ("Woof!").

    Use `super().speak()` rather than hard-coding "Woof".
    """

    def speak(self) -> str:
        raise NotImplementedError


class Shape:
    """Base class for 2D shapes.

    Subclasses implement `area()` and `perimeter()` (the base versions raise
    NotImplementedError). The base class provides:

    - `describe()` -> "<ClassName> with area <area to 2 decimals>"
      e.g. "Rectangle with area 12.00". Use `type(self).__name__`.
    """

    def area(self) -> float:
        raise NotImplementedError

    def perimeter(self) -> float:
        raise NotImplementedError

    def describe(self) -> str:
        raise NotImplementedError


class Rectangle(Shape):
    """`Rectangle(width, height)`; `area()` and `perimeter()` as expected.

    >>> Rectangle(3, 4).area()
    12
    >>> Rectangle(3, 4).perimeter()
    14
    """

    def __init__(self, width: float, height: float):
        raise NotImplementedError

    def area(self) -> float:
        raise NotImplementedError

    def perimeter(self) -> float:
        raise NotImplementedError


class Square(Rectangle):
    """`Square(side)` -- a Rectangle with equal sides.

    Reuse Rectangle through `super().__init__`. `describe()` must say "Square".
    """

    def __init__(self, side: float):
        raise NotImplementedError


class Circle(Shape):
    """`Circle(radius)`; use `math.pi`. `perimeter()` is the circumference.

    >>> round(Circle(1).area(), 4)
    3.1416
    """

    def __init__(self, radius: float):
        raise NotImplementedError

    def area(self) -> float:
        raise NotImplementedError

    def perimeter(self) -> float:
        raise NotImplementedError


class Inventory:
    """A store inventory mapping item names to a quantity and unit price.

    - `add(name, qty, price)`: qty must be > 0 (else ValueError). If the item
      exists its quantity increases and its price is replaced by `price`.
    - `remove(name, qty)`: qty must be > 0 (ValueError). Unknown item or not
      enough stock -> ValueError (nothing changes). Removing everything leaves
      the item in the inventory with quantity 0.
    - `quantity(name)`: current quantity; 0 for unknown items.
    - `total_value()`: sum of quantity * price over all items.
    - `low_stock(threshold)`: sorted list of names with quantity < threshold.
    - `len(inventory)` is the number of distinct item names (implement `__len__`).

    >>> inv = Inventory()
    >>> inv.add("apple", 10, 0.5)
    >>> inv.remove("apple", 4)
    >>> inv.quantity("apple")
    6
    >>> inv.total_value()
    3.0
    """

    def __init__(self):
        raise NotImplementedError

    def add(self, name: str, qty: int, price: float) -> None:
        raise NotImplementedError

    def remove(self, name: str, qty: int) -> None:
        raise NotImplementedError

    def quantity(self, name: str) -> int:
        raise NotImplementedError

    def total_value(self) -> float:
        raise NotImplementedError

    def low_stock(self, threshold: int) -> list[str]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class Engine:
    """An engine that can be started and stopped.

    `Engine(horsepower)`; attributes `horsepower` and `running` (False at first).
    `start()` / `stop()` set `running` accordingly.
    """

    def __init__(self, horsepower: int):
        raise NotImplementedError

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError


class Car:
    """A car *has an* engine (composition, not inheritance).

    - `Car(make, engine)` stores both; `odometer` starts at 0.
    - `start()` / `stop()` delegate to the engine.
    - `drive(km)`: if the engine is not running raise RuntimeError; if km < 0
      raise ValueError; otherwise add km to `odometer` and return it.
    """

    def __init__(self, make: str, engine: Engine):
        raise NotImplementedError

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError

    def drive(self, km: float) -> float:
        raise NotImplementedError
