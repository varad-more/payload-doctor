from __future__ import annotations

import base64
import json
import logging
import time
from dataclasses import dataclass
from typing import Any

from analyzer.json_ops import JsonProblem, calculate_metrics, format_json, minify_json, parse_json, utf8_size
from analyzer.repair import repair_json
from analyzer.schema import validate_against_schema
from validators import validate_payload

MAX_PAYLOAD_BYTES = 1024 * 1024
MAX_SCHEMA_BYTES = 256 * 1024
OPERATIONS = {"diagnose", "format", "minify", "repair", "schema_validate"}
PAYLOAD_TYPES = {"generic", "api_gateway", "sqs", "sns", "eventbridge"}

logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class RequestProblem(ValueError):
    code: str
    message: str
    status: int = 400

    @property
    def error(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


def _request_body(event: dict[str, Any]) -> Any:
    body = event.get("body", event)
    if isinstance(body, dict):
        return body
    if not isinstance(body, str):
        raise RequestProblem("INVALID_REQUEST", "Request body must be a JSON object.")
    if event.get("isBase64Encoded"):
        try:
            body = base64.b64decode(body, validate=True).decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise RequestProblem("INVALID_REQUEST", "Request body is not valid base64-encoded UTF-8.") from exc
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RequestProblem("INVALID_REQUEST", "Request body must contain valid JSON.") from exc


def _validated_request(request: Any) -> tuple[str, str, str, str | None]:
    if not isinstance(request, dict):
        raise RequestProblem("INVALID_REQUEST", "Request body must be a JSON object.")
    operation = request.get("operation")
    payload_type = request.get("payloadType")
    content = request.get("content")
    schema = request.get("schema")

    if operation not in OPERATIONS:
        raise RequestProblem("INVALID_OPERATION", f"operation must be one of: {', '.join(sorted(OPERATIONS))}.")
    if payload_type not in PAYLOAD_TYPES:
        raise RequestProblem("INVALID_PAYLOAD_TYPE", f"payloadType must be one of: {', '.join(sorted(PAYLOAD_TYPES))}.")
    if not isinstance(content, str):
        raise RequestProblem("INVALID_CONTENT", "content must be a string.")
    if utf8_size(content) > MAX_PAYLOAD_BYTES:
        raise RequestProblem("PAYLOAD_TOO_LARGE", "Payload exceeds the 1 MiB limit.", 413)
    if schema is not None and not isinstance(schema, str):
        raise RequestProblem("INVALID_SCHEMA", "schema must be a string or null.")
    if isinstance(schema, str) and utf8_size(schema) > MAX_SCHEMA_BYTES:
        raise RequestProblem("SCHEMA_TOO_LARGE", "Schema exceeds the 256 KiB limit.", 413)
    if operation == "schema_validate" and not isinstance(schema, str):
        raise RequestProblem("SCHEMA_REQUIRED", "schema is required for schema_validate.")
    return operation, payload_type, content, schema


def _base_response(operation: str, payload_type: str, value: Any, content: str) -> dict[str, Any]:
    return {
        "success": True,
        "operation": operation,
        "payloadType": payload_type,
        "jsonValid": True,
        "structureValid": True,
        "errors": [],
        "warnings": [],
        "metrics": calculate_metrics(value, content),
        "output": None,
    }


def analyze_request(request: Any) -> dict[str, Any]:
    operation, payload_type, content, schema = _validated_request(request)

    if operation == "repair":
        repair = repair_json(content)
        response: dict[str, Any] = {
            "success": True,
            "operation": operation,
            "payloadType": payload_type,
            "jsonValid": bool(repair.get("output")),
            "structureValid": False,
            "errors": [],
            "warnings": [],
            "metrics": {"bytes": utf8_size(content), "depth": 0, "keys": 0, "arrays": 0, "values": 0},
            **repair,
        }
        if repair.get("output"):
            value = parse_json(repair["output"])
            response["metrics"] = calculate_metrics(value, repair["output"])
            response["errors"], response["warnings"] = validate_payload(payload_type, value)
            response["structureValid"] = not response["errors"]
        return response

    value = parse_json(content)
    response = _base_response(operation, payload_type, value, content)

    if operation == "diagnose":
        response["errors"], response["warnings"] = validate_payload(payload_type, value)
        response["structureValid"] = not response["errors"]
    elif operation == "format":
        output = format_json(value)
        response["output"] = output
        response["sizes"] = {"originalBytes": utf8_size(content), "formattedBytes": utf8_size(output)}
    elif operation == "minify":
        output = minify_json(value)
        original_bytes = utf8_size(content)
        minified_bytes = utf8_size(output)
        saved = max(0, original_bytes - minified_bytes)
        response["output"] = output
        response["sizes"] = {
            "originalBytes": original_bytes,
            "minifiedBytes": minified_bytes,
            "bytesSaved": saved,
            "percentageReduction": round(saved / original_bytes * 100, 1) if original_bytes else 0,
        }
    elif operation == "schema_validate":
        schema_result = validate_against_schema(value, schema or "")
        response.update(schema_result)
        response["structureValid"] = schema_result["schemaValid"]
        response["errors"] = schema_result["errors"]
    return response


def handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    started = time.perf_counter()
    request_id = getattr(context, "aws_request_id", None) or event.get("requestContext", {}).get("requestId", "local")
    operation = payload_type = "unknown"
    payload_bytes = 0
    status = 200
    failure_category: str | None = None

    try:
        request = _request_body(event)
        if isinstance(request, dict):
            operation = str(request.get("operation", "unknown"))
            payload_type = str(request.get("payloadType", "unknown"))
            if isinstance(request.get("content"), str):
                payload_bytes = utf8_size(request["content"])
        response = analyze_request(request)
    except RequestProblem as exc:
        status = exc.status
        failure_category = exc.code
        response = {"success": False, "error": exc.error}
    except JsonProblem as exc:
        status = 422
        failure_category = exc.error["code"]
        response = {"success": False, "error": exc.error}
    except Exception:
        status = 500
        failure_category = "INTERNAL_ERROR"
        logger.error(
            json.dumps(
                {
                    "requestId": request_id,
                    "operation": operation,
                    "payloadType": payload_type,
                    "payloadBytes": payload_bytes,
                    "failureCategory": failure_category,
                }
            )
        )
        response = {
            "success": False,
            "error": {"code": "INTERNAL_ERROR", "message": "Payload analysis failed unexpectedly."},
        }

    logger.info(
        json.dumps(
            {
                "requestId": request_id,
                "operation": operation,
                "payloadType": payload_type,
                "payloadBytes": payload_bytes,
                "durationMs": round((time.perf_counter() - started) * 1000, 2),
                "success": response["success"],
                **({"failureCategory": failure_category} if failure_category else {}),
            }
        )
    )
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json; charset=utf-8"},
        "body": json.dumps(response, ensure_ascii=False),
    }
