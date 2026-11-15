# 4.07 — Bytecode & the AST

## Learning goals
- Describe the pipeline source -> tokens -> AST -> bytecode -> evaluation loop
- Use `compile()` and inspect code objects (`co_names`, `co_varnames`, `co_consts`, `co_argcount`)
- Read `dis` output and `dis.get_instructions` at a conceptual level
- Parse, inspect, and rewrite code with `ast` (`NodeVisitor`, `NodeTransformer`, `unparse`)
- Explain why `eval`/`exec` on untrusted input is dangerous and what to use instead

## 1. The pipeline

When you run a `.py` file (or call `exec`), CPython does roughly this:

1. **Tokenize**: text becomes tokens (`NAME`, `NUMBER`, `OP`, `INDENT`...). See the `tokenize` module.
2. **Parse**: tokens become an **abstract syntax tree** (AST): a tree of nodes like `BinOp`, `Call`, `If`.
3. **Compile**: the AST is turned into **bytecode** stored in a *code object*.
4. **Execute**: the interpreter's *eval loop* runs the bytecode on a stack-based virtual machine.

Bytecode is cached in `__pycache__/*.pyc` so steps 1-3 are skipped for unchanged imports.
Every step is reachable from Python, which is what makes linters, formatters, and test frameworks
(e.g. pytest's assertion rewriting) possible.

## 2. `compile()` and code objects

```python
>>> code = compile("x = 1 + 2\nprint(x)", "<demo>", "exec")
>>> type(code)
<class 'code'>
>>> exec(code)
3
```
Modes: `"exec"` (a module/block of statements), `"eval"` (one expression; `eval(code)` returns its value),
`"single"` (one interactive statement). `compile` also accepts an AST object instead of text.

A function carries its code in `f.__code__`. A module-level code object holds nested function code
objects inside `co_consts`:

```python
>>> def f(a, b):
...     c = a + b
...     return len([c]) * 2
>>> co = f.__code__
>>> co.co_argcount, co.co_varnames
(2, ('a', 'b', 'c'))
>>> co.co_names                   # global and attribute names used
('len',)
>>> co.co_consts                  # constants (exact contents vary by version)
(None, 2)
>>> co.co_name, co.co_filename
('f', '<stdin>')
```
- `co_varnames`: local variables (parameters first).
- `co_names`: names looked up as globals/builtins or attributes.
- `co_consts`: literals the function uses (nested code objects appear here too).
- A code object is immutable and has no state; a *function* is code + globals + defaults + closure.

## 3. Disassembly with `dis`

```python
>>> import dis
>>> dis.dis(f)
  ...  LOAD_FAST   a
  ...  LOAD_FAST   b
  ...  BINARY_OP   +
  ...  STORE_FAST  c
  ...
```
The instruction set is a **stack machine**: instructions push/pop values on a per-frame stack.
`LOAD_FAST` pushes a local, `BINARY_OP` pops two values and pushes the result, `STORE_FAST` pops into a local.

**Opcode names and counts change between CPython versions** (3.11 added specialising adaptive
instructions, 3.12/3.13 renamed and merged many). Treat `dis` as a learning and debugging aid,
never as a stable API to assert against.

For programmatic use, `dis.get_instructions` yields `Instruction` objects:

```python
>>> for ins in dis.get_instructions(f):
...     print(ins.opname, ins.argval)
```
Useful fields: `opname`, `argval` (decoded operand, e.g. the name or constant), `starts_line`/`line_number`, `offset`.
`argval` is more stable than the opname: names like `'len'` still show up.

## 4. The AST

```python
>>> import ast
>>> tree = ast.parse("x = 1 + 2 * y")
>>> print(ast.dump(tree, indent=2))
Module(
  body=[
    Assign(
      targets=[Name(id='x', ctx=Store())],
      value=BinOp(
        left=Constant(value=1),
        op=Add(),
        right=BinOp(left=Constant(value=2), op=Mult(), right=Name(id='y', ctx=Load()))))])
```
- `ast.parse(src, mode="exec" | "eval")` returns a tree; `mode="eval"` gives an `Expression` root.
- Nodes have `_fields` (children) and, for most, `lineno`, `col_offset`, `end_lineno`, `end_col_offset`.
- `ast.walk(tree)` yields every node (breadth-first, no order guarantees you should rely on).
- `ast.unparse(tree)` turns a tree back into source (comments and original formatting are lost).
- Constants are `ast.Constant` (`True`, `None`, and numbers are Constants too; `type(v) is int` excludes bool).
- Syntax errors are raised at `ast.parse`/`compile` time as `SyntaxError`.

## 5. `NodeVisitor`

Subclass and define `visit_<ClassName>` methods. `visit(node)` dispatches; call `self.generic_visit(node)`
to continue into children (if you forget, the subtree is skipped).

```python
class CallCounter(ast.NodeVisitor):
    def __init__(self):
        self.calls = 0
    def visit_Call(self, node):
        self.calls += 1
        self.generic_visit(node)       # f(g(1)) has two calls

v = CallCounter(); v.visit(ast.parse("f(g(1))")); v.calls    # 2
```
Use plain `ast.walk` for "find all X"; use a visitor when you need context (e.g. "inside which function?").

## 6. `NodeTransformer`

A visitor whose `visit_*` methods **return the replacement node** (or `None` to delete it, or a list to splice).

```python
class Double(ast.NodeTransformer):
    def visit_Constant(self, node):
        if type(node.value) is int:
            return ast.copy_location(ast.Constant(node.value * 2), node)
        return node

tree = Double().visit(ast.parse("x = 3 + y"))
ast.fix_missing_locations(tree)        # new nodes need lineno/col_offset for compile()
ast.unparse(tree)                      # 'x = 6 + y'
```
- Always `return node` for nodes you keep.
- Call `generic_visit` *first* if you want to rewrite bottom-up (constant folding needs this).
- After transforming, call `ast.fix_missing_locations(tree)` before `compile(tree, ...)`.
- `ast.copy_location(new, old)` copies position info for a single replaced node.

Run the result: `exec(compile(tree, "<ast>", "exec"))`.

## 7. Why `eval` is dangerous

```python
user = "__import__('os').system('rm -rf ~')"   # imagine this came from a web form
eval(user)                                       # runs it. Do not do this.
```
`eval`/`exec` run arbitrary code with your privileges. Stripping `__builtins__` (`eval(s, {"__builtins__": {}})`)
is **not** a sandbox: attribute chains like `().__class__.__base__.__subclasses__()` escape it.

Safer options, in order:
1. `ast.literal_eval(text)`: accepts only Python literals (numbers, strings, tuples, lists, dicts, sets, `None`, booleans). Great for config values.
2. Parse with `ast.parse(mode="eval")` and **walk the tree yourself with an allowlist** of node types. Anything not explicitly allowed is an error.
3. Use a real data format (`json`, `tomllib`) instead of Python syntax.

```python
def calc(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return calc(node.left) + calc(node.right)
    raise ValueError("not allowed")
```
Remember resource attacks too: `9 ** 9 ** 9` is only arithmetic but never finishes. An allowlist stops code
execution, not denial of service; add limits if input is hostile.

## 8. Practical uses
- **Linters and checkers** (flake8 plugins, pylint, ruff's Python predecessors) are visitors.
- **Refactoring tools** transform trees (but need `libcst` to preserve comments/formatting).
- **Test frameworks** rewrite `assert` statements to show intermediate values.
- **Metrics**: complexity, import graphs, dead-code detection (see exercises).
- **Macros/DSLs**: parse, transform, compile, `exec`.

## Common mistakes
- Forgetting `generic_visit`, so nested nodes are never visited.
- Returning nothing from a `NodeTransformer.visit_*` method (that *deletes* the node).
- Not calling `ast.fix_missing_locations` on transformed trees before `compile`.
- Asserting on exact opcode names or instruction counts; they differ between versions.
- Treating `ast.unparse` as format-preserving; comments and layout are gone.
- Confusing `co_names` (globals/attributes) with `co_varnames` (locals).
- Believing `eval(s, {"__builtins__": {}})` is safe.
- Checking `isinstance(v, int)` for numbers when `bool` should be excluded.
- Mutating a tree while iterating `ast.walk` over it (use a transformer instead).

## Further reading
- `ast`, `dis`, `symtable`, `tokenize` module docs (docs.python.org/3/library/)
- *Green Tree Snakes: the missing Python AST docs* (greentreesnakes.readthedocs.io)
- CPython internals: *Inside the Python Virtual Machine* (Obi Ike-Nwosu)
- PEP 617 (the PEG parser) and the `Python/ceval.c` source

## Practice
Open `exercises.py`, implement each item, then run:

```bash
python check.py 4.07
```
