import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_timer():
    t = ex.Timer()
    assert t.elapsed is None
    with t as t2:
        assert t2 is t
        sum(range(1000))
    assert isinstance(t.elapsed, float)
    assert t.elapsed >= 0


def test_timer_does_not_suppress():
    t = ex.Timer()
    try:
        with t:
            raise ValueError("x")
        assert False, "expected ValueError"
    except ValueError:
        pass
    assert t.elapsed is not None


def test_temp_env_var_new_variable():
    name = "PM_TEST_NEW_VAR"
    os.environ.pop(name, None)
    with ex.temp_env_var(name, "abc"):
        assert os.environ[name] == "abc"
    assert name not in os.environ


def test_temp_env_var_restores_existing_even_on_error():
    name = "PM_TEST_EXISTING_VAR"
    os.environ[name] = "original"
    try:
        with ex.temp_env_var(name, "temp"):
            assert os.environ[name] == "temp"
            raise KeyError("boom")
    except KeyError:
        pass
    assert os.environ[name] == "original"
    del os.environ[name]


def test_changed_directory(tmp_path):
    before = os.getcwd()
    sub = tmp_path / "sub"
    sub.mkdir()
    with ex.changed_directory(sub) as cwd:
        assert os.path.samefile(os.getcwd(), sub)
        assert os.path.samefile(cwd, sub)
        assert hasattr(cwd, "name")  # a pathlib.Path
    assert os.getcwd() == before
    try:
        with ex.changed_directory(tmp_path):
            raise KeyError("x")
    except KeyError:
        pass
    assert os.getcwd() == before


def test_transaction_commit():
    d = {"a": 1}
    with ex.Transaction(d) as t:
        assert t is d
        t["a"] = 2
        t["b"] = 3
    assert d == {"a": 2, "b": 3}


def test_transaction_rollback():
    d = {"a": 1, "b": 2}
    try:
        with ex.Transaction(d) as t:
            t["a"] = 100
            del t["b"]
            t["c"] = 3
            raise ValueError("fail")
        assert False, "exception should propagate"
    except ValueError as e:
        assert str(e) == "fail"
    assert d == {"a": 1, "b": 2}


def test_suppress_and_record():
    with ex.suppress_and_record(KeyError, ValueError) as errors:
        assert errors == []
        {}["x"]
        assert False, "not reached"
    assert len(errors) == 1
    assert isinstance(errors[0], KeyError)

    with ex.suppress_and_record(ValueError) as errors:
        int("zz")
    assert isinstance(errors[0], ValueError)

    with ex.suppress_and_record(ValueError) as errors:
        pass
    assert errors == []


def test_suppress_and_record_propagates_others():
    try:
        with ex.suppress_and_record(KeyError) as errors:
            raise TypeError("t")
        assert False, "expected TypeError"
    except TypeError:
        pass
    try:
        with ex.suppress_and_record() as errors:
            raise TypeError("t")
        assert False, "expected TypeError"
    except TypeError:
        pass


def test_capture_output():
    import sys
    original = sys.stdout
    with ex.capture_output() as out:
        print("hello")
        print("world", end="!")
    assert out.getvalue() == "hello\nworld!"
    assert sys.stdout is original


def test_open_all(tmp_path):
    paths = []
    for i in range(3):
        p = tmp_path / f"f{i}.txt"
        p.write_text(f"file {i}")
        paths.append(p)
    with ex.open_all(paths) as files:
        assert [f.read() for f in files] == ["file 0", "file 1", "file 2"]
    assert all(f.closed for f in files)


def test_open_all_closes_on_error(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("a")
    captured = []
    try:
        with ex.open_all([a]) as files:
            captured.extend(files)
            raise ValueError("body failed")
        assert False, "expected ValueError"
    except ValueError:
        pass
    assert captured[0].closed


def test_open_all_open_failure_closes_earlier(tmp_path):
    a = tmp_path / "a.txt"
    a.write_text("a")
    missing = tmp_path / "missing.txt"
    opened = []
    real_open = open

    import builtins

    def spy(*args, **kwargs):
        f = real_open(*args, **kwargs)
        opened.append(f)
        return f

    builtins.open = spy
    try:
        try:
            with ex.open_all([a, missing]):
                assert False, "should not enter"
            assert False, "expected FileNotFoundError"
        except FileNotFoundError:
            pass
    finally:
        builtins.open = real_open
    assert len(opened) == 1 and opened[0].closed


def test_indenter():
    ind = ex.Indenter("  ")
    assert ind.depth == 0
    assert ind.line("root") == "root"
    with ind as same:
        assert same is ind
        assert ind.depth == 1
        assert ind.line("child") == "  child"
        with ind:
            assert ind.line("leaf") == "    leaf"
    assert ind.depth == 0
    assert ind.line("back") == "back"
    assert ex.Indenter().line("x") == "x"


def test_indenter_restores_on_exception():
    ind = ex.Indenter()
    try:
        with ind:
            raise ValueError
    except ValueError:
        pass
    assert ind.depth == 0
    assert ind.line("x") == "x"
