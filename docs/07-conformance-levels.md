# Conformance Levels & Implementation Profiles

> **Status: in development - Roadmap P4.** This stub states intended scope so reviewers can challenge the plan before the text lands. Comments welcome via the issue templates.
>
> **Authority:** this document is the **normative home** for the SE-C ladder and implementation profiles once filled. The root [`CONFORMANCE.md`](../CONFORMANCE.md) is the operator / worked guide (Golden Trace corpus verification vs emitter claims). Until this stub is replaced, treat SE-C language in CONFORMANCE.md as illustration only.

The graded ladder - SE-C0 schema-valid - SE-C1 execution-traceable - SE-C2 authority-evidenced - SE-C3 topology-evidenced - SE-C4 assurance-report-capable - SE-C5 lossless-pipeline-capable (append-only persistence before ACK, idempotency, replay, DLQ, deterministic rebuild) - and the orthogonal implementation profiles (minimum emitter, connector, audit-grade, security telemetry, AI context, data lineage, platform substrate). Includes the anti-sampling rule for commit-boundary streams and the aggregate-pattern reporting rule.

**Related programme work:** a distinct **control-re-evaluable** claim surface (beyond "authority fields present" / SE-C2) is tracked as CRE-011 in [`registers/three-layer-evidence-and-control-reevaluation.md`](../registers/three-layer-evidence-and-control-reevaluation.md) - not yet part of this ladder text.
