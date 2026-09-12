from __future__ import annotations

import re
from typing import Any

from analyzer.json_ops import JsonProblem, format_json, parse_json


def _line_at(text: str, position: int) -> int:
    return text.count("\n", 0, position) + 1


def _single_quotes(text: str) -> tuple[str, list[dict[str, Any]]] | None:
    output: list[str] = []
    changes: list[dict[str, Any]] = []
    index = 0
    in_double = False
    escaped = False

    while index < len(text):
        char = text[index]
        if in_double:
            output.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_double = False
            index += 1
            continue
        if char == '"':
            in_double = True
            output.append(char)
            index += 1
            continue
        if char != "'":
            output.append(char)
            index += 1
            continue

        start = index
        index += 1
        converted: list[str] = []
        while index < len(text):
            char = text[index]
            if char in "\r\n":
                return None
            if char == "'":
                break
            if char == "\\":
                if index + 1 >= len(text):
                    return None
                following = text[index + 1]
                if following == "'":
                    converted.append("'")
                elif following in '\"\\/bfnrt':
                    converted.extend(("\\", following))
                elif following == "u" and re.match(r"^[0-9a-fA-F]{4}$", text[index + 2 : index + 6]):
                    converted.extend(("\\", "u", text[index + 2 : index + 6]))
                    index += 4
                else:
                    return None
                index += 2
                continue
            converted.append('\\"' if char == '"' else char)
            index += 1
        if index >= len(text):
            return None
        output.extend(('"', "".join(converted), '"'))
        changes.append(
            {
                "type": "SINGLE_QUOTED_STRING",
                "message": "Converted a single-quoted string to JSON double quotes.",
                "line": _line_at(text, start),
            }
        )
        index += 1

    return "".join(output), changes


def _outside_string_positions(text: str) -> list[bool]:
    outside = [True] * len(text)
    in_string = escaped = False
    for index, char in enumerate(text):
        outside[index] = not in_string
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
    return outside


def _unquoted_keys(text: str) -> tuple[str, list[dict[str, Any]]]:
    pattern = re.compile(r"(?P<prefix>[{,])(?P<space>\s*)(?P<key>[A-Za-z_][A-Za-z0-9_]*)(?P<tail>\s*:)")
    outside = _outside_string_positions(text)
    output: list[str] = []
    changes: list[dict[str, Any]] = []
    previous = 0
    for match in pattern.finditer(text):
        key_start = match.start("key")
        if not outside[match.start()] or not outside[key_start]:
            continue
        output.extend((text[previous:key_start], '"', match.group("key"), '"'))
        previous = match.end("key")
        changes.append(
            {
                "type": "UNQUOTED_KEY",
                "message": f'Quoted object key "{match.group("key")}".',
                "line": _line_at(text, key_start),
            }
        )
    output.append(text[previous:])
    return "".join(output), changes


def _python_literals(text: str) -> tuple[str, list[dict[str, Any]]]:
    pattern = re.compile(r"\b(True|False|None)\b")
    replacements = {"True": "true", "False": "false", "None": "null"}
    outside = _outside_string_positions(text)
    output: list[str] = []
    changes: list[dict[str, Any]] = []
    previous = 0
    for match in pattern.finditer(text):
        if not outside[match.start()]:
            continue
        prior = text[: match.start()].rstrip()
        if prior and prior[-1] not in ":[,":
            continue
        output.extend((text[previous : match.start()], replacements[match.group()]))
        previous = match.end()
        changes.append(
            {
                "type": "PYTHON_LITERAL",
                "message": f"Converted {match.group()} to {replacements[match.group()] }.",
                "line": _line_at(text, match.start()),
            }
        )
    output.append(text[previous:])
    return "".join(output), changes


def _trailing_commas(text: str) -> tuple[str, list[dict[str, Any]]]:
    outside = _outside_string_positions(text)
    output: list[str] = []
    changes: list[dict[str, Any]] = []
    previous = 0
    for index, char in enumerate(text):
        if char != "," or not outside[index]:
            continue
        following = index + 1
        while following < len(text) and text[following].isspace():
            following += 1
        prior = index - 1
        while prior >= 0 and text[prior].isspace():
            prior -= 1
        if following < len(text) and text[following] in "}]" and prior >= 0 and text[prior] not in "[{,:":
            output.append(text[previous:index])
            previous = index + 1
            changes.append(
                {
                    "type": "TRAILING_COMMA",
                    "message": "Removed a trailing comma before a closing bracket.",
                    "line": _line_at(text, index),
                }
            )
    output.append(text[previous:])
    return "".join(output), changes


def repair_json(content: str) -> dict[str, Any]:
    try:
        parse_json(content)
        return {
            "repaired": False,
            "message": "Payload is already valid JSON.",
            "output": content,
            "changes": [],
        }
    except JsonProblem:
        pass

    quoted = _single_quotes(content)
    if quoted is None:
        return {"repaired": False, "message": "Payload could not be repaired safely.", "changes": []}

    candidate, changes = quoted
    for repair in (_unquoted_keys, _python_literals, _trailing_commas):
        candidate, new_changes = repair(candidate)
        changes.extend(new_changes)

    if not changes:
        return {"repaired": False, "message": "Payload could not be repaired safely.", "changes": []}

    try:
        value = parse_json(candidate)
    except JsonProblem:
        return {"repaired": False, "message": "Payload could not be repaired safely.", "changes": []}

    return {
        "repaired": True,
        "message": f"Applied {len(changes)} safe repair{'s' if len(changes) != 1 else ''}.",
        "changes": changes,
        "output": format_json(value),
    }
