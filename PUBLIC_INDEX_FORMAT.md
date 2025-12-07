# Public Event Index Format
**Project:** Public Legal Record System (PLRS)  
**File:** PUBLIC_INDEX_FORMAT.md  
**Status:** Core Ledger Structure  
**Purpose:** To define the canonical format for the append-only public index of PLRS Events and their hashes.

---

## 1. OBJECTIVE

This document specifies how PLRS Events and their integrity hashes are represented in a **public, append-only index**.

Goals:

- Simple enough to host as:
  - Static JSON files
  - Git-tracked text
  - IPFS objects
- Strict enough to:
  - Prevent silent reordering
  - Detect deletions
  - Enable independent verification

This is the **public-facing ledger format**, not the internal Event schema.

---

## 2. INDEX LAYOUT OPTIONS

Implementations may use one or more of the following:

1. **Flat Index**
   - Single file containing all entries

2. **Sharded Index**
   - One file per time period (e.g., per day, per month, per year)

3. **Per-Event Files + Master Index**
   - Individual Event JSON + a central index referencing them

All variants MUST follow the same **entry format** defined below.

---

## 3. INDEX ENTRY FORMAT

Each index entry represents **one Event + its integrity hash**.

### 3.1 JSON Array Style

Minimal, recommended format:

```json
[
  {
    "Event_ID": "E001",
    "Timestamp_UTC": "2025-12-07T20:14:33Z",
    "Hash": "c4ab3b0f2a713c3a5b145fed3b9b1d3f6b0c50a8ff9c2aa88f6a1aa27f3b7f10",
    "Public_Visibility": true,
    "Index_Seq": 1
  },
  {
    "Event_ID": "E002",
    "Timestamp_UTC": "2025-12-07T21:02:10Z",
    "Hash": "9a8c71c3f6d2e05f9f429768d8a5ffb3214bf3c07b321c25b89a2d9240b067e2",
    "Public_Visibility": true,
    "Index_Seq": 2
  }
]
