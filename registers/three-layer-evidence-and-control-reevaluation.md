# Three-layer evidence coverage and control re-evaluation

> **Status: programme tracker - Band A complete (2026-07-24); Band B open.** Informative workstream under doctrine §5 (evidence lane, not enforcement). Does not freeze schema. Does not redefine SE-C levels. Cross-refs: D-014, TRK-024, GAP-EXEC-005, GAP-EXEC-021, REQ-EXT-007, P1-1, P1-3, P1-4, Modules 03/04/12/14/15, D-008.

## Why this exists

External agent-governance discussions have converged on three bound artifacts for accountable autonomous action: a **pre-execution decision**, the **control specification in force at decision time**, and a **post-execution outcome**, all keyed to one action identity. AXES already speaks to each of these as *evidence*, but today's Golden Trace and catalogue mostly bind **names, versions, and recorded results** - not a content-addressed control context that a competent third party can **re-evaluate**.

This tracker has two bands:

1. **Near-term surfacing (TLC-*)** - make AXES's existing coverage of the three layers honest and discoverable, without overclaim.
2. **Control re-evaluation path (CRE-*)** - close the gap from versioned refs to independent re-evaluation under the controls that were active.

Both bands stay inside AXES doctrine: append-only envelopes, pointers-and-hashes, fact vs interpretation, scoped assurance language, vendor neutrality, and **no drift into policy engines or blocking**.

---

## Doctrine constraints (non-negotiable for this workstream)

| Constraint | Implication for tasks |
|---|---|
| AXES evidences; it never enforces | Mapping docs describe *evidence coverage of* the three layers - never claim AXES *is* a governance/authorization stack |
| No frozen JSON Schema until P1-1 (D-006) | README and examples surface a **working envelope shape**, never "the SE v0.1 schema" |
| Golden Trace is exemplar/corpus, not normative (D-008) | Corpus verification ≠ emitter conformance claim |
| Conformance is defined by public spec, validator, and test vectors - never by vendor ingestion (incl. ARBITR) | Do not use Magentix AI-authored reports A-D as proof of SE-C4 |
| Correlation ≠ cryptographic action binding | Today's `trace_id` / `span_id` / `transaction_ref` are a **correlation spine**; content-addressed action binding awaits P1-1 / Module 14 |
| Faithful capture is orthogonal | Sealing the right snapshot does not prove the runtime evaluated that snapshot; custody/attestation tracked separately (threat model, Module 14/15) |
| Policy-language neutrality | Envelope binds digests + declared evaluation profile; re-run happens in an external engine - AXES does not interpret Cedar/OPA/etc. |

---

## The three layers (evidence framing)

| Layer | Reader question | What "closed" looks like in AXES |
|---|---|---|
| **L1 - Decision** | What was decided before consequence, on what observed basis? | Pre-commit envelope(s) with controls/approvals, assertion basis, sealed under settled canonicalisation |
| **L2 - Control-in-force** | Which exact controls evaluated that decision, and can they be re-run? | Content-addressed **control-context snapshot** (policy + permissions + reference data digests) with effective time, bound into the decision envelope; retrievable under the access model |
| **L3 - Outcome** | What became real, under the same action identity? | Commit-boundary envelope(s) + acknowledgment ladder + artefact refs, bound to the same action key as L1 |

**Honest state today:** L1 and L3 are substantially exercised by Golden Trace v1 (with disclosed stubs). L2 is **partial**: `policy_ref` / `policy_version` / `control_set_ref` / per-check results exist; re-evaluable snapshot bytes and input digests do not.

---

## Band A - Near-term surfacing (TLC-*)

Ship discoverability and claim hygiene first. No fake schema. No conformance theatre.

| ID | Task | Deliverable | Done when | Depends | Status |
|---|---|---|---|---|---|
| TLC-001 | README: working envelope shape | Section titled **Working envelope shape (exemplar)** - status, link Module 01 + module map + why `schema/` is empty; trimmed sample or three-moment table; never say "the schema" | Reader can see shape without mistaking it for a freeze | - | ✅ 2026-07-24 |
| TLC-002 | Three-moment illustration | Same payment: policy-check → commit (+ link ack accretion) using Golden Trace samples; shows L1/L2-partial/L3 without one JSON pretending to be all three | Table or paired links in README and/or interop note | TLC-001 | ✅ 2026-07-24 |
| TLC-003 | Informative three-layer coverage note | `docs/interop/three-layer-evidence-coverage.md` - evidence-coverage framing; field map; gap callout on L2; correlation spine vs pending action binding; one-line custody/basis pointer | Citeable without overclaim; filename not owned by one external venue | TLC-002 | ✅ 2026-07-24 |
| TLC-004 | Root `CONFORMANCE.md` as operator guide | Corpus verification vs conformance claims split; soft SE-C0..C5 illustration against Golden Trace; explicit: passing Golden Trace ≠ SE-Cx claim; `docs/07` remains normative ladder home | Two-doc authority line clear; no C0 theatre before schema | D-008 | ✅ 2026-07-24 |
| TLC-005 | Legacy example quarantine | Label or move pre-Golden-Trace dialect examples (`openclaw-file-write.json`, langgraph, etc.) so onboarding has one current shape | README/examples point only at current dialect | TLC-001 | ✅ 2026-07-24 |
| TLC-006 | Wire and govern | README map + CONTRIBUTING pointer; CHANGELOG; adjacent-standards watch row for agent-governance evidence discussions (differentiate: control lane vs evidence lane); optional register cross-links only | Discoverable from repo root | TLC-001..005 | ✅ 2026-07-24 |
| TLC-007 | Claim language review | Pass all new text against doctrine §3.10 and category discipline §5; no "AXES authorizes / enforces / certifies" | Review checklist ticked on PR | TLC-003, TLC-004 | ✅ 2026-07-24 |

**Explicit non-goals for Band A:** populate `schema/` with a preview JSON Schema; claim SE-C0 validity; equate Magentix AI reports with third-party reportability; assert L2 re-evaluation is already met.

---

## Band B - Control re-evaluation path (CRE-*)

Target: a competent third party, given the evidence bundle and authorised dereference of control-context artifacts, can **reproduce** the load-bearing control checks (or prove why replay is invalid) - not merely read that "policy v3.2 passed."

### B1 - Design decisions (catalogue / P1)

| ID | Task | Deliverable | Done when | Depends |
|---|---|---|---|---|
| CRE-001 | Control-context composition | Normative definition of what a **control-context snapshot** must include for re-evaluation claims (policy/rules + effective permissions + referenced master-data digests such as beneficiary lists / limits); disclosure rule when the set is partial | Decision-register entry; Module 03/04/12 draft text | GAP-EXEC-021 |
| CRE-002 | Content-addressed snapshot fields | Catalogue keys: e.g. `policy_snapshot_ref` + digest, `control_context_hash`, effective dating (`effective_from` / `effective_until` or equivalent) on versioned control refs (closes GAP-EXEC-005 for this use) | Module catalogue entries with maturity + triggers | CRE-001 |
| CRE-003 | Evaluated-input digest | Field(s) for normalized input the controls saw (amount, beneficiary key, capability, …) - pointers/hashes only; declared hash scope | Catalogue + P1-1 hash-scope note | CRE-002, P1-1 |
| CRE-004 | Decision binding triple | Envelope commits to `(action/input digest, control-context digest, decision outcome)` inside hash scope; correlation spine remains; content-addressed action key profiled after P1-1 | Module 14 + Module 01 correlation note; negative examples of timestamp-only binding | CRE-003, P1-1 |
| CRE-005 | Evaluation-profile neutrality | Slot for `evaluation_profile_id` / engine id+version so re-run means *same declared semantics*; AXES does not embed a policy language | Catalogue + standards-alignment note | CRE-001 |
| CRE-006 | Reproducible vs observed-only checks | Vocabulary/rule: which control results may support re-evaluation assurance vs `observed_only` (e.g. non-deterministic judges); assurance statements must not rest re-evaluation claims on observed-only checks | Controlled vocab + conformance rule | CRE-001 |
| CRE-007 | Snapshot access & redaction | How restricted exports still prove digests (Merkle / salted commitments); dereference under P1-3; interaction with `content_erased` / retention | docs/10 normative subsection | CRE-002, P1-3 |
| CRE-008 | L1/L3 receipt alignment | Ensure acknowledgment ladder / receipt slot (P1-4) and commit module bind outcomes to the same action key as the decision envelope; rungs may accrete over time (GT-003) | P1-4 + Module 06 catalogue consistency | CRE-004, P1-4 |

### B2 - Proof in corpus and conformance

| ID | Task | Deliverable | Done when | Depends |
|---|---|---|---|---|
| CRE-009 | Golden Trace v2 control-context pack | Publish hashed control-context artifacts (policy + supplier-master + limits as applicable) beside envelopes; decision envelopes carry digests; public procedure to re-run CTL-* checks from bundle + artifacts | `generate_golden_trace.py` verifies re-evaluation for reproducible checks; stubs disclosed | CRE-002..006, P1-1, D-008 |
| CRE-010 | Negative / mismatch vectors | Fixtures: version without digest; digest without retrievable artifact; input mismatch; effective-time miss; observed-only check offered as re-evaluable | Byte-level or validator vectors fail closed | CRE-009 |
| CRE-011 | Conformance profile flag | Distinct claim surface (profile or SE-C gate) for **control-re-evaluable** evidence - separate from "authority fields present" (SE-C2) | docs/07 + CONFORMANCE.md updated; cannot be satisfied by `policy_version` alone | CRE-009, CRE-010, TRK-019 |
| CRE-012 | Third-party re-evaluation test | Protocol: give an independent party only open bundle + control-context artifacts + draft field defs; they re-run checks and report pass/fail without Magentix AI tooling | Published result or divergence log entry | CRE-009, CRE-011 |

### B3 - Explicitly deferred (related, not this bar)

| ID | Item | Why deferred here |
|---|---|---|
| CRE-D01 | Faithful-capture / independent witness | Integrity of sealed bytes ≠ proof of faithful emission; threat model + Module 14/15 / EU-007 custody - do not block CRE-001..012 but must not be silently claimed as solved |
| CRE-D02 | AXES-as-policy-engine | Rejected by doctrine; evaluation stays external |
| CRE-D03 | Schema freeze before P1-1 | Forbidden by D-006 |

---

## Band C - External existence bound (EB-*) — orthogonal to L2

Local hash chains do not prove independent existence-in-time. Closing the simulated Golden Trace anchor is tracked here (feeds TRK-001 / D-015), not under CRE-*.

| ID | Task | Deliverable | Done when | Depends | Status |
|---|---|---|---|---|---|
| EB-001 | Reading rule for SIMULATED anchors | Documented: `externally_anchored` + SIMULATED ≠ closed existence bound; GT README + interop note | Public text cannot be misread as a real bound | D-015 | ✅ 2026-07-24 |
| EB-002 | Mechanism-agnostic `anchoring_method` vocabulary | Normative list / registry posture: `timestamp_authority`, `transparency_log` (SCITT instance), `opentimestamps`, `write_once_store`, `distributed_ledger`, … with **verify-path** requirements; MUST NOT hard-require SCITT | Catalogue / Module 14 draft | TRK-001 | Open |
| EB-003 | Profile EvidenceAnchor-class **and SCITT** receipts | Map AGT EvidenceAnchor / Rekor / **SCITT (TS id, statement digest, receipt, inclusion proof)** / RFC 3161 / OTS → SE `anchoring.*` without depending on AGT's Python ABC or any single TS | Interop table in Module 14 or docs/12; rules in docs/interop/x402-and-anchoring.md | D-015, EB-002 | Open |
| EB-004 | Golden Trace v2 real anchor | At least one backend whose receipt verifies without Magentix AI infrastructure (SCITT **or** OTS **or** TSA peer); forensic step 5 becomes real; `SIG-STUB` replaced per signing profile | GT v2 + CONFORMANCE corpus note | P1-1, D-008, EB-002 | Open - [#4](https://github.com/magentixai/axes/issues/4); related candidate [#3](https://github.com/magentixai/axes/issues/3) |
| EB-005 | Conformance: silent overclaim rejected | Vector/rule: SIMULATED or missing verify-path cannot claim externally_anchored for assurance | Negative vector or CONFORMANCE.md rule | EB-001, EB-004 | Open |
| EB-006 | Ack-ladder vs existence-bound discipline | Normative note: SCITT/TSA/OTS receipt is a higher corroboration rung; MUST NOT verify as transport/protocol/business/settlement ack; optional dual registration (decision digest + outcome digest) on same action key | P1-4 + Module 06/14 text | P1-4, GT-003 | Open |

Detail: [`docs/interop/x402-and-anchoring.md`](../docs/interop/x402-and-anchoring.md).

---

## Suggested sequencing

```
Band A (TLC-001..007)          # discoverability + claim hygiene  ✅
        |
        v
CRE-001 composition  ->  CRE-002 fields + effective time
        |                        |
        +---- CRE-005 profile ---+
        |                        |
        v                        v
P1-1 settles  ->  CRE-003 input digest + CRE-004 binding
        |
        +-> CRE-006 reproducible rule
        +-> CRE-007 access (with P1-3)
        +-> CRE-008 L3/receipt alignment (with P1-4)
        |
        v
CRE-009 Golden Trace v2  ->  CRE-010 vectors  ->  CRE-011 profile  ->  CRE-012 third-party test

# Parallel (does not wait on L2):
EB-001 ✅ -> EB-002 vocabulary -> EB-003 profiles (incl. SCITT) -> EB-006 ack discipline
        -> EB-004 GT v2 real anchor (+ signatures) -> EB-005
```

Catalogue priority implication: Module **03 Authority**, **04 Capability**, and **12 Risk/Control** should absorb CRE-001/002/005/006; Module **06** and P1-4 absorb CRE-008; Module **14** absorbs CRE-003/004 and EB-002/003 with P1-1. Module 06 remains next for commit-boundary catalogue work; CRE/EB field drafts may proceed in parallel as long as they do not freeze hashed structure before P1-1.

---

## Acceptance test for "L2 closed"

All of the following are true:

1. A decision envelope carries digests for control-context and evaluated inputs inside the envelope hash scope.
2. The control-context artifacts are retrievable (or their absence is disclosed so re-evaluation is not claimable).
3. Effective time selects one snapshot; two verifiers cannot pick different bytes for the same version label.
4. An independent procedure re-runs the reproducible checks and matches recorded results, or explains invalidity.
5. Conformance materials reject "policy_version present" as sufficient for a control-re-evaluable claim.
6. Public text still states AXES does not enforce policy and does not certify compliance.

Until then, public mapping language MUST describe L2 as **partial (versioned refs and recorded control results)**.
