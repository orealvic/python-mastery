import ast
import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    return False


def test_count_defs_and_calls():
    src = "def f():\n    return g(h(1))\n\nclass C:\n    def m(self):\n        print(1)\n\nasync def a():\n    pass\n\nk = lambda: 0\n"
    assert ex.count_defs_and_calls(src) == {"functions": 3, "calls": 3}
    assert ex.count_defs_and_calls("x = 1") == {"functions": 0, "calls": 0}


def test_describe_code():
    info = ex.describe_code("def f(a, b):\n    c = a + b\n    return len([c])\n")
    assert info["argcount"] == 2
    assert tuple(info["varnames"]) == ("a", "b", "c")
    assert tuple(info["names"]) == ("len",)


def test_describe_code_names_sorted_distinct():
    info = ex.describe_code("def g(x):\n    return zeta(x) + alpha(x) + zeta(1)\n")
    assert info["argcount"] == 1
    assert tuple(info["names"]) == ("alpha", "zeta")
    assert tuple(info["varnames"]) == ("x",)


def test_dis_names():
    def f(x):
        y = x
        return helper(x.attr) + len(y)  # noqa: F821

    assert ex.dis_names(f) == ["attr", "helper", "len"]


def test_imported_modules():
    src = (
        "import os.path\nimport a, b as c\nfrom collections.abc import Mapping\n"
        "from . import x\nfrom .pkg import y\nimport os\n"
        "def f():\n    import json\n"
    )
    assert ex.imported_modules(src) == ["a", "b", "collections", "json", "os"]
    assert ex.imported_modules("x = 1") == []


def test_lint_bare_except():
    src = "try:\n    pass\nexcept:\n    pass\ntry:\n    pass\nexcept ValueError:\n    pass\n"
    assert ex.lint(src) == [(3, "bare-except")]


def test_lint_mutable_defaults():
    src = (
        "def f(a=[], b=1):\n    pass\n\n"
        "async def g(*, k={}):\n    pass\n\n"
        "h = lambda s={1}: s\n\n"
        "def ok(a=None, b=(1, 2)):\n    pass\n"
    )
    assert ex.lint(src) == [(1, "mutable-default"), (4, "mutable-default"), (7, "mutable-default")]


def test_lint_nested_and_clean():
    src = "def outer():\n    def inner(x=[]):\n        try:\n            pass\n        except:\n            pass\n"
    assert ex.lint(src) == [(2, "mutable-default"), (5, "bare-except")]
    assert ex.lint("x = 1\n") == []


def test_lint_visitor_class():
    v = ex.LintVisitor()
    assert isinstance(v, ast.NodeVisitor)
    v.visit(ast.parse("def f(a={}):\n    pass\n"))
    assert v.problems == [(1, "mutable-default")]


def test_fold_constants():
    assert ex.fold_constants("x = 2 * 3 + 4") == "x = 10"
    assert ex.fold_constants("x = a + 2 * 3") == "x = a + 6"
    assert ex.fold_constants("z = (1 + 2) * x") == "z = 3 * x"
    assert ex.fold_constants("y = 2 - -3") == "y = 5"
    assert ex.fold_constants("f(1 + 1, k=2.5 * 2)") == "f(2, k=5.0)"


def test_fold_constants_leaves_others():
    assert ex.fold_constants("y = 'a' + 'b'") == "y = 'a' + 'b'"
    assert ex.fold_constants("y = x + 1") == "y = x + 1"
    assert ex.fold_constants("y = 1 / 2") == "y = 1 / 2"


def test_constant_folder_is_transformer():
    tree = ast.parse("v = 1 + 2")
    new = ex.ConstantFolder().visit(tree)
    assign = new.body[0]
    assert isinstance(assign.value, ast.Constant) and assign.value.value == 3


def test_safe_eval_values():
    assert ex.safe_eval("2 + 3 * 4") == 14
    assert ex.safe_eval("-(2 ** 3) / 4") == -2.0
    assert ex.safe_eval("  10 / 4 ") == 2.5
    assert ex.safe_eval("--3") == 3
    assert ex.safe_eval("1.5 * 2") == 3.0


def test_safe_eval_rejects():
    for bad in ["__import__('os')", "x", "'a'", "True", "1 if 1 else 2", "2 // 3",
                "7 % 2", "+1", "(1).real", "abs(1)", "[1, 2]", "1 < 2", "1 +", "", "1j"]:
        assert raises(ValueError, ex.safe_eval, bad), bad


def test_rename_variable():
    src = "def f(x):\n    y = x + 1\n    return x * y\n"
    assert ex.rename_variable(src, "x", "t") == "def f(t):\n    y = t + 1\n    return t * y"


def test_rename_variable_leaves_attrs_and_strings():
    src = "x.x = f(x=x)\nprint('x')\ndel x\n"
    assert ex.rename_variable(src, "x", "t") == "t.x = f(x=t)\nprint('x')\ndel t"


def test_complexity():
    assert ex.complexity("x = 1") == 1
    assert ex.complexity("if a:\n    pass\nelif b:\n    pass\nelse:\n    pass\n") == 3
    assert ex.complexity("for i in r:\n    if i:\n        pass\n") == 3
    assert ex.complexity("x = a and b or c") == 3
    assert ex.complexity("try:\n    pass\nexcept A:\n    pass\nexcept B:\n    pass\n") == 3
    assert ex.complexity("while x:\n    pass\n") == 2
    assert ex.complexity("y = 1 if a else 2") == 2
    assert ex.complexity("y = [i for i in r if i if i > 1]") == 4


def test_parse_literal():
    assert ex.parse_literal("[1, 2, {'a': (3, None)}]") == [1, 2, {"a": (3, None)}]
    assert ex.parse_literal("  'hi'".strip()) == "hi"
    assert ex.parse_literal("__import__('os').system('ls')", default="bad") == "bad"
    assert ex.parse_literal("1 +") is None
    assert ex.parse_literal("name", default=0) == 0
