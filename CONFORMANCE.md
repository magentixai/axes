# Conformance guide (operator)

> **Authority line:** this file is the **operator / worked guide**. The normative conformance ladder and profiles live in [`docs/07-conformance-levels.md`](docs/07-conformance-levels.md) (Roadmap P4 - currently a stub of intended scope). If the two ever diverge, **docs/07 wins** once it is filled; until then treat SE-C language here as illustration against the Golden Trace corpus only.

**Conformance is defined by this specification, the public validator, and the public test vectors - never by any vendor's ingestion behaviour, including Magentix ARBITR** ([GOVERNANCE.md](GOVERNANCE.md)).

## Two different checks (do not collapse them)

| Check | Question it answers | What passes today |
|---|---|---|
| **Corpus verification** | Is *this* Golden Trace bundle intact and regenerable? | `python3 generate_golden_trace.py` in `examples/golden-trace/`; forensic procedure in `report_D_forensic.md` |
| **Emitter conformance claim** | May an implementation claim SE-Cx or a named profile? | **Almost nothing normative yet** - no frozen JSON Schema (P1-1 gate), no public validator, no byte-level vectors. Do not claim SE-C0 (schema-valid) before `schema/` is published |

**Passing Golden Trace verification is not an SE-Cx conformance claim** (D-008). The Golden Trace is a v1 working exemplar and test corpus.

## Ladder cheat-sheet (SE-C0 → SE-C5)

Intended meanings (normative text pending in docs/07):

| Level | Intent |
|---|---|
| **SE-C0** | Schema-valid envelopes |
| **SE-C1** | Execution-traceable (identity, ordering, sequence) |
| **SE-C2** | Authority-evidenced (delegation, capability, policy/control context) |
| **SE-C3** | Topology-evidenced (lineage, boundaries, continuations) |
| **SE-C4** | Assurance-report-capable from the open evidence alone |
| **SE-C5** | Lossless-pipeline-capable (persist-before-ACK, idempotency, replay, deterministic rebuild) |

Implementation **profiles** (minimum emitter, connector, audit-grade, …) are orthogonal: profile = scope implemented; C-level = completeness achieved.

## Worked illustration: Golden Trace v1

How the corpus *exercises* the ladder - illustration only, not a badge:

| Level | What to look for in the bundle | Caveat |
|---|---|---|
| C0-shaped | Envelopes parse as JSON; core identity fields present (`se_version`, `envelope_id`, `event_kind`, org/tenant/env, times) | Not schema-validated against a published schema |
| C1-shaped | Shared `trace_id`; `span_id` / `parent_span_id`; contiguous `sequence_number`; hash chain | Hashing is informal (`GT-JCS-0`); signatures stubbed |
| C2-shaped | `authority.*` on policy-check and commit envelopes; control checks pre-commit | Control-in-force is versioned refs, not re-evaluable snapshots ([GAP-EXEC-021](registers/requirements-register.md)) |
| C3-shaped | Batch→payment parent spans; boundary and reconciliation events | - |
| C4-shaped | Reports A-D cite named fields in named envelopes | Reports are steward-authored exemplars. The **third-party report test** (independent party, open bundle only) is the real C4 proof and remains a next step - not satisfied by Magentix-authored markdown |
| C5-shaped | Fail-closed emission posture; heartbeats; deterministic regenerate | Pipeline semantics beyond the generator are not fully claimed |

## How to verify the Golden Trace corpus

From `examples/golden-trace/`:

```bash
python3 generate_golden_trace.py
```

The generator regenerates envelopes, artefacts, manifest, and reports, then re-verifies the hash chain (asserts on failure). Manual steps that need only the published bundle are in [`examples/golden-trace/out/reports/report_D_forensic.md`](examples/golden-trace/out/reports/report_D_forensic.md).

Known stubs (disclosed): envelope signatures (`SIG-STUB`), external anchor store, some counterparty authenticity bases. See [`examples/golden-trace/README.md`](examples/golden-trace/README.md).

## Claiming conformance (today)

An emitter **may**:

- Say it emits envelopes in the spirit of the Public Working Draft and Module 01 draft keys
- Point at Golden Trace as an interoperability illustration
- File conformance-test proposals via [CONTRIBUTING.md](CONTRIBUTING.md)

An emitter **must not** (yet):

- Claim "SE-C0 conformant" or any SE-Cx badge without a published schema and public vectors
- Equate "accepted by ARBITR" (or any product) with AXES conformance
- Claim independent **control re-evaluation** from `policy_version` alone (see [three-layer coverage note](docs/interop/three-layer-evidence-coverage.md) and CRE-* tasks)

## Related

- Normative ladder stub: [docs/07-conformance-levels.md](docs/07-conformance-levels.md)
- Three-layer evidence coverage (informative): [docs/interop/three-layer-evidence-coverage.md](docs/interop/three-layer-evidence-coverage.md)
- Programme tracker: [registers/three-layer-evidence-and-control-reevaluation.md](registers/three-layer-evidence-and-control-reevaluation.md)
