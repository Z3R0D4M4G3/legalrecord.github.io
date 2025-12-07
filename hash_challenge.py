#!/usr/bin/env python3
"""
hash_challenge.py

Public Legal Record System (PLRS)
Challenge Hashing & Integrity Lock Utility

Purpose:
    Produce a cryptographic hash of a fully validated PLRS Challenge JSON file.
    This hash serves as the immutable integrity anchor for public verification,
    audit, and court use of Challenge records.

Spec basis:
    - challenge_schema.json (structural validation must already be complete)
    - PIPELINE.md (Challenge extension of Step 4 — Hashing & Integrity Lock)
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


def canonical_serialize(challenge_data: Dict[str, Any]) -> bytes:
    """
    Serialize the Challenge into a canonical, deterministic JSON byte sequence.

    Rules:
        - UTF-8 encoding
        - Sorted keys
        - No trailing whitespace
        - Stable separators

    This ensures that the same Challenge always produces the same hash.
    """
    canonical_str = json.dumps(
        challenge_data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":")
    )
    return canonical_str.encode("utf-8")


def hash_challenge(challenge_data: Dict[str, Any], algorithm: str = "sha256") -> str:
    """
    Hash the canonical serialized Challenge.

    Default:
        SHA-256 (hex encoded)
    """
    data_bytes = canonical_serialize(challenge_data)

    try:
        h = hashlib.new(algorithm)
    except ValueError:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    h.update(data_bytes)
    return h.hexdigest()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a cryptographic hash for a fully-valid PLRS Challenge JSON file. "
            "This hash anchors the Challenge for immutable public verification."
        )
    )
    parser.add_argument(
        "challenge_file",
        help="Path to the normalized and schema-valid Challenge JSON file."
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
        help="Write the resulting hash to a .hash file alongside the Challenge."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    challenge_path = Path(args.challenge_file)

    try:
        challenge_data = load_json_file(challenge_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    try:
        digest = hash_challenge(challenge_data, algorithm=args.algorithm)
    except ValueError as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    sys.stdout.write(f"[HASH] {digest}\n")

    if args.write:
        hash_path = challenge_path.with_suffix(challenge_path.suffix + ".hash")
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
