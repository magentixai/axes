> **Status: Golden Trace gt-v2.1 (industrial), corpus of record - not normative.** Tag `corpus/2026-10-12-gt-v2.1`; digests in [`RELEASES.md`](../../RELEASES.md). Regenerated under the Module 14 anchoring block, `basis_status` and the docs/19 key changes. Superseded releases: gt-v2.0 (tag `corpus/2026-08-08-gt-v2`, still verified at its tag) and v1 under [`../../archive/golden-trace-v1-ind/`](../../archive/golden-trace-v1-ind/).

# SE v0.1 Golden Trace gt-v2.1 (Industrial) - MRUN-2026-06-11-A (Pristine Variant)

A fully synthetic, deterministic, end-to-end Agentic Execution Evidence trace for the canonical manufacturing scenario, built report-backwards so that **every sentence of the board-grade promise paragraph resolves to named schema fields in named envelopes**:

> *"An authorised autonomous process released 14 machined parts under delegated authority MD-5120. Every part remained within released engineering tolerance. No exceptions requiring human intervention occurred. Evidence integrity validated. No cross-programme contamination detected."*

## Scenario
**Ironmark Precision Ltd** (fictional, AS9100-style precision manufacturer) runs an autonomous manufacturing release agent that dispositions 14 units of hydraulic manifold **IMP-4471 rev D** under delegated authority **MD-5120** (Quality Director -> agent; released-drawing tolerance; Cpk floor 1.33; material lot HT-88213; no quality-engineer disposition required inside tolerance). The manufacturing interop flow follows the shop-floor pattern: in-line CMM inspection (QIF 3.0) -> OPC-UA release disposition -> MES release record (**ACCEPTED**) -> end-of-shift ISA-95 batch record (B2MML) for reconciliation. Downstream subcontract heat-treatment and plating are **outside the declared capture boundary** - disclosed, evidenced indirectly via EN 10204 3.1 material certificate.

## Contents
```
generate_golden_trace.py     deterministic generator (requires `jcs` - see requirements-dev.txt)
out/envelopes.jsonl          76 hash-chained SE envelopes
out/samples/*.json           4 pretty-printed exemplar envelopes
out/artifacts/*.xml          31 manufacturing stand-ins
out/manifest.json            evidence bundle manifest (sorted file list, forward-slash keys)
out/reports/                 Board / quality audit / conformity / forensic
```

## What is real vs simulated

| Element | In this corpus | Field a verifier reads |
|---|---|---|
| Hash chain, sequence, time ordering, artefact hashes, manifest and bundle hash | **Real** and re-verifiable (RFC 8785 JCS, SHA-256) | `integrity.envelope_hash`, `integrity.previous_envelope_hash`, `manifest.json` |
| Chain head named by each anchor | **Real**: the local chain head at that moment | `anchoring.anchored_subject_hash` |
| In-trace anchors (every 300 s and the export's final anchor) | **Simulated**: nothing is written to a mechanism; never `externally_anchored` | `anchoring.anchors[].basis_status: simulated` |
| Envelope signatures (`SIG-STUB(...)`) | **Stubbed** | `integrity.envelope_signature_basis_status: stubbed` |
| QIF result (QMS mTLS) and MES batch-record authenticity | **Stubbed** | `acknowledgments[].basis_status: stubbed`, `reconciliation.acknowledgment_rung.basis_status: stubbed` |
| OPC-UA transport and MES acceptance acknowledgment rungs | **Simulated** (the trace is synthetic; no channel existed) | `acknowledgments[].basis_status: simulated` |
| The gt-v2.1 release statement over this corpus | **Real external anchors**: RFC 3161 (FreeTSA) and OpenTimestamps (Bitcoin), verified offline with `tools/anchoring/` | [`RELEASES.md`](../../RELEASES.md), [`VERIFY.md`](../../VERIFY.md) |

Measurements and Cpk are exact decimal strings with the unit in `measurement_unit`; derived utilisation ratios live in the report layer only; zero JSON floats in hash scope.

**Two layers, stated plainly.** The trace is synthetic, so its in-trace anchors cannot be anchored at fictional past instants, and pretending otherwise would be an overclaim. In gt-v2.1 they are simulated and say so in `basis_status`, which a verifier reads; the reference verifier reports them `indeterminate` / `basis_not_demonstrated`, never `verified` and never `contradicted`. The existence bound is on the release instead: the release statement committing to both chain heads and both bundle digests is anchored for real, and anyone can check it.

**Fixed in gt-v2.1:** the stored `anchoring_latency_ms: 740` (an illustrative value that reconciled with no pair of timestamps, WO16 Task 4b) is gone: each anchor carries `anchor_requested_at`, and the lag `anchored_at - anchor_requested_at` is derived, never stored (D-017). An anchor is requested at its tick, after the record whose chain head it anchors was emitted, and is anchored before the record that carries it is emitted; the generator asserts both.

**Reading rule for gt-v2.0 and earlier (D-015):** gt-v2.0 envelopes carry `anchoring_method: "write_once_store (SIMULATED)"` with `corroboration_state: externally_anchored`; that must **not** be read as an independently verifiable existence bound. Every key that changed between gt-v2.0 and gt-v2.1 is in [docs/19](../../docs/19-key-change-index.md).

## Verify
```bash
pip install -r requirements-dev.txt
python3 generate_golden_trace.py
python3 ../../tools/axes_verify.py
```
Full procedure, including the release anchors: [`VERIFY.md`](../../VERIFY.md).

## Determinism
No randomness; fixed timestamps. Regeneration is byte-identical across platforms (manifest keys sorted, paths use `/`).
