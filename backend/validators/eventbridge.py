from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from validators.common import issue, json_type, require_object, wrong_type


def validate(data: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors = require_object(data, "An EventBridge event")
    warnings: list[dict[str, Any]] = []
    if errors:
        return errors, warnings

    string_fields = ("version", "id", "detail-type", "source", "account", "time", "region")
    for field in string_fields:
        path = f"$.{field}"
        if field not in data:
            errors.append(issue("MISSING_FIELD", path, f"EventBridge event must include {field}."))
        elif not isinstance(data[field], str):
            errors.append(wrong_type(path, "string", data[field]))
    if "resources" not in data:
        errors.append(issue("MISSING_FIELD", "$.resources", "EventBridge event must include resources."))
    elif not isinstance(data["resources"], list):
        errors.append(wrong_type("$.resources", "array", data["resources"]))
    if "detail" not in data:
        errors.append(issue("MISSING_FIELD", "$.detail", "EventBridge event must include detail."))
    elif not isinstance(data["detail"], dict):
        warnings.append(
            issue(
                "SUSPICIOUS_DETAIL",
                "$.detail",
                "EventBridge detail is usually an object, though other JSON values are possible.",
                expected="object",
                received=json_type(data["detail"]),
            )
        )

    if isinstance(data.get("version"), str) and data["version"] != "0":
        warnings.append(issue("UNEXPECTED_VALUE", "$.version", 'EventBridge version normally equals "0".'))
    if isinstance(data.get("account"), str) and not re.fullmatch(r"\d{12}", data["account"]):
        warnings.append(issue("SUSPICIOUS_ACCOUNT", "$.account", "AWS account is normally a 12-digit string."))
    if isinstance(data.get("time"), str):
        try:
            datetime.fromisoformat(data["time"].replace("Z", "+00:00"))
        except ValueError:
            warnings.append(issue("SUSPICIOUS_TIME", "$.time", "time is not a recognizable ISO 8601 timestamp."))
    return errors, warnings
