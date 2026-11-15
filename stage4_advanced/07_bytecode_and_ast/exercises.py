"""4.07 — Bytecode & the AST

Replace each `raise NotImplementedError` with your implementation.
Run `python check.py 4.07` from the course root to test your work.

Visitor/transformer stubs raise NotImplementedError when *used*, so tests
that run them show as "not started" until implemented.
Tests never depend on specific opcode names (they change between versions).
"""
import ast
import dis
import types


def count_defs_and_calls(source: str) -> dict:
    """Parse `source` and count function definitions and calls.

    Returns {"functions": n, "calls": m} where
    - `functions` counts every `def` and `async def` (including nested
      functions and methods). Lambdas are NOT counted.
    - `calls` counts every `ast.Call` node (including calls nested in
      arguments, e.g. `f(g(1))` is 2 calls).

    >>> count_defs_and_calls("def f():\\n    return g(h(1))\\n")
    {'functions': 1, 'calls': 2}
    """
    raise NotImplementedError


def describe_code(source: str) -> dict:
    """Compile `source` (a module whose first statement is a `def`) and
    describe that function's code object.

    Use `compile(source, "<exercise>", "exec")`; the function's code object
    is the first `types.CodeType` in the module code's `co_consts`.
    Return {"argcount": co_argcount,
            "varnames": co_varnames (tuple),
            "names": sorted tuple of the distinct strings in co_names}.

    >>> describe_code("def f(a, b):\\n    c = a + b\\n    return len([c])\\n")
    {'argcount': 2, 'varnames': ('a', 'b', 'c'), 'names': ('len',)}
    """
    raise NotImplementedError


def dis_names(func) -> list:
    """Use `dis.get_instructions(func)` to list the global/attribute names
    that `func` refers to.

    Return the sorted list of distinct instruction `argval`s that are strings
    AND appear in `func.__code__.co_names`. Local variable names
    (co_varnames) are therefore excluded.

    >>> def f(x): return helper(x.attr) + len(x)
    >>> dis_names(f)
    ['attr', 'helper', 'len']
    """
    raise NotImplementedError


def imported_modules(source: str) -> list:
    """Return the sorted, de-duplicated list of TOP-LEVEL module names that
    `source` imports (anywhere, including inside functions).

    - `import os.path` -> "os"; `import a, b as c` -> "a", "b"
    - `from collections.abc import Mapping` -> "collections"
    - relative imports (`from . import x`, `from .pkg import y`) are ignored.

    >>> imported_modules("import os.path\\nfrom json import loads\\nfrom . import x")
    ['json', 'os']
    """
    raise NotImplementedError


class LintVisitor(ast.NodeVisitor):
    """NodeVisitor that records style problems in `self.problems`.

    `self.problems` is a list of (lineno, code) tuples (initialise it in
    `__init__`). Two codes exist:
    - "bare-except": an `except:` handler with no exception type;
      lineno is the handler's line.
    - "mutable-default": a function/async function/lambda parameter default
      (positional OR keyword-only) that is a list, dict or set literal or
      comprehension (`[]`, `{}`, `{1}`, `[x for x in y]`...); lineno is the
      default expression's line.
    Make sure nested nodes are still visited (call `generic_visit`).
    """

    def __init__(self):
        raise NotImplementedError

    def visit_ExceptHandler(self, node):
        raise NotImplementedError

    def visit_FunctionDef(self, node):
        raise NotImplementedError

    def visit_AsyncFunctionDef(self, node):
        raise NotImplementedError

    def visit_Lambda(self, node):
        raise NotImplementedError


def lint(source: str) -> list:
    """Run `LintVisitor` over `source` and return its problems sorted by
    (lineno, code).

    >>> lint("def f(a=[]):\\n    try:\\n        pass\\n    except:\\n        pass\\n")
    [(1, 'mutable-default'), (4, 'bare-except')]
    """
    raise NotImplementedError


class ConstantFolder(ast.NodeTransformer):
    """NodeTransformer that folds constant arithmetic.

    - A `BinOp` whose operator is `+`, `-` or `*` and whose two operands are
      (after folding their own children first) numeric constants -- `int` or
      `float`, NOT bool, NOT str -- is replaced by a single `ast.Constant`
      holding the result.
    - A unary minus applied to a numeric constant is folded too.
    - Anything else is left alone (but its children are still processed).
    Return the new node from the `visit_*` methods.
    """

    def visit_BinOp(self, node):
        raise NotImplementedError

    def visit_UnaryOp(self, node):
        raise NotImplementedError


def fold_constants(source: str) -> str:
    """Parse `source`, apply `ConstantFolder`, call
    `ast.fix_missing_locations` on the tree, and return `ast.unparse(tree)`.

    >>> fold_constants("x = a + 2 * 3")
    'x = a + 6'
    >>> fold_constants("y = 'a' + 'b'")
    "y = 'a' + 'b'"
    """
    raise NotImplementedError


def safe_eval(expr: str):
    """Evaluate an arithmetic expression WITHOUT using eval/exec.

    Parse with `ast.parse(expr.strip(), mode="eval")` and walk the tree.
    Allowed: int/float constants (not bool, not strings, not complex),
    binary `+ - * / **`, unary minus `-`, and parentheses (which are not
    nodes). Everything else -- names, calls, attributes, comparisons, `//`,
    `%`, unary plus, f-strings, ternaries, ... -- raises ValueError, and so
    does text that is not valid Python syntax.

    >>> safe_eval("2 + 3 * 4")
    14
    >>> safe_eval("-(2 ** 3) / 4")
    -2.0
    >>> safe_eval("__import__('os')")
    Traceback (most recent call last):
    ValueError: ...
    """
    raise NotImplementedError


def rename_variable(source: str, old: str, new: str) -> str:
    """Rename the variable `old` to `new` and return the new source via
    `ast.unparse`.

    Rename every `ast.Name` whose id is `old` (loads, stores, deletes) and
    every function parameter (`ast.arg`) named `old`. Do NOT touch attribute
    names (`obj.old`), keyword-argument names (`f(old=1)`), or strings.
    Use a `NodeTransformer` (or visitor that mutates in place).

    >>> rename_variable("def f(x):\\n    return x * 2\\n", "x", "n")
    'def f(n):\\n    return n * 2'
    """
    raise NotImplementedError


def complexity(source: str) -> int:
    """Estimate the cyclomatic complexity of the whole of `source`.

    Start at 1 and add:
    - 1 for each `if` statement (an `elif` is a nested `if`), `if` expression
      (ternary), `for`, `async for`, `while`, and `except` handler;
    - (number of values - 1) for each `and`/`or` BoolOp (so `a and b or c`
      adds 2);
    - for each comprehension generator: 1 + the number of its `if` clauses.

    >>> complexity("x = 1")
    1
    >>> complexity("if a:\\n    pass\\nelif b:\\n    pass\\nelse:\\n    pass\\n")
    3
    """
    raise NotImplementedError


def parse_literal(text: str, default=None):
    """Safely turn the text of a Python literal into a value with
    `ast.literal_eval`.

    Return `default` if the text is not a valid literal (ValueError,
    SyntaxError, and also MemoryError/RecursionError for hostile input).

    >>> parse_literal("[1, 2, {'a': (3, None)}]")
    [1, 2, {'a': (3, None)}]
    >>> parse_literal("__import__('os').system('ls')", default="bad")
    'bad'
    """
    raise NotImplementedError
