#!/usr/bin/env python3
"""
validate_challenge.py

Public Legal Record System (PLRS)
Challenge Validation Utility

Purpose:
    Validate a PLRS Challenge JSON file against challenge_schema.json,
    ensuring structural correctness before normalization, hashing,
    storage, or linkage into the ledger.

Spec basis:
    - challenge_schema.json
    - challenge_schema Extended Description
    - TIME_NORMALIZATION.md (Timestamp_UTC must be canonical when present)
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


def validate_challenge(challenge_data: Dict[str, Any], schema_data: Dict[str, Any]) -> None:
    """
    Validate challenge_data against schema_data.

    Raises:
        jsonschema.exceptions.ValidationError on failure.
    """
    validator = Draft7Validator(schema_data)
    errors = sorted(validator.iter_errors(challenge_data), key=lambda e: e.path)

    if errors:
        for err in errors:
            loc = ".".join(str(p) for p in err.path) or "<root>"
            sys.stderr.write(f"[SCHEMA ERROR] {loc}: {err.message}\n")
        # Raise the first one programmatically
        raise errors[0]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a PLRS Challenge JSON file against challenge_schema.json. "
            "Use this before hashing or linking a Challenge into the ledger."
        )
    )
    parser.add_argument(
        "challenge_file",
        help="Path to the Challenge JSON file to validate."
    )
    parser.add_argument(
        "--schema",
        dest="schema_file",
        default="challenge_schema.json",
        help="Path to the challenge_schema.json file (default: challenge_schema.json in current directory)."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    challenge_path = Path(args.challenge_file)
    schema_path = Path(args.schema_file)

    try:
        challenge_data = load_json_file(challenge_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    try:
        schema_data = load_json_file(schema_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    try:
        validate_challenge(challenge_data, schema_data)
    except js_exceptions.ValidationError:
        sys.stderr.write("[RESULT] INVALID: Challenge does NOT conform to challenge_schema.json\n")
        return 1

    sys.stdout.write("[RESULT] VALID: Challenge conforms to challenge_schema.json\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
