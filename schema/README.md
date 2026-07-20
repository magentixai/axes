# Schema

## `se-v0.1-draft.schema.json` — historical ingest draft (superseded in progress)

This is the original single-envelope ingest contract (May 2026, ~25 fields). It is **retained deliberately** so early implementers have something concrete to validate against today, and both `examples/*.json` single-envelope examples validate against it.

It predates the six-audience requirements programme and **undersells the current architecture** — the 16-module map, two-axis commit boundaries, acknowledgment ladder, provenance axes and conformance ladder are documented in `docs/` and the registers. The modular, catalogue-derived `se-v0.1.schema.json` + `.yaml` replace this file in Roadmap P3, after the canonicalisation decision (P1-1) — the one gate that prevents an immediate breaking revision.

Validation example:

```bash
pip install jsonschema
python3 -m jsonschema -i ../examples/openclaw-file-write.json se-v0.1-draft.schema.json
```
