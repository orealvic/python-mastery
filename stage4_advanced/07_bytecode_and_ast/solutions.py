"""Reference solutions for 4.07. Try the exercises yourself first!"""
import ast
import dis
import types


def count_defs_and_calls(source: str) -> dict:
    tree = ast.parse(source)
    funcs = calls = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs += 1
        elif isinstance(node, ast.Call):
            calls += 1
    return {"functions": funcs, "calls": calls}


def describe_code(source: str) -> dict:
    module_code = compile(source, "<exercise>", "exec")
    code = next(c for c in module_code.co_consts if isinstance(c, types.CodeType))
    return {
        "argcount": code.co_argcount,
        "varnames": tuple(code.co_varnames),
        "names": tuple(sorted(set(code.co_names))),
    }


def dis_names(func) -> list:
    names = set(func.__code__.co_names)
    return sorted({i.argval for i in dis.get_instructions(func)
                   if isinstance(i.argval, str) and i.argval in names})


def imported_modules(source: str) -> list:
    found = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module:
                found.add(node.module.split(".")[0])
    return sorted(found)


class LintVisitor(ast.NodeVisitor):
    def __init__(self):
        self.problems = []

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.problems.append((node.lineno, "bare-except"))
        self.generic_visit(node)

    def _check_defaults(self, node):
        defaults = list(node.args.defaults) + [d for d in node.args.kw_defaults if d is not None]
        for d in defaults:
            if isinstance(d, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)):
                self.problems.append((d.lineno, "mutable-default"))
        self.generic_visit(node)

    visit_FunctionDef = _check_defaults
    visit_AsyncFunctionDef = _check_defaults
    visit_Lambda = _check_defaults


def lint(source: str) -> list:
    v = LintVisitor()
    v.visit(ast.parse(source))
    return sorted(v.problems)


class ConstantFolder(ast.NodeTransformer):
    _OPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b, ast.Mult: lambda a, b: a * b}

    @staticmethod
    def _is_num(n):
        return isinstance(n, ast.Constant) and type(n.value) in (int, float)

    def visit_BinOp(self, node):
        self.generic_visit(node)
        op = self._OPS.get(type(node.op))
        if op and self._is_num(node.left) and self._is_num(node.right):
            return ast.copy_location(ast.Constant(op(node.left.value, node.right.value)), node)
        return node

    def visit_UnaryOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.USub) and self._is_num(node.operand):
            return ast.copy_location(ast.Constant(-node.operand.value), node)
        return node


def fold_constants(source: str) -> str:
    tree = ConstantFolder().visit(ast.parse(source))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


_BIN = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
}


def safe_eval(expr: str):
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as e:
        raise ValueError(f"invalid expression: {e}") from None

    def ev(node):
        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value
            raise ValueError(f"constant not allowed: {node.value!r}")
        if isinstance(node, ast.BinOp) and type(node.op) in _BIN:
            return _BIN[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -ev(node.operand)
        raise ValueError(f"{type(node).__name__} not allowed")

    return ev(tree.body)


def rename_variable(source: str, old: str, new: str) -> str:
    class Renamer(ast.NodeTransformer):
        def visit_Name(self, node):
            if node.id == old:
                node.id = new
            return node

        def visit_arg(self, node):
            if node.arg == old:
                node.arg = new
            return node

    tree = Renamer().visit(ast.parse(source))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def complexity(source: str) -> int:
    total = 1
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler)):
            total += 1
        elif isinstance(node, ast.BoolOp):
            total += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            total += 1 + len(node.ifs)
    return total


def parse_literal(text: str, default=None):
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        return default
