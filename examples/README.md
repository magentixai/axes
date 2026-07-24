# Examples

## Current dialect - `golden-trace/` (v1 working exemplar)

A complete, deterministic, re-verifiable evidence bundle: an autonomous AP agent executing 14 SEPA Instant payments under delegated authority AD-7844. 76 hash-chained envelopes, 29 ISO 20022 artefacts, an evidence-bundle manifest, and four target reports (board / audit / regulator / forensic) in which every sentence resolves to named fields in named envelopes. `python3 generate_golden_trace.py` regenerates it byte-identically and re-verifies the chain.

**Status:** *v1 working exemplar and test corpus* - not normative (D-008). Informal hashing; stubbed signatures (disclosed). Golden Trace v2 will regenerate under settled canonicalisation (P1-1) and seed byte-level test vectors.

Pretty-printed samples (current shape):

- [`golden-trace/out/samples/envelope_payment03_policy_check.json`](golden-trace/out/samples/envelope_payment03_policy_check.json) - pre-commit decision + control checks
- [`golden-trace/out/samples/envelope_payment03_commit_succeeded.json`](golden-trace/out/samples/envelope_payment03_commit_succeeded.json) - commit outcome + acknowledgment ladder
- [`golden-trace/out/samples/envelope_reconciliation.json`](golden-trace/out/samples/envelope_reconciliation.json) - settlement rung accretion
- [`golden-trace/out/samples/envelope_anchor.json`](golden-trace/out/samples/envelope_anchor.json) - external anchoring event

Operator verification vs conformance claims: [`../CONFORMANCE.md`](../CONFORMANCE.md).

## Legacy dialect - `legacy/`

Pre-catalogue single-envelope examples (`version: se.v1.draft`) live in [`legacy/`](legacy/). They are design history aligned with the archived May 2026 sketch - **not** the current working envelope shape. Do not implement against them.
