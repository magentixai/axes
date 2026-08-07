# AXES Decision Register

Every accepted, deferred and rejected design element is recorded here with its rationale. Nothing is deleted, only staged. Decision states: `accept-core` · `accept-conditional` · `accept-recommended` · `experimental` · `derived-only` · `implementation-layer` · `presentation-only` · `defer` · `reject`.

IDs reference [`requirements-register.md`](requirements-register.md).

## Programme decisions

| # | Decision | State | Rationale / notes |
|---|---|---|---|
| D-001 | Standard named **AXES - Autonomous eXecution Evidence Standard**; envelope artefact remains **SE (Standards Envelope)** | decided 2026-07-20 | Anchors on autonomous execution (durable superset; agentic is the flagship profile). Canonical keys, `se.*` namespace and SE-C ladder unchanged |
| D-002 | Publish early as **Public Working Draft**; breadth visible, maturity labelled | decided | Prevents market convergence on narrower evidence models; governed openness over polished delay |
| D-003 | IPR: CC-BY-4.0 spec · Apache-2.0 code · royalty-free patent pledge on AXES core · DCO, no assignment | decided 2026-07-20 (wording pending counsel) | GAP-STD-001 / TRK-017 - "the adoption gate". Interpretation layer stays protectable |
| D-004 | Venue path: incubate at a recognised body once a second independent implementation passes the public test vectors | decided | BLD-018; coupled with D-003 |
| D-005 | Reference emitter, validator, test vectors and a basic derived-fields annex are **open**, not proprietary | decided | GAP-STD-002 / TRK-018 - placement correction from the Standards review |
| D-006 | Schema freeze is **gated on the canonicalisation decision** (incl. field-level redaction-tolerant hashing) | decided (sequencing) | TRK-023: freezing first forces a breaking v0.2 |
| D-007 | May 2026 ingest sketch **archived as design history** (`archive/2026-05-ingest-draft/`), removed from `schema/`; its "v1" label recorded as an error of ambition | decided 2026-07-20 | A ~25-field pre-programme sketch must not be readable as "the standard"; showing design history with honest commentary is itself a governance signal |
| D-008 | Golden Trace v1 classed as **working exemplar / test corpus, not normative**; Golden Trace v2 regenerated 2026-08-03 under RFC 8785 JCS with integer Amount fields (v1 archived at `archive/golden-trace-v1-fin/`) | decided 2026-07-20; v2 landed 2026-08-03 | v1's informal hashing and stub signatures are disclosed; v2 removes JSON floats from hash scope and seeds byte-level vectors |
| D-009 | **JSON-LD posture: compatibility, not dependency.** Publish a versioned, hash-pinned `@context` mapping canonical keys to field-registry IRIs so any envelope can be *interpreted as* JSON-LD; envelopes remain plain JSON; hashing is defined over plain-JSON canonical form; verifiers MUST NOT fetch remote contexts. JSON-LD processing as a normative requirement: **reject** | decided 2026-07-20 (compatibility profile: experimental, P4) | Semantic-web interoperability and knowledge-graph value without the canonicalisation conflict (RDF canonicalisation vs envelope hashing), the implementer burden, or the context-substitution attack surface - an evidence standard cannot let a remote document change what a record means |
| D-010 | **Depth position adopted as doctrine** (docs/01 §6): deep schema, light-touch on-ramp; conditional modules; conformance ladder; published evidence cost model | decided 2026-07-20 | Evidence cannot be retrofitted; the implementer is increasingly a machine; the valued readings live beyond a minimal envelope |
| D-012 | **Module 01 (Envelope Core) catalogue draft published** - 23 entries incl. three-point time model, sequence/stream gap arithmetic, typed correlation keys, execution_phase/mode split, append-only amendment mechanism; 5 open questions routed to public challenge | decided 2026-07-20 (draft) | Keys proposed-canonical until module freeze; hash/signature fields deferred to Module 14 pending P1-1 |
| D-013 | **EU AI Act review absorbed** (EU-001..009): oversight-quality, intervention-timing, transparency-disclosure and content-marking, substantial-modification clusters accepted as catalogue candidates (open, conditional); regulatory identity as a conditional profile; article mapping stays implementation-layer; deployer log custody to implementation guidance | decided 2026-07-22 | Regulation-sourced demand independently confirms multiple adopted items (provenance axes, agent disclosure, retention/WORM, incident fields). Core stays regulation-neutral; profiles carry the regulatory surface |
| D-014 | **Three-layer evidence coverage + control re-evaluation programme opened** - AXES maps to pre-execution decision, control-in-force, and post-execution outcome as *evidence coverage* (not as an enforcement stack). Near-term surfacing (TLC-*) uses working envelope shape + honest L2 gap disclosure. Closing independent **control re-evaluation** (CRE-*) requires content-addressed control-context snapshots, evaluated-input digests, effective dating, evaluation-profile neutrality, and Golden Trace v2 proof - tracked in [`three-layer-evidence-and-control-reevaluation.md`](three-layer-evidence-and-control-reevaluation.md). Faithful-capture/witness remains orthogonal (CRE-D01) | decided 2026-07-24 | External governance threads converge on three bound artifacts; AXES already covers L1/L3 substantially and L2 only as versioned refs. Doctrine §5 forbids lane drift. TRK-024 / GAP-EXEC-021 |
| D-015 | **x402 / EvidenceAnchor posture and simulated-anchor reading rule** - (1) x402 settles payment; AXES evidences delegated execution; action-receipt (x402#2906) profiles as an acknowledgment-ladder rung; evidence-capture before adjudication/enforcement (x402#2887). (2) AGT **EvidenceAnchor** (AGT PR #2244) is a *runtime plugin SPI*; AXES does **not** implement that ABC - emitters may; the standard profiles portable `anchoring.*` receipt semantics so backends are interchangeable. (3) Golden Trace v1 `write_once_store (SIMULATED)` + `corroboration_state: externally_anchored` must not be read as a closed existence bound; local `chain_head_hash` is real, external verify is not - GT v2 must ship a real method. Note: x402 issue #2244 is unrelated | decided 2026-07-24 | Docs: [`docs/interop/x402-and-anchoring.md`](../docs/interop/x402-and-anchoring.md). TRK-001 / GAP-TECH-001 / CRE-D01 / EB-* |
| D-016 | **Microsoft Agent 365 / Purview are adjacent governance surfaces, not AXES substitutes** - map exportable events into SE where useful; differentiate control-plane vs evidence-plane; independence argument mandatory in Magentix AI positioning (Microsoft-operated logs of Microsoft-estate agents are not independent auditor evidence). ARBITR import pack tracked as BLD-031; Magentix AI battlecard is proprietary (gitignored, not published here) | decided 2026-07-24 | [`docs/interop/agent365-purview-se-mapping.md`](../docs/interop/agent365-purview-se-mapping.md) |
| D-011 | Contribution assessment expanded to **11 fixed questions**, absorbing the programme's 10-point requirements-governance addendum (claim traceability, reliance wording, fact-vs-inference check) | decided 2026-07-20 | The addendum arrived mid-programme; waves 2-6 absorbed it, the Executive wave did not - its dedicated re-pass is tracked as BLD-030 |

## Pre-schema design decisions (the P1 five)

| # | Question | State | Notes |
|---|---|---|---|
| P1-1 | Canonicalisation incl. redaction-tolerant hashing (salted per-field vs Merkle-structured) | **decided (canonical form + numeric kinds, 2026-08-03)** - redaction hashing still open · [#5](https://github.com/magentixai/axes/issues/5) | **Canonical byte form:** RFC 8785 JCS. **Numeric kinds:** Amount, Ratio; temperature/top_p as exact decimal strings; derived ratios in report layer only. Golden Trace v2 regenerated; vectors in [`vectors/`](../vectors/) (axes#6). Credit: MarkovianProtocol (canoncheck), Tersign (@wowlegend). GAP-EA-001 / TRK-005 |
| P1-2 | Append-only amendment model (`supersedes_envelope_id`, `amendment_reason`) | accept-core (wording in progress) | GAP-EA-004 / TRK-006; admissibility requirement |
| P1-3 | Access & Restriction Model (redaction escrow + dereference authorisation + finding-level restriction incl. `tipping_off_restricted`) | accept (normative section in progress) | GAP-IA-002 / TRK-004 |
| P1-4 | Receipt slot / acknowledgment ladder (rungs 0–5; outbound receipts; boundary receipts; rungs accrete over time) | accept (structure settled; format spec in progress) | TRK-003; three-perspective validation (demand/legal/supply); GT-003 |
| P1-5 | IPR posture | decided → D-003 | - |

## Settled adoptions (multi-wave convergence - accepted ahead of full catalogue)

| Item | State | Source |
|---|---|---|
| External anchoring module (`external_anchor_ref`, `anchoring_method`, RFC 3161 / SCITT profiling, witness chains, WORM retention proof) | accept-conditional (core at commit boundaries) | TRK-001 - five-wave demand |
| `execution_phase` + `execution_mode` two-field semantics | accept-core | TRK-002 - EA semantics adopted |
| `emission_fail_posture` (`fail_closed` / `fail_open` / `mixed` / `unknown`) | accept-core for commit-boundary classes | TRK-013 - defines the evidentiary meaning of silence |
| Silence-semantics cluster: `heartbeat_event`, `declared_heartbeat_interval`, derived `liveness_status`, silent-window register | accept | BLD-009/025, GT-002 - documented as one story with sequence continuity + fail posture |
| `correlation_keys[]` typed family (counterparty, data_subject pseudonymous, incident, recovery_session, equivalent_input, attack_trace) | accept-core | TRK-010 |
| Two-axis commit boundary: `commit_mechanism` + `commit_impact_class` | accept-core | Harmonisation §2.2 - four wave variants reconciled |
| Three provenance axes: `evidence_origin` / `assertion_basis` / `corroboration_state` (retiring `value_origin_type` as alias) | accept-core | Harmonisation §2.9 |
| `capture_status` incl. `outside_capture_boundary`, `missing_recoverable` / `missing_irrecoverable` | accept-core | Harmonisation §2.9; GT-006 |
| SE-C0→C5 conformance ladder + orthogonal implementation profiles | accept | TRK-019 / SG 10.2 |
| `must_understand` + `unknown_field_policy` extension semantics | accept-core | SG 11.6 - also settles unknown-field hashing treatment |
| Agent disclosure marker (`agent_disclosure_status`) | accept-conditional (counterparty-facing actions) | TRK-009 - cheap to standardise now |
| Commitment/promise evidence cluster (+ `contractual_commitment` commit type) | accept-conditional | TRK-008 - three-wave convergence |
| Findings/Action object (severity, owner, access class, timeframe, lifecycle) | accept (derived layer, open annex) | TRK-007 - five-wave confirmation |
| Sampling-parameters block + "reproducible in distribution, not in instance" replay language | accept-conditional | TRK-014 |
| Approval-quality fields (`approval_requested_at` / `approval_granted_at` → latency) | accept-conditional on approvals | BLD-011 - the rubber-stamp hole |
| `authority_utilisation_ratio` + proximity banding | accept (derived, open annex; **report layer only** - not stored in hash scope as of v2) | GAP-EXEC-012; GT-005 - pass/fail → leading indicator |
| Event kinds `source_system_reconciliation`, `heartbeat_event`, authority lifecycle (`authority_granted/revoked/suspended`), `containment_action`, `redaction_applied`, `trace_continuation_declared` | accept into canonical `event_kind` merge | GT-001/002; harmonisation §2.10 |
| Insurer audience + `underwriting_representation_ref` / `representation_conformance_status` | accept-conditional (insurance profile) | TRK-015 |
| Aggregate-pattern principle (per-action conformance ≠ assurance) | accept as conformance rule + report-profile rule | TRK-011 |
| Erasure vs immutability: crypto-shred referenced content, `content_erased` resolution, subject-key separation generalised to all human references | accept as conformance rules | TRK-016, BLD-006/028 |
| Verifiable agent identity slot (`agent_identity_assertion_ref`) | experimental | BLD-017 - industry-wide unsolved; slot reserved |

## External contribution credits

| Date | Component | Decision | Source / credit | Reference | Status |
|---|---|---|---|---|---|
| 2026-08-07 | P1-1 canonical byte form + numeric representation | Adopt RFC 8785 JCS; Amount for money/limits with namespaced asset (`iso4217:` / `caip19:`); Ratio optional in-record; temperature/top_p and dimensional measurements as exact decimal strings; derived ratios report-layer only; no JSON floats in hash scope; SHA-256 declared agile over canonical bytes. Fin corpus uses EUR (decimals=2); vectors include USDC decimals=6 | MarkovianProtocol (canoncheck): byte-divergence measurement, vector layout; Tersign (@wowlegend): integral/fractional split, evaluator disqualifications, keccak256 vs SHA-256 distinction; ISO 20022 fractionDigits=5 / ISO 4217 minor units cited as reason not to decimalise money | axes#6; D-006; docs/09 | **Decided** |
| 2026-07-29 | Custody axis (`capture_relationship`) | Assess a typed custody field; independence must be backed by a signer outside both executor and deployer domains | Proposed by neldan00077 (TrustLayers); reference implementation custody-ref-v1 by giskard09 | AGT#276; axes#3; Field proposal axes#10 | Under assessment; deployer-capturer vectors seeded in [`vectors/`](../vectors/) |
| 2026-07-29 | Action identity / content-addressed refs | Confirm SHA-256(JCS(preimage)) baseline for action identity | Converges with draft-etcheverry-action-ref (giskard09) and x402#2906 (jsuich); baseline RFC 8785 | axes#3; x402#2906; P1-1 | Convergence recorded |
| 2026-07-29 | Real anchoring instance (`distributed_ledger`) | Track a real, third-party-verifiable anchoring_method to replace the SIMULATED stub | argentum-core on-chain anchor (giskard09) | axes#3; EB-004 (axes#4) | Tracked for Golden Trace v2 |
| 2026-07-29 | Evaluator disqualifications (independence, completeness) | Adopt as evaluator-audience constraints, mechanism-agnostic | Tersign (Kevin Zhang) | axes#2; x402#2853 | Recorded |
| 2026-07-29 | Conformance oracle discipline | Require one pinned outcome per edge; reject disjunctive oracles | Point made by Rul1an in public review | AGT#276; conformance seed axes#6 | Adopted |
| 2026-07-29 | Byte-identity vector methodology (JCS baseline) | Record independent convergence on RFC 8785 JCS + SHA-256 byte-identity testing; AXES seeds its own envelope-shaped vectors under the same discipline | MarkovianProtocol (canoncheck) - convergence on methodology and vector bar, not adoption of their codebase | axes#6; P1-1; AGT#276 | Convergence recorded |

## Deferred / rejected (initial entries)

| Item | State | Reason |
|---|---|---|
| Mandatory hidden chain-of-thought capture | reject | Independently ruled out by four waves; refs/hashes/guardrail results suffice; safety and practicality (doctrine §3.12) |
| UI/rendering fields in the open envelope | reject | Presentation-layer concern; canonical keys immutable, display naming external |
| Absolute-assurance vocabulary ("compliant", "safe", "guaranteed") anywhere in schema or profiles | reject | Doctrine §3.10; scoped language only |
| Support-session metadata in raw envelopes | implementation-layer | REQ-TECH-015 - must not pollute the evidence stream |
| Sector obligation-mapping libraries, insurance policy mappings | derived-only / implementation-layer | Universal core stays neutral; libraries are maintained interpretation content |
| Records-custodian affidavit machinery | implementation-layer (operational obligation) | GAP-EA-004 - an operator duty, not a field |
| Storage-level cross-domain trace merging | reject | Doctrine §3.7 - navigation, not merge |

*This register grows module-by-module as the field catalogue (P2) is decided. Every catalogue element will land here with a state and a reason.*
