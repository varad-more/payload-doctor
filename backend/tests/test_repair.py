import json

import pytest

from analyzer.repair import repair_json


@pytest.mark.parametrize(
    ("source", "expected", "change_type"),
    [
        ('{"name": "Suraj",}', {"name": "Suraj"}, "TRAILING_COMMA"),
        ("{'name': 'Suraj'}", {"name": "Suraj"}, "SINGLE_QUOTED_STRING"),
        ('{name: "Suraj", region: "us-east-1"}', {"name": "Suraj", "region": "us-east-1"}, "UNQUOTED_KEY"),
        ('{"active": True, "deleted": False, "value": None}', {"active": True, "deleted": False, "value": None}, "PYTHON_LITERAL"),
    ],
)
def test_supported_repairs(source, expected, change_type):
    result = repair_json(source)
    assert result["repaired"] is True
    assert json.loads(result["output"]) == expected
    assert change_type in {change["type"] for change in result["changes"]}


def test_canonical_broken_example_repairs_strictly():
    source = """{
  name: 'Payload Doctor',
  services: [
    'Lambda',
    'API Gateway',
  ],
}"""
    result = repair_json(source)
    assert result["repaired"] is True
    assert json.loads(result["output"]) == {
        "name": "Payload Doctor",
        "services": ["Lambda", "API Gateway"],
    }
    assert len(result["changes"]) == 7


@pytest.mark.parametrize(
    "source",
    [
        '{"name": "missing brace"',
        '{name: unknownValue}',
        "{'name': 'unterminated}",
        '{"price": 12..4}',
        "{,}",
        "[,]",
        '{"name":,}',
    ],
)
def test_unsafe_or_unknown_repairs_are_refused(source):
    result = repair_json(source)
    assert result["repaired"] is False
    assert "output" not in result
    assert result["changes"] == []


@pytest.mark.parametrize(
    "source",
    [
        '{"name":"already valid"}',
        '{"text":"hello,}"}',
        '{"text":"True False None"}',
        '{"url":"https://example.com?a:b"}',
        '{"message":"name: test"}',
        '{"apostrophe":"Suraj\'s project"}',
        '{"message":"He said \\"hello\\""}',
    ],
)
def test_valid_json_is_not_modified(source):
    result = repair_json(source)
    assert result == {
        "repaired": False,
        "message": "Payload is already valid JSON.",
        "output": source,
        "changes": [],
    }


def test_repairs_do_not_change_string_contents():
    source = "{'note': 'True, None, and {name: x} are text'}"
    result = repair_json(source)
    assert json.loads(result["output"])["note"] == "True, None, and {name: x} are text"
