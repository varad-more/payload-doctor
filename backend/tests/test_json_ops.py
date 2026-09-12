import pytest

from analyzer.json_ops import JsonProblem, calculate_metrics, format_json, minify_json, parse_json, utf8_size


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ('{"name":"Payload Doctor","active":true}', {"name": "Payload Doctor", "active": True}),
        ("[1,2,3]", [1, 2, 3]),
        ('{"outer":{"items":[{"ok":true}]}}', {"outer": {"items": [{"ok": True}]}}),
        ('{"message":"Hello, 世界 🩺"}', {"message": "Hello, 世界 🩺"}),
        ("{}", {}),
        ("[]", []),
        ("true", True),
        ("null", None),
        ("42", 42),
        ('"hello"', "hello"),
    ],
)
def test_valid_json(source, expected):
    assert parse_json(source) == expected


def test_malformed_json_has_location():
    with pytest.raises(JsonProblem) as captured:
        parse_json('{\n  "name": "doctor",\n}')
    assert captured.value.error["line"] == 3
    assert captured.value.error["column"] == 1
    assert captured.value.error["position"] == 22
    assert "trailing comma" in captured.value.error["reason"]


@pytest.mark.parametrize("source", ['{"a":}', '{"a": 1 "b": 2}', "{", "hello"])
def test_other_malformed_json_is_controlled(source):
    with pytest.raises(JsonProblem) as captured:
        parse_json(source)
    assert captured.value.error["code"] == "INVALID_JSON"
    assert captured.value.error["line"] >= 1
    assert captured.value.error["column"] >= 1


def test_nonstandard_numbers_are_rejected():
    with pytest.raises(JsonProblem, match="not valid JSON"):
        parse_json('{"value": NaN}')


def test_numbers_that_overflow_float_are_rejected():
    with pytest.raises(JsonProblem, match="finite range"):
        parse_json('{"value": 1e9999}')


def test_format_minify_and_metrics_use_utf8_bytes():
    source = '{"name":"🩺","nested":{"items":[1,2]}}'
    value = parse_json(source)
    formatted = format_json(value)
    assert "\n  \"name\"" in formatted
    assert minify_json(value) == source
    assert utf8_size(source) == len(source.encode("utf-8"))
    assert calculate_metrics(value, source) == {
        "bytes": len(source.encode("utf-8")),
        "depth": 3,
        "keys": 3,
        "arrays": 1,
        "values": 3,
    }


def test_format_preserves_all_json_value_types_and_uses_two_spaces():
    source = '{"unicode":"こんにちは 🌎","number":42.5,"flag":true,"empty":null,"items":[1,false]}'
    value = parse_json(source)
    formatted = format_json(value)
    assert '\n  "unicode"' in formatted
    assert parse_json(formatted) == value


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("{}", {"bytes": 2, "depth": 1, "keys": 0, "arrays": 0, "values": 0}),
        ("[]", {"bytes": 2, "depth": 1, "keys": 0, "arrays": 1, "values": 0}),
        ('{"a":[{"b":[1]}]}', {"bytes": 17, "depth": 4, "keys": 2, "arrays": 2, "values": 1}),
    ],
)
def test_metric_boundaries(source, expected):
    assert calculate_metrics(parse_json(source), source) == expected
