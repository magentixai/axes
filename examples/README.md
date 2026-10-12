# Examples

Two complete, deterministic, re-verifiable Golden Trace bundles share the **same evidence skeleton** (76 hash-chained envelopes, heartbeats, simulated anchors, four role-specific reports, manifest). Only the domain and artifact standards differ - proving sector flexibility without normative schema claims.

**Status (both):** Golden Trace **v2** (2026-08) - RFC 8785 JCS, no JSON floats in hash scope. Financial Amounts use `iso4217:EUR` (decimals=2); crypto Amounts (`caip19:…` USDC decimals=6) are exercised in [`../vectors/`](../vectors/). v1 corpora archived under [`../archive/golden-trace-v1-fin/`](../archive/golden-trace-v1-fin/) and [`../archive/golden-trace-v1-ind/`](../archive/golden-trace-v1-ind/).

Operator verification vs conformance claims: [`../CONFORMANCE.md`](../CONFORMANCE.md).

---

## Financial services - `golden-trace/` (Fin)

An autonomous AP agent executing 14 SEPA Instant payments under delegated authority AD-7844. 29 ISO 20022 artefacts (pain.001, pacs.002, camt.053). Run reference **APRUN-2026-06-09-A**.

```bash
pip install -r requirements-dev.txt
python3 generate_golden_trace.py
```

---

## Industrial and manufacturing - `golden-trace-ind/` (Ind)

An autonomous production release agent dispositioning 14 units of IMP-4471 rev D under delegated authority MD-5120. 31 manufacturing stand-ins (QIF 3.0, MES release, B2MML, MTConnect, EN 10204 material cert). Run reference **MRUN-2026-06-11-A**.

```bash
pip install -r requirements-dev.txt
python3 generate_golden_trace.py
```

---

## Legacy dialect - `legacy/`

Pre-catalogue single-envelope examples (`version: se.v1.draft`) live in [`legacy/`](legacy/). They are design history aligned with the archived May 2026 sketch - **not** the current working envelope shape. Do not implement against them.
