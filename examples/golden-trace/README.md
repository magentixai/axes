> **Status: Golden Trace v2 working exemplar and test corpus - not normative.** Regenerated 2026-08-03 under the P1-1 canonicalisation ruling (RFC 8785 JCS, integer Amount fields, no JSON floats in hash scope). v1 preserved under [`../../archive/golden-trace-v1-fin/`](../../archive/golden-trace-v1-fin/). Signatures remain stubs; anchor store simulated pending EB-004 confirmation on axes#3.

# SE v0.1 Golden Trace v2 - APRUN-2026-06-09-A (Pristine Variant)

A fully synthetic, deterministic, end-to-end Agentic Execution Evidence trace for the canonical ARBITR scenario, built report-backwards so that **every sentence of the board-grade promise paragraph resolves to named schema fields in named envelopes**:

> *"An authorised autonomous process executed 14 payment instructions under delegated authority AD-7844. All payments remained within approved policy boundaries. No exceptions requiring human intervention occurred. Evidence integrity validated. No cross-tenant data exposure detected."*

## Scenario
**Caldera Robotics Ltd** (fictional, non-regulated mid-size manufacturer) runs an autonomous AP agent that pays 14 approved supplier invoices by SEPA Instant credit transfer under delegated authority **AD-7844** (CFO → agent; EUR 25,000/payment; EUR 150,000/batch; approved-beneficiary list; no human approval required within limits). The ISO 20022 flow follows the instant-payments message pattern: the agent's instruction (pain.001) → interbank leg (pacs.008, **outside the declared capture boundary** - disclosed, evidenced indirectly) → bank status report (**pacs.002 ACSC**) → end-of-day statement (**camt.053**) for reconciliation.

The pristine variant deliberately exercises the hard machinery through *positive* evidence rather than exceptions:
- **42 pre-commit control evaluations** (approved-beneficiary, per-payment limit, duplicate-idempotency × 14), all passed - prevention evidence, not post-hoc logging
- **Three-rung acknowledgment ladder** per payment (transport HTTPS / protocol ACCEPTED / business pacs.002 ACSC) + **settlement rung** via camt.053 - external confirmation, not self-assertion
- **Measured completeness**: independently reconciled population (ERP queue 14 due + bank statement 14 booked) → coverage 14/14, with `population_basis: independently_reconciled`
- **Silence semantics**: heartbeats every 60s (zero silent windows) + `emission_fail_posture: fail_closed` ⇒ absence of evidence = absence of action within the boundary
- **External anchoring** every 300s (simulated store, real chain-head hashes) + final export anchor
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

## What is real vs stubbed
**Real and re-verifiable:** SHA-256 hash chain over **RFC 8785 JCS** canonical JSON (`canonicalisation_version: RFC8785-JCS`; `envelope_hash` and `signature` excluded from hash input; signing-key identity *included*), contiguous sequencing, time ordering, artifact hashes, manifest/bundle hash, integer `Amount` monetary fields (EUR ISO4217 minor units, `decimals: 2`), zero JSON floats in hash scope. On anchor envelopes, `anchoring.chain_head_hash` is the real local chain head at that moment.

**Stubbed and disclosed as such:** envelope signatures (`SIG-STUB`); the external anchor store (`anchoring_method: "write_once_store (SIMULATED)"`, demo `anchor_store_ref`); webhook mTLS authenticity of pacs.002. Real `distributed_ledger` anchor (EB-004) pending giskard09 confirmation on axes#3. The reports disclose every stub - practising the scoped-assurance language the standard mandates.

**Reading rule for anchors (D-015):** `evidence_quality.corroboration_state: externally_anchored` on a SIMULATED method must **not** be treated as an independently verifiable existence bound.

## Verify it yourself
```bash
pip install -r requirements-dev.txt
python3 generate_golden_trace.py
python3 ../../tools/generate_conformance_vectors.py
```
Regenerates everything and re-verifies the chain (asserts on failure, including zero-float check). Byte-level vectors land in [`../../vectors/`](../../vectors/). The vendor-neutral manual procedure is in `report_D_forensic.md` section 1.

## v1 → v2 hash changes
All 76 envelope hashes changed from v1 (GT-JCS-0 + JSON floats) to v2 (RFC 8785 JCS + Amount fields). This is expected and is the substance of the P1-1 ruling (axes#6). v1 bytes are preserved under [`../../archive/golden-trace-v1-fin/`](../../archive/golden-trace-v1-fin/).

## Determinism
No randomness; fixed timestamps (run window 2026-06-09 09:00 UTC). Regeneration is byte-identical on any platform (manifest file list is sorted lexicographically).
