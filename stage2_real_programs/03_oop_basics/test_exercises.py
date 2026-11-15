import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def test_ticket():
    ex.Ticket.next_id = 1
    a, b = ex.Ticket("login bug"), ex.Ticket("typo")
    assert (a.id, b.id) == (1, 2)
    assert ex.Ticket.next_id == 3
    assert a.title == "login bug" and a.done is False
    a.close()
    assert a.done is True and b.done is False
    assert "next_id" not in vars(a)  # shared state lives on the class


def test_bank_account_basic():
    acct = ex.BankAccount("Ada", 100)
    assert acct.owner == "Ada"
    assert acct.deposit(50) == 150
    assert acct.withdraw(30) == 120
    assert acct.balance == 120
    assert acct.transactions == [("deposit", 50), ("withdraw", 30)]
    assert ex.BankAccount("Bob").balance == 0


def test_bank_account_errors():
    acct = ex.BankAccount("Ada", 100)
    assert raises(ValueError, acct.deposit, 0)
    assert raises(ValueError, acct.deposit, -5)
    assert raises(ValueError, acct.withdraw, 0)
    assert raises(ValueError, acct.withdraw, 101)
    assert acct.balance == 100
    assert acct.transactions == []
    assert acct.withdraw(100) == 0  # exact balance is allowed


def test_bank_account_instances_are_independent():
    a, b = ex.BankAccount("A"), ex.BankAccount("B")
    a.deposit(10)
    assert b.transactions == [] and b.balance == 0


def test_savings_account():
    s = ex.SavingsAccount("Ada", 1000, rate=0.05)
    assert isinstance(s, ex.BankAccount)
    assert s.rate == 0.05
    assert s.add_interest() == 1050.0
    assert s.transactions == [("deposit", 50.0)]
    assert s.withdraw(50.0) == 1000.0
    assert ex.SavingsAccount("Bob").rate == 0.02
    z = ex.SavingsAccount("Zed")
    assert z.add_interest() == 0
    assert z.transactions == []


def test_animals():
    assert ex.Animal("Generic").intro() == "Generic says ..."
    assert ex.Dog("Rex").intro() == "Rex says Woof"
    assert ex.Puppy("Bit").speak() == "Woof!"
    assert ex.Puppy("Bit").intro() == "Bit says Woof!"
    assert issubclass(ex.Puppy, ex.Dog) and issubclass(ex.Dog, ex.Animal)
    assert ex.Dog("Rex").name == "Rex"


def test_shapes():
    r = ex.Rectangle(3, 4)
    assert r.area() == 12 and r.perimeter() == 14
    s = ex.Square(5)
    assert s.area() == 25 and s.perimeter() == 20
    assert isinstance(s, ex.Rectangle) and isinstance(s, ex.Shape)
    assert s.width == 5 and s.height == 5
    c = ex.Circle(1)
    assert abs(c.area() - 3.141592653589793) < 1e-9
    assert abs(c.perimeter() - 6.283185307179586) < 1e-9


def test_shape_describe():
    assert ex.Rectangle(3, 4).describe() == "Rectangle with area 12.00"
    assert ex.Square(2).describe() == "Square with area 4.00"
    assert ex.Circle(1).describe() == "Circle with area 3.14"


def test_inventory():
    inv = ex.Inventory()
    assert len(inv) == 0 and inv.quantity("apple") == 0 and inv.total_value() == 0
    inv.add("apple", 10, 0.5)
    inv.add("pear", 2, 1.0)
    inv.remove("apple", 4)
    assert inv.quantity("apple") == 6
    assert inv.total_value() == 5.0
    assert len(inv) == 2
    inv.add("apple", 4, 1.0)  # quantity grows, price replaced
    assert inv.quantity("apple") == 10
    assert inv.total_value() == 12.0
    assert inv.low_stock(5) == ["pear"]
    assert inv.low_stock(11) == ["apple", "pear"]
    assert inv.low_stock(0) == []


def test_inventory_errors():
    inv = ex.Inventory()
    inv.add("a", 3, 1.0)
    assert raises(ValueError, inv.add, "b", 0, 1.0)
    assert raises(ValueError, inv.remove, "a", 4)
    assert raises(ValueError, inv.remove, "zzz", 1)
    assert raises(ValueError, inv.remove, "a", 0)
    assert inv.quantity("a") == 3
    inv.remove("a", 3)
    assert inv.quantity("a") == 0 and len(inv) == 1 and inv.low_stock(1) == ["a"]


def test_inventories_are_independent():
    a, b = ex.Inventory(), ex.Inventory()
    a.add("x", 1, 1.0)
    assert len(b) == 0


def test_engine_and_car():
    e = ex.Engine(150)
    assert e.horsepower == 150 and e.running is False
    car = ex.Car("Mini", e)
    assert car.engine is e and car.make == "Mini" and car.odometer == 0
    assert raises(RuntimeError, car.drive, 10)
    car.start()
    assert e.running is True
    assert car.drive(10) == 10
    assert car.drive(5.5) == 15.5
    assert raises(ValueError, car.drive, -1)
    car.stop()
    assert e.running is False
    assert raises(RuntimeError, car.drive, 1)
    assert car.odometer == 15.5
