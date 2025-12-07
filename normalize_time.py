#!/usr/bin/env python3
"""
normalize_time.py

Public Legal Record System (PLRS)
Time Normalization Utility

Purpose:
    Convert raw, user-supplied timestamps into a single canonical format:
    UTC, 24-hour, ISO 8601 / RFC 3339 (e.g. 2025-12-07T20:14:33Z).

Spec basis:
    - TIME_NORMALIZATION.md
    - schema.json (Timestamp_UTC)
"""

import sys
import argparse
from datetime import datetime
from typing import Optional

try:
    # Requires: python-dateutil
    from dateutil import parser as date_parser
    from dateutil import tz
except ImportError:
    sys.stderr.write(
        "[FATAL] python-dateutil is required. Install with:\n"
        "    pip install python-dateutil\n"
    )
    sys.exit(1)


def normalize_timestamp(raw: str, default_tz: Optional[str] = None) -> str:
    """
    Normalize a raw timestamp string into canonical UTC ISO 8601.

    Input:
        raw: Arbitrary human-readable timestamp string.
        default_tz: Optional IANA timezone (e.g., 'America/Los_Angeles')
                    used ONLY when the input has no timezone information.

    Output:
        Canonical UTC ISO 8601 string with 'Z' suffix, 24-hour clock:
            e.g. '2025-12-07T20:14:33Z' or '2025-12-07T20:14:33.482Z'

    Rules:
        - If input has timezone/offset: use it, convert to UTC.
        - If input is naive (no timezone):
            - If default_tz is provided: interpret as that zone, then convert to UTC.
            - Else: raise ValueError (ambiguous time, must be rejected).
        - If input cannot be parsed cleanly: raise ValueError.
    """
    if not raw or not raw.strip():
        raise ValueError("Empty timestamp input is not allowed.")

    raw = raw.strip()

    try:
        # Parse with dateutil, allowing many human formats
        dt = date_parser.parse(raw)
    except (ValueError, OverflowError) as exc:
        raise ValueError(f"Unrecognized or ambiguous time format: {raw!r}") from exc

    # If dt has no tzinfo, we must decide based on default_tz
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        if not default_tz:
            raise ValueError(
                "Naive timestamp (no timezone) provided and no default timezone specified. "
                "This is ambiguous and must be rejected per TIME_NORMALIZATION.md."
            )
        zone = tz.gettz(default_tz)
        if zone is None:
            raise ValueError(f"Invalid default timezone identifier: {default_tz!r}")
        dt = dt.replace(tzinfo=zone)

    # Convert to UTC
    dt_utc = dt.astimezone(tz.UTC)

    # Format with or without microseconds depending on presence
    if dt_utc.microsecond:
        iso_str = dt_utc.isoformat(timespec="milliseconds").replace("+00:00", "Z")
    else:
        iso_str = dt_utc.isoformat(timespec="seconds").replace("+00:00", "Z")

    return iso_str


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize a raw timestamp into canonical PLRS format: "
            "UTC, 24-hour, ISO 8601 with 'Z' suffix."
        )
    )
    parser.add_argument(
        "timestamp",
        help="Raw timestamp string (e.g. '12/07/2025 8:14 PM', '2025-12-07T20:14:33Z')."
    )
    parser.add_argument(
        "--default-tz",
        dest="default_tz",
        metavar="TZ",
        help=(
            "Default IANA timezone used ONLY when input has no timezone. "
            "Example: 'America/Los_Angeles'. If omitted and input is naive, "
            "the timestamp will be rejected as ambiguous."
        ),
        default=None,
    )
    parser.add_argument(
        "--show-original",
        action="store_true",
        help="Print both original and normalized timestamps."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    raw = args.timestamp
    default_tz = args.default_tz

    try:
        normalized = normalize_timestamp(raw, default_tz=default_tz)
    except ValueError as exc:
        sys.stderr.write(f"[ERROR] {exc}\n")
        return 1

    if args.show_original:
        sys.stdout.write(f"Original:   {raw}\n")
        sys.stdout.write(f"Normalized: {normalized}\n")
    else:
        sys.stdout.write(normalized + "\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
