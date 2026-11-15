import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_celsius_to_fahrenheit():
    assert ex.celsius_to_fahrenheit(0) == 32
    assert ex.celsius_to_fahrenheit(100) == 212
    assert ex.celsius_to_fahrenheit(-40) == -40
    assert abs(ex.celsius_to_fahrenheit(37) - 98.6) < 1e-9


def test_is_even():
    assert ex.is_even(4) is True
    assert ex.is_even(7) is False
    assert ex.is_even(0) is True
    assert ex.is_even(-2) is True


def test_split_bill():
    assert ex.split_bill(100, 3) == 33.33
    assert ex.split_bill(90, 3) == 30.0
    assert ex.split_bill(10, 4) == 2.5


def test_initials():
    assert ex.initials("ada lovelace") == "A.L."
    assert ex.initials("  grace   brewster  hopper ") == "G.B.H."
    assert ex.initials("Guido") == "G."


def test_is_palindrome():
    assert ex.is_palindrome("racecar") is True
    assert ex.is_palindrome("Never odd or even") is True
    assert ex.is_palindrome("python") is False
    assert ex.is_palindrome("") is True


def test_format_receipt_line():
    assert ex.format_receipt_line("Coffee", 2, 3.5) == "Coffee      x2      7.00"
    assert ex.format_receipt_line("Bagel", 10, 1.25) == "Bagel       x10    12.50"


def test_seconds_to_hms():
    assert ex.seconds_to_hms(0) == "0:00:00"
    assert ex.seconds_to_hms(59) == "0:00:59"
    assert ex.seconds_to_hms(3725) == "1:02:05"
    assert ex.seconds_to_hms(86399) == "23:59:59"
