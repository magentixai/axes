# Schema

The modular, catalogue-derived `se-v0.1.schema.json` + `.yaml` land here per [ROADMAP](../ROADMAP.md) Phase 3 — generated from the field catalogue, after the canonicalisation decision (P1-1), which is the one gate that prevents an immediate breaking revision of anything published here.

**Why is this directory not populated yet?** Deliberately. Freezing a JSON Schema before the hash scheme, amendment model, access model and receipt structure are settled would force a breaking v0.2 within weeks — the worst possible signal for an evidence standard. The architecture the schema will express is fully public today: the [module map](../docs/04-module-map.md), the [controlled vocabularies](../docs/06-controlled-vocabularies.md), the [requirements register](../registers/requirements-register.md) and the working [Golden Trace](../examples/golden-trace/) envelopes.

A first exploratory sketch from May 2026 exists in [`archive/2026-05-ingest-draft/`](../archive/2026-05-ingest-draft/) — preserved as design history with an honest account of why it was insufficient. It is not the standard and should not be implemented against.
