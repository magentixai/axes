# Adjacent Standards Watch

One page, reviewed periodically. For each adjacent effort: **profile** (adopt/reference it) or **differentiate** (state why AXES diverges). AXES prefers profiling existing primitives over reinventing them (REQ-STD-022).

| Standard / effort | Relationship | Decision posture |
|---|---|---|
| **W3C Trace Context** | Trace identity propagation | Profile - SE trace identity SHOULD be Trace Context compatible (GAP-TECH-014) |
| **OpenTelemetry (incl. GenAI semantic conventions)** | Telemetry/observability | Differentiate + map - observability serves engineers; AXES serves accountability. Publish a mapping, never merge concerns |
| **JSON Schema 2020-12** | Schema language | Adopt |
| **RFC 8785 (JCS)** | JSON canonicalisation | Profile candidate - baseline for the canonicalisation spike (P1-1) |
| **JWS / COSE** | Signatures | Profile for envelope/bundle signing |
| **RFC 3161 (TSA)** | Trusted timestamps | Profile - external anchoring module (`anchoring_method: timestamp_authority`) |
| **IETF SCITT** | Transparency/countersigning | Profile candidate for anchoring + receipts |
| **W3C Verifiable Credentials** | Attestations, delegation receipts, agent identity | Profile candidate - `agent_identity_assertion_ref` carrier |
| **ISO 20022** | Payments messaging | Map - acknowledgment-ladder scheme mapping registry (pain.001/pacs.002/camt.053 exercised in the Golden Trace) |
| **C2PA** | Content provenance | Watch - artefact-provenance analogies; different subject matter |
| **SPDX / SBOM** | Category-defining precedent + component provenance | Watch; naming/adoption model reference |
| **ISO/IEC 42001, NIST AI RMF** | AI management/risk frameworks | Map - evidence supports their control expectations; AXES certifies nothing |
| **OWASP agentic security work** | Threat taxonomies | Feed threat model (docs/11) |
| **EU AI Act (Reg. 2024/1689, as amended by the 2026 Digital Omnibus)** | Regulatory demand-side: Art 12 logging/traceability, Art 14 oversight, Art 26 deployer log custody (>=6 months), Art 50 transparency (applies 2026-08-02), serious-incident reporting | Map - EU-001..009 in the requirements register; field slots open, article mapping implementation-layer (D-013). Re-verify dates against Council/Commission pages before public citation |
| **CEN-CENELEC JTC 21 harmonised standards** | EU AI Act presumption-of-conformity standards (risk management, logging, oversight, QMS, post-market monitoring) | Position AXES as complementary: harmonised standards describe what compliant controls should achieve; AXES describes how evidence of autonomous execution is recorded and transported across runtimes. Monitor drafts; profile where they land |
| **x402 (Linux Foundation)** | Agentic payments protocol; Signed Offers & Receipts extension; action-receipt proposal (#2906) notably adopts JWS + RFC 8785 - the same canonicalisation baseline as AXES P1-1 | Complementary - x402 standardises how agents pay; AXES standardises evidence that execution (incl. payment) was authorised, in-scope and properly executed. Lifecycle hooks are a natural emission point |
| **Microsoft Agent Control Specification** | Agent governance/control | Differentiate - control/enforcement lane; AXES is the evidence lane |
| **[CrossMsg-Signing](https://github.com/magentixai/CrossMsg-Signing)** (steward prior art, Apache-2.0) | Cross-format (XML↔JSON) selective-scope signing of ISO 20022 business content; JCS+JWS vs XML C14N vs detached-hash comparison | Adopt as P1-1 spike input - JCS baseline evidence, declared-hash-scope concept, ack-ladder cross-syntax test vectors (see docs/09) |
