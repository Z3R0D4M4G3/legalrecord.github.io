#!/usr/bin/env python3
"""
verify_index.py

Public Legal Record System (PLRS)
Public Ledger Verification Utility

Purpose:
    Verify the integrity of a PLRS public index file by:

    - Ensuring Index_Seq is strictly increasing and gapless.
    - Recomputing each Event's hash and comparing it to the index.
    - Reporting mismatches, missing files, or structural issues.

Spec basis:
    - PUBLIC_INDEX_FORMAT.md
    - PIPELINE.md (Verification workflow)
    - hash_event.py (hash logic)
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List

from hash_event import hash_event, canonical_serialize  # Reuse same logic


def load_json_file(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file: {path}") from exc


def verify_index_sequence(index_data: List[Dict[str, Any]]) -> List[str]:
    """
    Verify that Index_Seq is strictly increasing and gapless.
    Returns a list of human-readable error strings (empty list if OK).
    """
    errors = []
    expected = 1
    for entry in index_data:
        seq = entry.get("Index_Seq")
        if seq != expected:
            errors.append(
                f"Index_Seq error: expected {expected}, found {seq} for Event_ID={entry.get('Event_ID')}"
            )
            expected = seq if isinstance(seq, int) else expected
        expected += 1
    return errors


def verify_index_hashes(
    index_data: List[Dict[str, Any]],
    events_dir: Path,
    algo: str = "sha256"
) -> List[str]:
    """
    For each index entry:
        - Load corresponding Event JSON (Event_ID.json in events_dir).
        - Recompute its hash via hash_event.py logic.
        - Compare with the Hash field in the index.

    Returns a list of human-readable error strings (empty list if OK).
    """
    errors = []
    for entry in index_data:
        event_id = entry.get("Event_ID")
        expected_hash = entry.get("Hash")
        if not event_id or not expected_hash:
            errors.append(f"Missing Event_ID or Hash in index entry: {entry}")
            continue

        event_file = events_dir / f"{event_id}.json"
        try:
            event_data = load_json_file(event_file)
        except (FileNotFoundError, ValueError) as exc:
            errors.append(f"[MISSING/INVALID EVENT] {event_id}: {exc}")
            continue

        try:
            computed_hash = hash_event(event_data, algorithm=algo)
        except Exception as exc:
            errors.append(f"[HASH ERROR] {event_id}: failed to compute hash: {exc}")
            continue

        if computed_hash != expected_hash:
            errors.append(
                f"[HASH MISMATCH] {event_id}: index={expected_hash}, computed={computed_hash}"
            )

    return errors


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify a PLRS public index file and its referenced Event JSON files. "
            "Checks sequence ordering and recomputes hashes for integrity."
        )
    )
    parser.add_argument(
        "index_file",
        help="Path to the public index file (e.g., public_index.json)."
    )
    parser.add_argument(
        "--events-dir",
        dest="events_dir",
        default=".",
        help="Directory containing Event JSON files named as Event_ID.json (default: current directory)."
    )
    parser.add_argument(
        "--algo",
        dest="algorithm",
        default="sha256",
        help="Hash algorithm used (default: sha256). Must match hash_event.py usage."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    index_path = Path(args.index_file)
    events_dir = Path(args.events_dir)

    # Load index
    try:
        index_data = load_json_file(index_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    if not isinstance(index_data, list):
        sys.stderr.write("[ERROR] Index file must contain a JSON array of entries.\n")
        return 1

    overall_errors: List[str] = []

    # Sequence verification
    seq_errors = verify_index_sequence(index_data)
    overall_errors.extend(seq_errors)

    # Hash verification
    hash_errors = verify_index_hashes(index_data, events_dir=events_dir, algo=args.algorithm)
    overall_errors.extend(hash_errors)

    if overall_errors:
        sys.stderr.write("[RESULT] INDEX VERIFICATION FAILED\n")
        for err in overall_errors:
            sys.stderr.write(f" - {err}\n")
        return 1

    sys.stdout.write("[RESULT] INDEX VERIFICATION PASSED: all entries consistent and hashes match.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
