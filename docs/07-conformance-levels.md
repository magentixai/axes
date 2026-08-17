# Conformance Levels & Implementation Profiles

> **Status: in development - Roadmap P4.** This stub states intended scope so reviewers can challenge the plan before the text lands. Comments welcome via the issue templates.
>
> **Authority:** this document is the **normative home** for the SE-C ladder and implementation profiles once filled. The root [`CONFORMANCE.md`](../CONFORMANCE.md) is the operator / worked guide (Golden Trace corpus verification vs emitter claims). Until this stub is replaced, treat SE-C language in CONFORMANCE.md as illustration only.

The graded ladder - SE-C0 schema-valid - SE-C1 execution-traceable - SE-C2 authority-evidenced - SE-C3 topology-evidenced - SE-C4 assurance-report-capable - SE-C5 lossless-pipeline-capable (append-only persistence before ACK, idempotency, replay, DLQ, deterministic rebuild) - and the orthogonal implementation profiles (minimum emitter, connector, audit-grade, security telemetry, AI context, data lineage, platform substrate). Includes the anti-sampling rule for commit-boundary streams and the aggregate-pattern reporting rule.

**Identifier attribution (consumer rule).** A consumer MUST attribute only on identifiers whose `verification_status` meets its stated threshold. Unverified identifiers are recorded but are not attributable. A derivation asked to attribute value to a party whose only matching identifier is `unverified` MUST return `underivable_unverified_identifier` rather than a value. A conformance predicate MUST NOT be bound to one identity syntax; unparseable identifiers yield `verification_unavailable`, never a false-negative reject.

**SE-C4 testability (DPR-011).** "Assurance-report-capable from the open evidence alone" becomes mechanical only against a named, versioned, digest-pinned derivation profile (DPR-* in the requirements register). This document does not award SE-C4, or any SE-Cx badge, to any implementation. Nothing may claim SE-C0 or any SE-Cx badge before a published schema and public vectors exist ([`CONFORMANCE.md`](../CONFORMANCE.md)).

**Related programme work:** a distinct **control-re-evaluable** claim surface (beyond "authority fields present" / SE-C2) is tracked as CRE-011 in [`registers/three-layer-evidence-and-control-reevaluation.md`](../registers/three-layer-evidence-and-control-reevaluation.md) - not yet part of this ladder text.
