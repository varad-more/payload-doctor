import copy

import pytest

from validators import validate_payload


VALID_EVENTS = {
    "sqs": {
        "Records": [
            {
                "messageId": "abc-123",
                "receiptHandle": "handle",
                "body": '{"orderId":"ORD-42"}',
                "attributes": {},
                "messageAttributes": {},
                "md5OfBody": "deadbeef",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:orders",
                "awsRegion": "us-east-1",
            }
        ]
    },
    "sns": {
        "Records": [
            {
                "EventSource": "aws:sns",
                "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789012:topic:subscription",
                "Sns": {
                    "Type": "Notification",
                    "MessageId": "abc-123",
                    "TopicArn": "arn:aws:sns:us-east-1:123456789012:topic",
                    "Message": "hello",
                    "Timestamp": "2026-09-12T12:00:00.000Z",
                    "MessageAttributes": {},
                },
            }
        ]
    },
    "eventbridge": {
        "version": "0",
        "id": "abc-123",
        "detail-type": "Order created",
        "source": "com.example.orders",
        "account": "123456789012",
        "time": "2026-09-12T12:00:00Z",
        "region": "us-east-1",
        "resources": [],
        "detail": {"orderId": "ORD-42"},
    },
    "api_gateway": {
        "resource": "/orders",
        "path": "/orders",
        "httpMethod": "POST",
        "headers": {"content-type": "application/json"},
        "requestContext": {},
        "body": '{"orderId":"ORD-42"}',
        "isBase64Encoded": False,
    },
}


@pytest.mark.parametrize("payload_type", VALID_EVENTS)
def test_valid_event_passes(payload_type):
    errors, warnings = validate_payload(payload_type, VALID_EVENTS[payload_type])
    assert errors == []
    assert warnings == []


@pytest.mark.parametrize("payload_type", VALID_EVENTS)
def test_unexpected_additional_field_does_not_fail(payload_type):
    event = copy.deepcopy(VALID_EVENTS[payload_type])
    event["futureAwsField"] = {"preserved": True}
    errors, _ = validate_payload(payload_type, event)
    assert errors == []


@pytest.mark.parametrize(
    ("payload_type", "event", "path"),
    [
        ("sqs", {}, "$.Records"),
        ("sns", {"Records": [{}]}, "$.Records[0].EventSource"),
        ("eventbridge", {"version": "0"}, "$.id"),
        ("api_gateway", {}, "$.httpMethod"),
    ],
)
def test_missing_important_field_fails(payload_type, event, path):
    errors, _ = validate_payload(payload_type, event)
    assert path in {error["path"] for error in errors}


@pytest.mark.parametrize(
    ("payload_type", "mutate", "path"),
    [
        ("sqs", lambda event: event["Records"][0].update(body={"not": "a string"}), "$.Records[0].body"),
        ("sns", lambda event: event["Records"][0].update(Sns=[]), "$.Records[0].Sns"),
        ("eventbridge", lambda event: event.update(resources={}), "$.resources"),
        ("api_gateway", lambda event: event.update(isBase64Encoded="false"), "$.isBase64Encoded"),
    ],
)
def test_wrong_type_fails(payload_type, mutate, path):
    event = copy.deepcopy(VALID_EVENTS[payload_type])
    mutate(event)
    errors, _ = validate_payload(payload_type, event)
    assert path in {error["path"] for error in errors}


def test_sqs_demo_returns_exact_actionable_issue():
    event = {
        "Records": [
            {
                "messageId": "abc-123",
                "body": {"orderId": "ORD-42"},
                "eventSource": "aws:sqs",
                "awsRegion": "us-east-1",
            }
        ]
    }
    errors, warnings = validate_payload("sqs", event)
    assert warnings == []
    assert errors == [
        {
            "code": "WRONG_TYPE",
            "path": "$.Records[0].body",
            "message": "$.Records[0].body must be string.",
            "expected": "string",
            "received": "object",
            "hint": "SQS delivers message bodies as strings. JSON inside a message is encoded as a string.",
        }
    ]


def test_suspicious_event_source_is_a_warning():
    event = copy.deepcopy(VALID_EVENTS["sqs"])
    event["Records"][0]["eventSource"] = "aws:sns"
    errors, warnings = validate_payload("sqs", event)
    assert errors == []
    assert warnings[0]["path"] == "$.Records[0].eventSource"


def test_sqs_event_source_wrong_type_is_an_error():
    event = copy.deepcopy(VALID_EVENTS["sqs"])
    event["Records"][0]["eventSource"] = 42
    errors, warnings = validate_payload("sqs", event)
    assert warnings == []
    assert errors[0]["path"] == "$.Records[0].eventSource"


@pytest.mark.parametrize("records", [{}, [], None])
def test_sqs_records_shape_is_enforced(records):
    errors, warnings = validate_payload("sqs", {"Records": records})
    assert warnings == []
    assert errors[0]["path"] == "$.Records"


def test_sns_required_notification_fields_are_enforced_but_subject_is_optional():
    event = copy.deepcopy(VALID_EVENTS["sns"])
    event["Records"][0]["Sns"].pop("Message")
    event["Records"][0]["Sns"]["MessageId"] = 42
    event["Records"][0]["Sns"]["futureField"] = {"preserved": True}
    errors, warnings = validate_payload("sns", event)
    assert warnings == []
    assert {error["path"] for error in errors} == {
        "$.Records[0].Sns.Message",
        "$.Records[0].Sns.MessageId",
    }


def test_eventbridge_object_detail_and_additional_fields_pass():
    event = copy.deepcopy(VALID_EVENTS["eventbridge"])
    event["detail"]["futureField"] = True
    event["futureTopLevelField"] = []
    assert validate_payload("eventbridge", event) == ([], [])


def test_api_gateway_nullable_fields_pass():
    event = copy.deepcopy(VALID_EVENTS["api_gateway"])
    event.update(
        headers=None,
        multiValueHeaders=None,
        queryStringParameters=None,
        multiValueQueryStringParameters=None,
        pathParameters=None,
        stageVariables=None,
        body=None,
    )
    assert validate_payload("api_gateway", event) == ([], [])


def test_api_gateway_version_marker_does_not_replace_required_v1_fields():
    errors, warnings = validate_payload("api_gateway", {"version": "1.0"})

    assert warnings == []
    assert {(error["path"], error["code"], error["message"]) for error in errors} == {
        (
            "$.httpMethod",
            "MISSING_FIELD",
            "API Gateway REST proxy event must include httpMethod.",
        ),
        (
            "$.requestContext",
            "MISSING_FIELD",
            "API Gateway REST proxy event must include requestContext.",
        ),
    }


@pytest.mark.parametrize(
    ("event", "missing_path"),
    [
        ({"httpMethod": "GET"}, "$.requestContext"),
        ({"requestContext": {}}, "$.httpMethod"),
    ],
)
def test_api_gateway_requires_both_v1_fields(event, missing_path):
    errors, warnings = validate_payload("api_gateway", event)

    assert warnings == []
    assert [(error["path"], error["code"]) for error in errors] == [(missing_path, "MISSING_FIELD")]


@pytest.mark.parametrize(
    ("event", "wrong_path"),
    [
        ({"httpMethod": 123, "requestContext": {}}, "$.httpMethod"),
        ({"httpMethod": "GET", "requestContext": "invalid"}, "$.requestContext"),
    ],
)
def test_api_gateway_required_v1_field_types(event, wrong_path):
    errors, warnings = validate_payload("api_gateway", event)

    assert warnings == []
    assert len(errors) == 1
    assert errors[0]["path"] == wrong_path
    assert errors[0]["code"] == "WRONG_TYPE"


def test_api_gateway_multi_value_query_parameters_type_is_validated():
    event = copy.deepcopy(VALID_EVENTS["api_gateway"])
    event["multiValueQueryStringParameters"] = []

    errors, warnings = validate_payload("api_gateway", event)

    assert warnings == []
    assert [(error["path"], error["code"]) for error in errors] == [
        ("$.multiValueQueryStringParameters", "WRONG_TYPE")
    ]


def test_api_gateway_http_api_v2_is_not_misrepresented_as_supported():
    errors, warnings = validate_payload(
        "api_gateway",
        {
            "version": "2.0",
            "requestContext": {"http": {"method": "GET", "path": "/orders"}},
            "headers": {},
            "body": None,
            "isBase64Encoded": False,
        },
    )
    assert warnings == []
    assert errors[0]["code"] == "UNSUPPORTED_EVENT_VERSION"
    assert errors[0]["path"] == "$.version"
