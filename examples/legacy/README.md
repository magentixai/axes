# Legacy example dialects (design history)

> **Not the current working envelope shape.** Do not implement against these files.

These single-envelope examples use the May 2026 exploratory ingest dialect (`version: se.v1.draft`, flat field layout). They validate, if at all, against the archived sketch in [`archive/2026-05-ingest-draft/`](../../archive/2026-05-ingest-draft/) - itself design history, not the standard (D-007).

| File | Scenario |
|---|---|
| `openclaw-file-write.json` | Local-runtime file-write execution event |
| `langgraph-crm-update.json` | Orchestrated CRM update crossing a commit boundary |

**Current dialect:** use [`../golden-trace/`](../golden-trace/) samples (`se_version: 0.1-draft`, modular objects). Those examples will be re-issued against the catalogue-derived schema in Roadmap P3 after the P1-1 canonicalisation decision.
