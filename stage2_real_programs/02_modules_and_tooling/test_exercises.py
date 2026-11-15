import importlib
import os

ex = importlib.import_module(os.environ.get("PM_TARGET", "exercises"))


def test_parse_requirement():
    assert ex.parse_requirement("requests>=2.31") == ("requests", ">=", "2.31")
    assert ex.parse_requirement("  Flask == 3.0.0   # web framework") == ("Flask", "==", "3.0.0")
    assert ex.parse_requirement("pytest") == ("pytest", "", "")
    assert ex.parse_requirement("numpy~=1.26") == ("numpy", "~=", "1.26")
    assert ex.parse_requirement("django<5") == ("django", "<", "5")
    assert ex.parse_requirement("a!=1.0") == ("a", "!=", "1.0")
    assert ex.parse_requirement("my_pkg-x.y <= 2") == ("my_pkg-x.y", "<=", "2")
    assert ex.parse_requirement("") is None
    assert ex.parse_requirement("   ") is None
    assert ex.parse_requirement("# just a comment") is None
    assert ex.parse_requirement("  pytest  # test runner") == ("pytest", "", "")


def test_normalize_requirements():
    lines = ["Flask==3", "# hi", "requests", "typing_extensions", "flask", ""]
    assert ex.normalize_requirements(lines) == ["flask", "requests", "typing-extensions"]
    assert ex.normalize_requirements([]) == []
    assert ex.normalize_requirements(["Zope.Interface>=5", "zope-interface"]) == ["zope-interface"]
    assert ex.normalize_requirements(["b", "a", "c>=1"]) == ["a", "b", "c"]


def test_parse_config_basic():
    text = 'name = "demo"\n[tool]\nline = 88\nfast = true'
    assert ex.parse_config(text) == {"": {"name": "demo"}, "tool": {"line": 88, "fast": True}}


def test_parse_config_details():
    text = """
# a comment
[project]
name = "my app"
debug = false
offset = -5
url = http://x.test/?a=b
empty = ""

[empty_section]
[project]
name = "second"
"""
    cfg = ex.parse_config(text)
    assert "" not in cfg
    assert cfg["project"]["name"] == "second"
    assert cfg["project"]["debug"] is False
    assert cfg["project"]["offset"] == -5
    assert cfg["project"]["url"] == "http://x.test/?a=b"
    assert cfg["project"]["empty"] == ""
    assert cfg["empty_section"] == {}
    assert ex.parse_config("") == {}
    assert ex.parse_config("  [ a ] \n x=1 ") == {"a": {"x": 1}}


def test_parse_config_invalid():
    try:
        ex.parse_config("[a]\nnot a pair")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_module_path_to_dotted():
    assert ex.module_path_to_dotted("src/mypkg/utils/io.py") == "mypkg.utils.io"
    assert ex.module_path_to_dotted("src/mypkg/__init__.py") == "mypkg"
    assert ex.module_path_to_dotted("tools/build.py") == "tools.build"
    assert ex.module_path_to_dotted("main.py") == "main"
    assert ex.module_path_to_dotted("lib/a/b.py", root="lib") == "a.b"
    assert ex.module_path_to_dotted("src/src/x.py") == "src.x"
    assert ex.module_path_to_dotted("src/pkg/sub/__init__.py") == "pkg.sub"
    try:
        ex.module_path_to_dotted("src/pkg/data.json")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_resolve_relative():
    r = ex.resolve_relative
    assert r("pkg.sub.mod", ".sibling") == "pkg.sub.sibling"
    assert r("pkg.sub.mod", "..other.thing") == "pkg.other.thing"
    assert r("pkg.sub", ".child", is_package=True) == "pkg.sub.child"
    assert r("pkg.sub", "..other", is_package=True) == "pkg.other"
    assert r("pkg.mod", ".") == "pkg"
    assert r("pkg.sub.mod", "..") == "pkg"
    assert r("pkg.sub", ".", is_package=True) == "pkg.sub"
    assert r("pkg.mod", "os.path") == "os.path"
    assert r("pkg", ".a", is_package=True) == "pkg.a"


def test_resolve_relative_errors():
    for args in [("pkg.mod", "..x"), ("top", ".x"), ("pkg", "..x", True)]:
        try:
            ex.resolve_relative(*args)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {args}")


def test_build_pyproject():
    assert ex.build_pyproject("demo", "0.1.0", []) == (
        '[project]\nname = "demo"\nversion = "0.1.0"\ndependencies = []\n'
    )
    assert ex.build_pyproject("demo", "1.0", ["requests>=2", "rich"]) == (
        '[project]\nname = "demo"\nversion = "1.0"\n'
        'dependencies = [\n    "requests>=2",\n    "rich",\n]\n'
    )


def test_find_missing_imports():
    src = "import os\nimport requests.adapters\nfrom rich import print\n"
    assert ex.find_missing_imports(src, {"os"}) == ["requests", "rich"]
    assert ex.find_missing_imports("", set()) == []
    assert ex.find_missing_imports("from . import x\nfrom .m import y\n", set()) == []
    assert ex.find_missing_imports("def f():\n    import numpy as np\n    from a.b import c\n", set()) == ["a", "numpy"]
    assert ex.find_missing_imports("import a, b\nimport a\n", {"b"}) == ["a"]
    assert ex.find_missing_imports("import os", {"os", "sys"}) == []


def test_entry_message():
    assert ex.entry_message("__main__") == "running as script"
    assert ex.entry_message("mypkg.tools") == "imported as mypkg.tools"
