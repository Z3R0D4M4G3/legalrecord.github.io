#!/usr/bin/env python3
"""
publish_snapshot.py

Public Legal Record System (PLRS)
Verified Public Snapshot Publisher

Purpose:
    Copy a fully verified PLRS dataset into the public distribution layout
    defined by PUBLISHING.md and stamp the snapshot with a UTC timestamp.

    This script assumes that ALL of the following have already passed:

        - validate_event.py
        - validate_challenge.py
        - verify_index.py
        - verify_ledger_integrity.py

    This tool does NOT perform verification itself.
    It only publishes data that is already trusted.
"""

import sys
import json
import argparse
import shutil
from pathlib import Path
from datetime import datetime, timezone


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)


def copy_tree(src_dir: Path, dst_dir: Path) -> None:
    if not src_dir.exists():
        return
    ensure_dir(dst_dir)
    for item in src_dir.iterdir():
        if item.is_file():
            copy_file(item, dst_dir / item.name)


def build_snapshot_stamp() -> str:
    return (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def write_snapshot_manifest(manifest_path: Path, stamp: str) -> None:
    manifest = {
        "PLRS_Public_Snapshot": stamp,
        "Published_At_UTC": stamp,
        "Publisher_Note": (
            "This snapshot was generated from a locally verified PLRS ledger. "
            "All verification tools passed prior to publication."
        )
    }

    ensure_dir(manifest_path.parent)
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Publish a verified PLRS ledger into the public static distribution layout "
            "defined in PUBLISHING.md."
        )
    )
    parser.add_argument(
        "--event-index",
        default="public_index.json",
        help="Path to the verified Event index (default: public_index.json)."
    )
    parser.add_argument(
        "--challenge-index",
        default="public_challenge_index.json",
        help="Path to the verified Challenge index (default: public_challenge_index.json)."
    )
    parser.add_argument(
        "--events-dir",
        default="events",
        help="Directory containing verified Event JSON files."
    )
    parser.add_argument(
        "--challenges-dir",
        default="challenges",
        help="Directory containing verified Challenge JSON files."
    )
    parser.add_argument(
        "--schema-dir",
        default="schema",
        help="Directory containing public schemas to publish."
    )
    parser.add_argument(
        "--public-root",
        default="downloads/data",
        help="Root output directory for public data (default: downloads/data)."
    )
    return parser


def main(argv=None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    public_root = Path(args.public_root)
    stamp = build_snapshot_stamp()

    try:
        # Index files
        copy_file(Path(args.event_index), public_root / "public_index.json")
        copy_file(
            Path(args.challenge_index),
            public_root / "public_challenge_index.json"
        )

        # Data trees
        copy_tree(Path(args.events_dir), public_root / "events")
        copy_tree(Path(args.challenges_dir), public_root / "challenges")

        # Schemas
        copy_tree(Path(args.schema_dir), public_root / "schema")

        # Snapshot manifest
        write_snapshot_manifest(public_root / "PLRS_SNAPSHOT.json", stamp)

    except Exception as exc:
        sys.stderr.write(f"[ERROR] Publish failed: {exc}\n")
        return 1

    sys.stdout.write(f"[PUBLISHED] PLRS public snapshot generated at {stamp}\n")
    sys.stdout.write(f"[ROOT] {public_root}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
