from __future__ import annotations

from typing import Any

from validators.common import issue, require_object, wrong_type


def validate(data: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors = require_object(data, "An SNS event")
    warnings: list[dict[str, Any]] = []
    if errors:
        return errors, warnings

    records = data.get("Records")
    if records is None:
        return [issue("MISSING_FIELD", "$.Records", "SNS event must include Records.")], warnings
    if not isinstance(records, list):
        return [wrong_type("$.Records", "array", records)], warnings
    if not records:
        return [issue("EMPTY_RECORDS", "$.Records", "SNS Records must contain at least one record.")], warnings

    for index, record in enumerate(records):
        path = f"$.Records[{index}]"
        if not isinstance(record, dict):
            errors.append(wrong_type(path, "object", record))
            continue
        source = record.get("EventSource")
        if source is None:
            errors.append(issue("MISSING_FIELD", f"{path}.EventSource", "SNS record must include EventSource."))
        elif not isinstance(source, str):
            errors.append(wrong_type(f"{path}.EventSource", "string", source))
        elif source != "aws:sns":
            warnings.append(
                issue(
                    "UNEXPECTED_VALUE",
                    f"{path}.EventSource",
                    'EventSource normally equals "aws:sns".',
                    expected="aws:sns",
                    received=source,
                )
            )
        subscription = record.get("EventSubscriptionArn")
        if subscription is None:
            errors.append(
                issue("MISSING_FIELD", f"{path}.EventSubscriptionArn", "SNS record must include EventSubscriptionArn.")
            )
        elif not isinstance(subscription, str):
            errors.append(wrong_type(f"{path}.EventSubscriptionArn", "string", subscription))

        sns = record.get("Sns")
        if sns is None:
            errors.append(issue("MISSING_FIELD", f"{path}.Sns", "SNS record must include Sns."))
            continue
        if not isinstance(sns, dict):
            errors.append(wrong_type(f"{path}.Sns", "object", sns))
            continue
        for field in ("Type", "MessageId", "TopicArn", "Message", "Timestamp"):
            field_path = f"{path}.Sns.{field}"
            if field not in sns:
                errors.append(issue("MISSING_FIELD", field_path, f"{field_path} is required for an SNS notification."))
            elif not isinstance(sns[field], str):
                errors.append(wrong_type(field_path, "string", sns[field]))
        for field in ("Subject", "SignatureVersion", "Signature", "SigningCertUrl", "UnsubscribeUrl"):
            if field in sns and sns[field] is not None and not isinstance(sns[field], str):
                errors.append(wrong_type(f"{path}.Sns.{field}", "string or null", sns[field]))
        if "MessageAttributes" in sns and not isinstance(sns["MessageAttributes"], dict):
            errors.append(wrong_type(f"{path}.Sns.MessageAttributes", "object", sns["MessageAttributes"]))
    return errors, warnings
