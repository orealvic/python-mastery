import contextlib
import importlib
import io
import itertools
import logging
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))
_names = itertools.count()


def raises(exc, fn, *args):
    try:
        fn(*args)
    except exc:
        return True
    return False


def run_main(argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = ex.main(argv)
    return code, out.getvalue(), err.getvalue()


def parse_exit_code(parser, argv):
    err = io.StringIO()
    try:
        with contextlib.redirect_stderr(err):
            parser.parse_args(argv)
    except SystemExit as e:
        return e.code
    return None


def new_logger(level=logging.DEBUG):
    handler = ex.ListHandler()
    logger = ex.configure_logger(f"pm-test-{next(_names)}", level, handler)
    return logger, handler


def test_build_parser_defaults_and_options():
    p = ex.build_parser()
    a = p.parse_args(["Ada"])
    assert (a.name, a.times, a.shout, a.greeting) == ("Ada", 1, False, "Hello")
    a = p.parse_args(["Ada", "-n", "2", "--shout"])
    assert (a.name, a.times, a.shout, a.greeting) == ("Ada", 2, True, "Hello")
    a = p.parse_args(["--greeting", "Hi", "--times", "3", "-s", "Bob"])
    assert (a.name, a.times, a.shout, a.greeting) == ("Bob", 3, True, "Hi")
    a = p.parse_args(["-g", "Yo", "Eve"])
    assert a.greeting == "Yo"
    assert p.prog == "greet"


def test_build_parser_errors():
    p = ex.build_parser()
    assert parse_exit_code(p, []) == 2
    assert parse_exit_code(p, ["Ada", "--times", "abc"]) == 2
    assert parse_exit_code(p, ["Ada", "--unknown"]) == 2
    assert parse_exit_code(p, ["Ada"]) is None


def test_greet_lines():
    p = ex.build_parser()
    assert ex.greet_lines(p.parse_args(["Ada", "-g", "Hi"])) == ["Hi, Ada!"]
    assert ex.greet_lines(p.parse_args(["Ada", "-s", "-n", "2"])) == ["HELLO, ADA!", "HELLO, ADA!"]
    assert ex.greet_lines(p.parse_args(["Ada", "-n", "0"])) == []


def test_main_success_and_failure():
    assert run_main(["Ada", "-n", "2"]) == (0, "Hello, Ada!\nHello, Ada!\n", "")
    assert run_main(["Ada", "-s"]) == (0, "HELLO, ADA!\n", "")
    code, out, err = run_main(["Ada", "--times", "0"])
    assert code == 2 and out == "" and err == "error: --times must be >= 1\n"
    code, out, err = run_main(["Ada", "-n", "-3"])
    assert code == 2 and out == ""


def test_main_argparse_error_exits():
    try:
        run_main([])
    except SystemExit as e:
        assert e.code == 2
    else:
        raise AssertionError("argparse should exit with status 2 when name is missing")


def test_build_calc_parser():
    p = ex.build_calc_parser()
    a = p.parse_args(["--precision", "3", "add", "1", "2.5"])
    assert (a.command, a.numbers, a.precision) == ("add", [1.0, 2.5], 3)
    a = p.parse_args(["mul", "2", "3", "4"])
    assert (a.command, a.numbers, a.precision) == ("mul", [2.0, 3.0, 4.0], 2)
    assert p.prog == "calc"
    assert parse_exit_code(p, []) == 2                  # sub-command is required
    assert parse_exit_code(p, ["add"]) == 2             # needs at least one number
    assert parse_exit_code(p, ["div", "1"]) == 2        # unknown sub-command
    assert parse_exit_code(p, ["add", "x"]) == 2        # not a number


def test_run_calc():
    assert ex.run_calc(["add", "1", "2.5"]) == "3.50"
    assert ex.run_calc(["--precision", "0", "mul", "2", "3"]) == "6"
    assert ex.run_calc(["mul", "1.5", "2", "4"]) == "12.00"
    assert ex.run_calc(["--precision", "4", "add", "0.1", "0.2"]) == "0.3000"
    assert ex.run_calc(["add", "-1", "-2"]) == "-3.00"
    assert ex.run_calc(["add", "5"]) == "5.00"


def test_configure_logger():
    buf = io.StringIO()
    logger = ex.configure_logger("pm-test-config", logging.INFO, logging.StreamHandler(buf))
    assert isinstance(logger, logging.Logger) and logger.name == "pm-test-config"
    assert logger.level == logging.INFO and logger.propagate is False
    logger.debug("hidden")
    logger.info("hello %s", "world")
    logger.error("boom")
    assert buf.getvalue() == "INFO:pm-test-config:hello world\nERROR:pm-test-config:boom\n"


def test_configure_logger_twice_does_not_duplicate():
    name = f"pm-test-{next(_names)}"
    first, second = io.StringIO(), io.StringIO()
    ex.configure_logger(name, logging.DEBUG, logging.StreamHandler(first))
    logger = ex.configure_logger(name, logging.WARNING, logging.StreamHandler(second))
    logger.warning("once")
    logger.info("filtered")
    assert len(logger.handlers) == 1
    assert first.getvalue() == ""
    assert second.getvalue() == f"WARNING:{name}:once\n"


def test_list_handler():
    h = ex.ListHandler()
    assert isinstance(h, logging.Handler) and h.records == []
    logger = logging.getLogger(f"pm-test-{next(_names)}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(h)
    logger.info("a %d", 1)
    logger.error("b")
    assert h.messages() == ["a 1", "b"]
    assert h.levels() == ["INFO", "ERROR"]
    assert len(h.records) == 2 and h.records[0].levelno == logging.INFO


def test_list_handler_respects_level():
    h = ex.ListHandler(logging.WARNING)
    logger = logging.getLogger(f"pm-test-{next(_names)}")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.addHandler(h)
    logger.info("skip")
    logger.warning("keep")
    assert h.messages() == ["keep"]


def test_process_items():
    logger, h = new_logger()
    assert ex.process_items([1, -2, "x", 3], logger) == 4
    assert h.levels() == ["DEBUG", "WARNING", "ERROR", "DEBUG"]
    assert h.messages() == ["ok item: 1", "negative item: -2", "bad item: 'x'", "ok item: 3"]


def test_process_items_uses_lazy_args():
    logger, h = new_logger()
    ex.process_items([5, "y"], logger)
    assert h.records[0].msg == "ok item: %d" and h.records[0].args == (5,)
    assert h.records[1].msg == "bad item: %r" and h.records[1].args == ("y",)


def test_process_items_respects_logger_level_and_empty():
    logger, h = new_logger(logging.WARNING)
    assert ex.process_items([1, -1], logger) == 1
    assert h.levels() == ["WARNING"]
    logger2, h2 = new_logger()
    assert ex.process_items([], logger2) == 0 and h2.records == []
    assert ex.process_items([0, 0], logger2) == 0 and len(h2.records) == 2


def test_exit_code_for():
    f = ex.exit_code_for
    assert f(None) == 0
    assert f(KeyboardInterrupt()) == 130
    assert f(ValueError("x")) == 2
    assert f(FileNotFoundError("x")) == 74
    assert f(PermissionError()) == 74
    assert f(OSError()) == 74
    assert f(RuntimeError("x")) == 1
    assert f(KeyError("k")) == 1
    assert f(__import__("json").JSONDecodeError("m", "d", 0)) == 2  # a ValueError subclass


def test_run_cli():
    def capture(func, argv=()):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = ex.run_cli(func, list(argv))
        return code, err.getvalue()

    assert capture(lambda argv: 3) == (3, "")
    assert capture(lambda argv: None) == (0, "")
    assert capture(lambda argv: len(argv), ["a", "b"]) == (2, "")

    def bad_value(argv):
        raise ValueError("bad input")
    assert capture(bad_value) == (2, "error: bad input\n")

    def missing(argv):
        raise FileNotFoundError("nope.txt")
    assert capture(missing) == (74, "error: nope.txt\n")

    def crash(argv):
        raise RuntimeError("kaput")
    assert capture(crash) == (1, "error: kaput\n")

    def interrupted(argv):
        raise KeyboardInterrupt
    assert capture(interrupted) == (130, "interrupted\n")


def test_run_cli_lets_system_exit_through():
    def exits(argv):
        raise SystemExit(5)
    try:
        ex.run_cli(exits, [])
    except SystemExit as e:
        assert e.code == 5
    else:
        raise AssertionError("SystemExit must propagate")
