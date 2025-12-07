#!/usr/bin/env python3
"""
export_affidavit.py

Public Legal Record System (PLRS)
Court Export — Affidavit Template Generator (Event)

Purpose:
    Generate a human-readable affidavit / declaration text file that:
        - Identifies a specific PLRS Event and its hash
        - References the associated Event Evidence Bundle
        - Provides a structured template for a declarant to swear under penalty of perjury
        - Includes clear, plain-language verification instructions

    This is not legal advice and is intentionally jurisdiction-agnostic.
    It is a structured starting point for counsel or self-represented parties.
"""

import sys
import json
import argparse
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


def build_affidavit_text(bundle: Dict[str, Any]) -> str:
    """
    Build a plain-text affidavit template that references the Event bundle.
    """
    event = bundle.get("Event", {})
    event_id = event.get("Event_ID", "<UNKNOWN_EVENT_ID>")
    timestamp_utc = event.get("Timestamp_UTC", "<UNKNOWN_TIMESTAMP_UTC>")
    location_id = event.get("Location_ID", "<UNKNOWN_LOCATION_ID>")
    event_type = event.get("Event_Type", "<UNKNOWN_EVENT_TYPE>")
    narrative = event.get("Narrative_Statement", "<NARRATIVE_NOT_AVAILABLE>")

    event_hash = bundle.get("Event_Hash", "<UNKNOWN_HASH>")
    index_entry = bundle.get("Index_Entry")
    index_file_ref = bundle.get("Index_File_Reference")

    generated_at = bundle.get("Generated_At_UTC", "<UNKNOWN_GENERATED_TIME>")
    bundle_version = bundle.get("Bundle_Version", "<UNKNOWN_VERSION>")

    # Optional index info
    index_line = ""
    if index_entry is not None:
        idx_seq = index_entry.get("Index_Seq", "<UNKNOWN_INDEX_SEQ>")
        idx_ts = index_entry.get("Timestamp_UTC", "<UNKNOWN_INDEX_TIMESTAMP>")
        index_line = (
            f"\n3. The Event is listed in the PLRS public index with Index_Seq {idx_seq} "
            f"and index timestamp {idx_ts}. The index entry contains the same hash value as "
            f"The PLRS Event Evidence Bundle ({event_hash})."
        )
    else:
        index_line = (
            "\n3. I understand that this Event may be listed, or may later be listed, in the "
            "PLRS public index. At the time of this affidavit, no specific index entry is "
            "referenced here."
        )

    if index_file_ref:
        index_ref_line = (
            f"\n   a. Referenced index file: {index_file_ref}"
        )
    else:
        index_ref_line = ""

    text = f"""\
[COURT NAME / CAPTION]
[CASE NAME]
[CASE NUMBER]

DECLARATION REGARDING PUBLIC LEGAL RECORD SYSTEM (PLRS) EVENT

I, ______________________________, declare as follows:

1. I am a party, witness, or other person with knowledge relevant to the PLRS Event identified
   as Event_ID {event_id}. I make this declaration based on my personal knowledge, except where
   stated on information and belief, and as to those matters I believe them to be true.

2. Attached and incorporated by reference is a PLRS Event Evidence Bundle with the following details:
   a. Bundle Type: {bundle.get("Bundle_Type", "<UNKNOWN_BUNDLE_TYPE>")}
   b. Bundle Version: {bundle_version}
   c. Bundle Generated At (UTC): {generated_at}
   d. Event_ID: {event_id}
   e. Event Timestamp_UTC: {timestamp_utc}
   f. Event Location_ID: {location_id}
   g. Event Type: {event_type}
   h. Event Hash (canonical): {event_hash}{index_line}{index_ref_line}

4. The PLRS Event Evidence Bundle contains a complete JSON representation of the Event and its
   associated cryptographic integrity information. Anyone with technical ability may independently
   verify the integrity of the Event by:

   a. Validating the Event against the PLRS schema using `validate_event.py`.
   b. Recomputing the Event hash using `hash_event.py` and confirming it matches: {event_hash}
   c. If an index entry is provided, confirming the same hash appears in the public index.
   d. Optionally auditing the index itself using `verify_index.py`.

5. The narrative portion of the Event currently states:

   \"\"\"{narrative}\"\"\"

6. If I am the original reporter of this Event, I confirm that this narrative is a true and accurate
   description of the Event to the best of my knowledge and belief at the time it was submitted.
   If I am not the original reporter, I am submitting this declaration to authenticate the use of
   the PLRS Event Evidence Bundle in this matter and to explain how it may be verified.

7. I understand that the PLRS system is designed so that once an Event is recorded, hashed, and
   indexed, it cannot be edited in place without detection. Any attempt to change the Event will
   produce a different hash, making tampering mathematically detectable.

I declare under penalty of perjury under the laws of the State of ____________ and/or the laws
of the United States of America that the foregoing is true and correct.

Executed on ________________ (date) at ____________________________ (city, state).


____________________________________
Signature of Declarant

____________________________________
Printed Name of Declarant

[Optional: Contact or attorney information]


NOTE:
This template is jurisdiction-neutral and may need to be adapted by counsel to comply with
specific local rules of court or evidentiary requirements. It is intended to preserve the
integrity chain of the PLRS Event and make verification straightforward for all parties.
"""

    return text


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a court-ready affidavit/declaration text template that references "
            "a PLRS Event Evidence Bundle."
        )
    )
    parser.add_argument(
        "bundle_file",
        help="Path to the PLRS Event Evidence Bundle JSON file (from export_event_bundle.py)."
    )
    parser.add_argument(
        "--output",
        dest="output_file",
        default=None,
        help="Optional output path for the affidavit text file. "
             "Defaults to a name derived from the Event_ID."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    bundle_path = Path(args.bundle_file)

    # Load bundle
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

    affidavit_text = build_affidavit_text(bundle)

    # Determine output path
    if args.output_file:
        out_path = Path(args.output_file)
    else:
        out_name = f"PLRS_EventAffidavit_{event_id}.txt"
        out_path = Path(out_name)

    try:
        with out_path.open("w", encoding="utf-8") as f:
            f.write(affidavit_text)
    except OSError as exc:
        sys.stderr.write(f"[ERROR] Failed to write affidavit file: {exc}\n")
        return 1

    sys.stdout.write(f"[AFFIDAVIT CREATED] {out_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
