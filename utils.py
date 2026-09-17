import ast
import operator
import logging


def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        ))
        logger.addHandler(h)
    return logger


# --- Safe math evaluator (replaces eval) ---
_ALLOWED_OPS = {
    ast.Add: operator.add,       ast.Sub: operator.sub,
    ast.Mult: operator.mul,      ast.Div: operator.truediv,
    ast.Pow: operator.pow,       ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,      ast.UAdd: operator.pos,
}


def safe_eval(expr: str):
    """Evaluate a math expression safely via AST."""
    try:
        node = ast.parse(expr, mode="eval").body
    except SyntaxError:
        raise ValueError("Invalid expression")
    return _eval(node)


def _eval(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numeric constants allowed")
    if isinstance(node, ast.BinOp):
        op = _ALLOWED_OPS.get(type(node.op))
        if not op:
            raise ValueError("Operator not allowed")
        return op(_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        op = _ALLOWED_OPS.get(type(node.op))
        if not op:
            raise ValueError("Unary op not allowed")
        return op(_eval(node.operand))
    raise ValueError(f"Unsupported node: {type(node).__name__}")