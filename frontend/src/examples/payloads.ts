import type { PayloadType } from "../types/api";

export const EXAMPLES: Record<PayloadType, { valid: string; broken: string }> = {
  generic: {
    valid: `{
  "name": "Payload Doctor",
  "active": true,
  "services": ["Lambda", "API Gateway"]
}`,
    broken: `{
  name: 'Payload Doctor',
  services: [
    'Lambda',
    'API Gateway',
  ],
}`,
  },
  sqs: {
    valid: `{
  "Records": [
    {
      "messageId": "abc-123",
      "receiptHandle": "AQEB-example",
      "body": "{\\"orderId\\":\\"ORD-42\\"}",
      "attributes": {},
      "messageAttributes": {},
      "md5OfBody": "3be4a20a",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:orders",
      "awsRegion": "us-east-1"
    }
  ]
}`,
    broken: `{
  "Records": [
    {
      "messageId": "abc-123",
      "body": {
        "orderId": "ORD-42"
      },
      "eventSource": "aws:sqs",
      "awsRegion": "us-east-1"
    }
  ]
}`,
  },
  sns: {
    valid: `{
  "Records": [
    {
      "EventSource": "aws:sns",
      "EventSubscriptionArn": "arn:aws:sns:us-east-1:123456789012:orders:sub",
      "Sns": {
        "Type": "Notification",
        "MessageId": "msg-123",
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:orders",
        "Message": "{\\"orderId\\":\\"ORD-42\\"}",
        "Timestamp": "2026-09-12T12:00:00.000Z",
        "MessageAttributes": {}
      }
    }
  ]
}`,
    broken: `{
  "Records": [
    {
      "EventSource": "aws:sns",
      "EventSubscriptionArn": 42,
      "Sns": {
        "Type": "Notification",
        "Message": "Order created"
      }
    }
  ]
}`,
  },
  eventbridge: {
    valid: `{
  "version": "0",
  "id": "7bf73129-1428-4cd3-a780-95db273d1602",
  "detail-type": "Order Created",
  "source": "com.example.orders",
  "account": "123456789012",
  "time": "2026-09-12T12:00:00Z",
  "region": "us-east-1",
  "resources": [],
  "detail": {
    "orderId": "ORD-42"
  }
}`,
    broken: `{
  "version": "1",
  "id": 42,
  "detail-type": "Order Created",
  "source": "com.example.orders",
  "account": "demo",
  "time": "yesterday",
  "region": "us-east-1",
  "resources": {},
  "detail": "ORD-42"
}`,
  },
  api_gateway: {
    valid: `{
  "resource": "/orders",
  "path": "/orders",
  "httpMethod": "POST",
  "headers": {
    "content-type": "application/json"
  },
  "requestContext": {},
  "body": "{\\"orderId\\":\\"ORD-42\\"}",
  "isBase64Encoded": false
}`,
    broken: `{
  "path": "/orders",
  "httpMethod": 42,
  "headers": [],
  "requestContext": "missing",
  "body": {
    "orderId": "ORD-42"
  },
  "isBase64Encoded": "false"
}`,
  },
};
