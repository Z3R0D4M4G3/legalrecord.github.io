#!/usr/bin/env python3
"""
verify_ledger_integrity.py

Public Legal Record System (PLRS)
Global Ledger Integrity Auditor

Purpose:
    Perform a cross-ledger audit over:

        - Event index (public_index.json)
        - Challenge index (public_challenge_index.json)
        - Event JSON files
        - Challenge JSON files

    Checks performed:

        1. Index structural integrity:
            - JSON array
            - Strict, gapless Index_Seq sequence
        2. Record existence:
            - Each Event_ID in the Event index has a corresponding Event JSON file
            - Each Challenge_ID in the Challenge index has a corresponding Challenge JSON file
        3. Hash correctness:
            - Recompute hash for each Event and compare to index Hash
            - Recompute hash for each Challenge and compare to challenge index Hash
        4. Cross-link sanity:
            - Each Challenge's Challenged_Event_ID exists in the Event index

    This provides a top-level "ledger health" report for PLRS instances.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List

from hash_event import hash_event  # type: ignore
from hash_challenge import hash_challenge  # type: ignore


def load_json_file(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file: {path}") from exc


def verify_index_sequence(index_data: List[Dict[str, Any]], label: str) -> List[str]:
    errors: List[str] = []
    expected = 1
    for entry in index_data:
        seq = entry.get("Index_Seq")
        if seq != expected:
            errors.append(
                f"[{label}] Index_Seq error: expected {expected}, found {seq} "
                f"for entry {entry}"
            )
            # Attempt to resync if possible
            try:
                expected = int(seq)
            except Exception:
                pass
        expected += 1
    return errors


def verify_event_index(
    index_data: List[Dict[str, Any]],
    events_dir: Path
) -> List[str]:
    errors: List[str] = []

    # Sequence integrity
    errors.extend(verify_index_sequence(index_data, "EVENT_INDEX"))

    # Existence + hash correctness
    for entry in index_data:
        event_id = entry.get("Event_ID")
        index_hash = entry.get("Hash")

        if not event_id or not index_hash:
            errors.append(
                f"[EVENT_INDEX] Missing Event_ID or Hash in entry: {entry}"
            )
            continue

        event_file = events_dir / f"{event_id}.json"

        if not event_file.exists():
            errors.append(
                f"[EVENT_INDEX] Missing Event JSON file for Event_ID={event_id} "
                f"at {event_file}"
            )
            continue

        try:
            event_data = load_json_file(event_file)
        except (FileNotFoundError, ValueError) as exc:
            errors.append(
                f"[EVENT_INDEX] Failed to load Event file for Event_ID={event_id}: {exc}"
            )
            continue

        try:
            computed_hash = hash_event(event_data)
        except Exception as exc:
            errors.append(
                f"[EVENT_INDEX] Failed to compute hash for Event_ID={event_id}: {exc}"
            )
            continue

        if computed_hash != index_hash:
            errors.append(
                f"[EVENT_INDEX] Hash mismatch for Event_ID={event_id}: "
                f"index={index_hash}, computed={computed_hash}"
            )

    return errors


def verify_challenge_index(
    index_data: List[Dict[str, Any]],
    challenges_dir: Path,
    known_event_ids: List[str]
) -> List[str]:
    errors: List[str] = []

    # Sequence integrity
    errors.extend(verify_index_sequence(index_data, "CHALLENGE_INDEX"))

    # Existence + hash correctness + cross-linking
    for entry in index_data:
        challenge_id = entry.get("Challenge_ID")
        index_hash = entry.get("Hash")
        challenged_event_id = entry.get("Challenged_Event_ID")

        if not challenge_id or not index_hash:
            errors.append(
                f"[CHALLENGE_INDEX] Missing Challenge_ID or Hash in entry: {entry}"
            )
            continue

        challenge_file = challenges_dir / f"{challenge_id}.json"

        if not challenge_file.exists():
            errors.append(
                f"[CHALLENGE_INDEX] Missing Challenge JSON file for Challenge_ID={challenge_id} "
                f"at {challenge_file}"
            )
            continue

        try:
            challenge_data = load_json_file(challenge_file)
        except (FileNotFoundError, ValueError) as exc:
            errors.append(
                f"[CHALLENGE_INDEX] Failed to load Challenge file for Challenge_ID={challenge_id}: {exc}"
            )
            continue

        # Hash correctness
        try:
            computed_hash = hash_challenge(challenge_data)
        except Exception as exc:
            errors.append(
                f"[CHALLENGE_INDEX] Failed to compute hash for Challenge_ID={challenge_id}: {exc}"
            )
            continue

        if computed_hash != index_hash:
            errors.append(
                f"[CHALLENGE_INDEX] Hash mismatch for Challenge_ID={challenge_id}: "
                f"index={index_hash}, computed={computed_hash}"
            )

        # Cross-link: Challenged_Event_ID must exist
        if challenged_event_id and challenged_event_id not in known_event_ids:
            errors.append(
                f"[CHALLENGE_INDEX] Challenged_Event_ID={challenged_event_id} "
                f"for Challenge_ID={challenge_id} does not exist in Event index."
            )

    return errors


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Perform a cross-ledger integrity audit for PLRS: "
            "Events ↔ Event index ↔ Challenges ↔ Challenge index."
        )
    )
    parser.add_argument(
        "--event-index",
        dest="event_index_file",
        default="public_index.json",
        help="Path to the Event index file (default: public_index.json)."
    )
    parser.add_argument(
        "--challenge-index",
        dest="challenge_index_file",
        default="public_challenge_index.json",
        help="Path to the Challenge index file (default: public_challenge_index.json)."
    )
    parser.add_argument(
        "--events-dir",
        dest="events_dir",
        default=".",
        help="Directory containing Event JSON files (default: current directory)."
    )
    parser.add_argument(
        "--challenges-dir",
        dest="challenges_dir",
        default=".",
        help="Directory containing Challenge JSON files (default: current directory)."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    event_index_path = Path(args.event_index_file)
    challenge_index_path = Path(args.challenge_index_file)
    events_dir = Path(args.events_dir)
    challenges_dir = Path(args.challenges_dir)

    overall_errors: List[str] = []

    # Load indices
    try:
        event_index_data = load_json_file(event_index_path)
        if not isinstance(event_index_data, list):
            raise ValueError("Event index file must contain a JSON array.")
    except (FileNotFoundError, ValueError) as exc:
        overall_errors.append(f"[EVENT_INDEX] {exc}")
        event_index_data = []

    try:
        challenge_index_data = load_json_file(challenge_index_path)
        if not isinstance(challenge_index_data, list):
            raise ValueError("Challenge index file must contain a JSON array.")
    except (FileNotFoundError, ValueError) as exc:
        overall_errors.append(f"[CHALLENGE_INDEX] {exc}")
        challenge_index_data = []

    # Verify event side
    if event_index_data:
        overall_errors.extend(
            verify_event_index(event_index_data, events_dir=events_dir)
        )

    # Known Event IDs for cross-links
    known_event_ids = [
        entry.get("Event_ID")
        for entry in event_index_data
        if isinstance(entry.get("Event_ID"), str)
    ]

    # Verify challenge side
    if challenge_index_data:
        overall_errors.extend(
            verify_challenge_index(
                challenge_index_data,
                challenges_dir=challenges_dir,
                known_event_ids=known_event_ids
            )
        )

    if overall_errors:
        sys.stderr.write("[RESULT] LEDGER INTEGRITY AUDIT FAILED.\n")
        for err in overall_errors:
            sys.stderr.write(f" - {err}\n")
        return 1

    sys.stdout.write("[RESULT] LEDGER INTEGRITY AUDIT PASSED: all indices and records consistent.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
