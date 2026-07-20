# AXES Decision Register

Every accepted, deferred and rejected design element is recorded here with its rationale. Nothing is deleted, only staged. Decision states: `accept-core` · `accept-conditional` · `accept-recommended` · `experimental` · `derived-only` · `implementation-layer` · `presentation-only` · `defer` · `reject`.

IDs reference [`requirements-register.md`](requirements-register.md).

## Programme decisions

| # | Decision | State | Rationale / notes |
|---|---|---|---|
| D-001 | Standard named **AXES — Autonomous eXecution Evidence Standard**; envelope artefact remains **SE (Standards Envelope)** | decided 2026-07-20 | Anchors on autonomous execution (durable superset; agentic is the flagship profile). Canonical keys, `se.*` namespace and SE-C ladder unchanged |
| D-002 | Publish early as **Public Working Draft**; breadth visible, maturity labelled | decided | Prevents market convergence on narrower evidence models; governed openness over polished delay |
| D-003 | IPR: CC-BY-4.0 spec · Apache-2.0 code · royalty-free patent pledge on AXES core · DCO, no assignment | decided 2026-07-20 (wording pending counsel) | GAP-STD-001 / TRK-017 — "the adoption gate". Interpretation layer stays protectable |
| D-004 | Venue path: incubate at a recognised body once a second independent implementation passes the public test vectors | decided | BLD-018; coupled with D-003 |
| D-005 | Reference emitter, validator, test vectors and a basic derived-fields annex are **open**, not proprietary | decided | GAP-STD-002 / TRK-018 — placement correction from the Standards review |
| D-006 | Schema freeze is **gated on the canonicalisation decision** (incl. field-level redaction-tolerant hashing) | decided (sequencing) | TRK-023: freezing first forces a breaking v0.2 |
| D-007 | May 2026 ingest sketch **archived as design history** (`archive/2026-05-ingest-draft/`), removed from `schema/`; its "v1" label recorded as an error of ambition | decided 2026-07-20 | A ~25-field pre-programme sketch must not be readable as "the standard"; showing design history with honest commentary is itself a governance signal |
| D-008 | Golden Trace v1 classed as **working exemplar / test corpus, not normative**; Golden Trace v2 to be regenerated under the settled canonicalisation with per-profile signatures | decided 2026-07-20 | v1's informal hashing and stub signatures are disclosed; its role is to make machinery concrete and seed test vectors |
| D-009 | **JSON-LD posture: compatibility, not dependency.** Publish a versioned, hash-pinned `@context` mapping canonical keys to field-registry IRIs so any envelope can be *interpreted as* JSON-LD; envelopes remain plain JSON; hashing is defined over plain-JSON canonical form; verifiers MUST NOT fetch remote contexts. JSON-LD processing as a normative requirement: **reject** | decided 2026-07-20 (compatibility profile: experimental, P4) | Semantic-web interoperability and knowledge-graph value without the canonicalisation conflict (RDF canonicalisation vs envelope hashing), the implementer burden, or the context-substitution attack surface — an evidence standard cannot let a remote document change what a record means |
| D-010 | **Depth position adopted as doctrine** (docs/01 §6): deep schema, light-touch on-ramp; conditional modules; conformance ladder; published evidence cost model | decided 2026-07-20 | Evidence cannot be retrofitted; the implementer is increasingly a machine; the valued readings live beyond a minimal envelope |
| D-011 | Contribution assessment expanded to **11 fixed questions**, absorbing the programme's 10-point requirements-governance addendum (claim traceability, reliance wording, fact-vs-inference check) | decided 2026-07-20 | The addendum arrived mid-programme; waves 2-6 absorbed it, the Executive wave did not — its dedicated re-pass is tracked as BLD-030 |

## Pre-schema design decisions (the P1 five)

| # | Question | State | Notes |
|---|---|---|---|
| P1-1 | Canonicalisation incl. redaction-tolerant hashing (salted per-field vs Merkle-structured) | **open — active spike** | Golden Trace is the test corpus; JCS (RFC 8785) as baseline profile candidate. GAP-EA-001 / TRK-005 |
| P1-2 | Append-only amendment model (`supersedes_envelope_id`, `amendment_reason`) | accept-core (wording in progress) | GAP-EA-004 / TRK-006; admissibility requirement |
| P1-3 | Access & Restriction Model (redaction escrow + dereference authorisation + finding-level restriction incl. `tipping_off_restricted`) | accept (normative section in progress) | GAP-IA-002 / TRK-004 |
| P1-4 | Receipt slot / acknowledgment ladder (rungs 0–5; outbound receipts; boundary receipts; rungs accrete over time) | accept (structure settled; format spec in progress) | TRK-003; three-perspective validation (demand/legal/supply); GT-003 |
| P1-5 | IPR posture | decided → D-003 | — |

## Settled adoptions (multi-wave convergence — accepted ahead of full catalogue)

| Item | State | Source |
|---|---|---|
| External anchoring module (`external_anchor_ref`, `anchoring_method`, RFC 3161 / SCITT profiling, witness chains, WORM retention proof) | accept-conditional (core at commit boundaries) | TRK-001 — five-wave demand |
| `execution_phase` + `execution_mode` two-field semantics | accept-core | TRK-002 — EA semantics adopted |
| `emission_fail_posture` (`fail_closed` / `fail_open` / `mixed` / `unknown`) | accept-core for commit-boundary classes | TRK-013 — defines the evidentiary meaning of silence |
| Silence-semantics cluster: `heartbeat_event`, `declared_heartbeat_interval`, derived `liveness_status`, silent-window register | accept | BLD-009/025, GT-002 — documented as one story with sequence continuity + fail posture |
| `correlation_keys[]` typed family (counterparty, data_subject pseudonymous, incident, recovery_session, equivalent_input, attack_trace) | accept-core | TRK-010 |
| Two-axis commit boundary: `commit_mechanism` + `commit_impact_class` | accept-core | Harmonisation §2.2 — four wave variants reconciled |
| Three provenance axes: `evidence_origin` / `assertion_basis` / `corroboration_state` (retiring `value_origin_type` as alias) | accept-core | Harmonisation §2.9 |
| `capture_status` incl. `outside_capture_boundary`, `missing_recoverable` / `missing_irrecoverable` | accept-core | Harmonisation §2.9; GT-006 |
| SE-C0→C5 conformance ladder + orthogonal implementation profiles | accept | TRK-019 / SG 10.2 |
| `must_understand` + `unknown_field_policy` extension semantics | accept-core | SG 11.6 — also settles unknown-field hashing treatment |
| Agent disclosure marker (`agent_disclosure_status`) | accept-conditional (counterparty-facing actions) | TRK-009 — cheap to standardise now |
| Commitment/promise evidence cluster (+ `contractual_commitment` commit type) | accept-conditional | TRK-008 — three-wave convergence |
| Findings/Action object (severity, owner, access class, timeframe, lifecycle) | accept (derived layer, open annex) | TRK-007 — five-wave confirmation |
| Sampling-parameters block + "reproducible in distribution, not in instance" replay language | accept-conditional | TRK-014 |
| Approval-quality fields (`approval_requested_at` / `approval_granted_at` → latency) | accept-conditional on approvals | BLD-011 — the rubber-stamp hole |
| `authority_utilisation_ratio` + proximity banding | accept (derived, open annex) | GAP-EXEC-012; GT-005 — pass/fail → leading indicator |
| Event kinds `source_system_reconciliation`, `heartbeat_event`, authority lifecycle (`authority_granted/revoked/suspended`), `containment_action`, `redaction_applied`, `trace_continuation_declared` | accept into canonical `event_kind` merge | GT-001/002; harmonisation §2.10 |
| Insurer audience + `underwriting_representation_ref` / `representation_conformance_status` | accept-conditional (insurance profile) | TRK-015 |
| Aggregate-pattern principle (per-action conformance ≠ assurance) | accept as conformance rule + report-profile rule | TRK-011 |
| Erasure vs immutability: crypto-shred referenced content, `content_erased` resolution, subject-key separation generalised to all human references | accept as conformance rules | TRK-016, BLD-006/028 |
| Verifiable agent identity slot (`agent_identity_assertion_ref`) | experimental | BLD-017 — industry-wide unsolved; slot reserved |

## Deferred / rejected (initial entries)

| Item | State | Reason |
|---|---|---|
| Mandatory hidden chain-of-thought capture | reject | Independently ruled out by four waves; refs/hashes/guardrail results suffice; safety and practicality (doctrine §3.12) |
| UI/rendering fields in the open envelope | reject | Presentation-layer concern; canonical keys immutable, display naming external |
| Absolute-assurance vocabulary ("compliant", "safe", "guaranteed") anywhere in schema or profiles | reject | Doctrine §3.10; scoped language only |
| Support-session metadata in raw envelopes | implementation-layer | REQ-TECH-015 — must not pollute the evidence stream |
| Sector obligation-mapping libraries, insurance policy mappings | derived-only / implementation-layer | Universal core stays neutral; libraries are maintained interpretation content |
| Records-custodian affidavit machinery | implementation-layer (operational obligation) | GAP-EA-004 — an operator duty, not a field |
| Storage-level cross-domain trace merging | reject | Doctrine §3.7 — navigation, not merge |

*This register grows module-by-module as the field catalogue (P2) is decided. Every catalogue element will land here with a state and a reason.*
