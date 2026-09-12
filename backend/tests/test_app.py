import json

import pytest

from app import MAX_PAYLOAD_BYTES, MAX_SCHEMA_BYTES, RequestProblem, analyze_request, handler


def request(operation="diagnose", payload_type="generic", content="{}", schema=None):
    return {"operation": operation, "payloadType": payload_type, "content": content, "schema": schema}


def test_diagnose_generic():
    result = analyze_request(request(content='{"name":"doctor"}'))
    assert result["success"] is True
    assert result["jsonValid"] is True
    assert result["structureValid"] is True


def test_format_and_minify_sizes():
    formatted = analyze_request(request("format", content='{"name":"🩺"}'))
    assert formatted["output"] == '{\n  "name": "🩺"\n}'
    assert formatted["sizes"]["formattedBytes"] == len(formatted["output"].encode("utf-8"))

    minified = analyze_request(request("minify", content='{\n  "name": "🩺"\n}'))
    assert minified["output"] == '{"name":"🩺"}'
    original_bytes = len('{\n  "name": "🩺"\n}'.encode("utf-8"))
    minified_bytes = len(minified["output"].encode("utf-8"))
    saved = original_bytes - minified_bytes
    assert minified["sizes"] == {
        "originalBytes": original_bytes,
        "minifiedBytes": minified_bytes,
        "bytesSaved": saved,
        "percentageReduction": round(saved / original_bytes * 100, 1),
    }


def test_schema_operation():
    result = analyze_request(
        request(
            "schema_validate",
            content='{"name": null}',
            schema='{"type":"object","properties":{"name":{"type":"string"}}}',
        )
    )
    assert result["schemaAccepted"] is True
    assert result["schemaValid"] is False
    assert result["errors"][0]["path"] == "$.name"


def test_repair_reports_strict_output_as_valid():
    result = analyze_request(request("repair", content="{name: 'doctor',}"))
    assert result["repaired"] is True
    assert result["jsonValid"] is True
    assert json.loads(result["output"]) == {"name": "doctor"}


@pytest.mark.parametrize(
    "bad_request",
    [
        request(operation="launch"),
        request(payload_type="kinesis"),
        {"operation": "diagnose", "payloadType": "generic", "content": {}},
        request("schema_validate", schema=None),
    ],
)
def test_request_validation(bad_request):
    with pytest.raises(RequestProblem):
        analyze_request(bad_request)


def test_payload_limit_uses_utf8_bytes():
    with pytest.raises(RequestProblem) as captured:
        analyze_request(request(content="🩺" * (MAX_PAYLOAD_BYTES // 4 + 1)))
    assert captured.value.code == "PAYLOAD_TOO_LARGE"
    assert captured.value.status == 413


def test_handler_returns_safe_json_error_and_logs_metadata_only(caplog):
    secret = "DO-NOT-LOG-ME"
    event = {"body": json.dumps(request(content=f'{{"secret":"{secret}",}}'))}
    response = handler(event, None)
    body = json.loads(response["body"])
    assert response["statusCode"] == 422
    assert body["error"]["code"] == "INVALID_JSON"
    assert body["error"]["line"] == 1
    assert secret not in caplog.text
    assert '"payloadBytes"' in caplog.text


def test_handler_internal_error_does_not_log_payload(monkeypatch, caplog):
    secret = "DO-NOT-LOG-INTERNAL-FAILURE"

    def explode(_request):
        raise RuntimeError(secret)

    monkeypatch.setattr("app.analyze_request", explode)
    response = handler({"body": json.dumps(request(content=secret))}, None)
    assert response["statusCode"] == 500
    assert json.loads(response["body"])["error"]["code"] == "INTERNAL_ERROR"
    assert secret not in caplog.text


@pytest.mark.parametrize(
    ("body", "status", "code"),
    [
        ("not json", 400, "INVALID_REQUEST"),
        (json.dumps({"payloadType": "generic", "content": "{}"}), 400, "INVALID_OPERATION"),
        (json.dumps({"operation": "hack", "payloadType": "generic", "content": "{}"}), 400, "INVALID_OPERATION"),
        (json.dumps({"operation": "diagnose", "payloadType": "generic"}), 400, "INVALID_CONTENT"),
        (json.dumps({"operation": "diagnose", "payloadType": "kinesis", "content": "{}"}), 400, "INVALID_PAYLOAD_TYPE"),
    ],
)
def test_handler_request_errors_use_4xx(body, status, code):
    response = handler({"body": body}, None)
    assert response["statusCode"] == status
    assert json.loads(response["body"])["error"]["code"] == code


def test_handler_enforces_both_size_limits():
    payload_response = handler(
        {"body": json.dumps(request(content="x" * (MAX_PAYLOAD_BYTES + 1)))},
        None,
    )
    assert payload_response["statusCode"] == 413
    assert json.loads(payload_response["body"])["error"]["code"] == "PAYLOAD_TOO_LARGE"

    schema_response = handler(
        {
            "body": json.dumps(
                request("schema_validate", schema="x" * (MAX_SCHEMA_BYTES + 1))
            )
        },
        None,
    )
    assert schema_response["statusCode"] == 413
    assert json.loads(schema_response["body"])["error"]["code"] == "SCHEMA_TOO_LARGE"


def test_deeply_nested_json_fails_without_a_500():
    content = "[" * 1100 + "0" + "]" * 1100
    response = handler({"body": json.dumps(request(content=content))}, None)
    assert response["statusCode"] in {200, 422}
    body = json.loads(response["body"])
    if response["statusCode"] == 200:
        assert body["metrics"]["depth"] == 1100
    else:
        assert body["error"] == {
            "code": "INVALID_JSON",
            "message": "JSON nesting is too deep.",
        }
