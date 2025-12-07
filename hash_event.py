#!/usr/bin/env python3
"""
hash_event.py

Public Legal Record System (PLRS)
Event Hashing & Integrity Lock Utility

Purpose:
    Produce a cryptographic hash of a fully normalized and schema-valid
    PLRS Event JSON file. This hash serves as the immutable integrity anchor
    for public verification, audit, and court use.

Spec basis:
    - SPEC.md (Immutability Rule)
    - PIPELINE.md (Step 4 — Hashing & Integrity Lock)
    - schema.json (Structural validation must already be complete)
"""

import sys
import json
import argparse
import hashlib
from pathlib import Path
from typing import Any, Dict


def load_json_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file: {path}") from exc


def canonical_serialize(event_data: Dict[str, Any]) -> bytes:
    """
    Serialize the Event into a canonical, deterministic JSON byte sequence.

    Rules:
        - UTF-8 encoding
        - Sorted keys
        - No trailing whitespace
        - Stable separators

    This ensures that the same Event always produces the same hash.
    """
    canonical_str = json.dumps(
        event_data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )
    return canonical_str.encode("utf-8")


def hash_event(event_data: Dict[str, Any], algorithm: str = "sha256") -> str:
    """
    Hash the canonical serialized Event.

    Default:
        SHA-256 (hex encoded)
    """
    data_bytes = canonical_serialize(event_data)

    try:
        h = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    h.update(data_bytes)
    return h.hexdigest()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a cryptographic hash for a fully-valid PLRS Event JSON file. "
            "This hash anchors the record for immutable public verification."
        )
    )
    parser.add_argument(
        "event_file",
        help="Path to the normalized and schema-valid Event JSON file."
    )
    parser.add_argument(
        "--algo",
        dest="algorithm",
        default="sha256",
        help="Hash algorithm to use (default: sha256)."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the resulting hash to a .hash file alongside the Event."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    event_path = Path(args.event_file)

    try:
        event_data = load_json_file(event_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    try:
        digest = hash_event(event_data, algorithm=args.algorithm)
    except ValueError as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    sys.stdout.write(f"[HASH] {digest}\n")

    if args.write:
        hash_path = event_path.with_suffix(event_path.suffix + ".hash")
        try:
            with hash_path.open("w", encoding="utf-8") as f:
                f.write(digest + "\n")
        except OSError as exc:
            sys.stderr.write(f"[ERROR] Failed to write hash file: {exc}\n")
            return 1

        sys.stdout.write(f"[SAVED] {hash_path}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
