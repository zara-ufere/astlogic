"""Translate Python source code into a Prolog ``program([...])`` term.

Python's ``ast`` module parses source text into a tree without running it.
Each node type has a converter function, registered in a dispatch table.
Names and strings become Prolog strings so that capital letters are not
mistaken for Prolog variables.
"""
import ast


class UnsupportedNodeError(Exception):
    """Raised in strict mode when the source uses an unhandled node type."""


def quote(text):
    """Return text as a Prolog double-quoted string with escapes applied."""
    escaped = (text.replace("\\", "\\\\").replace('"', '\\"')
               .replace("\n", "\\n").replace("\r", "\\r"))
    return f'"{escaped}"'


BIN_OPS = {ast.Add: "add", ast.Sub: "sub", ast.Mult: "mult", ast.Div: "div",
           ast.FloorDiv: "floordiv", ast.Mod: "mod", ast.Pow: "pow"}
CMP_OPS = {ast.Lt: "lt", ast.LtE: "lte", ast.Gt: "gt", ast.GtE: "gte",
           ast.Eq: "eq", ast.NotEq: "neq", ast.In: "in", ast.NotIn: "not_in",
           ast.Is: "is", ast.IsNot: "is_not"}
KEYWORD_CONSTANTS = {None: "none", True: "true", False: "false"}


class Translator:
    def __init__(self, strict=False):
        self.strict = strict
        self.warnings = []
        self.table = {
            ast.FunctionDef: self.function_def, ast.Assign: self.assign,
            ast.AugAssign: self.aug_assign, ast.Return: self.return_,
            ast.For: self.for_, ast.While: self.while_, ast.If: self.if_,
            ast.Expr: self.expr, ast.Call: self.call, ast.BinOp: self.bin_op,
            ast.BoolOp: self.bool_op, ast.Compare: self.compare,
            ast.UnaryOp: self.unary_op, ast.Name: self.name,
            ast.Constant: self.constant, ast.List: self.list_,
            ast.Tuple: self.tuple_, ast.Dict: self.dict_,
            ast.Subscript: self.subscript, ast.Slice: self.slice_,
            ast.Attribute: self.attribute, ast.JoinedStr: self.fstring,
            ast.FormattedValue: self.formatted_value, ast.Import: self.import_,
            ast.ImportFrom: self.import_from, ast.With: self.with_,
            ast.Global: self.global_, ast.Pass: lambda n: "pass",
            ast.Break: lambda n: "break", ast.Continue: lambda n: "continue",
        }

    # -- dispatch ---------------------------------------------------------
    def node(self, n):
        converter = self.table.get(type(n))
        if converter is None:
            kind = type(n).__name__
            message = f"line {getattr(n, 'lineno', '?')}: unsupported {kind}"
            if self.strict:
                raise UnsupportedNodeError(message)
            self.warnings.append(message)
            return f"unknown({quote(kind)})"
        return converter(n)

    def body(self, stmts):
        return ", ".join(self.node(s) for s in stmts)

    def block(self, stmts):
        return f"body([{self.body(stmts)}])"

    def dotted(self, n):
        """Dotted name of a callee: plt.plot -> 'plt.plot'; input().strip -> 'input.strip'."""
        if isinstance(n, ast.Name):
            return n.id
        if isinstance(n, ast.Attribute):
            return f"{self.dotted(n.value)}.{n.attr}"
        if isinstance(n, ast.Call):
            return self.dotted(n.func)
        return "unknown"

    # -- statements -------------------------------------------------------
    def function_def(self, n):
        params = ", ".join(quote(a.arg) for a in n.args.args)
        return f"function({quote(n.name)}, [{params}], [{self.body(n.body)}])"

    def assign(self, n):
        return f"assign({self.node(n.targets[0])}, {self.node(n.value)})"

    def aug_assign(self, n):
        # x += y is expanded to x = x + y so rubrics only see plain assign.
        op = BIN_OPS.get(type(n.op), "unknown_op")
        target = self.node(n.target)
        return f'assign({target}, call("{op}", [{target}, {self.node(n.value)}]))'

    def return_(self, n):
        return f"return({self.node(n.value) if n.value else 'none'})"

    def for_(self, n):
        return f"for({self.node(n.target)}, {self.node(n.iter)}, {self.block(n.body)})"

    def while_(self, n):
        return f"while({self.node(n.test)}, {self.block(n.body)})"

    def if_(self, n):
        # One branch: if(Cond, Then). Two branches: if(Cond, Then, Else).
        # An elif is an if nested inside the else body.
        head = f"{self.node(n.test)}, {self.block(n.body)}"
        if n.orelse:
            return f"if({head}, {self.block(n.orelse)})"
        return f"if({head})"

    def expr(self, n):
        return self.node(n.value)

    def import_(self, n):
        return f"import([{', '.join(quote(a.name) for a in n.names)}])"

    def import_from(self, n):
        names = ", ".join(quote(a.name) for a in n.names)
        return f"import_from({quote(n.module or '')}, [{names}])"

    def with_(self, n):
        items = ", ".join(self.node(i.context_expr) for i in n.items)
        return f"with([{items}], {self.block(n.body)})"

    def global_(self, n):
        return f"global([{', '.join(quote(x) for x in n.names)}])"

    # -- expressions ------------------------------------------------------
    def call(self, n):
        args = ", ".join(self.node(a) for a in n.args)
        return f"call({quote(self.dotted(n.func))}, [{args}])"

    def bin_op(self, n):
        op = BIN_OPS.get(type(n.op), "unknown_op")
        return f'call("{op}", [{self.node(n.left)}, {self.node(n.right)}])'

    def bool_op(self, n):
        op = "and" if isinstance(n.op, ast.And) else "or"
        return f'call("{op}", [{", ".join(self.node(v) for v in n.values)}])'

    def compare(self, n):
        parts, left = [], n.left
        for op, right in zip(n.ops, n.comparators):
            name = CMP_OPS.get(type(op), "unknown_op")
            parts.append(f'call("{name}", [{self.node(left)}, {self.node(right)}])')
            left = right
        return parts[0] if len(parts) == 1 else f'call("and", [{", ".join(parts)}])'

    def unary_op(self, n):
        if isinstance(n.op, ast.USub) and isinstance(n.operand, ast.Constant) \
                and isinstance(n.operand.value, (int, float)):
            return str(-n.operand.value)  # -1 is UnaryOp(USub, 1) in the AST
        name = "not" if isinstance(n.op, ast.Not) else "neg"
        return f'call("{name}", [{self.node(n.operand)}])'

    def name(self, n):
        return quote(n.id)

    def constant(self, n):
        v = n.value
        if v is None or isinstance(v, bool):
            return KEYWORD_CONSTANTS[v]  # None/True/False would be Prolog variables
        if isinstance(v, (int, float)):
            return repr(v)
        return quote(str(v))

    def list_(self, n):
        return f"list([{', '.join(self.node(e) for e in n.elts)}])"

    def tuple_(self, n):
        return f"tuple([{', '.join(self.node(e) for e in n.elts)}])"

    def dict_(self, n):
        pairs = (f"pair({self.node(k) if k else 'none'}, {self.node(v)})"
                 for k, v in zip(n.keys, n.values))
        return f"dict([{', '.join(pairs)}])"

    def subscript(self, n):
        return f"subscript({self.node(n.value)}, {self.node(n.slice)})"

    def slice_(self, n):
        lower = self.node(n.lower) if n.lower else "none"
        upper = self.node(n.upper) if n.upper else "none"
        return f"slice({lower}, {upper})"

    def attribute(self, n):
        return quote(self.dotted(n))

    def fstring(self, n):
        return "fstring"  # text content is irrelevant to structure

    def formatted_value(self, n):
        return self.node(n.value)


def is_main_guard(stmt):
    """True for `if __name__ == '__main__':` test scaffolding."""
    return (isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Compare)
            and isinstance(stmt.test.left, ast.Name)
            and stmt.test.left.id == "__name__")


def translate(source, strict=False):
    """Return (prolog_text, warnings) for a Python source string."""
    tree = ast.parse(source)
    t = Translator(strict=strict)
    stmts = [s for s in tree.body if not is_main_guard(s)]
    lines = ",\n".join(f"    {t.node(s)}" for s in stmts)
    return f"program([\n{lines}\n]).\n", t.warnings
