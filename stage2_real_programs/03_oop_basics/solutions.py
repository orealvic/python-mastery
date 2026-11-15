"""Reference solutions for 2.03. Try the exercises yourself first!"""
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
        self.id = Ticket.next_id
        Ticket.next_id += 1
        self.title = title
        self.done = False

    def close(self) -> None:
        self.done = True


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
        self.owner = owner
        self.balance = balance
        self.transactions: list[tuple[str, float]] = []

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount
        self.transactions.append(("deposit", amount))
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        self.transactions.append(("withdraw", amount))
        return self.balance


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
        super().__init__(owner, balance)
        self.rate = rate

    def add_interest(self) -> float:
        interest = self.balance * self.rate
        if interest == 0:
            return self.balance
        return self.deposit(interest)


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
        self.name = name

    def speak(self) -> str:
        return "..."

    def intro(self) -> str:
        return f"{self.name} says {self.speak()}"


class Dog(Animal):
    """An Animal whose `speak()` returns "Woof"."""

    def speak(self) -> str:
        return "Woof"


class Puppy(Dog):
    """A Dog whose `speak()` is the Dog's sound followed by "!" ("Woof!").

    Use `super().speak()` rather than hard-coding "Woof".
    """

    def speak(self) -> str:
        return super().speak() + "!"


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
        return f"{type(self).__name__} with area {self.area():.2f}"


class Rectangle(Shape):
    """`Rectangle(width, height)`; `area()` and `perimeter()` as expected.

    >>> Rectangle(3, 4).area()
    12
    >>> Rectangle(3, 4).perimeter()
    14
    """

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def area(self) -> float:
        return self.width * self.height

    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Square(Rectangle):
    """`Square(side)` -- a Rectangle with equal sides.

    Reuse Rectangle through `super().__init__`. `describe()` must say "Square".
    """

    def __init__(self, side: float):
        super().__init__(side, side)


class Circle(Shape):
    """`Circle(radius)`; use `math.pi`. `perimeter()` is the circumference.

    >>> round(Circle(1).area(), 4)
    3.1416
    """

    def __init__(self, radius: float):
        self.radius = radius

    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2

    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


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
        self._items: dict[str, list[float]] = {}  # name -> [qty, price]

    def add(self, name: str, qty: int, price: float) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self._items:
            self._items[name][0] += qty
            self._items[name][1] = price
        else:
            self._items[name] = [qty, price]

    def remove(self, name: str, qty: int) -> None:
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name not in self._items or self._items[name][0] < qty:
            raise ValueError(f"not enough {name}")
        self._items[name][0] -= qty

    def quantity(self, name: str) -> int:
        return self._items[name][0] if name in self._items else 0

    def total_value(self) -> float:
        return sum(qty * price for qty, price in self._items.values())

    def low_stock(self, threshold: int) -> list[str]:
        return sorted(n for n, (qty, _) in self._items.items() if qty < threshold)

    def __len__(self) -> int:
        return len(self._items)


class Engine:
    """An engine that can be started and stopped.

    `Engine(horsepower)`; attributes `horsepower` and `running` (False at first).
    `start()` / `stop()` set `running` accordingly.
    """

    def __init__(self, horsepower: int):
        self.horsepower = horsepower
        self.running = False

    def start(self) -> None:
        self.running = True

    def stop(self) -> None:
        self.running = False


class Car:
    """A car *has an* engine (composition, not inheritance).

    - `Car(make, engine)` stores both; `odometer` starts at 0.
    - `start()` / `stop()` delegate to the engine.
    - `drive(km)`: if the engine is not running raise RuntimeError; if km < 0
      raise ValueError; otherwise add km to `odometer` and return it.
    """

    def __init__(self, make: str, engine: Engine):
        self.make = make
        self.engine = engine
        self.odometer = 0

    def start(self) -> None:
        self.engine.start()

    def stop(self) -> None:
        self.engine.stop()

    def drive(self, km: float) -> float:
        if not self.engine.running:
            raise RuntimeError("engine is not running")
        if km < 0:
            raise ValueError("km must be >= 0")
        self.odometer += km
        return self.odometer
