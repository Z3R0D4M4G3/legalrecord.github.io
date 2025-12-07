# PLRS Release Notes
**Project:** Public Legal Record System (PLRS)  
**File:** RELEASE_NOTES.md  

---

## Version 0.1.0 — Core Integrity Pipeline

**Release Date:** 2025-12-07  
**Status:** Initial Public Draft (Local-First, Offline-Capable)

### Overview

This release delivers the first fully functional, offline-capable integrity pipeline for the Public Legal Record System. It allows a user to:

1. Generate a structured Event locally
2. Normalize its timestamp into canonical UTC
3. Validate it against a formal JSON schema
4. Hash it with deterministic, cryptographic integrity
5. Append it to an append-only public ledger
6. Re-verify the ledger independently at any time

This marks the transition from a conceptual standard to a working enforcement toolchain.

---

## Included Artifacts

### Core Doctrine & Standards

- `README.md`  
  Project overview and public mission.

- `LICENSE`  
  Legal usage and protection terms.

- `SPEC.md`  
  Public Legal Record Standard (PLRS) — object model, principles, and immutability rules.

- `THREAT_MODEL.md`  
  Adversary classes, attack vectors, and enforced defenses.

- `TIME_NORMALIZATION.md`  
  Canonical time standard and normalization rules.

- `PIPELINE.md`  
  End-to-end processing pipeline from human input to immutable record.

- `PUBLIC_INDEX_FORMAT.md`  
  Canonical format for the append-only public ledger.

---

### Validation & Enforcement

- `schema.json`  
  JSON Schema for PLRS Event records (structural validation, required fields, patterns).

- `normalize_time.py`  
  Converts raw timestamps into canonical UTC ISO 8601 (24-hour, `Z` suffix). Rejects ambiguous or naive time inputs per Time Normalization Standard.

- `validate_event.py`  
  Validates Event JSON files against `schema.json` before hashing, storage, or court use.

- `hash_event.py`  
  Produces deterministic cryptographic hashes from canonical Event JSON, forming the immutability anchor.

- `build_index.py`  
  Appends verified Events and hashes to a public, append-only index (`public_index.json`) with enforced `Index_Seq` ordering.

- `verify_index.py`  
  Audits the public index for sequence integrity and recomputes hashes to detect tampering, truncation, or corruption.

---

### User-Facing Tools & Examples

- `event_form.html`  
  Local-only Event generator for creating draft Events in the browser.

- `event_form_export.html`  
  Extended Event generator with one-click JSON file export.

- `EVENT_TEMPLATE.json`  
  Canonical example Event that passes schema validation and timestamp rules.

---

## Capabilities in v0.1.0

- Fully offline operation (no server required).
- Anonymized entity references (S###, L###, R###).
- Canonical UTC time enforcement.
- Schema-driven structural validation.
- Deterministic cryptographic hashing.
- Append-only public ledger structure.
- Independent ledger verification by any third party.

---

## Known Limitations

- No networked submission, syncing, or mirroring yet.
- No GUI for time normalization or validation (CLI tools only).
- No challenge/appeal UI; Challenge Events are not yet formally modeled as a separate schema.
- No jurisdiction-specific export/affidavit bundles included.

---

## Planned for Next Version (0.2.x)

- Challenge Event schema and tooling.
- Basic public-facing documentation site (e.g., GitHub Pages).
- Hash + index integration with distributed storage (initial IPFS/IPNS exploration).
- Optional GUI wrappers around CLI tools for non-technical users.
- Jurisdiction overlay templates for court-ready export bundles.

---

**Tag:** `v0.1.0-core-pipeline`  
**Summary:** First verifiable path from human narrative to cryptographic, publicly auditable legal record.
