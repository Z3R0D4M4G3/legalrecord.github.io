# PLRS Public Distribution & Publishing Guide
**File:** PUBLISHING.md  
**Scope:** Static hosting, public mirrors, and publishing workflow for PLRS records.

---

## 1. GOALS

Public distribution of PLRS data must:

1. Preserve **immutability** and **verifiability**.
2. Avoid exposing **identifying information**.
3. Be hostable on **simple static infrastructure** (e.g., GitHub Pages, Netlify).
4. Allow **anyone** to independently:
   - Download the raw data
   - Run integrity checks locally
   - Mirror the dataset

This document defines the **folder layout**, **public files**, and **publishing steps** for a complete PLRS static mirror.

---

## 2. RECOMMENDED PUBLIC DIRECTORY LAYOUT

When publishing to the web (e.g., `/` being the root of a GitHub Pages site):

```text
/
├─ index.html                 # Human-facing overview / landing page
├─ ABOUT_PLRS.html            # Non-technical explanation of PLRS + usage
├─ HOW_TO_VERIFY.html         # Step-by-step verification instructions
├─ downloads/
│  ├─ tools/                  # Pre-built tool snapshots (optional)
│  │  ├─ README_TOOLS.txt
│  │  └─ (optional zipped/compiled tools)
│  └─ data/
│     ├─ public_index.json                # Event index (append-only)
│     ├─ public_challenge_index.json      # Challenge index (append-only)
│     ├─ events/
│     │  └─ E###.json                     # Anonymized Event records
│     └─ challenges/
│        └─ C###.json                     # Anonymized Challenge records
├─ schema/
│  ├─ schema_event.json                   # Copy of schema.json
│  └─ schema_challenge.json               # Copy of challenge_schema.json
└─ docs/
   ├─ SPEC_public.html                    # Rendered SPEC.md (no internal notes)
   ├─ THREAT_MODEL_public.html            # Rendered THREAT_MODEL.md (sanitized if needed)
   └─ PUBLISHING.html                     # Rendered version of this file
