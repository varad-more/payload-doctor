from __future__ import annotations

from typing import Any

from validators.common import issue, require_object, wrong_type


def validate(data: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    errors = require_object(data, "An SQS event")
    warnings: list[dict[str, Any]] = []
    if errors:
        return errors, warnings

    if "Records" not in data:
        return [issue("MISSING_FIELD", "$.Records", "SQS event must include Records.")], warnings
    records = data["Records"]
    if not isinstance(records, list):
        return [wrong_type("$.Records", "array", records)], warnings
    if not records:
        return [issue("EMPTY_RECORDS", "$.Records", "SQS Records must contain at least one record.")], warnings

    for index, record in enumerate(records):
        path = f"$.Records[{index}]"
        if not isinstance(record, dict):
            errors.append(wrong_type(path, "object", record))
            continue
        for field in ("messageId", "body", "awsRegion"):
            field_path = f"{path}.{field}"
            if field not in record:
                errors.append(issue("MISSING_FIELD", field_path, f"{field_path} is required for an SQS record."))
            elif not isinstance(record[field], str):
                error = wrong_type(field_path, "string", record[field])
                if field == "body":
                    error["hint"] = "SQS delivers message bodies as strings. JSON inside a message is encoded as a string."
                errors.append(error)
        if "eventSource" not in record:
            errors.append(issue("MISSING_FIELD", f"{path}.eventSource", "SQS record must include eventSource."))
        elif not isinstance(record["eventSource"], str):
            errors.append(wrong_type(f"{path}.eventSource", "string", record["eventSource"]))
        elif record["eventSource"] != "aws:sqs":
            warnings.append(
                issue(
                    "UNEXPECTED_VALUE",
                    f"{path}.eventSource",
                    'eventSource normally equals "aws:sqs".',
                    expected="aws:sqs",
                    received=record["eventSource"],
                )
            )
        for field in ("receiptHandle", "md5OfBody", "eventSourceARN"):
            if field in record and not isinstance(record[field], str):
                errors.append(wrong_type(f"{path}.{field}", "string", record[field]))
        for field in ("attributes", "messageAttributes"):
            if field in record and not isinstance(record[field], dict):
                errors.append(wrong_type(f"{path}.{field}", "object", record[field]))
    return errors, warnings
