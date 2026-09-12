# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

React and TypeScript with Vite, backed by a Python 3.12 AWS Lambda exposed through Amazon API Gateway and deployed with AWS SAM. The frontend is hosted by AWS Amplify.

## Users

Developers debugging JSON and common AWS event payloads during development, integration testing, incident response, and demos. Their primary job is to find small syntax or structural defects quickly without sending payloads to a storage service.

## Product Purpose

Payload Doctor validates, diagnoses, formats, minifies, and conservatively repairs JSON. It also validates the useful structural fields of API Gateway proxy, SQS, SNS, and EventBridge events and can check data against a user-provided JSON Schema. Success means a user can paste a payload, understand the exact fault, and copy a corrected result in seconds.

## Positioning

Unlike a generic JSON formatter, Payload Doctor separates strict JSON syntax validity from pragmatic AWS event structure validation. The defining proof is an SQS payload that is valid JSON but fails because `Records[0].body` is an object instead of the string SQS normally delivers.

## Operating Context

The primary surface is a desktop developer workbench with payload input and diagnosis visible side by side; it stacks into a single flow on mobile. Payloads may contain sensitive information and are processed transiently through the AWS backend.

## Capabilities and Constraints

- Supports generic JSON, API Gateway proxy, SQS, SNS, and EventBridge payload types.
- Uses strict JSON parsing, deterministic metrics, conservative non-executing repair, and standards-based JSON Schema validation.
- Limits payloads to 1 MiB and schemas to 256 KiB.
- Does not store payload history, authenticate users, execute input, or add a database.
- AWS checks are described as payload structure validation, not a reproduction of every AWS internal validation rule.

## Brand Commitments

The product name is **Payload Doctor** and the tagline is **Debug JSON and AWS event payloads instantly.** The interface is a polished, dark developer tool rather than a generic CRUD dashboard. Copy is concise, factual, and diagnostic. The AWS architecture section remains subtle.

## Evidence on Hand

The supplied SQS and broken generic JSON demo scenarios are the canonical product demonstrations. No customer claims, testimonials, usage statistics, or performance benchmarks are available and none should be fabricated.

## Product Principles

- Diagnose the actionable defect, not merely whether parsing failed.
- Keep results deterministic and explainable.
- Treat payload privacy as a product behavior, not fine print.
- Prefer fast, reliable, boring infrastructure over feature breadth.
- Make the two canonical demos work without setup or external data.

## Accessibility & Inclusion

All workflows must be keyboard operable, use semantic labels and visible focus states, maintain sufficient contrast, and expose validation summaries and status changes to assistive technology.
