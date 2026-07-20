# Examples

## `golden-trace/` — the canonical end-to-end bundle (v1 working exemplar)

A complete, deterministic, re-verifiable evidence bundle: an autonomous AP agent executing 14 SEPA Instant payments under delegated authority AD-7844. 76 hash-chained envelopes, 29 ISO 20022 artefacts, an evidence-bundle manifest, and four target reports (board / audit / regulator / forensic) in which every sentence resolves to named fields in named envelopes. `python3 generate_golden_trace.py` regenerates it byte-identically and re-verifies the chain.

**Status:** this is a *v1 working exemplar and test corpus* — scaffolding to make the machinery concrete, not a normative artefact. Its hashing is informal (its own build caught two silent hash-scope mistakes — exactly the class of bug the canonicalisation decision P1-1 exists to eliminate), and its signatures are stubbed and disclosed as such. **Golden Trace v2** will be regenerated under the settled canonicalisation, with per-profile signatures, and will seed the byte-level test vectors. Treat v1 as the direction of travel, not the destination.

## Single-envelope examples

- `openclaw-file-write.json` — a local-runtime file-write execution event
- `langgraph-crm-update.json` — an orchestrated CRM record update crossing a commit boundary

These validate against the archived May 2026 exploratory sketch (`archive/2026-05-ingest-draft/`) and will be re-issued against the catalogue-derived schema in Roadmap P3.
