#!/usr/bin/env python3
"""
validate_event.py

Public Legal Record System (PLRS)
Event Validation Utility

Purpose:
    Validate a PLRS Event JSON file against schema.json, ensuring structural
    correctness before storage, hashing, or court use.

Spec basis:
    - SPEC.md
    - schema.json
    - TIME_NORMALIZATION.md (assumes Timestamp_UTC already normalized)
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict

try:
    from jsonschema import Draft7Validator, exceptions as js_exceptions
except ImportError:
    sys.stderr.write(
        "[FATAL] jsonschema is required. Install with:\n"
        "    pip install jsonschema\n"
    )
    sys.exit(1)


def load_json_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file: {path}") from exc


def validate_event(event_data: Dict[str, Any], schema_data: Dict[str, Any]) -> None:
    """
    Validate event_data against schema_data.

    Raises:
        jsonschema.exceptions.ValidationError on failure.
    """
    validator = Draft7Validator(schema_data)
    errors = sorted(validator.iter_errors(event_data), key=lambda e: e.path)

    if errors:
        # Raise the first error but also print a summary
        for err in errors:
            loc = ".".join(str(p) for p in err.path) or "<root>"
            sys.stderr.write(f"[SCHEMA ERROR] {loc}: {err.message}\n")
        # Raise the first one to signal failure programmatically
        raise errors[0]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a PLRS Event JSON file against schema.json. "
            "Use this before storing or hashing a record."
        )
    )
    parser.add_argument(
        "event_file",
        help="Path to the Event JSON file to validate."
    )
    parser.add_argument(
        "--schema",
        dest="schema_file",
        default="schema.json",
        help="Path to the schema.json file (default: schema.json in current directory)."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    event_path = Path(args.event_file)
    schema_path = Path(args.schema_file)

    try:
        event_data = load_json_file(event_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    try:
        schema_data = load_json_file(schema_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    try:
        validate_event(event_data, schema_data)
    except js_exceptions.ValidationError:
        # Errors already printed in validate_event
        sys.stderr.write("[RESULT] INVALID: Event does NOT conform to schema.json\n")
        return 1

    sys.stdout.write("[RESULT] VALID: Event conforms to schema.json\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
