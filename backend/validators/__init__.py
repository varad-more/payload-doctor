from __future__ import annotations

from typing import Any, Callable

from validators import api_gateway, eventbridge, sns, sqs

Validator = Callable[[Any], tuple[list[dict[str, Any]], list[dict[str, Any]]]]

VALIDATORS: dict[str, Validator] = {
    "api_gateway": api_gateway.validate,
    "sqs": sqs.validate,
    "sns": sns.validate,
    "eventbridge": eventbridge.validate,
}


def validate_payload(payload_type: str, data: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    validator = VALIDATORS.get(payload_type)
    return validator(data) if validator else ([], [])
