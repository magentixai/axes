> **Status: v1 working exemplar and test corpus - not normative.** Built to prove the report-backwards machinery end to end and to seed test vectors. It will be regenerated as Golden Trace v2 under the P1-1 canonicalisation decision, with per-profile signatures. Known limitations are disclosed inline below - that disclosure discipline is itself part of the standard.

# SE v0.1 Golden Trace - APRUN-2026-06-09-A (Pristine Variant)

A fully synthetic, deterministic, end-to-end Agentic Execution Evidence trace for the canonical ARBITR scenario, built report-backwards so that **every sentence of the board-grade promise paragraph resolves to named schema fields in named envelopes**:

> *"An authorised autonomous process executed 14 payment instructions under delegated authority AD-7844. All payments remained within approved policy boundaries. No exceptions requiring human intervention occurred. Evidence integrity validated. No cross-tenant data exposure detected."*

## Scenario
**Caldera Robotics Ltd** (fictional, non-regulated mid-size manufacturer) runs an autonomous AP agent that pays 14 approved supplier invoices by SEPA Instant credit transfer under delegated authority **AD-7844** (CFO → agent; €25,000/payment; €150,000/batch; approved-beneficiary list; no human approval required within limits). The ISO 20022 flow follows the instant-payments message pattern: the agent's instruction (pain.001) → interbank leg (pacs.008, **outside the declared capture boundary** - disclosed, evidenced indirectly) → bank status report (**pacs.002 ACSC**) → end-of-day statement (**camt.053**) for reconciliation.

The pristine variant deliberately exercises the hard machinery through *positive* evidence rather than exceptions:
- **42 pre-commit control evaluations** (approved-beneficiary, per-payment limit, duplicate-idempotency × 14), all passed - prevention evidence, not post-hoc logging
- **Three-rung acknowledgment ladder** per payment (transport HTTPS / protocol ACCEPTED / business pacs.002 ACSC) + **settlement rung** via camt.053 - external confirmation, not self-assertion
- **Measured completeness**: independently reconciled population (ERP queue 14 due + bank statement 14 booked) → coverage 14/14, with `population_basis: independently_reconciled`
- **Silence semantics**: heartbeats every 60s (zero silent windows) + `emission_fail_posture: fail_closed` ⇒ absence of evidence = absence of action within the boundary
- **External anchoring** every 300s (simulated store, real chain-head hashes) + final export anchor
- **Proximity, not just pass/fail**: payment 3 at **95.6%** of its limit → surfaces as a leading-indicator observation, not an exception
- **Privacy by reference**: beneficiary/debtor IBANs redacted by hash substitution under a named redaction profile; delegator recorded as pseudonymous key
- **Scoped AI context**: sampling parameters recorded; replay claim scoped ("reproducible in distribution, not in instance"); reasoning artifacts `provider_withheld` - disclosed, never silent

## Contents
```
generate_golden_trace.py     deterministic generator (no dependencies, stdlib only)
out/envelopes.jsonl          76 hash-chained SE envelopes (time-ordered, contiguous sequence)
out/samples/*.json           4 pretty-printed exemplar envelopes
out/artifacts/*.xml          29 ISO 20022 stand-ins (pain.001 ×14, pacs.002 ×14, camt.053)
out/manifest.json            evidence bundle manifest (per-file SHA-256, bundle hash)
out/reports/report_A_board.md       Board assurance summary (claim-cited)
out/reports/report_B_audit.md       Audit & control view
out/reports/report_C_regulator.md   Regulator / external assurance pack
out/reports/report_D_forensic.md    Forensic execution pack (incl. verification procedure)
```

## What is real vs stubbed
**Real and re-verifiable:** SHA-256 hash chain over canonical JSON (sorted keys, compact separators; `envelope_hash` and `signature` excluded from hash input; signing-key identity *included*), contiguous sequencing, time ordering, artifact hashes, manifest/bundle hash, all coverage and utilisation arithmetic. On anchor envelopes, `anchoring.chain_head_hash` is the real local chain head at that moment.
**Stubbed and disclosed as such:** envelope signatures (`SIG-STUB`); the external anchor store (`anchoring_method: "write_once_store (SIMULATED)"`, demo `anchor_store_ref`); webhook mTLS authenticity of pacs.002. The reports disclose every stub - practising the scoped-assurance language the standard mandates.

**Reading rule for anchors (D-015):** `evidence_quality.corroboration_state: externally_anchored` on a SIMULATED method must **not** be treated as an independently verifiable existence bound. A third party cannot verify that the bytes existed unmodified at wall-clock time without trusting the generator. Local chain integrity ≠ external existence. Golden Trace v2 replaces the stub with a real `anchoring_method` instance (see [`docs/interop/x402-and-anchoring.md`](../../docs/interop/x402-and-anchoring.md)).

## Verify it yourself
`python3 generate_golden_trace.py` regenerates everything and re-verifies the chain (asserts on failure). The vendor-neutral manual procedure is in `report_D_forensic.md` §1 - it is executable from the bundle alone, which is the point.

## The third-party report test (next step)
Per the design rule - *a competent third party should be able to generate a credible report from the open schema alone; ARBITR should generate a better one* - the protocol: give a third party (or a different model) only `envelopes.jsonl` + `manifest.json` + `artifacts/` + the draft field definitions, ask for a board summary and an audit view, then diff against reports A and B for (a) factual accuracy, (b) claim→evidence citation discipline, (c) scoped language, (d) interpretation depth (proximity insight, corroboration decomposition, leading indicators). The delta is the measured interpretation value - and the proof that the open schema alone is sufficient for a credible report.

## Schema findings surfaced by building this trace (feed back to the Field Catalogue)
1. `source_system_reconciliation` was needed as an event kind - present in no wave's `event_kind` vocabulary; the reconciliation evidence had no natural home without it.
2. `heartbeat_event` likewise (per the Blind Spots document §4) - confirmed necessary in practice.
3. The acknowledgment ladder fits naturally as an array on the commit-success envelope, with the settlement rung arriving later on the reconciliation envelope - i.e. **the ladder spans envelopes over time**; the catalogue should state that rungs accrete rather than requiring completeness at commit time.
4. Hash-scope discipline matters in practice: the first build accidentally excluded `signing_key_id` from the hashed content and assigned `envelope_id` post-hash - both silently weaken the chain and were caught only by the verifier. This is a concrete argument for the Standards wave's byte-level test vectors, and this trace can seed them.
5. `authority_utilisation_ratio` earns its place immediately: it converts a pass/fail control into a leading indicator (95.6%) the board report can actually use.
6. The interbank pacs.008 leg demonstrates `outside_capture_boundary` as an honest disclosure rather than a gap - the capture-boundary declaration belongs in every regulator pack.

## Determinism
No randomness; fixed timestamps (run window 2026-06-09 09:00 UTC). Regeneration is byte-identical, so the bundle hash is a stable test vector.
