# Design history — May 2026 ingest draft (superseded)

> **Status: archived. This is not the AXES schema.** It is preserved as design history because a standard that shows its working earns more trust than one that hides it.

`se-ingest-draft-2026-05.schema.json` was the very first sketch: a ~25-field, single-object SaaS ingest contract written in May 2026, *before* the requirements programme ran. It was a starter-for-six — useful for proving that envelopes could be emitted, validated and ingested at all, and for surfacing repeated fields during early in-house testing — and it was mislabelled "SE v1" at the time with an ambition its content did not remotely justify.

## Why it was insufficient (the honest list)

- **Flat envelope, no module architecture.** The requirements programme produced a 16-module architecture; this draft has none of it.
- **Authority reduced to two strings.** `authority_scope` + optional context — no delegation chain, validity windows, revocation, approval quality, or delegator identity.
- **No commit-boundary model.** A `result_status` enum cannot distinguish advisory activity from irreversible real-world consequence, let alone mechanism vs impact class, reversibility, or external corroboration (the acknowledgment ladder).
- **No provenance semantics.** Nothing distinguishes observed fact from assertion, inference or interpretation — the single most demanded property across every audience surveyed.
- **No evidence-quality model.** Completeness, gaps, capture status, population coverage, silence semantics: all absent.
- **No canonicalisation or hashing rules.** A reserved nullable `signature` field is not an integrity model.
- **No conformance structure, no vocabularies discipline, no amendment model, no privacy-by-reference rules.**

Its one lasting contribution: the append-only, idempotent, pointers-and-hashes, tenant-scoped ingest instincts were correct and survive in the doctrine.

## What replaced it

The six-audience requirements programme (58 roles, six model runs each, compressed, gap-analysed and harmonised — see [`../../registers/requirements-register.md`](../../registers/requirements-register.md)), the [doctrine](../../docs/01-doctrine-and-non-negotiables.md), the 16-module map, and the catalogue-derived modular schema that lands per the [ROADMAP](../../ROADMAP.md) once the canonicalisation decision (P1-1) is settled.

`field-guidance-2026-05.md` is the companion guidance from the same period, archived for the same reason.
