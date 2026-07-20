# Canonicalisation, Hashing & Amendment

> **Status: in development - Roadmap P1/P3.** This stub states intended scope so reviewers can challenge the plan before the text lands. Comments welcome via the issue templates.

THE open core-design question (P1-1) - gates the schema freeze. Scope: canonical byte form (JCS/RFC 8785 baseline candidate), envelope hash scope (Golden Trace finding: signing-key identity inside, hash and signature outside), chain rules, field-level redaction-tolerant hashing (salted per-field vs Merkle), redaction tombstones, unknown-field treatment, the append-only amendment model, and byte-level test vectors seeded from the Golden Trace.

## Prior art and inputs to the P1-1 spike

**Steward prior art - [CrossMsg-Signing](https://github.com/magentixai/CrossMsg-Signing)** (Apache-2.0): a working test suite proving that ISO 20022 payment-message *business content* can be canonicalised and signed such that the signature survives XML↔JSON syntax conversion. It implements and compares three strategies side by side - XML C14N 1.1 + XMLDSig, **RFC 8785 (JCS) + JWS**, and a detached-hash approach - over real pacs.008 content, with a documented Signature Exclusion Principle and a declarative exclusion set for transport-mutable fields. Three things carry over:

1. **JCS + JWS as the canonicalisation baseline** enters the spike as steward-tested evidence over payments-domain content, not just a literature preference. The spike therefore focuses on the *commitment* half of the problem.
2. **Declared hash scope** as a first-class, versioned concept: an explicit machine-readable declaration of what is inside and outside the envelope hash (signature and `envelope_hash` out; recipient-stamped `recorded_at` out; everything else in) - generalising CrossMsg's `ConversionRules` exclusion set, and the systematic fix for the silent hash-scope bugs the Golden Trace build surfaced.
3. **Cross-syntax digest identity** for the acknowledgment ladder, where JSON envelopes bind to ISO 20022 XML artefacts; CrossMsg's canonical-KVP pattern and its XML/JSON sample pairs seed those test vectors.

**A distinction the spec will state explicitly:** *exclusion-at-signing is not redaction-after-signing.* CrossMsg-style scope exclusion leaves excluded fields unauthenticated - correct for transport-mutable fields, wrong for evidence. AXES requires the inverse for sensitive values: committed at emission, selectively **disclosable** later (salted per-field commitments in the SD-JWT tradition, or Merkle-structured envelopes - the spike's remaining decision), so a redacted export still verifies and a tombstone proves presence. The two primitives are complementary and must never be conflated.
