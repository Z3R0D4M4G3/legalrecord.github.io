#!/usr/bin/env python3
"""
verify_bundle.py

Public Legal Record System (PLRS)
Bundle Verification Utility (Event & Challenge)

Purpose:
    Verify a PLRS Evidence Bundle JSON file by:

    - Checking basic bundle structure and required fields
    - Recomputing the hash from the embedded record (Event or Challenge)
    - Comparing it against the hash stored in the bundle
    - If an Index_Entry is present, confirming the hash matches the index entry
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict

# We reuse existing hashing functions to ensure identical logic.
# If these live in separate modules, adjust imports accordingly.
try:
    from hash_event import hash_event, canonical_serialize as event_serialize  # type: ignore
except ImportError:
    hash_event = None
    event_serialize = None

try:
    from hash_challenge import hash_challenge, canonical_serialize as challenge_serialize  # type: ignore
except ImportError:
    hash_challenge = None
    challenge_serialize = None


def load_json_file(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file: {path}") from exc


def verify_event_bundle(bundle: Dict[str, Any]) -> bool:
    if hash_event is None:
        raise RuntimeError("hash_event.py not available in import path.")

    ok = True
    event = bundle.get("Event")
    bundle_hash = bundle.get("Event_Hash")
    index_entry = bundle.get("Index_Entry")

    if not isinstance(event, dict):
        sys.stderr.write("[ERROR] Event bundle missing or invalid 'Event' object.\n")
        ok = False

    if not isinstance(bundle_hash, str) or not bundle_hash:
        sys.stderr.write("[ERROR] Event bundle missing or invalid 'Event_Hash'.\n")
        ok = False

    if not ok:
        return False

    # Recompute hash
    try:
        computed_hash = hash_event(event)
    except Exception as exc:
        sys.stderr.write(f"[ERROR] Failed to compute Event hash: {exc}\n")
        return False

    if computed_hash != bundle_hash:
        sys.stderr.write(
            f"[ERROR] Event hash mismatch: bundle={bundle_hash}, computed={computed_hash}\n"
        )
        ok = False
    else:
        sys.stdout.write("[OK] Event hash matches bundle hash.\n")

    # If index entry is present, verify it too
    if index_entry is not None:
        idx_hash = index_entry.get("Hash")
        if idx_hash != bundle_hash:
            sys.stderr.write(
                f"[ERROR] Index_Entry.Hash mismatch: index={idx_hash}, bundle={bundle_hash}\n"
            )
            ok = False
        else:
            sys.stdout.write("[OK] Index_Entry.Hash matches bundle hash.\n")

    return ok


def verify_challenge_bundle(bundle: Dict[str, Any]) -> bool:
    if hash_challenge is None:
        raise RuntimeError("hash_challenge.py not available in import path.")

    ok = True
    challenge = bundle.get("Challenge")
    bundle_hash = bundle.get("Challenge_Hash")
    index_entry = bundle.get("Index_Entry")

    if not isinstance(challenge, dict):
        sys.stderr.write("[ERROR] Challenge bundle missing or invalid 'Challenge' object.\n")
        ok = False

    if not isinstance(bundle_hash, str) or not bundle_hash:
        sys.stderr.write("[ERROR] Challenge bundle missing or invalid 'Challenge_Hash'.\n")
        ok = False

    if not ok:
        return False

    # Recompute hash
    try:
        computed_hash = hash_challenge(challenge)
    except Exception as exc:
        sys.stderr.write(f"[ERROR] Failed to compute Challenge hash: {exc}\n")
        return False

    if computed_hash != bundle_hash:
        sys.stderr.write(
            f"[ERROR] Challenge hash mismatch: bundle={bundle_hash}, computed={computed_hash}\n"
        )
        ok = False
    else:
        sys.stdout.write("[OK] Challenge hash matches bundle hash.\n")

    # If index entry is present, verify it too
    if index_entry is not None:
        idx_hash = index_entry.get("Hash")
        if idx_hash != bundle_hash:
            sys.stderr.write(
                f"[ERROR] Index_Entry.Hash mismatch: index={idx_hash}, bundle={bundle_hash}\n"
            )
            ok = False
        else:
            sys.stdout.write("[OK] Index_Entry.Hash matches bundle hash.\n")

    return ok


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify a PLRS Event or Challenge Evidence Bundle. "
            "Recomputes hashes and checks consistency with any embedded index entry."
        )
    )
    parser.add_argument(
        "bundle_file",
        help="Path to the Evidence Bundle JSON (Event or Challenge)."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    bundle_path = Path(args.bundle_file)

    try:
        bundle = load_json_file(bundle_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    bundle_type = bundle.get("Bundle_Type", "")

    if bundle_type == "PLRS_Event_Evidence_Bundle":
        ok = verify_event_bundle(bundle)
    elif bundle_type == "PLRS_Challenge_Evidence_Bundle":
        ok = verify_challenge_bundle(bundle)
    else:
        sys.stderr.write(
            f"[ERROR] Unknown or missing Bundle_Type: {bundle_type!r}. "
            "Expected 'PLRS_Event_Evidence_Bundle' or 'PLRS_Challenge_Evidence_Bundle'.\n"
        )
        return 1

    if not ok:
        sys.stderr.write("[RESULT] BUNDLE VERIFICATION FAILED.\n")
        return 1

    sys.stdout.write("[RESULT] BUNDLE VERIFICATION PASSED.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
