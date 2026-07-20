# AXES Roadmap & Maturity Register

**Posture:** publish breadth early, govern maturity visibly. The full conceptual scope is public from this first draft; each area carries an explicit maturity state below rather than being hidden until "ready". This register is updated with every substantive merge.

## Where the standard is now

The corpus behind this draft: a six-audience requirements programme (executive/board, business process owners, internal assurance, technical, external assurance, standards/ecosystem — 58 roles surveyed across six independent model runs each, then compressed and gap-analysed), a cross-wave vocabulary harmonisation pass, a programme blind-spots review, and a working end-to-end evidence bundle (the Golden Trace). All of it is traceable in [`registers/requirements-register.md`](registers/requirements-register.md) — 251 rows. Requirements are tagged *persona-derived, pending human confirmation*; human design-partner validation is a scheduled phase, not an afterthought.

## Phase status

| Phase | Delivers | Status |
|---|---|---|
| **P0 — Foundations** | Doctrine, governance, licences & patent pledge, contribution pipeline, registers, Golden Trace published | ✅ This release |
| **P1 — Pre-schema design decisions** | (1) canonicalisation incl. field-level redaction-tolerant hashing · (2) append-only amendment model · (3) access & restriction model · (4) receipt-slot / acknowledgment-ladder structure · (5) IPR posture | (5) ✅ decided (see PATENTS.md) · (2)(3)(4) drafted in corpus, normative text in progress · (1) open spike — **gates schema freeze** |
| **P2 — Field catalogue** | 16-module catalogue: per-field descriptors, canonical keys, maturity labels, requirement traceability; decision register populated module-by-module | In progress — modules ship as individual commits |
| **P3 — Schema regeneration** | Modular `se-v0.1.schema.json` + `.yaml` generated from the catalogue; examples revalidated; byte-level canonicalisation test vectors seeded from the Golden Trace; third-party report ("moat") test executed and published | Blocked on P1(1) + P2 |
| **P4 — Standards package** | Conformance levels & profiles, extension/namespace model, canonicalisation spec, access & restriction model, threat model, standards-alignment doc, implementation guidance, evidence cost model, open reference validator | Partial drafts |
| **P5 — Candidate draft & human validation** | v0.1.0 Candidate tag; 3–5 human design partners (external audit, insurance, payment operations) reviewing the *reports*, with a published divergence log; adversarial persona review (attacker, opposing counsel, respondent org, affected individual) | Planned |
| **P6 — Ecosystem** | Framework fit matrix (OpenAI, Bedrock, Copilot, Salesforce, MCP, coding agents, …); second independent implementation (venue-incubation trigger); interactive schema explorer | Planned |

## Module maturity snapshot

Sixteen modules make up the envelope architecture (full map: [docs/04-module-map.md](docs/04-module-map.md)). Current states:

| Module | State |
|---|---|
| 1 Envelope Core · 5 Target/Operation · 9 Evidence Artifact Refs | Stable draft (exercised by Golden Trace + historical schema) |
| 3 Authority & Delegation · 6 Commit Boundary & Consequence · 7 Topology & Lineage · 10 Evidence Quality · 14 Integrity/Hashing/Signature | Strong draft — catalogue formalisation pending |
| 2 Actor/Agent/Model/Runtime · 8 Boundary Entry/Exit · 12 Risk/Control/Exception · 16 Reportability | Draft |
| 4 Capability & Scope · 11 Behaviour Expectation & Security Signals · 13 Data/Privacy/Classification · 15 Attestation | Draft — vocabulary harmonisation applied, review wanted |
| Silence semantics (heartbeats · sequence continuity · emission fail-posture) | Adopted cluster, catalogue entry pending |
| Acknowledgment ladder & receipts · external anchoring · correlation keys · amendment model | Adopted by multi-wave convergence; normative wording in P1/P2 |
| Verifiable agent identity (`agent_identity_assertion_ref`) | Experimental |

## Known limitations of this draft (disclosed, not hidden)

- The published JSON Schema is the **historical ingest draft** (~25 fields); it undersells the module architecture and will be superseded by the catalogue-derived schema in P3. It is retained so early implementers have something concrete to validate against today.
- Requirements derive from multi-model persona simulation — a strong hypothesis generator, not human validation. P5 exists precisely to correct this.
- Canonicalisation (including redaction-tolerant hashing) is the one genuinely open core-design question; the schema will not freeze before it is settled.
- Envelope signatures in the Golden Trace are stubbed and disclosed as such; the hash chain, sequencing, artefact hashes and coverage arithmetic are real and re-verifiable.
