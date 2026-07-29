# Examples

Two complete, deterministic, re-verifiable Golden Trace bundles share the **same evidence skeleton** (76 hash-chained envelopes, heartbeats, simulated anchors, four role-specific reports, manifest). Only the domain and artifact standards differ - proving sector flexibility without normative schema claims.

**Status (both):** *v1 working exemplar and test corpus* - not normative (D-008). Informal hashing (`GT-JCS-0`); stubbed signatures and simulated anchors (disclosed). Golden Trace v2 will regenerate under settled canonicalisation (P1-1) and seed byte-level test vectors.

Operator verification vs conformance claims: [`../CONFORMANCE.md`](../CONFORMANCE.md).

---

## Financial services - `golden-trace/` (Fin)

An autonomous AP agent executing 14 SEPA Instant payments under delegated authority AD-7844. 29 ISO 20022 artefacts (pain.001, pacs.002, camt.053). Run reference **APRUN-2026-06-09-A**.

`python3 generate_golden_trace.py` in that directory regenerates the bundle byte-identically and re-verifies the chain.

Pretty-printed samples:

- [`golden-trace/out/samples/envelope_payment03_policy_check.json`](golden-trace/out/samples/envelope_payment03_policy_check.json) - pre-commit decision + control checks
- [`golden-trace/out/samples/envelope_payment03_commit_succeeded.json`](golden-trace/out/samples/envelope_payment03_commit_succeeded.json) - commit outcome + acknowledgment ladder
- [`golden-trace/out/samples/envelope_reconciliation.json`](golden-trace/out/samples/envelope_reconciliation.json) - settlement rung accretion
- [`golden-trace/out/samples/envelope_anchor.json`](golden-trace/out/samples/envelope_anchor.json) - external anchoring event

---

## Industrial and manufacturing - `golden-trace-ind/` (Ind)

An autonomous production release agent dispositioning 14 units of IMP-4471 rev D under delegated authority MD-5120. 31 manufacturing stand-ins (QIF 3.0, MES release, B2MML, MTConnect, EN 10204 material cert). Run reference **MRUN-2026-06-11-A**.

`python3 generate_golden_trace.py` in that directory regenerates the bundle byte-identically and re-verifies the chain.

Pretty-printed samples:

- [`golden-trace-ind/out/samples/envelope_part03_quality_gate.json`](golden-trace-ind/out/samples/envelope_part03_quality_gate.json) - pre-release quality gates + control checks
- [`golden-trace-ind/out/samples/envelope_part03_commit_succeeded.json`](golden-trace-ind/out/samples/envelope_part03_commit_succeeded.json) - release outcome + acknowledgment ladder
- [`golden-trace-ind/out/samples/envelope_reconciliation.json`](golden-trace-ind/out/samples/envelope_reconciliation.json) - batch-record settlement rung
- [`golden-trace-ind/out/samples/envelope_anchor.json`](golden-trace-ind/out/samples/envelope_anchor.json) - external anchoring event

Role-specific reports (board / quality audit / conformity assessment / forensic) live under each bundle's `out/reports/`. The [magentix.ai AXES report hub](https://magentix.ai/axes/report/) renders both examples for professional feedback.

---

## Legacy dialect - `legacy/`

Pre-catalogue single-envelope examples (`version: se.v1.draft`) live in [`legacy/`](legacy/). They are design history aligned with the archived May 2026 sketch - **not** the current working envelope shape. Do not implement against them.
