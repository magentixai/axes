# Governance

## Steward

AXES is created and stewarded by **Magentix AI** (magentix.ai). Stewardship means: maintaining this repository, running the contribution process below, publishing versioned drafts, and funding the reference tooling. It does not mean privileged semantics: **conformance to AXES is defined by the published specification, the public validator and the public test vectors - never by the ingestion behaviour of any vendor's product, including Magentix AI's own ARBITR.**

## The open / proprietary boundary (stated plainly)

The open standard defines **evidence capture** and **evidence semantics**: the envelope, its modules, controlled vocabularies, canonicalisation and hashing, conformance levels, the extension model, the minimum assurance-report profile, an open annex of basic derived fields, the reference emitter/validator, and test vectors.

Evidence **interpretation** - scoring, narrative generation, report design, exception prioritisation, terminology mapping, benchmarking, client-specific control mappings - is implementation territory, where vendors (Magentix AI included, via ARBITR) compete. The standard is generous enough to be useful without any vendor; implementations must earn preference on interpretation quality alone.

## Decision process

1. **Proposals** are made as GitHub issues using the category templates (see CONTRIBUTING.md). Substantive spec changes arrive as pull requests referencing an accepted proposal.
2. **Assessment** follows the fixed question set in CONTRIBUTING.md, applied in the open on the issue thread.
3. **Decisions** are recorded in [`registers/decision-register.md`](registers/decision-register.md) with one of: `accept-core`, `accept-conditional`, `accept-recommended`, `experimental`, `derived-only`, `implementation-layer`, `presentation-only`, `defer`, `reject`. **Every deferral and rejection records its reason.** Nothing is deleted, only staged.
4. **Canonical keys are immutable** once published at `core` or `conditional` maturity. Renames are prohibited; deprecation with a successor key is the only path. Display naming is a presentation-layer concern outside this standard.
5. **Versioning:** working drafts iterate as v0.x with a changelog entry per merged change. Breaking changes to hashed structure or canonicalisation require a minor version and migration notes. The internal target for a stable release is SE v1.
6. Maintainers are listed in this file's history; the initial maintainer is the steward. Additional maintainers are appointed on demonstrated contribution.

## Venue path (declared intent)

The steward's declared intent is to bring AXES to a recognised standards venue (e.g. a Linux Foundation project, IETF, or equivalent) for incubation **once a second independent implementation exists** (an emitter or consumer not built by Magentix AI that passes the public test vectors). Early incubation conversations are welcome sooner. This commitment is coupled to the IPR posture in PATENTS.md: the royalty-free pledge and the venue path stand together.

Recognition matters beyond adoption: portable execution evidence has evidentiary value in audit, regulatory and legal settings partly through recognition of the standard it conforms to. Publishing openly, with a public verification procedure, is a deliberate step on that path.

### Trigger status (2026-10-10)

The venue-path trigger - a second independent implementation, defined above as an emitter or consumer not built by Magentix AI that passes the public test vectors - is met. Independent third parties have reproduced and checked the published Golden Trace corpus from the specification alone, with no dependency on this repository's tooling:

- argentum-core (giskard09 / Pablo Etcheverry) - `custody-ref` reference implementation and a real on-chain `distributed_ledger` anchor instance; its own content-addressed `-ref` primitives and verifiers run against the corpus. See axes#3.
- evidence-record-conformance (Tersign / Kevin Zhang) - a two-sided conformance verifier for the independence and completeness disqualifications; matches the pinned custody-twin verdicts 2/2. See axes#2 and axes#6.
- canoncheck (MarkovianProtocol / Colin H Winter) - an independent cross-language JCS + SHA-256 byte-identity harness; reproduced the corpus 152/152 at tag `corpus/2026-08-08-gt-v2`. See axes#6.
- proofbundle (b7n0de) - an independent RFC 6962 inclusion recomputation written from the specification; reproduced a checkpoint root from leaf bytes and verified it with third-party witness keys, a flipped payload bit failing inclusion. See b7n0de/proofbundle#7 and [#136](https://github.com/b7n0de/proofbundle/pull/136).

This is a condition on independent implementation, not a claim that AXES is finished or adopted; AXES remains a public working draft that evidences and does not certify. Corpus verification is not an SE-Cx conformance badge (decision D-008), and the witnessed-checkpoint lane currently runs a single log operator - the 4-of-7 external witness quorum detects a silently forked log, it does not remove the fact of one operator. On this basis the steward will open incubation conversations with a recognised standards venue. Per-contribution credits are in registers/decision-register.md and PROVENANCE.md; the implementations are listed in the README.


## Conduct

Be professional, specific and generous. Critique designs, not people. Maintainers may moderate contributions that are off-topic, promotional, or repetitive.
