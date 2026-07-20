# AXES Doctrine and Non-Negotiables

This document is normative for the design process: every proposal, field and vocabulary is tested against it. Changes to this document require a decision-register entry.

## 1. What AXES is

AXES (Autonomous eXecution Evidence Standard) defines portable, tamper-evident, board-readable **evidence of autonomous execution**. Its unit of capture is **delegated execution**: an actor (human or system) has delegated authority to an autonomous process, and the process has taken actions under that authority. The evidence artefact is the **Standards Envelope (SE)**: an atomic, append-only execution-evidence event.

AXES is deliberately **not**:

- **not logging or observability** - logs serve engineers debugging software; AXES serves accountability for consequences
- **not a policy or blocking engine** - it evidences what happened; it never enforces
- **not an identity system** - it references and evidences identity and authority; it does not issue them
- **not a runtime or a payment rail**
- **not a compliance certificate** - conformant evidence supports scoped assurance statements; it certifies nothing

## 2. The governing design rule

> **A competent third party should be able to generate a credible, structured, board-readable assurance report from the open schema alone.** Implementations should generate a better one - through superior interpretation, topology reconstruction, control mapping, exception analysis, report design and context - from the same evidence.

If outsiders cannot build a credible report from the open schema, the industry has no reason to adopt it. The standard is therefore designed **report-backwards**: four target outputs (A: board assurance summary · B: audit and control view · C: regulator / external assurance pack · D: forensic execution pack) come first, and every field must trace to a report statement. *No report line without supporting fields; no schema field without report, audit, topology, authority, integrity or implementation value.*

## 3. Non-negotiables

1. **Append-only.** Envelopes are never edited. Corrections are new envelopes (`supersedes_envelope_id`, `amendment_reason`). This is an admissibility requirement, not a style choice.
2. **Pointers and hashes only.** No raw payloads, diffs, screenshots or secrets are persisted in envelopes. Evidence artefacts are referenced by URI + hash, with declared classification, redaction and retention.
3. **Fact separated from interpretation.** Every value carries its provenance (origin, epistemic basis, corroboration state). The schema never encodes speculative judgement as fact - there is no `agent_intent: trusted`; there is observed divergence, with confidence, and a review recommendation.
4. **Evidence gaps are disclosed, never hidden.** Completeness is measured against a declared population, not asserted. Silence has defined semantics (heartbeats + sequence continuity + emission fail-posture). `outside_capture_boundary` is an honest disclosure, not a failure.
5. **Authority is first-class.** Who delegated what, to whom, under which scope, valid when, revocable how - evidenced on every consequential action, including the human-approval question (required? present? how quickly granted?).
6. **The commit boundary is the pivot.** Advisory activity and real consequences are structurally distinct. Commit events carry mechanism, impact class, reversibility, and external corroboration (the acknowledgment ladder - rungs accrete across envelopes over time).
7. **Cross-boundary evidence navigates, never merges.** Journeys crossing providers, tenants or liability domains link by continuation references; storage-level trace merging across domains is prohibited.
8. **Canonical keys are immutable.** Renaming inside the envelope is prohibited. Display naming for audiences is a presentation-layer concern outside the standard.
9. **Vendor and runtime neutrality.** Every element must be emittable or mappable by any serious runtime, framework or connector. Conformance is defined by the public spec, validator and test vectors - never by any vendor's ingestion behaviour.
10. **Scoped assurance language only.** No element or definition may imply "compliant", "safe", "legally defensible" or "guaranteed". Assurance statements carry basis, confidence, limitations and reliance boundary.
11. **Privacy by design.** Personal data travels by reference with pseudonymous subject keys - never embedded. This applies to *all* human references (approvers, operators, customers, employees): execution evidence must not become a surveillance system. Envelope immutability coexists with erasure via crypto-shredding of referenced content (`content_erased` resolution).
12. **No mandatory hidden chain-of-thought.** Model behaviour is evidenced through prompt/context references and hashes, guardrail results, evaluations and behaviour summaries - deliberately not through compelled capture of hidden reasoning.
13. **Per-action conformance is not assurance.** A sequence of individually valid envelopes can evidence a harmful aggregate pattern. Report profiles must include aggregate-pattern analysis or disclose its absence as a limitation.
14. **Adversarial threat model.** The schema records claimed authority, evidence, boundaries, assertions and confidence. It does not prove an agent was trustworthy, and it must remain useful when the agent - or the emitter - is the adversary.

## 4. The four-layer architecture

| Layer | Contents | Status |
|---|---|---|
| **Open SE envelope** (`se.*`) | Raw, canonical evidence - this standard's core | Open, normative |
| **Derived report layer** (`derived.*`) | Values computed from envelopes, traceable to them; a basic open annex is part of the standard | Open (annex) + implementation |
| **Interpretation layer** (`arbitr.*` et al.) | Scoring, narratives, prioritisation, benchmarks | Implementation territory |
| **Presentation layer** (`view.*`) | Audience terminology, labels, report layout | Implementation territory |

Extensions are namespaced, declared, and must never override canonical fields; `must_understand` and `unknown_field_policy` govern safe processing of unknown content.

## 5. Category discipline

AXES occupies one lane: **the neutral evidence and interpretation-substrate layer for autonomous execution**. Runtime hardening, commit-time enforcement, compliance-coded blocking and payment execution are adjacent lanes occupied by others; the standard does not drift into them, however tempting richer semantics make it.

## 6. The depth position - why AXES is a deep schema

Messaging-standard history teaches a reflex: find the minimum viable field set, mark everything else optional, implement the least you can get away with. That reflex made sense when every field cost human implementation effort and the payload's reader was a human or a hand-written parser. Three things break the reflex for execution evidence:

1. **Evidence cannot be retrofitted.** In a payments message, an unimplemented optional field costs a feature you can add next release. In evidence, an uncaptured field costs *the past*: when the incident, audit or dispute arrives, the envelope you didn't emit cannot be re-emitted. The regret is asymmetric - over-capture costs storage; under-capture costs the answer. Depth is the rational default wherever consequence is possible.
2. **The implementer is increasingly a machine.** Connectors, mappings and emitters are now substantially AI-built, and both the marginal cost of emitting a rich envelope and the cost of the tokens and compute behind it are falling year on year. The historical price of depth - human engineering effort per field - is decaying; the value of depth (leading indicators, aggregate patterns, corroboration decomposition, proximity-to-limit measures) only exists if the fields exist.
3. **The rich readings are the point.** Nearly everything the six audiences valued most lives beyond a minimal envelope: authority-utilisation proximity rather than pass/fail, acknowledgment-ladder corroboration rather than self-assertion, population-measured completeness rather than asserted coverage, aggregate-pattern analysis rather than per-action validity. A minimum-viable evidence schema produces minimum-viable assurance - which no board, auditor or regulator actually wants.

**Depth is not mandatory weight.** The counterpart discipline that keeps depth adoptable: a small mandatory core; modules that become required only when the facts trigger them (cross a commit boundary → commit module required; touch personal data → privacy module required); a graded conformance ladder so partial depth is honestly claimable and weak implementations cannot claim full equivalence; implementation profiles as a staged on-ramp; and a published evidence cost model so depth is priced openly rather than discovered painfully. Lightness is an on-ramp, never the destination - and the standard says so out loud.

The ISO 20022 migrations taught the underlying lesson: when a rich standard is adopted minimum-viably (like-for-like, structured data stripped), the industry waits a decade for benefits it had already paid for. The failure was never that the schema was too deep; it was that depth was priced, staged and argued for badly. AXES prices it, stages it, and argues for it here.
