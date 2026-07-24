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
| **x402 (Linux Foundation)** | Agentic payments protocol; offer-receipt; action-receipt proposal ([#2906](https://github.com/x402-foundation/x402/issues/2906)) uses JWS + RFC 8785; correctness/dispute thread ([#2887](https://github.com/x402-foundation/x402/issues/2887)) converges on evidence-capture before adjudication/enforcement | Complementary (D-015) - x402 settles; AXES evidences authority/execution/outcome. Action-receipt ≈ acknowledgment-ladder rung. Do not collapse "paid" with "correct". Interop note: [`docs/interop/x402-and-anchoring.md`](../docs/interop/x402-and-anchoring.md) |
| **Microsoft Agent Control Specification** | Agent governance/control | Differentiate - control/enforcement lane; AXES is the evidence lane |
| **AGT EvidenceAnchor SPI** ([agent-governance-toolkit PR #2244](https://github.com/microsoft/agent-governance-toolkit/pull/2244)) | Runtime plugin ABC: `anchor` / `verify` for external existence bounds on evidence digests; `action_ref` canonicalisation; backends (WORM, Rekor, on-chain plugins) | Profile receipt semantics into SE `anchoring.*` (D-015). AXES standard does **not** implement the Python ABC; emitters/connectors may. Orthogonal to control re-evaluation (GAP-EXEC-021). Note: x402 issue #2244 is a different topic |
| **Agent governance evidence discussions** (e.g. microsoft/agent-governance-toolkit discussions on policy enforcement vs decision evidence) | Convergence on three bound artifacts: pre-execution decision, control-in-force at decision time, post-execution outcome | Differentiate + map - enforcement/runtime governance stays adjacent; AXES maps as evidence coverage only (D-014). L2 re-evaluation requires content-addressed control-context (GAP-EXEC-021), not version strings alone. Tracker: [`three-layer-evidence-and-control-reevaluation.md`](three-layer-evidence-and-control-reevaluation.md) |
| **[CrossMsg-Signing](https://github.com/magentixai/CrossMsg-Signing)** (steward prior art, Apache-2.0) | Cross-format (XML↔JSON) selective-scope signing of ISO 20022 business content; JCS+JWS vs XML C14N vs detached-hash comparison | Adopt as P1-1 spike input - JCS baseline evidence, declared-hash-scope concept, ack-ladder cross-syntax test vectors (see docs/09) |
