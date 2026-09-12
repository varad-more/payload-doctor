from __future__ import annotations

from typing import Any


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, (int, float)):
        return "number"
    return type(value).__name__


def issue(
    code: str,
    path: str,
    message: str,
    *,
    expected: Any | None = None,
    received: Any | None = None,
    hint: str | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"code": code, "path": path, "message": message}
    if expected is not None:
        result["expected"] = expected
    if received is not None:
        result["received"] = received
    if hint:
        result["hint"] = hint
    return result


def wrong_type(path: str, expected: str, value: Any) -> dict[str, Any]:
    received = json_type(value)
    return issue(
        "WRONG_TYPE",
        path,
        f"{path} must be {expected}.",
        expected=expected,
        received=received,
    )


def require_object(data: Any, label: str) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        return []
    return [wrong_type("$", "object", data) | {"message": f"{label} must be a JSON object."}]
