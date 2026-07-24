# AXES Roadmap & Maturity Register

**Posture:** publish breadth early, govern maturity visibly. The full conceptual scope is public from this first draft; each area carries an explicit maturity state below rather than being hidden until "ready". This register is updated with every substantive merge.

## Where the standard is now

The corpus behind this draft: a six-audience requirements programme (executive/board, business process owners, internal assurance, technical, external assurance, standards/ecosystem - 58 roles surveyed across six independent model runs each, then compressed and gap-analysed), a cross-wave vocabulary harmonisation pass, a programme blind-spots review, and a working end-to-end evidence bundle (the Golden Trace). All of it is traceable in [`registers/requirements-register.md`](registers/requirements-register.md). Requirements are tagged *persona-derived, pending human confirmation*; human design-partner validation is a scheduled phase, not an afterthought. Active evidence-coverage workstream: [three-layer evidence & control re-evaluation](registers/three-layer-evidence-and-control-reevaluation.md) (D-014).

## Phase status

| Phase | Delivers | Status |
|---|---|---|
| **P0 - Foundations** | Doctrine, governance, licences & patent pledge, contribution pipeline, registers, Golden Trace published | ✅ This release |
| **P1 - Pre-schema design decisions** | (1) canonicalisation incl. field-level redaction-tolerant hashing · (2) append-only amendment model · (3) access & restriction model · (4) receipt-slot / acknowledgment-ladder structure · (5) IPR posture | (5) ✅ decided (see PATENTS.md) · (2)(3)(4) drafted in corpus, normative text in progress · (1) open spike - **gates schema freeze** |
| **P2 - Field catalogue** | 16-module catalogue: per-field descriptors, canonical keys, maturity labels, requirement traceability; decision register populated module-by-module | **Started - Module 01 (Envelope Core) draft published**; Module 06 (Commit Boundary & Consequence) next |
| **P3 - Schema regeneration** | Modular `se-v0.1.schema.json` + `.yaml` generated from the catalogue; examples revalidated; byte-level canonicalisation test vectors seeded from the Golden Trace; third-party report test executed and published (can an independent party produce a credible report from the open bundle alone?) | Blocked on P1(1) + P2 |
| **P4 - Standards package** | Conformance levels & profiles, extension/namespace model, canonicalisation spec, access & restriction model, threat model, standards-alignment doc, implementation guidance, evidence cost model, open reference validator | Partial drafts |
| **P5 - Candidate draft & human validation** | v0.1.0 Candidate tag; 3–5 human design partners (external audit, insurance, payment operations) reviewing the *reports*, with a published divergence log; adversarial persona review (attacker, opposing counsel, respondent org, affected individual). **Recruiting now - see the Call for Review in the README**; design partners receive named acknowledgement in the candidate draft and their reactions drive the divergence log | Planned - **open for volunteers today** |
| **P6 - Ecosystem** | Framework fit matrix (OpenAI, Bedrock, Copilot, Salesforce, MCP, coding agents, …); second independent implementation (venue-incubation trigger); interactive schema explorer | Planned |

## Module maturity snapshot

Sixteen modules make up the envelope architecture (full map: [docs/04-module-map.md](docs/04-module-map.md)). Current states:

| Module | State |
|---|---|
| 1 Envelope Core | **Catalogue DRAFT published** (docs/05, 23 entries) - open for challenge |
| 5 Target/Operation · 9 Evidence Artifact Refs | Stable draft (exercised by Golden Trace + archived sketch) |
| 3 Authority & Delegation · 6 Commit Boundary & Consequence · 7 Topology & Lineage · 10 Evidence Quality · 14 Integrity/Hashing/Signature | Strong draft - catalogue formalisation pending |
| 2 Actor/Agent/Model/Runtime · 8 Boundary Entry/Exit · 12 Risk/Control/Exception · 16 Reportability | Draft |
| 4 Capability & Scope · 11 Behaviour Expectation & Security Signals · 13 Data/Privacy/Classification · 15 Attestation | Draft - vocabulary harmonisation applied, review wanted |
| Silence semantics (heartbeats · sequence continuity · emission fail-posture) | Adopted cluster, catalogue entry pending |
| Acknowledgment ladder & receipts · external anchoring · correlation keys · amendment model | Adopted by multi-wave convergence; normative wording in P1/P2 |
| Verifiable agent identity (`agent_identity_assertion_ref`) | Experimental |

## Active workstream: three-layer evidence coverage & control re-evaluation (D-014)

External governance discussions converge on three bound artifacts - pre-execution **decision**, **control specification in force**, post-execution **outcome** - keyed to one action. AXES responds in the **evidence lane only** (doctrine §5).

| Band | Goal | Status |
|---|---|---|
| **A - Surfacing (TLC-*)** | Working envelope shape in README; informative three-layer coverage note with L2 gap disclosed; CONFORMANCE.md that separates corpus verification from SE-Cx claims; legacy example quarantine | ✅ TLC-001..007 landed 2026-07-24 |
| **B - Control re-evaluation (CRE-*)** | Content-addressed control-context snapshot + evaluated-input digest + effective dating + evaluation-profile neutrality + Golden Trace v2 re-run proof + distinct conformance surface | Open - blocked on catalogue drafts + P1-1 for hashed binding; composition/field design may proceed in parallel |

Full task list and acceptance test: [`registers/three-layer-evidence-and-control-reevaluation.md`](registers/three-layer-evidence-and-control-reevaluation.md). Umbrella tracker: TRK-024 / GAP-EXEC-021.

**Catalogue sequencing note:** Module 06 (Commit Boundary) remains next for the general catalogue; CRE field drafts for Modules 03/04/12 may proceed in parallel provided they do not freeze hash structure before P1-1.

## Known limitations of this draft (disclosed, not hidden)

- **There is no published JSON Schema yet - deliberately.** The schema freezes only after the canonicalisation decision (P1-1); publishing before it would guarantee a breaking revision. The only prior schema artefact is a May 2026 exploratory sketch, archived with honest commentary in `archive/2026-05-ingest-draft/` - it is design history, not the standard.
- Requirements derive from multi-model persona simulation - a strong hypothesis generator, not human validation. P5 exists precisely to correct this, and is recruiting now.
- Canonicalisation (including redaction-tolerant hashing) is the one genuinely open core-design question; the schema will not freeze before it is settled.
- The Golden Trace is a **v1 working exemplar**: its hash chain, sequencing, artefact hashes and coverage arithmetic are real and re-verifiable, but its signatures are stubbed (disclosed) and its hashing is informal. Golden Trace v2 regenerates it under the settled canonicalisation and seeds the byte-level test vectors.
- **Control-in-force evidence is partial:** envelopes carry `policy_ref` / `policy_version` / `control_set_ref` and recorded check results; they do not yet carry a content-addressed control-context snapshot sufficient for independent re-evaluation (GAP-EXEC-021).
