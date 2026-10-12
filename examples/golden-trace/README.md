> **Status: Golden Trace gt-v2.1, corpus of record - not normative.** Tag `corpus/2026-10-12-gt-v2.1`; digests in [`RELEASES.md`](../../RELEASES.md). Regenerated under the Module 14 anchoring block, `basis_status` and the docs/19 key changes. Superseded releases: gt-v2.0 (tag `corpus/2026-08-08-gt-v2`, still verified at its tag) and v1 under [`../../archive/golden-trace-v1-fin/`](../../archive/golden-trace-v1-fin/).

# SE v0.1 Golden Trace gt-v2.1 - APRUN-2026-06-09-A (Pristine Variant)

A fully synthetic, deterministic, end-to-end Agentic Execution Evidence trace for the canonical ARBITR scenario, built report-backwards so that **every sentence of the board-grade promise paragraph resolves to named schema fields in named envelopes**:

> *"An authorised autonomous process executed 14 payment instructions under delegated authority AD-7844. All payments remained within approved policy boundaries. No exceptions requiring human intervention occurred. Evidence integrity validated. No cross-tenant data exposure detected."*

## Scenario
**Caldera Robotics Ltd** (fictional, non-regulated mid-size manufacturer) runs an autonomous AP agent that pays 14 approved supplier invoices by SEPA Instant credit transfer under delegated authority **AD-7844** (CFO → agent; EUR 25,000/payment; EUR 150,000/batch; approved-beneficiary list; no human approval required within limits). The ISO 20022 flow follows the instant-payments message pattern: the agent's instruction (pain.001) → interbank leg (pacs.008, **outside the declared capture boundary** - disclosed, evidenced indirectly) → bank status report (**pacs.002 ACSC**) → end-of-day statement (**camt.053**) for reconciliation.

The pristine variant deliberately exercises the hard machinery through *positive* evidence rather than exceptions:
- **42 pre-commit control evaluations** (approved-beneficiary, per-payment limit, duplicate-idempotency × 14), all passed - prevention evidence, not post-hoc logging
- **Three-rung acknowledgment ladder** per payment (transport HTTPS / protocol ACCEPTED / business pacs.002 ACSC) + **settlement rung** via camt.053 - external confirmation, not self-assertion
- **Measured completeness**: independently reconciled population (ERP queue 14 due + bank statement 14 booked) → coverage 14/14, with `population_basis: independently_reconciled`
- **Silence semantics**: heartbeats every 60s (zero silent windows) + `emission_fail_posture: fail_closed` ⇒ absence of evidence = absence of action within the boundary
- **Anchoring** every 300s plus a final export anchor: real chain-head hashes, simulated store, stated in `basis_status` (the release itself is anchored for real)
- **Proximity, not just pass/fail**: payment 3 at **95.6%** of its limit (report-layer derived from Amount operands) → surfaces as a leading-indicator observation, not an exception
- **Privacy by reference**: beneficiary/debtor IBANs redacted by hash substitution under a named redaction profile; delegator recorded as pseudonymous key
- **Scoped AI context**: sampling parameters recorded as exact decimal strings; replay claim scoped ("reproducible in distribution, not in instance"); reasoning artifacts `provider_withheld` - disclosed, never silent

## Contents
```
generate_golden_trace.py     deterministic generator (requires `jcs` - see requirements-dev.txt)
out/envelopes.jsonl          76 hash-chained SE envelopes (time-ordered, contiguous sequence)
out/samples/*.json           4 pretty-printed exemplar envelopes
out/artifacts/*.xml          29 ISO 20022 stand-ins (pain.001 ×14, pacs.002 ×14, camt.053)
out/manifest.json            evidence bundle manifest (sorted file list, per-file SHA-256, bundle hash)
out/reports/report_A_board.md       Board assurance summary (claim-cited)
out/reports/report_B_audit.md       Audit & control view
out/reports/report_C_regulator.md   Regulator / external assurance pack
out/reports/report_D_forensic.md    Forensic execution pack (incl. verification procedure)
```

## What is real vs simulated

| Element | In this corpus | Field a verifier reads |
|---|---|---|
| Hash chain, sequence, time ordering, artefact hashes, manifest and bundle hash | **Real** and re-verifiable (RFC 8785 JCS, SHA-256) | `integrity.envelope_hash`, `integrity.previous_envelope_hash`, `manifest.json` |
| Chain head named by each anchor | **Real**: the local chain head at that moment | `anchoring.anchored_subject_hash` |
| In-trace anchors (every 300 s and the export's final anchor) | **Simulated**: nothing is written to a mechanism; never `externally_anchored` | `anchoring.anchors[].basis_status: simulated` |
| Envelope signatures (`SIG-STUB(...)`) | **Stubbed** | `integrity.envelope_signature_basis_status: stubbed` |
| pacs.002 webhook (mTLS) and camt.053 statement-channel authenticity | **Stubbed** | `acknowledgments[].basis_status: stubbed`, `reconciliation.acknowledgment_rung.basis_status: stubbed` |
| HTTPS transport and bank-API protocol acknowledgment rungs | **Simulated** (the trace is synthetic; no channel existed) | `acknowledgments[].basis_status: simulated` |
| The gt-v2.1 release statement over this corpus | **Real external anchors**: RFC 3161 (FreeTSA) and OpenTimestamps (Bitcoin), verified offline with `tools/anchoring/` | [`RELEASES.md`](../../RELEASES.md), [`VERIFY.md`](../../VERIFY.md) |

**Two layers, stated plainly.** The trace is synthetic, so its in-trace anchors cannot be anchored at fictional past instants, and pretending otherwise would be an overclaim. In gt-v2.1 they are simulated and say so in `basis_status`, which a verifier reads; the reference verifier reports them `indeterminate` / `basis_not_demonstrated`, never `verified` and never `contradicted`. The existence bound is on the release instead: the release statement committing to both chain heads and both bundle digests is anchored for real, and anyone can check it.

**Fixed in gt-v2.1:** the stored `anchoring_latency_ms: 740` (an illustrative value that reconciled with no pair of timestamps, WO16 Task 4b) is gone: each anchor carries `anchor_requested_at`, and the lag `anchored_at - anchor_requested_at` is derived, never stored (D-017). An anchor is requested at its tick, after the record whose chain head it anchors was emitted, and is anchored before the record that carries it is emitted; the generator asserts both.

**Reading rule for gt-v2.0 and earlier (D-015):** gt-v2.0 envelopes carry `anchoring_method: "write_once_store (SIMULATED)"` with `corroboration_state: externally_anchored`; that must **not** be read as an independently verifiable existence bound. Every key that changed between gt-v2.0 and gt-v2.1 is in [docs/19](../../docs/19-key-change-index.md).

## Verify it yourself
```bash
pip install -r requirements-dev.txt
python3 generate_golden_trace.py
python3 ../../tools/axes_verify.py
```
Regenerates everything and re-verifies the chain (asserts on failure, including the zero-float and anchor-timing checks), then runs the reference verifier. Full procedure, including the release anchors: [`VERIFY.md`](../../VERIFY.md). Byte-level vectors land in [`../../vectors/`](../../vectors/). The vendor-neutral manual procedure is in `report_D_forensic.md` section 1.

## Hash changes between releases
All 76 envelope hashes changed from v1 (GT-JCS-0 + JSON floats) to v2 (RFC 8785 JCS + Amount fields), the substance of the P1-1 ruling (axes#6), and again from gt-v2.0 to gt-v2.1 (key changes listed in docs/19). The first anchor is envelope 36 in gt-v2.1 (37 in gt-v2.0): an anchor now sorts before any other event in the same second, because it anchors the chain head as it stood at the tick. v1 bytes are preserved under [`../../archive/golden-trace-v1-fin/`](../../archive/golden-trace-v1-fin/).

## Determinism
No randomness; fixed timestamps (run window 2026-06-09 09:00 UTC). Regeneration is byte-identical on any platform (manifest file list is sorted lexicographically).
