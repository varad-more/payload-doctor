from __future__ import annotations

from typing import Any

from validators.common import issue, require_object, wrong_type


def validate(data: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors = require_object(data, "An API Gateway REST API proxy event (v1.0)")
    warnings: list[dict[str, Any]] = []
    if errors:
        return errors, warnings

    if data.get("version") == "2.0":
        return [
            issue(
                "UNSUPPORTED_EVENT_VERSION",
                "$.version",
                "HTTP API payload v2.0 is not supported; select a REST API proxy payload v1.0 event.",
                expected="REST API payload v1.0",
                received="HTTP API payload v2.0",
            )
        ], warnings

    if not any(field in data for field in ("httpMethod", "requestContext", "version")):
        errors.append(
            issue(
                "MISSING_EVENT_MARKER",
                "$",
                "Payload does not contain an API Gateway proxy event marker such as httpMethod, requestContext, or version.",
            )
        )

    string_fields = ("resource", "path", "httpMethod")
    nullable_objects = (
        "headers",
        "multiValueHeaders",
        "queryStringParameters",
        "pathParameters",
        "stageVariables",
    )
    for field in string_fields:
        if field in data and not isinstance(data[field], str):
            errors.append(wrong_type(f"$.{field}", "string", data[field]))
    for field in nullable_objects:
        if field in data and data[field] is not None and not isinstance(data[field], dict):
            errors.append(wrong_type(f"$.{field}", "object or null", data[field]))
    if "requestContext" in data and not isinstance(data["requestContext"], dict):
        errors.append(wrong_type("$.requestContext", "object", data["requestContext"]))
    if "body" in data and data["body"] is not None and not isinstance(data["body"], str):
        errors.append(wrong_type("$.body", "string or null", data["body"]))
    if "isBase64Encoded" in data and not isinstance(data["isBase64Encoded"], bool):
        errors.append(wrong_type("$.isBase64Encoded", "boolean", data["isBase64Encoded"]))
    return errors, warnings
