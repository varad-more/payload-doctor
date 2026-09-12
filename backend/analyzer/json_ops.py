from __future__ import annotations

import json
import math
from typing import Any


class JsonProblem(ValueError):
    def __init__(self, error: dict[str, Any]):
        super().__init__(error["message"])
        self.error = error


def utf8_size(content: str) -> int:
    return len(content.encode("utf-8"))


def _reject_constant(value: str) -> None:
    raise ValueError(f"Non-standard numeric value {value} is not valid JSON.")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("JSON number is outside the supported finite range.")
    return number


def parse_json(content: str, *, code: str = "INVALID_JSON") -> Any:
    try:
        return json.loads(content, parse_constant=_reject_constant, parse_float=_finite_float)
    except json.JSONDecodeError as exc:
        line = content.splitlines()[exc.lineno - 1] if content.splitlines() else ""
        reason = exc.msg
        if exc.msg == "Expecting property name enclosed in double quotes":
            reason = "Expected a double-quoted property name; check for unquoted keys or a trailing comma."
        error = {
            "code": code,
            "message": f"Invalid JSON at line {exc.lineno}, column {exc.colno}.",
            "reason": reason,
            "line": exc.lineno,
            "column": exc.colno,
            "position": exc.pos,
        }
        if line:
            error["excerpt"] = line[:200]
        raise JsonProblem(error) from None
    except (RecursionError, ValueError) as exc:
        message = "JSON nesting is too deep." if isinstance(exc, RecursionError) else str(exc)
        raise JsonProblem({"code": code, "message": message}) from None


def format_json(value: Any) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False)


def minify_json(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), ensure_ascii=False)


def calculate_metrics(value: Any, source: str) -> dict[str, int]:
    depth = keys = arrays = values = 0
    stack: list[tuple[Any, int]] = [(value, 1 if isinstance(value, (dict, list)) else 0)]

    while stack:
        current, current_depth = stack.pop()
        depth = max(depth, current_depth)
        if isinstance(current, dict):
            keys += len(current)
            stack.extend(
                (child, current_depth + 1 if isinstance(child, (dict, list)) else current_depth)
                for child in current.values()
            )
        elif isinstance(current, list):
            arrays += 1
            stack.extend(
                (child, current_depth + 1 if isinstance(child, (dict, list)) else current_depth)
                for child in current
            )
        else:
            values += 1

    return {
        "bytes": utf8_size(source),
        "depth": depth,
        "keys": keys,
        "arrays": arrays,
        "values": values,
    }
