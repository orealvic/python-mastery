import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_fizzbuzz():
    assert ex.fizzbuzz(0) == []
    assert ex.fizzbuzz(5) == ["1", "2", "Fizz", "4", "Buzz"]
    out = ex.fizzbuzz(15)
    assert len(out) == 15
    assert out[14] == "FizzBuzz"
    assert out[9] == "Buzz"
    assert out[11] == "Fizz"


def test_letter_grade():
    assert ex.letter_grade(100) == "A"
    assert ex.letter_grade(90) == "A"
    assert ex.letter_grade(89) == "B"
    assert ex.letter_grade(80) == "B"
    assert ex.letter_grade(79) == "C"
    assert ex.letter_grade(70) == "C"
    assert ex.letter_grade(69) == "D"
    assert ex.letter_grade(60) == "D"
    assert ex.letter_grade(59) == "F"
    assert ex.letter_grade(0) == "F"


def test_letter_grade_invalid():
    for bad in (-1, 101):
        try:
            ex.letter_grade(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad}")


def test_count_truthy():
    assert ex.count_truthy([0, 1, "", "a", None, [], [0]]) == 3
    assert ex.count_truthy([]) == 0
    assert ex.count_truthy([0, 0.0, "", None, False]) == 0
    assert ex.count_truthy(["0", " ", True]) == 3


def test_running_totals():
    assert ex.running_totals([1, 2, 3, 4]) == [1, 3, 6, 10]
    assert ex.running_totals([]) == []
    assert ex.running_totals([5, -5, 5]) == [5, 0, 5]
    data = [1, 2, 3]
    ex.running_totals(data)
    assert data == [1, 2, 3]


def test_numbered():
    assert ex.numbered(["eggs", "milk"]) == ["1. eggs", "2. milk"]
    assert ex.numbered([]) == []
    assert ex.numbered(["a"] * 10)[9] == "10. a"


def test_pair_scores():
    assert ex.pair_scores(["ann", "bob", "cy"], [90, 72]) == {"ann": 90, "bob": 72}
    assert ex.pair_scores(["ann"], [1, 2, 3]) == {"ann": 1}
    assert ex.pair_scores([], []) == {}


def test_first_repeated():
    assert ex.first_repeated([3, 1, 4, 1, 5, 3]) == 1
    assert ex.first_repeated([1, 2, 3]) is None
    assert ex.first_repeated([]) is None
    assert ex.first_repeated(["a", "b", "b", "a"]) == "b"
    assert ex.first_repeated([0, 0]) == 0


def test_collatz_steps():
    assert ex.collatz_steps(1) == 0
    assert ex.collatz_steps(2) == 1
    assert ex.collatz_steps(6) == 8
    assert ex.collatz_steps(27) == 111


def test_collatz_invalid():
    for bad in (0, -5):
        try:
            ex.collatz_steps(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {bad}")


def test_is_prime():
    primes = [2, 3, 5, 7, 11, 13, 97, 7919]
    non_primes = [-7, 0, 1, 4, 9, 15, 25, 49, 100, 7917]
    for p in primes:
        assert ex.is_prime(p) is True, p
    for n in non_primes:
        assert ex.is_prime(n) is False, n


def test_primes_up_to():
    assert ex.primes_up_to(20) == [2, 3, 5, 7, 11, 13, 17, 19]
    assert ex.primes_up_to(2) == [2]
    assert ex.primes_up_to(1) == []
    assert ex.primes_up_to(0) == []
    assert len(ex.primes_up_to(100)) == 25
