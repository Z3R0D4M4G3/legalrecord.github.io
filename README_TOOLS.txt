Public Legal Record System (PLRS)
tools/README_TOOLS.txt

------------------------------------------------------------
PURPOSE
------------------------------------------------------------

This directory contains PLRS verification and export tools.

They allow ANY user (public, press, or court) to:

- Validate PLRS Event and Challenge records
- Compute and verify cryptographic hashes
- Check public indices for consistency
- Verify evidence bundles and chain-of-custody logs
- Audit the integrity of the entire PLRS ledger

These tools are provided as-is, without warranty, and are
intended for transparency, verification, and research.


------------------------------------------------------------
CONTENTS (TYPICAL)
------------------------------------------------------------

You may find some or all of the following files:

- validate_event.py
- validate_challenge.py
- hash_event.py
- hash_challenge.py
- build_index.py
- build_challenge_index.py
- verify_bundle.py
- verify_chain_of_custody.py
- verify_ledger_integrity.py
- export_event_bundle.py
- export_challenge_bundle.py
- export_affidavit.py
- export_challenge_affidavit.py
- export_chain_of_custody.py
- publish_snapshot.py

Not all deployments will expose every tool. Some operators
may provide a reduced set focused on verification only.


------------------------------------------------------------
REQUIREMENTS
------------------------------------------------------------

- Python 3.9 or newer (3.10+ recommended)
- Basic ability to run commands in a shell/terminal
- Read/write access to the PLRS data files you want to test

No special libraries should be required beyond Python’s
standard library unless noted in individual scripts.


------------------------------------------------------------
BASIC USAGE EXAMPLES
------------------------------------------------------------

1) Validate an Event record:

    python validate_event.py downloads/data/events/E123.json

2) Validate a Challenge record:

    python validate_challenge.py downloads/data/challenges/C45.json

3) Verify a single Event Evidence Bundle:

    python verify_bundle.py PLRS_EventBundle_E123.json

4) Verify a Challenge Evidence Bundle:

    python verify_bundle.py PLRS_ChallengeBundle_C45.json

5) Verify a Chain of Custody log:

    python verify_chain_of_custody.py PLRS_ChainOfCustody_E123.json

6) Audit the entire ledger:

    python verify_ledger_integrity.py \
      --event-index downloads/data/public_index.json \
      --challenge-index downloads/data/public_challenge_index.json \
      --events-dir downloads/data/events \
      --challenges-dir downloads/data/challenges


------------------------------------------------------------
SAFETY AND PRIVACY
------------------------------------------------------------

- These tools operate on local files only.
- They do NOT send data to any remote server.
- They are designed to be used offline for maximum privacy.

If you received PLRS data as part of a legal matter, you
may copy it to an isolated system and verify it there,
without any network connection.


------------------------------------------------------------
WHAT THESE TOOLS PROVE
------------------------------------------------------------

When used correctly, these tools can prove:

- Whether a PLRS record (Event or Challenge) has been altered
- Whether the public index matches the underlying records
- Whether a bundle presented in court matches the ledger
- Whether a chain-of-custody log is structurally consistent
- Whether the overall PLRS ledger has been tampered with

They do NOT decide who is right or wrong in a dispute.
They only prove whether records and timelines have changed.


------------------------------------------------------------
IF YOU ARE AN ATTORNEY OR COURT
------------------------------------------------------------

You can:

- Attach hash outputs and verifier logs as exhibits
- Use `verify_bundle.py` to confirm evidence integrity
- Use `verify_ledger_integrity.py` to support arguments
  about systemic tampering, pruning, or data suppression

See the public documentation pages:

- HOW_TO_VERIFY.html
- docs/SPEC_public.html
- docs/THREAT_MODEL_public.html
- docs/PUBLISHING.html

for more detail on how PLRS fits into evidentiary practice.


------------------------------------------------------------
IF YOU ARE A JOURNALIST OR ADVOCATE
------------------------------------------------------------

You can:

- Verify records before publication
- Detect silent changes between snapshots
- Archive hashes alongside reporting
- Provide your readers with instructions to verify the
  same records independently

This allows you to publish not only statements, but
cryptographically anchored evidence trails.


------------------------------------------------------------
DISCLAIMER
------------------------------------------------------------

These tools are provided for transparency, verification,
and auditability. They are NOT legal advice. Using them
does not create an attorney-client relationship with any
person or project associated with PLRS.

Always consult local law, court rules, and qualified
counsel when using PLRS data in active legal matters.
