from __future__ import annotations

from typing import Any

from jsonschema import SchemaError, ValidationError, validators
from referencing import Registry
from referencing.exceptions import Unresolvable

from analyzer.json_ops import parse_json
from validators.common import issue, json_type


def _path(parts: list[Any]) -> str:
    result = "$"
    for part in parts:
        result += f"[{part}]" if isinstance(part, int) else f".{part}"
    return result


def _schema_issue(error: ValidationError) -> dict[str, Any]:
    path = list(error.absolute_path)
    expected: Any = error.validator_value
    received = json_type(error.instance)
    message = error.message

    if error.validator == "required" and isinstance(error.instance, dict):
        missing = next(
            (
                name
                for name in error.validator_value
                if name not in error.instance and error.message == f"{name!r} is a required property"
            ),
            None,
        )
        if missing:
            path.append(missing)
            expected = "present"
            received = "missing"
            message = "Required property is missing."
    elif error.validator == "type":
        message = f"Expected {expected}; received {received}."

    return issue(
        "SCHEMA_VALIDATION_ERROR",
        _path(path),
        message,
        expected=expected,
        received=received,
    )


def validate_against_schema(data: Any, schema_content: str) -> dict[str, Any]:
    schema = parse_json(schema_content, code="INVALID_SCHEMA_JSON")
    if not isinstance(schema, (dict, bool)):
        return {
            "schemaValid": False,
            "schemaAccepted": False,
            "errors": [issue("INVALID_SCHEMA", "$", "JSON Schema must be an object or boolean.")],
        }
    validator_class = validators.validator_for(schema)
    try:
        validator_class.check_schema(schema)
    except SchemaError as error:
        return {
            "schemaValid": False,
            "schemaAccepted": False,
            "errors": [issue("INVALID_SCHEMA", _path(list(error.path)), error.message)],
        }

    try:
        errors = sorted(
            validator_class(schema, registry=Registry()).iter_errors(data),
            key=lambda error: (_path(list(error.absolute_path)), error.message),
        )
    except Unresolvable:
        return {
            "schemaValid": False,
            "schemaAccepted": False,
            "errors": [
                issue(
                    "UNRESOLVABLE_SCHEMA_REFERENCE",
                    "$",
                    "Schema reference could not be resolved. Inline referenced schemas; remote retrieval is disabled.",
                )
            ],
        }
    return {"schemaValid": not errors, "schemaAccepted": True, "errors": [_schema_issue(error) for error in errors]}
