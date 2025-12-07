# PLRS Development Roadmap
**Project:** Public Legal Record System (PLRS)  
**File:** ROADMAP.md  
**Status:** Active Execution Plan  
**Purpose:** To define the public, staged path from standard → validation → implementation → adoption.

---

## PHASE 0 — FOUNDATION (COMPLETED)

This phase establishes the system’s non-negotiable rules and defenses.

- [x] README.md — Public mission and overview  
- [x] LICENSE — Legal usage and protection  
- [x] SPEC.md — Core legal + structural standard  
- [x] THREAT_MODEL.md — Adversary and defense doctrine  
- [x] schema.json — Machine validation layer  
- [x] TIME_NORMALIZATION.md — Canonical time standard  

**Status:** ✅ Locked

---

## PHASE 1 — CORE TOOLING (NEXT BUILD TARGET)

This phase creates the minimum working pipeline for real records.

- [ ] `normalize_time` implementation (JS or Python)
- [ ] Local `schema.json` validator
- [ ] CLI tool:
  - Input raw Event
  - Normalize time
  - Validate against schema
  - Output canonical Event JSON
- [ ] Hashing utility for Evidence_Hashes
- [ ] Rejection logging for invalid records

**Outcome:**  
A developer or user can create a **fully valid, court-grade Event record locally**.

---

## PHASE 2 — EVENT INGEST PROTOTYPE

This phase introduces the first live intake surface.

- [ ] Minimal web form (static HTML + JS)
- [ ] Field-level validation
- [ ] Local-only record generation (no server required)
- [ ] Auto-hash of uploaded evidence
- [ ] Downloadable canonical Event file

**Outcome:**  
Non-technical users can generate **valid PLRS records without installing software**.

---

## PHASE 3 — PUBLIC MIRROR & IMMUTABILITY PROOF

This phase establishes public permanence.

- [ ] Static public mirror (GitHub Pages or IPFS)
- [ ] Append-only Event index
- [ ] Public hash verification tool
- [ ] Automatic validation on submission
- [ ] Public challenge submission format

**Outcome:**  
Events become **publicly auditable and independently verifiable**.

---

## PHASE 4 — CHALLENGE & APPEAL LAYER

This phase activates formal dispute mechanics.

- [ ] Challenge Event generator
- [ ] Public challenge linking
- [ ] Time-window enforcement
- [ ] Status locking after challenge expiration
- [ ] Visual Event/Challenge threading

**Outcome:**  
Disputes become **cryptographically traceable** instead of procedurally buried.

---

## PHASE 5 — LEGAL INTERFACE PACK

This phase makes PLRS court-operational.

- [ ] Court export format (PDF + JSON bundle)
- [ ] Hash verification affidavit template
- [ ] Expert declaration boilerplate
- [ ] Chain-of-custody verifier
- [ ] Appeal packet generator

**Outcome:**  
PLRS records become **drop-in appeal weapons**.

---

## PHASE 6 — DISTRIBUTED SURVIVAL

This phase hardens against de-platforming and suppression.

- [ ] Multi-host static mirrors
- [ ] IPFS replication
- [ ] Peer-to-peer index sync
- [ ] Offline verification packages
- [ ] Cold-storage public archives

**Outcome:**  
No single entity can erase PLRS history.

---

## PHASE 7 — PUBLIC ADOPTION & JURISDICTION PILOTS

This phase moves from technology into systemic use.

- [ ] Public education materials
- [ ] NGO and legal clinic pilots
- [ ] Independent journalist adoption
- [ ] Open audit contests
- [ ] Jurisdiction-specific compliance overlays (non-destructive)

**Outcome:**  
PLRS becomes **functionally unavoidable** in public record disputes.

---

## LONG-TERM PRINCIPLE

At no phase may:
- Immutability be weakened  
- Public visibility be replaced with discretion  
- Anonymization be compromised  
- Or time normalization be bypassed  

All phases inherit:
SPEC.md → TIME_NORMALIZATION.md → schema.json → THREAT_MODEL.md

---

**End of ROADMAP.md**
