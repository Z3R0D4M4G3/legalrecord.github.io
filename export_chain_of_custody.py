#!/usr/bin/env python3
"""
export_chain_of_custody.py

Public Legal Record System (PLRS)
Court Export — Chain of Custody Log (Event)

Purpose:
    Create or extend a JSON-based chain of custody log for a specific PLRS Event,
    tied to its canonical hash and Evidence Bundle.

    Each entry records:
        - Who handled the evidence
        - In what role
        - What action they took (e.g., Created, Transferred, Submitted_to_Court)
        - When they did it (UTC timestamp)
        - Optional location and notes

    This log is intended to be attached alongside the PLRS Event Evidence Bundle
    and affidavit, so that courts and parties can see a clear, time-ordered
    record of who controlled the evidence and when.

Notes:
    - This script does NOT enforce legal sufficiency for chain of custody.
      It provides a structured, append-only log to support evidentiary practice.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, timezone


def load_json_file(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in file: {path}") from exc


def init_or_load_coc(path: Path) -> Dict[str, Any]:
    """
    Load an existing chain of custody file or initialize a new one.
    """
    if path.exists():
        data = load_json_file(path)
        # Basic sanity: top-level object with Chain_Of_Custody list
        if not isinstance(data, dict) or "Chain_Of_Custody" not in data:
            raise ValueError("Existing chain of custody file has invalid structure.")
        if not isinstance(data["Chain_Of_Custody"], list):
            raise ValueError("Existing Chain_Of_Custody field must be a list.")
        return data

    # Initialize a new structure
    return {
        "CoC_Version": "1.0",
        "Event_ID": None,
        "Event_Hash": None,
        "Evidence_Bundle_File": None,
        "Chain_Of_Custody": []
    }


def append_coc_entry(
    coc: Dict[str, Any],
    event_id: str,
    event_hash: str,
    bundle_file: Path,
    holder_name: str,
    holder_role: str,
    action: str,
    location: str,
    notes: str
) -> None:
    """
    Append a new chain of custody entry.
    """
    # Initialize top-level fields if not set yet
    if coc.get("Event_ID") is None:
        coc["Event_ID"] = event_id
    elif coc["Event_ID"] != event_id:
        raise ValueError(
            f"Chain of custody file is bound to Event_ID {coc['Event_ID']}, "
            f"but attempted to append for Event_ID {event_id}."
        )

    if coc.get("Event_Hash") is None:
        coc["Event_Hash"] = event_hash
    elif coc["Event_Hash"] != event_hash:
        raise ValueError(
            "Event_Hash in chain of custody file does not match the provided Event hash. "
            "This may indicate an attempt to mix different versions of evidence."
        )

    if coc.get("Evidence_Bundle_File") is None:
        coc["Evidence_Bundle_File"] = str(bundle_file)

    now_utc = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    entry = {
        "Entry_Timestamp_UTC": now_utc,
        "Holder_Name": holder_name,
        "Holder_Role": holder_role,
        "Action": action,
        "Location": location or None,
        "Notes": notes or None
    }

    coc["Chain_Of_Custody"].append(entry)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create or append to a PLRS Event Chain of Custody JSON file, "
            "tied to a specific Event Evidence Bundle and hash."
        )
    )
    parser.add_argument(
        "bundle_file",
        help="Path to the PLRS Event Evidence Bundle JSON file (from export_event_bundle.py)."
    )
    parser.add_argument(
        "holder_name",
        help="Name of the person or entity currently handling the evidence (e.g., 'John Doe', 'Clerk of Court')."
    )
    parser.add_argument(
        "holder_role",
        help="Role of the holder (e.g., 'Parent', 'Attorney', 'Court_Clerk', 'Investigator')."
    )
    parser.add_argument(
        "action",
        help="Action taken with respect to the evidence (e.g., 'Created', 'Transferred', 'Submitted_to_Court')."
    )
    parser.add_argument(
        "--location",
        default="",
        help="Optional location description (e.g., 'Riverside County Superior Court')."
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional free-text notes (e.g., 'Submitted as Exhibit A to motion filed on ...')."
    )
    parser.add_argument(
        "--coc-file",
        dest="coc_file",
        default=None,
        help=(
            "Optional path to the chain of custody JSON file. If it exists, a new entry will "
            "be appended; if not, a new file will be created. Defaults to "
            "'PLRS_ChainOfCustody_<Event_ID>.json'."
        )
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    bundle_path = Path(args.bundle_file)

    # Load Event bundle
    try:
        bundle = load_json_file(bundle_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    event = bundle.get("Event", {})
    event_id = event.get("Event_ID")
    if not event_id:
        sys.stderr.write("[ERROR] Bundle does not contain an Event with Event_ID.\n")
        return 1

    event_hash = bundle.get("Event_Hash")
    if not event_hash:
        sys.stderr.write("[ERROR] Bundle does not contain Event_Hash.\n")
        return 1

    # Determine CoC file path
    if args.coc_file:
        coc_path = Path(args.coc_file)
    else:
        coc_name = f"PLRS_ChainOfCustody_{event_id}.json"
        coc_path = Path(coc_name)

    # Load or initialize CoC
    try:
        coc = init_or_load_coc(coc_path)
    except (FileNotFoundError, ValueError) as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    # Append new entry
    try:
        append_coc_entry(
            coc=coc,
            event_id=event_id,
            event_hash=event_hash,
            bundle_file=bundle_path,
            holder_name=args.holder_name,
            holder_role=args.holder_role,
            action=args.action,
            location=args.location,
            notes=args.notes,
        )
    except ValueError as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    # Save CoC file
    try:
        with coc_path.open("w", encoding="utf-8") as f:
            json.dump(coc, f, indent=2, ensure_ascii=False)
            f.write("\n")
    except OSError as exc:
        sys.stderr.write(f"[ERROR] Failed to write chain of custody file: {exc}\n")
        return 1

    sys.stdout.write(f"[CoC UPDATED] {coc_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
