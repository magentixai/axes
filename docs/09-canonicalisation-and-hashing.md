# Canonicalisation, Hashing & Amendment

> **Status: in development - Roadmap P1/P3.** This stub states intended scope so reviewers can challenge the plan before the text lands. Comments welcome via the issue templates.

THE open core-design question (P1-1) - gates the schema freeze. Scope: canonical byte form (JCS/RFC 8785 baseline candidate), envelope hash scope (Golden Trace finding: signing-key identity inside, hash and signature outside), chain rules, field-level redaction-tolerant hashing (salted per-field vs Merkle), redaction tombstones, unknown-field treatment, the append-only amendment model, and byte-level test vectors seeded from the Golden Trace.

## Prior art and inputs to the P1-1 spike

**Steward prior art - [CrossMsg-Signing](https://github.com/magentixai/CrossMsg-Signing)** (Apache-2.0): a working test suite proving that ISO 20022 payment-message *business content* can be canonicalised and signed such that the signature survives XML↔JSON syntax conversion. It implements and compares three strategies side by side - XML C14N 1.1 + XMLDSig, **RFC 8785 (JCS) + JWS**, and a detached-hash approach - over real pacs.008 content. Two contributions carry over, and they are not the same thing (see [docs/09a §3](09a-hash-scope-and-exclusions.md)):

1. **JCS + JWS as the canonicalisation baseline** enters the spike as steward-tested evidence over payments-domain content, not just a literature preference. The spike therefore focuses on the *commitment* half of the problem.
2. **Declared hash scope** as a first-class, versioned concept: an explicit machine-readable declaration of what is inside and outside the envelope hash. This generalises the **declared-field-set discipline** demonstrated by CrossMsg's canonical KVP mapping table (an **inclusion** set: business content extracted into a flat key-value map so document structure and element order never enter the signing material). It does **not** generalise `ConversionRules`, which is a JSON Schema generation and element-transformation configuration and contains no exclusion set for mutable fields. The inclusion-versus-exclusion fork, and why an evidence record defaults to inclusion, is [docs/09a §3](09a-hash-scope-and-exclusions.md).
3. **Cross-syntax digest identity** for the acknowledgment ladder, where JSON envelopes bind to ISO 20022 XML artefacts; CrossMsg's canonical-KVP pattern and its XML/JSON sample pairs seed those test vectors.

**Normative identifier `RFC8785-JCS`.** The Golden Trace corpus and `vectors/expected.json` at `776cc0b` ship `canonicalisation_version: "RFC8785-JCS"`. That string is the registry value. It dereferences to this immutable statement:

- Algorithm: RFC 8785 JSON Canonicalization Scheme (JCS) at its published revision.
- Output: UTF-8 bytes.
- Object members sorted by UTF-16 code unit (RFC 8785 §3.2.3), not by Unicode code point and not by locale collation.
- No Unicode normalisation is applied (RFC 8785 §3.1). NFC and NFD of the same visual key are distinct members.
- Digest algorithm is declared separately (`hash_algorithm`, currently SHA-256) and is **not** implied by this identifier.
- Digest encoding, currently: bare lowercase hex (no algorithm prefix). Encoding is pinned, not assumed.

A second implementer MUST be able to reproduce canonical bytes from this statement alone, without reading generator code. A change in any of those properties is a **new identifier**, never a redefinition of `RFC8785-JCS`. The earlier informal form `RFC8785` is retired.

**A distinction the spec will state explicitly:** *exclusion-at-signing is not redaction-after-signing.* Scope exclusion leaves excluded fields unauthenticated - correct for a self-referential signature, wrong as a way to hide sensitive evidence. AXES requires the inverse for sensitive values: committed at emission, selectively **disclosable** later (salted per-field commitments in the SD-JWT tradition, or Merkle-structured envelopes - the spike's remaining decision), so a redacted export still verifies and a tombstone proves presence. The two primitives are complementary and must never be conflated. Full treatment: [docs/09a](09a-hash-scope-and-exclusions.md).
