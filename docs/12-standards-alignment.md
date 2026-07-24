# Standards Alignment

> **Status: in development - Roadmap P4.** This stub states intended scope so reviewers can challenge the plan before the text lands. Comments welcome via the issue templates.

Normative profiling statements for adjacent standards (see registers/adjacent-standards-watch.md for the live watch): W3C Trace Context compatibility, JCS, JWS/COSE, RFC 3161, SCITT, W3C VC, ISO 20022 acknowledgment-scheme mapping registry, OTel mapping, ISO/IEC 42001 / NIST AI RMF evidence support, x402 action-receipt / evidence-record composition, AGT EvidenceAnchor as an anchoring-backend profile (not an AXES runtime dependency).

Informative interop notes (non-normative): [`docs/interop/x402-and-anchoring.md`](interop/x402-and-anchoring.md), [`docs/interop/three-layer-evidence-coverage.md`](interop/three-layer-evidence-coverage.md).

## EU AI Act and harmonised standards (position statement)

AXES does not compete with the EU AI Act's harmonised standards (CEN-CENELEC JTC 21) and does not claim conformity with anything. The relationship is complementary and deliberate: **harmonised standards describe what compliant controls should achieve; AXES describes how evidence of autonomous execution can be recorded, preserved and transported consistently across runtimes** so that organisations can populate and defend the runtime evidence those standards and the Act's record-keeping, oversight, transparency and incident provisions expect. Regulation-sourced requirements are traced as EU-* rows in the requirements register; the canonical core stays regulation-neutral, with regulatory surfaces carried by conditional profiles (decision D-013).
