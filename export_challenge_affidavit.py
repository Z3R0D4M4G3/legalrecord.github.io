#!/usr/bin/env python3
"""
export_challenge_affidavit.py

Public Legal Record System (PLRS)
Court Export — Affidavit Template Generator (Challenge)

Purpose:
    Generate a human-readable affidavit / declaration text file that:
        - Identifies a specific PLRS Challenge and its hash
        - References the associated Challenge Evidence Bundle
        - Explains which original Event is being challenged
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


def build_challenge_affidavit_text(bundle: Dict[str, Any]) -> str:
    """
    Build a plain-text affidavit template that references the Challenge bundle.
    """
    challenge = bundle.get("Challenge", {})
    challenge_id = challenge.get("Challenge_ID", "<UNKNOWN_CHALLENGE_ID>")
    challenged_event_id = challenge.get("Challenged_Event_ID", "<UNKNOWN_EVENT_ID>")
    timestamp_utc = challenge.get("Timestamp_UTC", "<UNKNOWN_TIMESTAMP_UTC>")
    challenger_id = challenge.get("Challenger_ID", "<UNKNOWN_CHALLENGER_ID>")
    challenger_role = challenge.get("Challenger_Role", "<UNKNOWN_ROLE>")
    challenge_type = challenge.get("Challenge_Type", "<UNKNOWN_CHALLENGE_TYPE>")
    challenge_statement = challenge.get("Challenge_Statement", "<STATEMENT_NOT_AVAILABLE>")

    challenge_hash = bundle.get("Challenge_Hash", "<UNKNOWN_HASH>")
    index_entry = bundle.get("Index_Entry")
    index_file_ref = bundle.get("Index_File_Reference")

    generated_at = bundle.get("Generated_At_UTC", "<UNKNOWN_GENERATED_TIME>")
    bundle_version = bundle.get("Bundle_Version", "<UNKNOWN_VERSION>")

    # Optional index info
    if index_entry is not None:
        idx_seq = index_entry.get("Index_Seq", "<UNKNOWN_INDEX_SEQ>")
        idx_ts = index_entry.get("Timestamp_UTC", "<UNKNOWN_INDEX_TIMESTAMP>")
        index_line = (
            f"\n3. The Challenge is listed in the PLRS public challenge index with Index_Seq {idx_seq} "
            f"and index timestamp {idx_ts}. The index entry contains the same hash value as "
            f"the PLRS Challenge Evidence Bundle ({challenge_hash})."
        )
    else:
        index_line = (
            "\n3. I understand that this Challenge may be listed, or may later be listed, in the "
            "PLRS public challenge index. At the time of this affidavit, no specific index entry is "
            "referenced here."
        )

    if index_file_ref:
        index_ref_line = f"\n   a. Referenced challenge index file: {index_file_ref}"
    else:
        index_ref_line = ""

    text = f"""\
[COURT NAME / CAPTION]
[CASE NAME]
[CASE NUMBER]

DECLARATION REGARDING PUBLIC LEGAL RECORD SYSTEM (PLRS) CHALLENGE

I, ______________________________, declare as follows:

1. I am a party, witness, or other person with knowledge relevant to the PLRS Challenge identified
   as Challenge_ID {challenge_id}, which contests PLRS Event_ID {challenged_event_id}. I make this
   declaration based on my personal knowledge, except where stated on information and belief, and
   as to those matters I believe them to be true.

2. Attached and incorporated by reference is a PLRS Challenge Evidence Bundle with the following details:
   a. Bundle Type: {bundle.get("Bundle_Type", "<UNKNOWN_BUNDLE_TYPE>")}
   b. Bundle Version: {bundle_version}
   c. Bundle Generated At (UTC): {generated_at}
   d. Challenge_ID: {challenge_id}
   e. Challenged_Event_ID: {challenged_event_id}
   f. Challenge Timestamp_UTC: {timestamp_utc}
   g. Challenger_ID (anonymized reporter identifier): {challenger_id}
   h. Challenger_Role: {challenger_role}
   i. Challenge Type: {challenge_type}
   j. Challenge Hash (canonical): {challenge_hash}{index_line}{index_ref_line}

4. The PLRS Challenge Evidence Bundle contains a complete JSON representation of the Challenge
   and its associated cryptographic integrity information. Anyone with technical ability may
   independently verify the integrity of the Challenge by:

   a. Validating the Challenge against the PLRS challenge schema using `validate_challenge.py`.
   b. Recomputing the Challenge hash using `hash_challenge.py` and confirming it matches: {challenge_hash}
   c. If a challenge index entry is provided, confirming the same hash appears in the public challenge index.
   d. Optionally auditing the challenge index itself using appropriate PLRS verification tools.

5. The narrative portion of the Challenge currently states:

   \"\"\"{challenge_statement}\"\"\"

6. If I am the original challenger for this record, I confirm that this statement accurately reflects
   the specific parts of Event_ID {challenged_event_id} that I contest, including any alleged false
   statements, timeline errors, omissions, or mischaracterizations, to the best of my knowledge and belief
   at the time it was submitted.

7. If I am not the original challenger, I am submitting this declaration to authenticate the use of
   the PLRS Challenge Evidence Bundle in this matter and to explain how it may be verified by the court
   and the parties.

8. I understand that the PLRS system is designed so that once a Challenge is recorded, hashed, and
   indexed, it cannot be edited in place without detection. Any attempt to change the Challenge will
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
integrity chain of the PLRS Challenge and make verification straightforward for all parties.
"""

    return text


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a court-ready affidavit/declaration text template that references "
            "a PLRS Challenge Evidence Bundle."
        )
    )
    parser.add_argument(
        "bundle_file",
        help="Path to the PLRS Challenge Evidence Bundle JSON file (from export_challenge_bundle.py)."
    )
    parser.add_argument(
        "--output",
        dest="output_file",
        default=None,
        help="Optional output path for the affidavit text file. "
             "Defaults to a name derived from the Challenge_ID."
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

    challenge = bundle.get("Challenge", {})
    challenge_id = challenge.get("Challenge_ID")
    if not challenge_id:
        sys.stderr.write("[ERROR] Bundle does not contain a Challenge with Challenge_ID.\n")
        return 1

    affidavit_text = build_challenge_affidavit_text(bundle)

    # Determine output path
    if args.output_file:
        out_path = Path(args.output_file)
    else:
        out_name = f"PLRS_ChallengeAffidavit_{challenge_id}.txt"
        out_path = Path(out_name)

    try:
        with out_path.open("w", encoding="utf-8") as f:
            f.write(affidavit_text)
    except OSError as exc:
        sys.stderr.write(f"[ERROR] Failed to write challenge affidavit file: {exc}\n")
        return 1

    sys.stdout.write(f"[CHALLENGE AFFIDAVIT CREATED] {out_path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
