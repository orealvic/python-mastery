# 3.06 — Testing

## Learning goals
- Write and run tests with **pytest**: asserts, fixtures, `parametrize`, `monkeypatch`, `tmp_path`
- Test exceptions, files, and time/randomness without flakiness
- Use `unittest.mock` (`Mock`, `MagicMock`, `patch`) and know when *not* to
- Design code for testability (dependency injection, pure functions)
- Measure coverage and practise TDD

> This course's runner (`check.py`) is a tiny stand-in for pytest. Your tests here are
> pytest-compatible: once you `pip install pytest`, `pytest` runs the same files. The
> exercises in this module are about the *design and tools* behind good tests, using only the stdlib.

## 1. pytest in 5 minutes

```bash
pip install pytest pytest-cov
pytest                      # discover test_*.py files, run test_* functions
pytest -x -q                # stop at first failure, quiet
pytest -k "slug and not unicode"   # select by name
pytest path/test_x.py::test_name   # one test
pytest --lf                 # re-run only last failures
pytest -s                   # don't capture print output
```

A test is a plain function with plain `assert`; pytest rewrites asserts to show detailed diffs:

```python
def test_slugify():
    assert slugify("Hello, World!") == "hello-world"
```

Testing exceptions:

```python
import pytest

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError, match="division"):
        1 / 0
```

Floats: `assert 0.1 + 0.2 == pytest.approx(0.3)`.

## 2. Fixtures

A **fixture** is reusable setup (and optional teardown), requested by naming it as a parameter:

```python
import pytest

@pytest.fixture
def user():
    return {"name": "ada", "id": 1}

@pytest.fixture
def db(tmp_path):                      # fixtures can request other fixtures
    conn = sqlite3.connect(tmp_path / "t.db")
    yield conn                         # test runs here
    conn.close()                       # teardown, even if the test failed

def test_user_name(user):
    assert user["name"] == "ada"
```

Scope: `@pytest.fixture(scope="module")` shares one instance across a module (also `"session"`).
Put shared fixtures in `conftest.py`; pytest finds them automatically.

Built-ins you'll use constantly:

| Fixture | Gives you |
|---|---|
| `tmp_path` | a fresh `pathlib.Path` temp directory per test |
| `monkeypatch` | safely patch attributes, dict items, env vars, cwd (auto-undone) |
| `capsys` | captured stdout/stderr: `capsys.readouterr().out` |
| `caplog` | captured log records |
| `request` | info about the requesting test |

## 3. `parametrize`: one test, many cases

```python
@pytest.mark.parametrize(
    "text, expected",
    [
        ("Hello World", "hello-world"),
        ("  spaces  ", "spaces"),
        ("a--b", "a-b"),
    ],
)
def test_slugify(text, expected):
    assert slugify(text) == expected
```

Each case is reported separately. Use `ids=[...]` for readable names, and stack decorators
for the cross-product. (One exercise has you build a mini version.)

## 4. `monkeypatch`

```python
def test_reads_env(monkeypatch):
    monkeypatch.setenv("APP_MODE", "test")
    assert get_mode() == "test"

def test_no_network(monkeypatch):
    monkeypatch.setattr("mymodule.requests.get", lambda *a, **k: FakeResponse())
```

Everything is restored at the end of the test, even on failure.

## 5. Mocking with `unittest.mock`

```python
from unittest.mock import Mock, MagicMock, patch

m = Mock(return_value=42)
m(1, x=2)                         # 42
m.assert_called_once_with(1, x=2)
m.call_args_list                  # [call(1, x=2)]

api = Mock()
api.get_user.return_value = {"id": 1}
api.get_user(1)
api.get_user.assert_called_with(1)

flaky = Mock(side_effect=[ConnectionError, ConnectionError, "ok"])   # sequence/exception
```

`patch` replaces a name **where it is looked up**, for the duration of a block:

```python
# mymodule.py:   from time import sleep   → patch "mymodule.sleep", NOT "time.sleep"
with patch("mymodule.sleep") as fake_sleep:
    run()
    fake_sleep.assert_called_once_with(1)

@patch("mymodule.requests.get")
def test_x(mock_get): ...
```

`create_autospec(real_function)` / `Mock(spec=Class)` make mocks refuse calls that the real
object wouldn't accept — much safer than a bare `Mock`.

**Don't over-mock.** Tests that assert on implementation details break on every refactor.
Prefer: real objects > fakes (small working in-memory versions) > stubs (canned answers)
> mocks (verify interactions). Mock *at the boundaries* (network, clock, disk, randomness).

## 6. Designing for testability

Hard to test:

```python
def greeting():
    hour = datetime.now().hour        # hidden dependency on the real clock
    return "Good morning" if hour < 12 else "Good afternoon"
```

Easy to test — **inject the dependency**:

```python
def greeting(now=datetime.now):       # default keeps production code unchanged
    ...
assert greeting(now=lambda: datetime(2024, 1, 1, 9)) == "Good morning"
```

Same idea for randomness (`rng: random.Random`), sleeping (`sleep=time.sleep`), HTTP clients,
repositories, and file systems. More rules of thumb:

- Prefer **pure functions** (inputs -> outputs, no side effects); push I/O to the edges.
- Depend on a small interface (`Protocol`), not a concrete class; swap in a **fake** in tests.
- Avoid global state, or reset it in a fixture.
- One behaviour per test; name tests after the behaviour (`test_rejects_negative_price`).
- Arrange – Act – Assert.

## 7. Coverage

```bash
pytest --cov=mypackage --cov-report=term-missing
pytest --cov=mypackage --cov-fail-under=80
```

Coverage tells you which lines *never ran* — it can't tell you the tests are good. 100% line coverage
with no assertions is worthless. Use `--cov-branch` to include `if` branches. Treat low numbers as a
prompt to investigate, not a score to game.

## 8. TDD: red, green, refactor

1. **Red** — write one small failing test for the next behaviour.
2. **Green** — write the simplest code that passes.
3. **Refactor** — clean up with the tests as a safety net.

Benefits: you design the API from the caller's viewpoint, and every line exists because a test needed it.
Also: when you find a bug, first write a test that reproduces it, then fix it (regression test).

## 9. Other testing tools worth knowing

| Tool | Use |
|---|---|
| `unittest` | stdlib framework (`TestCase`); pytest can run it too |
| `doctest` | run the `>>>` examples in docstrings |
| `hypothesis` | property-based testing (generates inputs for you) |
| `pytest-mock`, `freezegun`/`time-machine` | nicer mocking / freezing time |
| `tox` / `nox` | run tests across Python versions |
| `mypy` | static check complements tests (see 3.04) |

## Common mistakes
- **Patching the wrong name** (`time.sleep` instead of `mymodule.sleep`).
- **Tests that depend on each other** or on execution order; each test should set up its own state.
- **Mutable fixtures with a wide scope** leaking state between tests.
- **Asserting on mocks too much**, coupling tests to implementation.
- **`assert x == 0.3` with floats** — use `pytest.approx`.
- **Catching exceptions manually** and forgetting to fail if none is raised (use `pytest.raises`).
- **Real sleeps/clocks/networks in unit tests** — slow and flaky.
- **Chasing 100% coverage** instead of meaningful assertions.

## Practice
Open `exercises.py`, implement each, then run:

```bash
python check.py 3.06
```
