# Canonicalisation, Hashing & Amendment

> **Status: P1-1 canonical byte form decided (2026-08-03).** Field-level redaction-tolerant hashing and the full amendment model remain in progress. See [ROADMAP](../ROADMAP.md) P1/P3.

## Normative canonical form

**RFC 8785 (JSON Canonicalization Scheme, JCS)** is the normative canonical byte form for AXES envelope hashing and signing.

Requirements (RFC 8785 section 3.2):
- ECMAScript-compliant number serialisation (integral floats become integers in canonical form).
- UTF-8 output with no ASCII escaping of Unicode.
- Member keys sorted by UTF-16 code units.

The Golden Trace v2 generator implements JCS via the vetted [`jcs`](https://pypi.org/project/jcs/) Python package (`tools/axes_canonical.py`). Conformance vectors under [`vectors/`](../vectors/) pin expected canonical bytes and SHA-256 digests for cross-language verification (canoncheck layout, axes#6).

## Hash scope

The hash input is the envelope with these fields **removed**:
- `integrity.envelope_hash`
- `integrity.envelope_signature` (`integrity.signature` in gt-v2.0, renamed in gt-v2.1 under D-024; see [docs/19](19-key-change-index.md))

Everything else in the envelope at emission time is in scope, including `integrity.signing_key_id`, `integrity.signing_key_provenance_ref`, and `envelope_id` (assigned before hashing). This boundary is enforced in `examples/golden-trace/generate_golden_trace.py`.

## Digest (declared, agile)

The Golden Trace v2 generator emits **SHA-256** over the canonical bytes. SHA-256 is a declared mechanism choice, not a hard-coded sole permitted digest in the spec text. Other implementations may use a different agile digest (for example keccak256) over the **same** RFC 8785 bytes and remain conformant on byte identity; only the digest algorithm label differs.

`integrity.hash_algorithm` records the mechanism used for that envelope.

## Numeric representation (no JSON floats in hash scope)

One rule governs every quantity in the hash-scoped record:

> No JSON floats. Every quantity is exact and integer-based, with one canonical form per numeric kind.

### Amount

Any asset-denominated value (money, limits) uses the `Amount` type ([`schema/amount.schema.json`](../schema/amount.schema.json)):

```json
{
  "value": "2390000",
  "decimals": 2,
  "asset": "iso4217:EUR"
}
```

- `value` is a string of base-10 integer atomic units (clears the 2^53 JSON-number ceiling).
- `decimals` and `asset` are declared explicitly; never inferred at read time.
- `asset` is a **namespaced string**: fiat as `iso4217:<CODE>` (e.g. `iso4217:EUR`); crypto as `caip19:<CAIP-19 asset id>` (e.g. USDC on Base). The Amount type is asset-agnostic; the financial Golden Trace uses EUR, and conformance vectors include a USDC (`decimals` = 6) example.
- Money is not stored as JSON floats or fixed-precision decimal strings in hash scope. ISO 20022 allows five fraction digits in some paths; AXES uses integer atomic units with declared scale instead of decimalising money (ISO 4217 minor units for fiat).

### Ratio

Where a ratio must live in-record, use exact rationals ([`schema/ratio.schema.json`](../schema/ratio.schema.json)):

```json
{"numerator": "2390000", "denominator": "2500000"}
```

**Default:** derived ratios (`authority_utilisation_ratio`, `evidence_coverage_ratio`, `batch_limit_utilisation_ratio`, and similar) are **not** stored in the hash-scoped envelope. The assurance-report layer computes them from `Amount` operands for display.

### Bounded dimensionless config parameters

Model and config parameters such as `temperature` and `top_p` are neither money nor ratios. They are carried as **exact decimal strings** (for example `"0.7"`, `"0.179"`) to leave the JSON-float domain without inventing a third numeric kind.

## Derived values in the report layer

Assurance reports may render utilisation percentages, coverage ratios, and proximity bands from integer operands. Those renderings are outside the hash scope unless explicitly encoded as `Amount` or `Ratio` facts.

## Prior art

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

**Independent convergence (2026-07/08):** MarkovianProtocol (canoncheck) and Tersign (@wowlegend) measured GT-JCS-0 divergence from RFC 8785 and the residual fractional-float hazard; byte-identity vector methodology recorded in [`registers/decision-register.md`](../registers/decision-register.md).

## Still open under P1-1

- Field-level redaction-tolerant hashing (salted per-field vs Merkle-structured).
- Unknown-field treatment beyond `must_understand`.
- Full amendment model normative text.

