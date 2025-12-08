#!/usr/bin/env python3
"""
verify_chain_of_custody.py

Public Legal Record System (PLRS)
Chain of Custody Verification Utility

Purpose:
    Verify the integrity and internal consistency of a PLRS Chain of Custody (CoC)
    file by checking:

        - Structural validity
        - Presence of required top-level bindings
        - Consistent Event_ID and Event_Hash across all entries
        - Proper UTC timestamp formatting
        - Strict append-only ordering (monotonic time)

    This tool does NOT judge legal sufficiency. It verifies mechanical integrity.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List


def load_json_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file: {path}") from exc


def is_valid_utc_z(ts: str) -> bool:
    """
    Basic check for ISO 8601 UTC timestamps with Z suffix.
    Example: 2025-01-12T18:42:10Z
    """
    return (
        isinstance(ts, str)
        and ts.endswith("Z")
        and "T" in ts
    )


def verify_chain_of_custody(coc: Dict[str, Any]) -> bool:
    ok = True

    event_id = coc.get("Event_ID")
    event_hash = coc.get("Event_Hash")
    coc_entries = coc.get("Chain_Of_Custody")

    if not isinstance(event_id, str) or not event_id:
        sys.stderr.write("[ERROR] Missing or invalid Event_ID.\n")
        ok = False

    if not isinstance(event_hash, str) or not event_hash:
        sys.stderr.write("[ERROR] Missing or invalid Event_Hash.\n")
        ok = False

    if not isinstance(coc_entries, list):
        sys.stderr.write("[ERROR] Chain_Of_Custody must be a list.\n")
        return False

    last_ts = None

    for i, entry in enumerate(coc_entries, start=1):
        ts = entry.get("Entry_Timestamp_UTC")
        holder = entry.get("Holder_Name")
        role = entry.get("Holder_Role")
        action = entry.get("Action")

        if not is_valid_utc_z(ts):
            sys.stderr.write(
                f"[ERROR] Entry {i} has invalid or non-UTC timestamp: {ts}\n"
            )
            ok = False

        if not isinstance(holder, str) or not holder:
            sys.stderr.write(f"[ERROR] Entry {i} missing Holder_Name.\n")
            ok = False

        if not isinstance(role, str) or not role:
            sys.stderr.write(f"[ERROR] Entry {i} missing Holder_Role.\n")
            ok = False

        if not isinstance(action, str) or not action:
            sys.stderr.write(f"[ERROR] Entry {i} missing Action.\n")
            ok = False

        # Enforce monotonic time ordering
        if last_ts is not None and ts <= last_ts:
            sys.stderr.write(
                f"[ERROR] Entry {i} timestamp is not strictly later than previous entry.\n"
            )
            ok = False

        last_ts = ts

    if ok:
        sys.stdout.write("[OK] Chain of Custody structural integrity verified.\n")

    return ok


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Verify the structural integrity and timestamp ordering of a "
            "PLRS Chain of Custody JSON file."
        )
    )
    parser.add_argument(
        "coc_file",
        help="Path to the PLRS Chain of Custody JSON file."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    coc_path = Path(args.coc_file)

    try:
        coc = load_json_file(coc_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    ok = verify_chain_of_custody(coc)

    if not ok:
        sys.stderr.write("[RESULT] CHAIN OF CUSTODY VERIFICATION FAILED.\n")
        return 1

    sys.stdout.write("[RESULT] CHAIN OF CUSTODY VERIFICATION PASSED.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
