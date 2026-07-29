# Three-layer evidence coverage (informative)

> **Status: informative - not normative.** Does not freeze fields, schemas, or conformance levels. Programme: [D-014 / TRK-024](../../registers/three-layer-evidence-and-control-reevaluation.md). Doctrine: AXES is the **evidence lane** ([docs/01](../01-doctrine-and-non-negotiables.md) §5) - it records what happened under claimed authority; it does not enforce policy, issue authorization tokens, or certify compliance.

### Coming from AGT [#276](https://github.com/microsoft/agent-governance-toolkit/discussions/276)?

That discussion converged on three bound views of one action - **Decision**, **Control-in-force**, and **Outcome** - plus the separate need for byte-identity proof (not only a named canonicalisation rule). This page is AXES's informative reading of that split in the evidence lane only. Schema stays unfrozen; nothing here claims an SE-Cx level. Watchable follow-ups: [#4](https://github.com/magentixai/axes/issues/4) (EB-004), [#5](https://github.com/magentixai/axes/issues/5) (P1-1), [#6](https://github.com/magentixai/axes/issues/6) (conformance vectors / canoncheck-class), [#7](https://github.com/magentixai/axes/issues/7) (interop field lists).

## The three layers

Accountable autonomous execution needs three bound evidence views of the same action:

| Layer | Reader question | AXES coverage today |
|---|---|---|
| **L1 - Decision** | What was decided before consequence, on what observed basis? | **Substantial** - pre-commit envelopes (`policy_check_performed`, approval kinds) with control checks and assertion basis |
| **L2 - Control-in-force** | Which exact controls evaluated that decision, and can they be re-run? | **Partial** - versioned refs and recorded results; not yet a content-addressed control-context snapshot (GAP-EXEC-021) |
| **L3 - Outcome** | What became real, under the same action identity? | **Substantial** - commit-boundary envelopes, acknowledgment ladder (rungs may accrete later), artefact refs |

AXES answers these with **append-only envelopes** over time, not three fields on one object. One action typically yields several envelopes on a shared correlation spine.

## Field map (Golden Trace dialect)

Illustrative keys from [`examples/golden-trace/out/samples/`](../../examples/golden-trace/out/samples/). Catalogue modules will freeze canonical keys; until then treat names as working-draft.

### L1 - Decision (pre-execution)

| Concern | Working keys / location |
|---|---|
| Lifecycle moment | `event_kind: policy_check_performed` (also approval request/grant kinds) |
| Phase | `execution_phase: approval` (or equivalent pre-commit phase) |
| Who / under what delegation | `authority.authority_context_id`, `delegation_receipt_id`, `delegator_id`, `capability_id` |
| Human approval question | `authority.approval_status`, `approval_basis` |
| Control evaluation recorded | `controls.control_evaluation_phase`, `controls.checks[]` (`control_id`, `control_result`, observed values) |
| Epistemic basis | `evidence_quality.assertion_basis` (e.g. `observed`), `evidence_origin`, `corroboration_state` |
| Capture posture | `emission.capture_layer`, `capture_status`, `emission_fail_posture` |

Exemplar: [`envelope_payment03_policy_check.json`](../../examples/golden-trace/out/samples/envelope_payment03_policy_check.json).

### L2 - Control-in-force (at decision time)

| Concern | Working keys / location | Gap |
|---|---|---|
| Policy identity | `authority.policy_ref`, `authority.policy_version` | Version **label**, not snapshot bytes |
| Control set identity | `controls.control_set_ref` | Same |
| Per-check evidence pointers | `checks[].evidence_ref` (e.g. supplier master) | Pointers without required digests of the full control-context set |
| Effective dating | Discussed in vocab merge (`effective_from` / `effective_until`) | Not yet consistently on Golden Trace envelopes |

**What independent re-evaluation still needs** (CRE-* in the programme tracker): a content-addressed **control-context** (policy + permissions + reference-data digests), an **evaluated-input digest**, binding of `(input digest, control-context digest, decision outcome)` inside envelope hash scope, a declared **evaluation profile** (external engine - AXES does not interpret policy languages), and a **reproducible vs observed_only** rule for checks. Until those land, do not claim that `policy_version` alone meets a re-evaluation bar.

### L3 - Outcome (post-execution)

| Concern | Working keys / location |
|---|---|
| Commit | `event_kind: commit_succeeded` / `commit_failed`; `operation.commit_boundary_status`, `commit_mechanism`, `commit_impact_class` |
| Result | `result.result_status`, `side_effect_confirmation_status` |
| External corroboration | `acknowledgments[]` (transport / protocol / business rungs; settlement may arrive on a later reconciliation envelope - GT-003) |
| Artefacts | `ack_artifact_ref` + `ack_artifact_hash`; bundle `artifacts/` + `manifest.json` |

Exemplar: [`envelope_payment03_commit_succeeded.json`](../../examples/golden-trace/out/samples/envelope_payment03_commit_succeeded.json); settlement accretion: [`envelope_reconciliation.json`](../../examples/golden-trace/out/samples/envelope_reconciliation.json).

## Binding: correlation spine vs action digest

| Mechanism | Role today |
|---|---|
| `trace_id`, `span_id`, `parent_span_id`, `transaction_ref`, typed `correlation_keys[]` | **Correlation spine** - join L1/L2/L3 envelopes for one payment/action |
| Content-addressed action key (e.g. digest over canonical action preimage) | **Pending** P1-1 / Module 14 - do not equate correlation with cryptographic decision↔outcome binding |

## Custody and faithful capture (out of scope for this page)

Sealed, canonical bytes prove integrity **after** capture. They do not by themselves prove the runtime faithfully recorded what it evaluated, nor that the bytes existed at a wall-clock time independent of the emitter. Basis fields (`assertion_basis`, `capture_layer`) and attestation/custody work address the first; **external existence bounds** (`anchoring.*`, TRK-001 / EB-*) address the second. Golden Trace v1's SIMULATED anchor must not be read as closing that bound (D-015). See [`x402-and-anchoring.md`](x402-and-anchoring.md) and programme item CRE-D01 / EB-*.

## Related

- Programme tracker and acceptance test for L2 closed: [`registers/three-layer-evidence-and-control-reevaluation.md`](../../registers/three-layer-evidence-and-control-reevaluation.md)
- x402 composition + EvidenceAnchor SPI posture: [`x402-and-anchoring.md`](x402-and-anchoring.md)
- Operator conformance guide: [`CONFORMANCE.md`](../../CONFORMANCE.md)
- Normative ladder (stub): [`docs/07-conformance-levels.md`](../07-conformance-levels.md)
- Module map: [`docs/04-module-map.md`](../04-module-map.md)
