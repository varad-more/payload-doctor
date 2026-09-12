import pytest

from analyzer.json_ops import JsonProblem
from analyzer.schema import validate_against_schema


SCHEMA = """{
  "type": "object",
  "required": ["user", "items"],
  "properties": {
    "user": {
      "type": "object",
      "required": ["email"],
      "properties": {"email": {"type": "string"}}
    },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["price"],
        "properties": {"price": {"type": "number"}}
      }
    }
  }
}"""


def test_valid_schema_and_data():
    result = validate_against_schema({"user": {"email": "dev@example.com"}, "items": [{"price": 12}]}, SCHEMA)
    assert result == {"schemaValid": True, "schemaAccepted": True, "errors": []}


def test_valid_schema_and_invalid_data_has_stable_paths():
    result = validate_against_schema({"user": {"email": None}, "items": [{}, {"price": "free"}]}, SCHEMA)
    assert result["schemaAccepted"] is True
    assert result["schemaValid"] is False
    assert [error["path"] for error in result["errors"]] == [
        "$.items[0].price",
        "$.items[1].price",
        "$.user.email",
    ]
    assert result["errors"][0]["message"] == "Required property is missing."
    assert result["errors"][2]["expected"] == "string"
    assert result["errors"][2]["received"] == "null"


def test_invalid_schema():
    result = validate_against_schema({}, '{"type": "not-a-real-type"}')
    assert result["schemaAccepted"] is False
    assert result["schemaValid"] is False
    assert result["errors"][0]["code"] == "INVALID_SCHEMA"


@pytest.mark.parametrize("schema", ["42", "[]", '"string"', "null"])
def test_non_schema_json_values_are_rejected(schema):
    result = validate_against_schema({}, schema)
    assert result == {
        "schemaValid": False,
        "schemaAccepted": False,
        "errors": [
            {
                "code": "INVALID_SCHEMA",
                "path": "$",
                "message": "JSON Schema must be an object or boolean.",
            }
        ],
    }


def test_boolean_schemas_are_supported():
    assert validate_against_schema({}, "true") == {
        "schemaValid": True,
        "schemaAccepted": True,
        "errors": [],
    }
    rejected = validate_against_schema({}, "false")
    assert rejected["schemaAccepted"] is True
    assert rejected["schemaValid"] is False


def test_malformed_schema_json():
    with pytest.raises(JsonProblem) as captured:
        validate_against_schema({}, '{"type":}')
    assert captured.value.error["code"] == "INVALID_SCHEMA_JSON"


def test_local_schema_reference_works():
    schema = '{"$defs":{"id":{"type":"integer"}},"properties":{"id":{"$ref":"#/$defs/id"}}}'
    result = validate_against_schema({"id": "wrong"}, schema)
    assert result["schemaAccepted"] is True
    assert result["errors"][0]["path"] == "$.id"


def test_remote_schema_reference_is_not_fetched(monkeypatch):
    def fail_if_called(*_args, **_kwargs):
        raise AssertionError("network retrieval was attempted")

    monkeypatch.setattr("urllib.request.urlopen", fail_if_called)
    result = validate_against_schema({}, '{"$ref":"https://example.com/schema.json"}')
    assert result["schemaAccepted"] is False
    assert result["errors"][0]["code"] == "UNRESOLVABLE_SCHEMA_REFERENCE"


def test_multiple_missing_properties_have_distinct_paths():
    result = validate_against_schema({}, '{"type":"object","required":["first","second"]}')
    assert [error["path"] for error in result["errors"]] == ["$.first", "$.second"]
