> **Status: v1 working exemplar and test corpus - not normative.** Built to prove the report-backwards machinery end to end for a manufacturing scenario and to seed test vectors. It will be regenerated as Golden Trace v2 under the P1-1 canonicalisation decision, with per-profile signatures. Known limitations are disclosed inline below - that disclosure discipline is itself part of the standard.

# SE v0.1 Golden Trace (Industrial) - MRUN-2026-06-11-A (Pristine Variant)

A fully synthetic, deterministic, end-to-end Agentic Execution Evidence trace for the canonical manufacturing scenario, built report-backwards so that **every sentence of the board-grade promise paragraph resolves to named schema fields in named envelopes**:

> *"An authorised autonomous process released 14 machined parts under delegated authority MD-5120. Every part remained within released engineering tolerance. No exceptions requiring human intervention occurred. Evidence integrity validated. No cross-programme contamination detected."*

## Scenario
**Ironmark Precision Ltd** (fictional, AS9100-style precision manufacturer) runs an autonomous manufacturing release agent that dispositions 14 units of hydraulic manifold **IMP-4471 rev D** under delegated authority **MD-5120** (Quality Director -> agent; released-drawing tolerance; Cpk floor 1.33; material lot HT-88213; no quality-engineer disposition required inside tolerance). The manufacturing interop flow follows the shop-floor pattern: in-line CMM inspection (QIF 3.0) -> OPC-UA release disposition -> MES release record (**ACCEPTED**) -> end-of-shift ISA-95 batch record (B2MML) for reconciliation. Downstream subcontract heat-treatment and plating are **outside the declared capture boundary** - disclosed, evidenced indirectly via EN 10204 3.1 material certificate.

The pristine variant deliberately exercises the hard machinery through *positive* evidence rather than exceptions:
- **42 pre-release control evaluations** (CTL-DIM-01 dimension, CTL-SPC-02 process capability, CTL-MAT-03 material lot x 14), all passed - prevention evidence, not post-hoc logging
- **Three-rung acknowledgment ladder** per part (transport OPC-UA Good / machine MES ACCEPTED / quality QIF CONFORMING) + **settlement rung** via B2MML batch record - external confirmation, not self-assertion
- **Measured completeness**: independently reconciled population (MES production order 14 planned + goods-receipt 14 booked, 0 scrap) -> coverage 14/14, with `population_basis: independently_reconciled`
- **Silence semantics**: heartbeats every 60s (zero silent windows) + `emission_fail_posture: fail_closed` => absence of evidence = absence of action within the boundary
- **External anchoring** every 300s (simulated store, real chain-head hashes) + final export anchor
- **Proximity, not just pass/fail**: part 3 at **95.6%** of tolerance band with batch-lowest Cpk **1.41** -> surfaces as a leading-indicator observation, not an exception
- **Privacy by reference**: operator badge IDs redacted by hash substitution under a named redaction profile; delegator recorded as pseudonymous key
- **Scoped AI context**: sampling parameters recorded; replay claim scoped ("reproducible in distribution, not in instance"); reasoning artifacts `provider_withheld` - disclosed, never silent

## Contents
```
generate_golden_trace.py     deterministic generator (no dependencies, stdlib only)
out/envelopes.jsonl          76 hash-chained SE envelopes (time-ordered, contiguous sequence)
out/samples/*.json           4 pretty-printed exemplar envelopes
out/artifacts/*.xml          31 manufacturing stand-ins (QIF x14, MES release x14, B2MML, MTConnect, matcert)
out/manifest.json            evidence bundle manifest (per-file SHA-256, bundle hash)
out/reports/report_A_board.md       Board assurance summary (claim-cited)
out/reports/report_B_audit.md       Quality & control view
out/reports/report_C_regulator.md   Conformity assessment pack
out/reports/report_D_forensic.md    Forensic execution pack (incl. verification procedure)
```

## What is real vs stubbed
**Real and re-verifiable:** SHA-256 hash chain over canonical JSON (sorted keys, compact separators; `envelope_hash` and `signature` excluded from hash input; signing-key identity *included*), contiguous sequencing, time ordering, artifact hashes, manifest/bundle hash, all coverage and utilisation arithmetic. On anchor envelopes, `anchoring.chain_head_hash` is the real local chain head at that moment.
**Stubbed and disclosed as such:** envelope signatures (`SIG-STUB`); the external anchor store (`anchoring_method: "write_once_store (SIMULATED)"`, demo `anchor_store_ref`); QMS mTLS authenticity of QIF results; MES batch-record signing. The reports disclose every stub - practising the scoped-assurance language the standard mandates. Structured `basis_status` is specified in Module 01; corpus values land in gt-v2.1.

**Illustrative stored latency (WO16 Task 4b).** Same class of defect as the financial bundle: the published gt-v2.0 anchor envelope stores a derived latency that does not reconcile with the envelope timestamps. Disclosed until the announced regeneration. See [`examples/golden-trace/README.md`](../golden-trace/README.md).

**Reading rule for anchors (D-015):** `evidence_quality.corroboration_state: externally_anchored` on a SIMULATED method must **not** be treated as an independently verifiable existence bound. A third party cannot verify that the bytes existed unmodified at wall-clock time without trusting the generator. Local chain integrity != external existence. Golden Trace v2 replaces the stub with a real `anchoring_method` instance (see [`docs/interop/x402-and-anchoring.md`](../../docs/interop/x402-and-anchoring.md)).

## Verify it yourself
`python generate_golden_trace.py` regenerates everything and re-verifies the chain (asserts on failure). The vendor-neutral manual procedure is in `report_D_forensic.md` section 1 - it is executable from the bundle alone, which is the point.

## Relationship to the financial Golden Trace
[`examples/golden-trace/`](../golden-trace/) covers accounts-payable (14 SEPA Instant payments, ISO 20022). This directory applies the **same structural skeleton** (76 envelopes, GT-JCS-0, heartbeats, anchors, fail-closed, four reports) to a manufacturing release scenario with `part_index`, QIF/MES/B2MML artifacts, and shop-floor acknowledgment semantics. The two bundles prove sector flexibility without changing paths in the financial example.

## The third-party report test (next step)
Per the design rule - *a competent third party should be able to generate a credible report from the open schema alone* - the protocol: give a third party only `envelopes.jsonl` + `manifest.json` + `artifacts/` + the draft field definitions, ask for a board summary and a quality audit view, then diff against reports A and B for (a) factual accuracy, (b) claim->evidence citation discipline, (c) scoped language, (d) interpretation depth (proximity insight, corroboration decomposition, leading indicators).

## Determinism
No randomness; fixed timestamps (run window 2026-06-11 07:00 UTC). Regeneration is byte-identical, so the bundle hash is a stable test vector.
