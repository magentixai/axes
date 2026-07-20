# AXES Doctrine and Non-Negotiables

This document is normative for the design process: every proposal, field and vocabulary is tested against it. Changes to this document require a decision-register entry.

## 1. What AXES is

AXES (Autonomous eXecution Evidence Standard) defines portable, tamper-evident, board-readable **evidence of autonomous execution**. Its unit of capture is **delegated execution**: an actor (human or system) has delegated authority to an autonomous process, and the process has taken actions under that authority. The evidence artefact is the **Standards Envelope (SE)**: an atomic, append-only execution-evidence event.

AXES is deliberately **not**:

- **not logging or observability** — logs serve engineers debugging software; AXES serves accountability for consequences
- **not a policy or blocking engine** — it evidences what happened; it never enforces
- **not an identity system** — it references and evidences identity and authority; it does not issue them
- **not a runtime or a payment rail**
- **not a compliance certificate** — conformant evidence supports scoped assurance statements; it certifies nothing

## 2. The governing design rule

> **A competent third party should be able to generate a credible, structured, board-readable assurance report from the open schema alone.** Implementations should generate a better one — through superior interpretation, topology reconstruction, control mapping, exception analysis, report design and context — from the same evidence.

If outsiders cannot build a credible report from the open schema, the industry has no reason to adopt it. The standard is therefore designed **report-backwards**: four target outputs (A: board assurance summary · B: audit and control view · C: regulator / external assurance pack · D: forensic execution pack) come first, and every field must trace to a report statement. *No report line without supporting fields; no schema field without report, audit, topology, authority, integrity or implementation value.*

## 3. Non-negotiables

1. **Append-only.** Envelopes are never edited. Corrections are new envelopes (`supersedes_envelope_id`, `amendment_reason`). This is an admissibility requirement, not a style choice.
2. **Pointers and hashes only.** No raw payloads, diffs, screenshots or secrets are persisted in envelopes. Evidence artefacts are referenced by URI + hash, with declared classification, redaction and retention.
3. **Fact separated from interpretation.** Every value carries its provenance (origin, epistemic basis, corroboration state). The schema never encodes speculative judgement as fact — there is no `agent_intent: trusted`; there is observed divergence, with confidence, and a review recommendation.
4. **Evidence gaps are disclosed, never hidden.** Completeness is measured against a declared population, not asserted. Silence has defined semantics (heartbeats + sequence continuity + emission fail-posture). `outside_capture_boundary` is an honest disclosure, not a failure.
5. **Authority is first-class.** Who delegated what, to whom, under which scope, valid when, revocable how — evidenced on every consequential action, including the human-approval question (required? present? how quickly granted?).
6. **The commit boundary is the pivot.** Advisory activity and real consequences are structurally distinct. Commit events carry mechanism, impact class, reversibility, and external corroboration (the acknowledgment ladder — rungs accrete across envelopes over time).
7. **Cross-boundary evidence navigates, never merges.** Journeys crossing providers, tenants or liability domains link by continuation references; storage-level trace merging across domains is prohibited.
8. **Canonical keys are immutable.** Renaming inside the envelope is prohibited. Display naming for audiences is a presentation-layer concern outside the standard.
9. **Vendor and runtime neutrality.** Every element must be emittable or mappable by any serious runtime, framework or connector. Conformance is defined by the public spec, validator and test vectors — never by any vendor's ingestion behaviour.
10. **Scoped assurance language only.** No element or definition may imply "compliant", "safe", "legally defensible" or "guaranteed". Assurance statements carry basis, confidence, limitations and reliance boundary.
11. **Privacy by design.** Personal data travels by reference with pseudonymous subject keys — never embedded. This applies to *all* human references (approvers, operators, customers, employees): execution evidence must not become a surveillance system. Envelope immutability coexists with erasure via crypto-shredding of referenced content (`content_erased` resolution).
12. **No mandatory hidden chain-of-thought.** Model behaviour is evidenced through prompt/context references and hashes, guardrail results, evaluations and behaviour summaries — deliberately not through compelled capture of hidden reasoning.
13. **Per-action conformance is not assurance.** A sequence of individually valid envelopes can evidence a harmful aggregate pattern. Report profiles must include aggregate-pattern analysis or disclose its absence as a limitation.
14. **Adversarial threat model.** The schema records claimed authority, evidence, boundaries, assertions and confidence. It does not prove an agent was trustworthy, and it must remain useful when the agent — or the emitter — is the adversary.

## 4. The four-layer architecture

| Layer | Contents | Status |
|---|---|---|
| **Open SE envelope** (`se.*`) | Raw, canonical evidence — this standard's core | Open, normative |
| **Derived report layer** (`derived.*`) | Values computed from envelopes, traceable to them; a basic open annex is part of the standard | Open (annex) + implementation |
| **Interpretation layer** (`arbitr.*` et al.) | Scoring, narratives, prioritisation, benchmarks | Implementation territory |
| **Presentation layer** (`view.*`) | Audience terminology, labels, report layout | Implementation territory |

Extensions are namespaced, declared, and must never override canonical fields; `must_understand` and `unknown_field_policy` govern safe processing of unknown content.

## 5. Category discipline

AXES occupies one lane: **the neutral evidence and interpretation-substrate layer for autonomous execution**. Runtime hardening, commit-time enforcement, compliance-coded blocking and payment execution are adjacent lanes occupied by others; the standard does not drift into them, however tempting richer semantics make it.
