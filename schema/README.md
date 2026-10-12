# Schema

The modular, catalogue-derived `se-v0.1.schema.json` + `.yaml` land here per [ROADMAP](../ROADMAP.md) Phase 3 - generated from the field catalogue, after the canonicalisation decision (P1-1), which is the one gate that prevents an immediate breaking revision of anything published here.

**P1-1 progress (2026-08-03):** canonical byte form and numeric kinds are settled and exercised by Golden Trace v2. Partial JSON Schema for the closed numeric kinds is published now:

| File | Purpose |
|---|---|
| [`amount.schema.json`](amount.schema.json) | Integer atomic units for asset-denominated quantities |
| [`ratio.schema.json`](ratio.schema.json) | Exact rationals when a ratio must live in hash scope |

The full envelope schema remains blocked on redaction-tolerant hashing and catalogue completion.

**Why is the full schema not populated yet?** Deliberately. Freezing a JSON Schema before field-level redaction hashing and receipt structure are settled would force a breaking v0.2 within weeks. The architecture the schema will express is fully public today: the [module map](../docs/04-module-map.md), the [controlled vocabularies](../docs/06-controlled-vocabularies.md), the [requirements register](../registers/requirements-register.md), the [canonicalisation spec](../docs/09-canonicalisation-and-hashing.md), and the working [Golden Trace v2](../examples/golden-trace/) envelopes.

A first exploratory sketch from May 2026 exists in [`archive/2026-05-ingest-draft/`](../archive/2026-05-ingest-draft/) - preserved as design history with an honest account of why it was insufficient. Golden Trace v1 (GT-JCS-0) is archived under [`archive/golden-trace-v1-fin/`](../archive/golden-trace-v1-fin/).
