> **Status: Golden Trace v2 working exemplar and test corpus - not normative.** Regenerated 2026-08-07 under the P1-1 canonicalisation ruling (RFC 8785 JCS, no JSON floats in hash scope). v1 preserved under [`../../archive/golden-trace-v1-ind/`](../../archive/golden-trace-v1-ind/). Signatures remain stubs; anchor store simulated pending EB-004 confirmation on axes#3.

# SE v0.1 Golden Trace v2 (Industrial) - MRUN-2026-06-11-A (Pristine Variant)

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

## What is real vs stubbed
**Real and re-verifiable:** SHA-256 hash chain over **RFC 8785 JCS** (`canonicalisation_version: RFC8785-JCS`); measurements and Cpk as exact decimal strings; derived utilisation ratios in the report layer only; zero JSON floats in hash scope.

**Stubbed and disclosed:** envelope signatures (`SIG-STUB`); external anchor store (`write_once_store (SIMULATED)`); QMS/MES authenticity stubs. Real `distributed_ledger` anchor (EB-004) pending giskard09 confirmation on axes#3.

## Verify
```bash
pip install -r requirements-dev.txt
python3 generate_golden_trace.py
```

## Determinism
No randomness; fixed timestamps. Regeneration is byte-identical across platforms (manifest keys sorted, paths use `/`).
