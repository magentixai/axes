# Governance

## Steward

AXES is created and stewarded by **Magentix** (magentix.ai). Stewardship means: maintaining this repository, running the contribution process below, publishing versioned drafts, and funding the reference tooling. It does not mean privileged semantics: **conformance to AXES is defined by the published specification, the public validator and the public test vectors - never by the ingestion behaviour of any vendor's product, including Magentix's own ARBITR.**

## The open / proprietary boundary (stated plainly)

The open standard defines **evidence capture** and **evidence semantics**: the envelope, its modules, controlled vocabularies, canonicalisation and hashing, conformance levels, the extension model, the minimum assurance-report profile, an open annex of basic derived fields, the reference emitter/validator, and test vectors.

Evidence **interpretation** - scoring, narrative generation, report design, exception prioritisation, terminology mapping, benchmarking, client-specific control mappings - is implementation territory, where vendors (Magentix included, via ARBITR) compete. The standard is generous enough to be useful without any vendor; implementations must earn preference on interpretation quality alone.

## Decision process

1. **Proposals** are made as GitHub issues using the category templates (see CONTRIBUTING.md). Substantive spec changes arrive as pull requests referencing an accepted proposal.
2. **Assessment** follows the fixed question set in CONTRIBUTING.md, applied in the open on the issue thread.
3. **Decisions** are recorded in [`registers/decision-register.md`](registers/decision-register.md) with one of: `accept-core`, `accept-conditional`, `accept-recommended`, `experimental`, `derived-only`, `implementation-layer`, `presentation-only`, `defer`, `reject`. **Every deferral and rejection records its reason.** Nothing is deleted, only staged.
4. **Canonical keys are immutable** once published at `core` or `conditional` maturity. Renames are prohibited; deprecation with a successor key is the only path. Display naming is a presentation-layer concern outside this standard.
5. **Versioning:** working drafts iterate as v0.x with a changelog entry per merged change. Breaking changes to hashed structure or canonicalisation require a minor version and migration notes. The internal target for a stable release is SE v1.
6. Maintainers are listed in this file's history; the initial maintainer is the steward. Additional maintainers are appointed on demonstrated contribution.

## Venue path (declared intent)

The steward's declared intent is to bring AXES to a recognised standards venue (e.g. a Linux Foundation project, IETF, or equivalent) for incubation **once a second independent implementation exists** (an emitter or consumer not built by Magentix that passes the public test vectors). Early incubation conversations are welcome sooner. This commitment is coupled to the IPR posture in PATENTS.md: the royalty-free pledge and the venue path stand together.

Recognition matters beyond adoption: portable execution evidence has evidentiary value in audit, regulatory and legal settings partly through recognition of the standard it conforms to. Publishing openly, with a public verification procedure, is a deliberate step on that path.

## Conduct

Be professional, specific and generous. Critique designs, not people. Maintainers may moderate contributions that are off-topic, promotional, or repetitive.
