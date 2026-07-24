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
| **C - External existence bound (EB-*)** | Mechanism-agnostic `anchoring_method` vocabulary; profile SCITT / RFC 3161 / OTS / EvidenceAnchor receipts into `anchoring.*` (AXES does not implement runtime ABCs); Golden Trace v2 real anchor; reject SIMULATED overclaim | EB-001 ✅; EB-002..005 open - see detail below |

Full task list and acceptance test: [`registers/three-layer-evidence-and-control-reevaluation.md`](registers/three-layer-evidence-and-control-reevaluation.md). Umbrella tracker: TRK-024 / GAP-EXEC-021. SCITT composition rules: [`docs/interop/x402-and-anchoring.md`](docs/interop/x402-and-anchoring.md) (SCITT section).

**Catalogue sequencing note:** Module 06 (Commit Boundary) remains next for the general catalogue; CRE field drafts for Modules 03/04/12 and EB field drafts for Module 14 may proceed in parallel provided they do not freeze hash structure before P1-1.

### Band C detail - SCITT and peers (from AGT #276 alignment)

| Requirement | Roadmap treatment |
|---|---|
| Separate envelope digest from notarization | Normative in Module 14: register **digests** (envelope / bundle / export), never raw payloads |
| SCITT as profile, not core schema | EB-003: map Transparency Service id, statement digest, receipt, inclusion proof, verify path → `anchoring.*`; `anchoring_method` includes `transparency_log` / SCITT instance |
| Pluggable backends | EB-002: SCITT peer to RFC 3161, OpenTimestamps, Rekor-like logs, WORM+verify, chain registries - MUST NOT hard-require SCITT |
| Ack-ladder placement | P1-4 / Module 06: SCITT receipt = higher corroboration rung; must not verify as business/settlement ack |
| Optional pre/post registration | Same action key may be anchored at decision and at outcome (GT-003 accretion) |
| Explicit non-goals | SCITT does not close CRE-* (control re-evaluation) or CRE-D01 (faithful capture) |

### Ecosystem / Magentix implementation (feeds P6)

| Item | Status |
|---|---|
| Agent 365 / Purview → SE field map | ✅ Informative draft [`docs/interop/agent365-purview-se-mapping.md`](docs/interop/agent365-purview-se-mapping.md) |
| Positioning brief (independence argument) | ✅ Draft [`docs/interop/agent365-arbitr-brief.md`](docs/interop/agent365-arbitr-brief.md) |
| **BLD-031** ARBITR import pack (Agent 365 OTel + Purview audit → SE) | Raised - implementation layer |

## Known limitations of this draft (disclosed, not hidden)

- **There is no published JSON Schema yet - deliberately.** The schema freezes only after the canonicalisation decision (P1-1); publishing before it would guarantee a breaking revision. The only prior schema artefact is a May 2026 exploratory sketch, archived with honest commentary in `archive/2026-05-ingest-draft/` - it is design history, not the standard.
- Requirements derive from multi-model persona simulation - a strong hypothesis generator, not human validation. P5 exists precisely to correct this, and is recruiting now.
- Canonicalisation (including redaction-tolerant hashing) is the one genuinely open core-design question; the schema will not freeze before it is settled.
- The Golden Trace is a **v1 working exemplar**: its hash chain, sequencing, artefact hashes and coverage arithmetic are real and re-verifiable, but its signatures are stubbed (disclosed) and its hashing is informal. Golden Trace v2 regenerates it under the settled canonicalisation and seeds the byte-level test vectors.
- **Control-in-force evidence is partial:** envelopes carry `policy_ref` / `policy_version` / `control_set_ref` and recorded check results; they do not yet carry a content-addressed control-context snapshot sufficient for independent re-evaluation (GAP-EXEC-021).
- **External existence bound is stubbed in Golden Trace v1:** `anchoring_method: write_once_store (SIMULATED)` - local `chain_head_hash` is real; third-party existence verify is not. Do not read `corroboration_state: externally_anchored` on a simulated method as a closed bound (D-015 / EB-*). See [`docs/interop/x402-and-anchoring.md`](docs/interop/x402-and-anchoring.md).
