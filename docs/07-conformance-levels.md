# Conformance Levels & Implementation Profiles

> **Status: in development - Roadmap P4.** This stub states intended scope so reviewers can challenge the plan before the text lands. Comments welcome via the issue templates.
>
> **Authority:** this document is the **normative home** for the SE-C ladder and implementation profiles once filled. The root [`CONFORMANCE.md`](../CONFORMANCE.md) is the operator / worked guide (Golden Trace corpus verification vs emitter claims). Until this stub is replaced, treat SE-C language in CONFORMANCE.md as illustration only.

The graded ladder - SE-C0 schema-valid - SE-C1 execution-traceable - SE-C2 authority-evidenced - SE-C3 topology-evidenced - SE-C4 assurance-report-capable - SE-C5 lossless-pipeline-capable (append-only persistence before ACK, idempotency, replay, DLQ, deterministic rebuild) - and the orthogonal implementation profiles (minimum emitter, connector, audit-grade, security telemetry, AI context, data lineage, platform substrate). Includes the anti-sampling rule for commit-boundary streams and the aggregate-pattern reporting rule.

**Identifier attribution (consumer rule).** A consumer MUST attribute only on identifiers whose `verification_status` meets its stated threshold. Unverified identifiers are recorded but are not attributable. A derivation asked to attribute value to a party whose only matching identifier is `unverified` MUST return `underivable_unverified_identifier` rather than a value. A conformance predicate MUST NOT be bound to one identity syntax; unparseable identifiers yield `verification_unavailable`, never a false-negative reject.

**SE-C4 testability (DPR-011).** "Assurance-report-capable from the open evidence alone" becomes mechanical only against a named, versioned, digest-pinned derivation profile (DPR-* in the requirements register). This document does not award SE-C4, or any SE-Cx badge, to any implementation. Nothing may claim SE-C0 or any SE-Cx badge before a published schema and public vectors exist ([`CONFORMANCE.md`](../CONFORMANCE.md)).

**Related programme work:** a distinct **control-re-evaluable** claim surface (beyond "authority fields present" / SE-C2) is tracked as CRE-011 in [`registers/three-layer-evidence-and-control-reevaluation.md`](../registers/three-layer-evidence-and-control-reevaluation.md) - not yet part of this ladder text.

## Requirement profiles and evaluation (normative, WO19)

**Trust is computed, never stored (D-025).** An envelope carries facts and their epistemic status. It never carries a trust, confidence or sufficiency value about itself. A relying party applies a declared, versioned **requirement profile** to a declared **subject**, and the result is an **evaluation record**. There is no trust score anywhere (D-031).

**Conformance statements name both sides (D-027).** A statement of conformance always names the subject digest(s), the requirement profile (`requirement_profile_ref`, version, `requirement_profile_hash`) and the evaluation result. The unqualified phrase "AXES-conformant" is not used.

**Profiles.**
- Format: [`schema/requirement-profile.schema.json`](../schema/requirement-profile.schema.json). Reference profiles are in [`profiles/`](../profiles/).
- A profile is immutable at `id@version`, and its digest is the SHA-256 of its RFC 8785 bytes, computed by the evaluator from the bytes it executed (D-037).
- Reference profiles use the `axes:` namespace. Anyone may publish under their own namespace (D-033).
- Each profile lists `unsettled_question_notes`: the readings it deliberately does not pin.

**Composition (D-034).** A profile may extend others. Strictest wins per requirement. A requirement marked `floor_indicator: true` cannot be relaxed by an extending profile. A conflict is `indeterminate` / `profile_conflict`, never a silent winner.

**Evaluation (D-029, D-036).**
- Each requirement yields one result in the four-state vocabulary (D-023) under AXES key names, with a closed condition (docs/06 §2.13).
- **Overall state:**
  - any requirement `contradicted` gives `contradicted`;
  - otherwise any `indeterminate` or `not_evaluated` gives `indeterminate`;
  - otherwise `verified`.
- `guarantee_type` is `unconditional` only when every result is `verified` with no condition recorded.
- Evaluation is deterministic: no model, no network access, no clock read. External facts enter only as pinned evidence carrying the time the authority answered.
- Two evaluators given the same inputs produce the same `result_core_hash`. Format: [`schema/evaluation-record.schema.json`](../schema/evaluation-record.schema.json).

**Earlier releases.** A subject from an earlier corpus release is read through the key change index (`schema/key-aliases.json`). The evaluation record names the subject release and the translation. Translation is explicit, never silent (D-021).

**Reference evaluator.** `tools/axes_evaluate.py` on `golden-trace-v2`, with two-sided vectors in `vectors/profiles/` and published evaluations of gt-v2.0 in `evaluations/gt-v2.0/`. Under `axes:gt_fin_regulator@1`, gt-v2.0 evaluates `indeterminate`, with exactly two conditions:
- `basis_not_demonstrated`: the signatures are `SIG-STUB`;
- `anchor_insufficient`: the anchor is simulated.

That is the honest result, and it names what gt-v2.1 must fix.
