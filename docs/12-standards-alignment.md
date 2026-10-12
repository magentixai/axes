# Standards Alignment

> **Status: in development - Roadmap P4.** This stub states intended scope so reviewers can challenge the plan before the text lands. Comments welcome via the issue templates.

Normative profiling statements for adjacent standards (see registers/adjacent-standards-watch.md for the live watch): W3C Trace Context compatibility, JCS, JWS/COSE, RFC 3161, SCITT, W3C VC, ISO 20022 acknowledgment-scheme mapping registry, OTel mapping, ISO/IEC 42001 / NIST AI RMF evidence support, x402 action-receipt / evidence-record composition, AGT EvidenceAnchor as an anchoring-backend profile (not an AXES runtime dependency), Microsoft Agent 365 / Purview as adjacent governance surfaces (import map only; not substitutes for SE).

Informative interop notes (non-normative): [`docs/interop/x402-and-anchoring.md`](interop/x402-and-anchoring.md) (incl. SCITT profile rules), [`docs/interop/three-layer-evidence-coverage.md`](interop/three-layer-evidence-coverage.md), [`docs/interop/agent365-purview-se-mapping.md`](interop/agent365-purview-se-mapping.md). Magentix AI ARBITR commercial positioning lives outside this open repo.

## Cross-layer field spelling

A field's **key** takes the convention of its document: the x402 wire layer is camelCase; the AXES evidence layer is `lower_snake`. A field's **concept** is the interoperable unit. A registry declares both spellings and never derives one from the other. Camel-to-snake transforms are ambiguous at digit boundaries and acronyms; ISO 20022 stores abbreviations in the repository at design time rather than deriving them.

This is not tidiness. Under RFC 8785 JCS, two spellings sort to different positions, producing different canonical bytes, different digests, and two content identities. Designed exception: a relying-party-scoped identifier (`identifier_scope: relying_party_pairwise`) legitimately produces different digests at different relying parties (Module 01; docs/06 §2.11).

## EU AI Act and harmonised standards (position statement)

AXES does not compete with the EU AI Act's harmonised standards (CEN-CENELEC JTC 21) and does not claim conformity with anything. The relationship is complementary and deliberate: **harmonised standards describe what compliant controls should achieve; AXES describes how evidence of autonomous execution can be recorded, preserved and transported consistently across runtimes** so that organisations can populate and defend the runtime evidence those standards and the Act's record-keeping, oversight, transparency and incident provisions expect. Regulation-sourced requirements are traced as EU-* rows in the requirements register; the canonical core stays regulation-neutral, with regulatory surfaces carried by conditional profiles (decision D-013).
