# Changelog

All notable changes to the AXES specification and repository.

## [Unreleased - SE v0.1 Public Working Draft]

### 2026-08-17 - Corpus of record (docs/17 Phase 0, D-018)
- Tagged `corpus/2026-08-08-gt-v2` at `776cc0b` (externally verified Golden Trace v2) and `corpus/2026-08-15-pre-merge` at `b5b6d30` (retired default-branch lineage).
- README corpus-of-record note; [`RELEASES.md`](RELEASES.md) and [`VERIFY.md`](VERIFY.md). Default-branch HEAD is not the corpus third parties verified.

### 2026-08-17 - WO16 Task 12 - GATED
- Corpus regeneration (remove stored anchoring-latency field, add `anchor_requested_at`, heartbeat rename, timestamp reconcile) is **not started**. It ships only as the announced gt-v2.1 supersession after the verified corpus is merged onto default. See [`docs/17-AXES_Corpus_of_Record_Remediation_Plan.md`](docs/17-AXES_Corpus_of_Record_Remediation_Plan.md) Phase 1.

### 2026-08-17 - WO16 Task 1 - identifier_scope
- Closed `identifier_scope` vocabulary; companion `_scope` / `_resolution_authority`; IDS-001..003. Absent scope MUST NOT default to global.

### 2026-08-17 - WO16 Task 2 - identifier sets
- Content-keyed identifier objects (JCS set-versus-sequence); `entry_basis`, `verification_status`, `identifier_role`; unverified identifiers recorded but not attributable.

### 2026-08-17 - WO16 Task 3 - assertion_basis field scope
- `assertion_basis` at field or block scope; more specific declaration governs (IDS-004). Resolves derived-in-observed and unverified-in-observed.

### 2026-08-17 - WO16 Task 4 - derived values (catalogue only)
- Specify removal of stored anchoring-latency in favour of `anchor_requested_at` and named lag; disclose gt-v2.0 timestamp inconsistency; heartbeat rename specified for Task 12; `size_bytes` exempted; BLD-011/026 amended. Corpus bytes unchanged.

### 2026-08-17 - WO16 Task 5 - signer_presence
- Closed four-value vocabulary; `stripped` MUST fail regardless of strictness flag.

### 2026-08-17 - WO16 Task 7 - hash-scope note
- New [`docs/09a-hash-scope-and-exclusions.md`](docs/09a-hash-scope-and-exclusions.md); `hash_scope_exclusion_reason`.

### 2026-08-17 - WO16 Task 8 - CrossMsg citation
- docs/09 no longer attributes an exclusion set to `ConversionRules`; declared-field-set / KVP inclusion; link to 09a §3.

### 2026-08-17 - WO16 Task 9 - Derivation Profile Registry
- DPR-001..015; `derivation_outcome`; `axes.authority_valid_at_action` three-state return; decision entries.

### 2026-08-17 - WO16 Task 10 - casing
- `lower_snake` ratified; casing closed in docs/06 §3; cross-layer spelling rule in docs/12 (JCS consequence; pairwise exception).

### 2026-08-17 - WO16 Task 11 - custody, correlation, settlement_role
- Not-self-declared custody rule; third identity coordinate; `correlation_finding` / `triage_disposition`; direction-neutral `settlement_role`.

### 2026-08-17 - WO16 Task 13 - why this field exists
- Four-part house style in the field-catalogue README; notes in [`docs/05-field-catalogue/field-origin-notes.md`](docs/05-field-catalogue/field-origin-notes.md).

### 2026-08-17 - WO16 Task 14 - RFC8785-JCS
- Normative dereferenceable `canonicalisation_version`; informal `RFC8785` retired.

### 2026-08-17 - WO16 Task 17 - identity syntax portability
- Prefix table; predicates MUST NOT bind to one syntax; credit wowlegend / axes#6.

### 2026-08-17 - WO16 Task 6 - non-ASCII JCS vectors
- Four new property vectors on `golden-trace-v2` (surrogate-pair key, NFC/NFD pair, ä/z collation, digest encoding) plus a locale-comparator negative check. Existing pinned values unchanged. A property that is only named is not pinned.

### 2026-08-17 - WO16 Task 15 - reference verifier
- `tools/axes_verify.py` on `golden-trace-v2`: offline JCS/digest, chain, `expected.json` including reject reason codes, custody twins. Typed outcomes. Vectors README: verifier shipped, not Planned P4.

### 2026-08-17 - WO16 Task 16 - pass-and-fail predicates
- Standing rule in `vectors/README.md`; TLC-008. Chain-break fail-set marked unexercised as a committed negative (would mutate the corpus of record).

### 2026-08-17 - WO16 Task 18 - basis_status
- Structured `demonstrated` \| `stubbed` \| `simulated`; GAP-EXEC-002 annotated with 0/43 confirming-party measurement. Corpus values gated.

### 2026-08-17 - Field naming: no unit in the key (D-017)
- Renamed `anchoring_latency_ms` → `anchoring_latency` (unit = milliseconds, declared outside the identifier). Applies bar Rule 3 to our own corpus before raising it externally.
- Golden Trace fin/ind generators and sample anchor envelopes regenerated so hash chains stay consistent.
- Decision D-017 recorded; further `_ms` / `_s` key scrub tracked, not bulk-renamed in this change.

### 2026-08-14 - x402 / AEP coherence tracker and outstanding landings
- Coherence tracker, outstanding AXES landings (role enum, signing profile, identity provenance), payee settlement-role design note; ROADMAP and adjacent-standards watch pointers.

### 2026-07-24 - SCITT profile rules, Agent 365/Purview map, ARBITR import backlog
- SCITT existence-bound profile rules expanded in [`docs/interop/x402-and-anchoring.md`](docs/interop/x402-and-anchoring.md); ROADMAP Band C detail + EB-006; adjacent-standards watch updated (RFC 9943 family).
- Agent 365 OTel + Purview audit → SE mapping: [`docs/interop/agent365-purview-se-mapping.md`](docs/interop/agent365-purview-se-mapping.md) (incl. delegation/cross-estate/non-M365 gaps).
- BLD-031 raised (ARBITR Agent 365/Purview import pack); D-016 differentiate Microsoft control plane vs AXES evidence plane. Magentix AI ARBITR battlecard kept proprietary (gitignored; not published in this repo).

### 2026-07-24 - x402 composition, EvidenceAnchor posture, simulated-anchor reading rule
- Decision D-015: x402 settles / AXES evidences; action-receipt as ack-ladder rung; AGT EvidenceAnchor is a runtime SPI to *profile*, not for the AXES standard to implement; Golden Trace SIMULATED anchor must not be read as a closed existence bound.
- Informative note: [`docs/interop/x402-and-anchoring.md`](docs/interop/x402-and-anchoring.md).
- Band C (EB-001..005) added to the three-layer tracker for external existence bound; EB-001 landed (GT README reading rule).
- Adjacent-standards watch, ROADMAP known limitations, docs/12 stub updated.

### 2026-07-24 - Three-layer evidence coverage (Band A surfacing)
- Programme opened (D-014 / TRK-024 / GAP-EXEC-021); tracker: [`registers/three-layer-evidence-and-control-reevaluation.md`](registers/three-layer-evidence-and-control-reevaluation.md).
- README: **Working envelope shape (exemplar)** section - not a schema freeze; three-moment table + trimmed Golden Trace excerpt.
- Informative coverage note: [`docs/interop/three-layer-evidence-coverage.md`](docs/interop/three-layer-evidence-coverage.md) (L2 gap disclosed; correlation spine vs pending action digest).
- Root [`CONFORMANCE.md`](CONFORMANCE.md): corpus verification vs SE-Cx claims; docs/07 remains normative ladder home.
- Legacy May-sketch examples moved to [`examples/legacy/`](examples/legacy/); current dialect is Golden Trace only.
- ROADMAP, CONTRIBUTING, adjacent-standards watch, requirements index updated.

### 2026-07-20 - Canonicalisation prior art
- CrossMsg-Signing (steward prior art) referenced as P1-1 spike input: JCS+JWS baseline evidence over ISO 20022 content, declared-hash-scope concept, cross-syntax test-vector seeds; exclusion-vs-redaction distinction stated (docs/09).
- Repository references corrected to github.com/magentixai/axes.

### 2026-07-20 - Field catalogue begins
- Module 01 - Envelope Core published as DRAFT (docs/05): 23 entries with full descriptors, requirement traceability, and 5 open questions routed to public challenge (D-012). Module 06 (Commit Boundary & Consequence) queued next.
- Git history authored under the Magentix AI GitHub account.

### 2026-07-20 - Critical-review revision (pre-push)
- May 2026 ingest sketch moved to `archive/2026-05-ingest-draft/` with honest design-history commentary; `schema/` now states why it is deliberately empty until the canonicalisation decision (D-007).
- Golden Trace reclassified as v1 working exemplar / test corpus; v2 (post-canonicalisation, per-profile signatures) announced (D-008).
- Contribution assessment expanded to 11 fixed questions, absorbing the programme's requirements-governance addendum; Executive-wave re-pass tracked as BLD-030 (D-011).
- JSON-LD posture decided: compatibility profile (hash-pinned @context), not dependency (D-009).
- Depth position added to doctrine (docs/01 §6) and README (D-010).
- "Why AXES" wordmark story added to README; Call for Review (design partners) added to README and ROADMAP P5.
- Public-register language neutralised (implementation-layer terminology); SECURITY.md and CITATION.cff added.

### 2026-07-20 - Initial public scaffold
- Repository established: doctrine, governance, contribution pipeline (11 categories + fixed assessment questions), licences (CC-BY-4.0 / Apache-2.0), patent pledge, roadmap/maturity register.
- Requirements register published: 251 traceable rows from the six-audience requirements programme, gap analyses, close-out tracker and blind-spots review.
- Decision register seeded: programme decisions, the five pre-schema design decisions, multi-wave settled adoptions, initial deferrals/rejections with reasons.
- Golden Trace published (`examples/golden-trace/`): deterministic 76-envelope, 14-payment evidence bundle with four claim-cited target reports; regenerable and chain-verified.
- May 2026 exploratory ingest sketch preserved in `archive/2026-05-ingest-draft/` as design history.
- Cross-wave controlled-vocabulary harmonisation sheet published as working doc (docs/06).
