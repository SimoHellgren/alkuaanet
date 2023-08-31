from lark import Lark, Transformer
from pathlib import Path


class TreeToSQL(Transformer):
    def logical_expression(self, s):
        # operation is like `a AND b`
        if len(s) == 3:
            l, op, r = s
            return f"{l} {op.data} {r}"

        # operation is like `NOT a`
        if len(s) == 2:
            op, rest = s
            if op == "not":
                return f"not {rest}"

    def negation(self, s):
        (s,) = s
        return f"not {s}"

    def text_expression(self, s):
        left, op, right = s

        # strip quotation marks from string literal
        right = right[1:-1]
        if op.data == "startswith":
            return f"{left} ilike '{right}%'"

        if op.data == "endswith":
            return f"{left} ilike '%{right}'"

        if op.data == "contains":
            return f"{left} ilike '%{right}%'"

    def comparison_expression(self, s):
        left, op, right = s

        if right is None:
            return f"{left} is null"

        map = {"eq": "=", "gt": ">", "lt": "<", "ge": ">=", "le": "<="}

        return f"{left} {map[op.data]} {right}"

    def NAME(self, s):
        return s

    def NUMBER(self, s):
        return s

    def string_literal(self, s):
        (s,) = s
        return s

    true = lambda self, _: True
    false = lambda self, _: False
    null = lambda self, _: None


path = Path(__file__).parents[0] / "grammar.lark"

with open(path) as f:
    parser = Lark(f.read(), start="filter_expression", parser="lalr")


def parse_odata_filter(text):
    if not text:
        return ""
    parsed = parser.parse(text)
    transformer = TreeToSQL()
    return transformer.transform(parsed)


if __name__ == "__main__":
    text = "not (name eq null)"
    x = parse_odata_filter(text)
    print(x)
