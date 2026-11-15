import importlib
import os
import random
from datetime import datetime
from unittest.mock import Mock, MagicMock, call, patch

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_slugify():
    assert ex.slugify("Hello, World!") == "hello-world"
    assert ex.slugify("  spaces   everywhere  ") == "spaces-everywhere"
    assert ex.slugify("a--b__c") == "a-b-c"
    assert ex.slugify("!!!") == ""
    assert ex.slugify("") == ""
    assert ex.slugify("Python 3.14") == "python-3-14"


def test_greeting_boundaries():
    def at(h, m=0):
        return lambda: datetime(2024, 1, 1, h, m)

    assert ex.greeting(at(0)) == "Good morning"
    assert ex.greeting(at(11, 59)) == "Good morning"
    assert ex.greeting(at(12)) == "Good afternoon"
    assert ex.greeting(at(17, 59)) == "Good afternoon"
    assert ex.greeting(at(18)) == "Good evening"
    assert ex.greeting(at(23)) == "Good evening"


def test_greeting_default_clock_is_patchable():
    assert ex.greeting() in {"Good morning", "Good afternoon", "Good evening"}


def test_roll_dice_deterministic():
    a = ex.roll_dice(5, random.Random(42))
    b = ex.roll_dice(5, random.Random(42))
    assert a == b
    assert len(a) == 5 and all(1 <= d <= 6 for d in a)
    assert ex.roll_dice(0) == []
    expected = random.Random(7)
    assert ex.roll_dice(4, random.Random(7)) == [expected.randint(1, 6) for _ in range(4)]


def test_roll_dice_uses_injected_rng():
    rng = Mock()
    rng.randint.side_effect = [3, 1, 6]
    assert ex.roll_dice(3, rng) == [3, 1, 6]
    assert rng.randint.call_args_list == [call(1, 6)] * 3
    assert all(1 <= d <= 6 for d in ex.roll_dice(20))


def test_roll_dice_negative():
    try:
        ex.roll_dice(-1)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_fetch_with_retry_success_first_try():
    sleep = Mock()
    fetch = Mock(return_value="data")
    assert ex.fetch_with_retry(fetch, sleep=sleep) == "data"
    fetch.assert_called_once_with()
    sleep.assert_not_called()


def test_fetch_with_retry_backoff():
    sleep = Mock()
    fetch = Mock(side_effect=[ConnectionError("a"), TimeoutError("b"), "ok"])
    assert ex.fetch_with_retry(fetch, retries=3, delay=0.5, sleep=sleep) == "ok"
    assert fetch.call_count == 3
    assert sleep.call_args_list == [call(0.5), call(1.0)]


def test_fetch_with_retry_exhausted():
    sleep = Mock()
    fetch = Mock(side_effect=[ValueError("1"), ValueError("2"), ValueError("3")])
    try:
        ex.fetch_with_retry(fetch, retries=2, delay=1, sleep=sleep)
        assert False, "expected ValueError"
    except ValueError as e:
        assert str(e) == "3"
    assert fetch.call_count == 3
    assert sleep.call_args_list == [call(1), call(2)]  # no sleep after last failure


def test_fetch_with_retry_does_not_catch_base_exceptions():
    fetch = Mock(side_effect=KeyboardInterrupt)
    sleep = Mock()
    try:
        ex.fetch_with_retry(fetch, sleep=sleep)
        assert False, "expected KeyboardInterrupt"
    except KeyboardInterrupt:
        pass
    assert fetch.call_count == 1


def test_calls_summary():
    m = Mock()
    m(1, "a", x=3)
    m()
    m(None, k=[1])
    assert ex.calls_summary(m, "f") == ["f(1, 'a', x=3)", "f()", "f(None, k=[1])"]
    assert ex.calls_summary(Mock()) == []
    m2 = Mock()
    m2(1)
    assert ex.calls_summary(m2) == ["mock(1)"]


def test_fake_repo_save_and_get():
    repo = ex.FakeUserRepository()
    saved = repo.save({"name": "ada"})
    assert saved == {"name": "ada", "id": 1}
    assert repo.save({"name": "bob"})["id"] == 2
    assert repo.get(1) == {"name": "ada", "id": 1}
    assert repo.get(99) is None
    assert repo.save({"name": "zed", "id": 10})["id"] == 10
    assert repo.save({"name": "next"})["id"] == 11
    assert repo.save({"name": "ADA", "id": 1}) == {"name": "ADA", "id": 1}
    assert repo.get(1)["name"] == "ADA"


def test_fake_repo_copies_and_all_and_delete():
    repo = ex.FakeUserRepository()
    original = {"name": "ada"}
    saved = repo.save(original)
    original["name"] = "mutated"
    saved["name"] = "mutated too"
    got = repo.get(1)
    assert got["name"] == "ada"
    got["name"] = "changed"
    assert repo.get(1)["name"] == "ada"
    repo.save({"name": "b", "id": 5})
    repo.save({"name": "c", "id": 3})
    assert [u["id"] for u in repo.all()] == [1, 3, 5]
    assert repo.delete(3) is True
    assert repo.delete(3) is False
    assert [u["id"] for u in repo.all()] == [1, 5]


def test_fake_repo_records_calls():
    repo = ex.FakeUserRepository()
    assert repo.calls == []
    repo.save({"n": 1})
    repo.get(1)
    repo.all()
    repo.delete(1)
    assert repo.calls == [("save",), ("get",), ("all",), ("delete",)]


def test_register_user_happy_path():
    repo = MagicMock()
    repo.save.return_value = {"id": 7, "name": "Ada", "email": "a@x.io"}
    mailer = Mock()
    result = ex.register_user("  Ada ", "a@x.io", repo, mailer)
    assert result == {"id": 7, "name": "Ada", "email": "a@x.io"}
    repo.save.assert_called_once_with({"name": "Ada", "email": "a@x.io"})
    mailer.send.assert_called_once_with(to="a@x.io", subject="Welcome, Ada!")


def test_register_user_validation_has_no_side_effects():
    for name, email in [("Ada", "not-an-email"), ("   ", "a@x.io"), ("", "")]:
        repo, mailer = Mock(), Mock()
        try:
            ex.register_user(name, email, repo, mailer)
            assert False, "expected ValueError"
        except ValueError:
            pass
        repo.save.assert_not_called()
        mailer.send.assert_not_called()


def test_make_spy():
    def add(a, b=0):
        """Add."""
        return a + b

    spy = ex.make_spy(add)
    assert spy(1, 2) == 3
    assert spy(5, b=1) == 6
    assert spy.call_count == 2
    assert spy.calls == [((1, 2), {}), ((5,), {"b": 1})]
    assert spy.results == [3, 6]
    assert spy.__name__ == "add"


def test_make_spy_records_failing_calls():
    def boom(x):
        raise KeyError(x)

    spy = ex.make_spy(boom)
    try:
        spy("k")
        assert False, "expected KeyError"
    except KeyError:
        pass
    assert spy.call_count == 1
    assert spy.calls == [(("k",), {})]
    assert spy.results == []


def test_parametrize_runs_all_cases():
    seen = []

    @ex.parametrize("a, b, expected", [(1, 2, 3), (2, 2, 4), (0, 0, 0)])
    def check_add(a, b, expected):
        seen.append((a, b))
        assert a + b == expected

    assert check_add.case_count == 3
    assert check_add.__name__ == "check_add"
    assert check_add() is None
    assert seen == [(1, 2), (2, 2), (0, 0)]


def test_parametrize_single_name_and_failures():
    seen = []

    @ex.parametrize("n", [1, 2, 3, 4])
    def check(n):
        seen.append(n)
        assert n % 2 == 1, "even!"

    try:
        check()
        assert False, "expected AssertionError"
    except AssertionError as e:
        msg = str(e)
        assert "case 1" in msg and "case 3" in msg
        assert "case 0" not in msg and "case 2" not in msg
        assert "'n': 2" in msg
    assert seen == [1, 2, 3, 4]  # failures did not stop the run


def test_parametrize_multi_failure_message():
    @ex.parametrize("a,b,expected", [(1, 1, 2), (2, 2, 5)])
    def check(a, b, expected):
        assert a + b == expected

    try:
        check()
        assert False, "expected AssertionError"
    except AssertionError as e:
        assert "case 1: {'a': 2, 'b': 2, 'expected': 5}" in str(e)
