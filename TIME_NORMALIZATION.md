# Time Normalization Standard
**Project:** Public Legal Record System (PLRS)  
**File:** TIME_NORMALIZATION.md  
**Status:** Required Pre-Validation Layer  
**Purpose:** To define how all input timestamps are converted into a single canonical time format before records are validated or stored.

---

## 1. OBJECTIVE

All timestamps entering the system must be normalized into:

- **Format:** ISO 8601 / RFC 3339  
- **Example:** `2025-12-07T20:14:33.482Z`  
- **Timezone:** UTC only  
- **Clock:** 24-hour notation  

No record may reach `schema.json` validation or permanent storage using:

- 12-hour time (AM/PM)
- Local timezones
- Locale-specific date formats
- Free-text or ambiguous time strings

---

## 2. INPUT → OUTPUT CONTRACT

### 2.1 Accepted Input Styles (Examples)

The normalization layer MUST accept, at minimum, the following:

- `12/07/2025 8:14 PM`
- `2025-12-07 20:14`
- `07-12-2025 20:14`
- `2025/12/07 8:14pm`
- `2025-12-07T20:14:33Z`
- `2025-12-07T12:14:33-08:00`
- `Sun Dec 07 2025 20:14:33 GMT+0000`
- Any equivalent representation that contains:
  - A valid calendar date
  - A valid time of day
  - An optional timezone or offset

### 2.2 Canonical Output

All valid inputs MUST be converted to:

- Example (no milliseconds):  
  `2025-12-07T20:14:33Z`

- Example (with milliseconds):  
  `2025-12-07T20:14:33.482Z`

Milliseconds MAY be included or omitted, but:

- The output MUST always be:
  - UTC (`Z` suffix)
  - 24-hour time
  - Unambiguous

---

## 3. NORMALIZATION STEPS

For each raw timestamp received:

1. **Parse**
   - Attempt to parse using a robust, locale-agnostic date-time parser.
   - If parsing fails, the input MUST be rejected before validation.

2. **Apply Timezone**
   - If the input contains a timezone or offset (e.g., `PST`, `-08:00`), convert it to UTC.
   - If the input is naive (no timezone), treat it as:
     - **Client-specified default**, OR
     - **System default timezone** (documented), OR
     - **Rejected** if no default policy exists.

   The chosen policy MUST be documented here and never silently changed.

3. **Convert to Canonical Form**
   - Convert the parsed time to:
     - ISO 8601 / RFC 3339
     - 24-hour format
     - UTC with trailing `Z`
   - Example:  
     Input: `12/07/2025 8:14 PM PST`  
     Output: `2025-12-08T04:14:00Z`

4. **Emit to Validation**
   - Only after successful normalization is the timestamp passed to:
     - `Timestamp_UTC` in the Event object
     - `schema.json` validation

---

## 4. REJECTION RULES

The system MUST reject any timestamp that:

- Cannot be parsed unambiguously
- Conflicts with multiple possible dates (e.g., `03/04/05` without context)
- Uses:
  - Only a date with no time
  - Only a time with no date
- Lacks a viable timezone policy when required

On rejection:

- The Event MUST NOT be stored.
- The client MUST receive a clear, non-technical error (e.g., “Unrecognized or ambiguous time format. Please use a full date and time.”).

---

## 5. SECURITY & ANTI-MANIPULATION GOALS

Time normalization exists to prevent:

- **AM/PM ambiguity**
  - `8:00 PM` vs `8:00 AM` disputes
- **Timezone games**
  - Shifting events across dates by claiming local offsets
- **Locale confusion**
  - `07/12/2025`:
    - US: July 12, 2025
    - EU: 7 December, 2025
- **Backdating / forward-dating**
  - Exploiting local device time to misrepresent event order

Once normalized:

- All downstream logic, appeals, and audits rely on:
  - UTC timestamps
  - Strict ordering
  - Immutable recorded time

---

## 6. IMPLEMENTATION REQUIREMENTS

Any implementation of this standard MUST:

1. Use a well-tested date-time library where available.
2. Log normalization failures separately from general errors.
3. Never silently “guess” the date when ambiguity exists.
4. Provide a way to:
   - View the original submitted timestamp
   - View the normalized canonical timestamp
   - Audit the conversion rule used

---

## 7. EXAMPLES

### 7.1 Example 1 — US Local with AM/PM

- Input:  
  `12/07/2025 8:14 PM`  
  `America/Los_Angeles`

- Interpretation:  
  8:14 PM PST (UTC−08:00) on December 7, 2025

- Output:  
  `2025-12-08T04:14:00Z`

---

### 7.2 Example 2 — Already UTC, No Milliseconds

- Input:  
  `2025-12-07T20:14:33Z`

- Output (unchanged):  
  `2025-12-07T20:14:33Z`

---

### 7.3 Example 3 — Ambiguous, Rejected

- Input:  
  `03/04/05 14:00`

- Result:  
  REJECTED — ambiguous date format (could be 2005-03-04, 2005-04-03, etc.)

---

## 8. RELATIONSHIP TO SCHEMA

- `TIME_NORMALIZATION.md` governs **how raw timestamps become canonical**.
- `schema.json` governs **whether the canonical timestamp is structurally valid**.
- `SPEC.md` governs **what the timestamp means legally and structurally**.

The flow MUST always be:

1. Raw input  
2. Time Normalization (`TIME_NORMALIZATION.md`)  
3. Schema validation (`schema.json`)  
4. Storage and hashing (`SPEC.md` rules)

At no point may a non-normalized timestamp bypass this sequence.

---

**End of TIME_NORMALIZATION.md**
