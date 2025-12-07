# PLRS Processing Pipeline
**Project:** Public Legal Record System (PLRS)  
**File:** PIPELINE.md  
**Status:** Core Operational Flow  
**Purpose:** To define the end-to-end path from human input to immutable, verifiable public record.

---

## 1. OVERVIEW

All PLRS records must pass through a strict, ordered pipeline:

1. **Human Input (Local, Offline)**
2. **Time Normalization (Canonical UTC)**
3. **Schema Validation (Structural Compliance)**
4. **Hashing & Integrity Lock**
5. **Storage & Publication (Append-Only)**
6. **Challenge & Appeal Mechanics**

At no point may any step be skipped, reordered, or silently altered.

---

## 2. STEP 1 — HUMAN INPUT

**Primary tools:**
- `event_form.html`  
- `event_form_export.html`  
- Manual editing of `EVENT_TEMPLATE.json`  

**Purpose:**
- Collect:
  - `Event_ID`
  - `Location_ID`
  - `Subjects_Involved`
  - `Reporter_ID`
  - `Event_Type`
  - `Narrative_Statement`
  - `Evidence_Hashes`
  - `Public_Visibility`
  - `Challenge_Window_Days`
  - Raw timestamp (`Timestamp_RAW` or equivalent)

**Constraints:**
- No real names or direct identifiers
- All entities use anonymized IDs (S###, L###, R###)
- Files are generated/stored **locally**, with no server dependency

**Output:**
- A **draft Event JSON** that is human-complete but not yet canonical:
  - `Timestamp_RAW` present
  - `Timestamp_UTC` not yet enforced (or missing)

---

## 3. STEP 2 — TIME NORMALIZATION

**Primary tool:**
- `normalize_time.py`

**Input:**
- Draft Event JSON:
  - Contains `Timestamp_RAW` (any human-entered format)
  - May or may not contain timezone information

**Process:**
1. Extract raw timestamp string.
2. Apply normalization rules from `TIME_NORMALIZATION.md`:
   - Parse raw time
   - Apply timezone (explicit or default)
   - Convert to UTC
   - Output ISO 8601 / RFC 3339 (24-hour, `Z` suffix)

**Output:**
- Updated Event JSON where:
  - `Timestamp_UTC` is set to canonical value
  - `Timestamp_RAW` MAY be preserved for audit, but is **not authoritative**
- If normalization fails:
  - Event is **rejected**
  - MUST be corrected before proceeding

---

## 4. STEP 3 — SCHEMA VALIDATION

**Primary tool:**
- `validate_event.py`
- Schema:
  - `schema.json`

**Input:**
- Event JSON with:
  - Canonical `Timestamp_UTC`
  - All required fields filled

**Process:**
- Validate the Event against `schema.json`:
  - Required fields present
  - Types correct
  - Patterns (E###, L###, S###, R###) respected
  - `Immutable_Flag == true`
  - `Challenge_Window_Days` within allowed range
  - `Public_Visibility` is boolean

**Output:**
- If valid:
  - Event is marked **structurally compliant**
- If invalid:
  - Validation errors printed
  - Event must be corrected and re-run
- No Event may proceed without **full schema compliance**

---

## 5. STEP 4 — HASHING & INTEGRITY LOCK

**Primary tool (planned):**
- `hash_event.py` (not yet implemented)

**Input:**
- A fully validated Event JSON

**Process (intended):**
1. Serialize Event in canonical form.
2. Compute cryptographic hash (e.g., SHA-256).
3. Optionally:
   - Bundle Event + hash into a verification package.
4. Associate hash with:
   - Publication index
   - Chain-of-custody metadata

**Output:**
- Event hash:
  - Used as integrity anchor
  - Enables later verification that no bit has changed

No Event is considered **frozen** until hashing is complete.

---

## 6. STEP 5 — STORAGE & PUBLICATION

**Storage targets (examples):**
- Local append-only log files
- Git-based repositories (append-only policies)
- Static site indexes (e.g., GitHub Pages)
- Distributed storage (e.g., IPFS, future phase)

**Rules:**
- Events MUST:
  - Be appended, never overwritten
  - Retain original `Event_ID` and `Timestamp_UTC`
  - Maintain associated hash
- Corrections or follow-ups:
  - Are represented as **new Events**
  - Must reference original `Event_ID` in `Referenced_Event`
  - Original records remain immutable

**Output:**
- Public, auditable, append-only Event history

---

## 7. STEP 6 — CHALLENGE & APPEAL

**Conceptual tools (future):**
- Challenge record generator
- Threaded view of Event + Challenges
- Time-window enforcement

**Process:**
- During `Challenge_Window_Days`:
  - Counterparties can submit Challenge Events
  - Each Challenge references the original `Event_ID`
- After the window:
  - Event is considered **Locked**
  - New information becomes related Events, not edits

**Legal effect:**
- Appeals and disputes rely on:
  - Full Event + Challenge chain
  - Timestamps
  - Hash consistency
  - Public visibility

---

## 8. PIPELINE IN SHORT

1. **Generate** → Browser form or template  
2. **Normalize** → `normalize_time.py` (UTC enforcement)  
3. **Validate** → `validate_event.py` + `schema.json`  
4. **Hash** → Event integrity anchor (future `hash_event.py`)  
5. **Store** → Append-only, public or mirrored index  
6. **Challenge** → Time-bounded, linked dispute records  

At every stage:
- No silent edits  
- No backdating  
- No identity exposure  
- No privilege-based overrides  

---

## 9. NON-NEGOTIABLE ORDER

The following is strictly prohibited:

- Skipping normalization and using local times directly  
- Storing unvalidated Events as “official”  
- Editing stored Events in-place  
- Hashing different representations of the same Event silently  
- Accepting records without a clear pipeline trace  

If any step is violated, the resulting record is **not PLRS-compliant**.

---

**End of PIPELINE.md**
