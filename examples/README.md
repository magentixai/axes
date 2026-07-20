# Examples

## `golden-trace/` — the canonical end-to-end bundle

A complete, deterministic, re-verifiable evidence bundle: an autonomous AP agent executing 14 SEPA Instant payments under delegated authority AD-7844. 76 hash-chained envelopes, 29 ISO 20022 artefacts, an evidence-bundle manifest, and four target reports (board / audit / regulator / forensic) in which every sentence resolves to named fields in named envelopes. `python3 generate_golden_trace.py` regenerates it byte-identically and re-verifies the chain. See its README for what is real vs stubbed (stubs are disclosed — that discipline is itself part of the standard).

## Single-envelope examples (validate against the historical draft schema)

- `openclaw-file-write.json` — a local-runtime file-write execution event
- `langgraph-crm-update.json` — an orchestrated CRM record update crossing a commit boundary
