# Provenance

AXES (Autonomous eXecution Evidence Standard), stewarded by Magentix AI (magentix.ai), is built on open published standards, on the worked material in this repository, and on contributions credited to the people who made them. This file records, primitive by primitive, where each load-bearing element comes from. It is maintained alongside the decision register (`registers/decision-register.md`), which records the assessment and adoption of each change.

## How to read this

Each primitive traces to one of three sources:

- an open standard (an RFC, ISO, or FIPS specification), cited by number;
- prior work in this repository (the Golden Trace corpus, the module catalogue, the requirements register, the canonicalisation spike);
- a named external contribution, credited to its author at the point of adoption.

## Provenance ledger

| Primitive | What it is | Source |
|---|---|---|
| Canonical byte form | JCS canonicalisation then SHA-256 over the canonical preimage | RFC 8785 (JSON Canonicalization Scheme); FIPS 180-4 (SHA-256). Adopted via the repository canonicalisation spike (P1-1) |
| Envelope hash and hash chain | Per-envelope digest excluding the signature, linked by previous-hash, genesis of sixty-four zeros | Established hash-chaining practice (Haber and Stornetta 1991; Merkle trees; RFC 6962, Certificate Transparency). Digest computed over this repository own envelope field set |
| Content-addressed references | SHA-256(JCS(preimage)) identifiers for actions and custody | Content-addressing practice (RFC 6920, Naming Things with Hashes). Action identity converges with draft-etcheverry-action-ref (giskard09 / Pablo Etcheverry) and with the action-receipt proposal in x402#2906 (jsuich), both independently on RFC 8785 |
| Corroboration grading | corroboration_state and emitter_independence_level | This repository graded vocabulary. The independence and completeness disqualifications were contributed by Tersign (Kevin Zhang), axes#2 |
| Custody axis | capture_relationship / custody-ref (self, same_domain, deployer_domain, independent_third_party) | Proposed by neldan00077 (TrustLayers); reference implementation custody-ref-v1 contributed by giskard09, axes#3; independence predicate and capture-boundary composition from this repository |
| Declared capture boundary and fail-closed emission | Scope of capture is declared; within it, absence of an envelope means absence of a commit-boundary action | This repository Golden Trace design; completeness-under-a-committed-head from Tersign, axes#2 |
| Anchoring vocabulary | anchoring_method: distributed_ledger, transparency_log, timestamp_authority | RFC 3161 (Time-Stamp Protocol); IETF transparency work (SCITT); OpenTimestamps; on-chain anchoring reference instance via argentum-core (giskard09), tracked as EB-004 / axes#4 |
| Signature suites | Envelope signatures profiled over JWS and COSE | RFC 7515 (JWS); RFC 9052 and RFC 9053 (COSE) |
| Acknowledgement ladder | Three-layer acknowledgement (transport, protocol, business-level settlement) | This repository Golden Trace design, grounded in ISO 20022 message semantics |
| Conformance ladder and vectors | SE-C0 to SE-C5; two-sided vectors with one pinned outcome per edge, verifiable from bytes with a standard-library verifier | Standard conformance-test practice. The "one pinned outcome per edge" requirement follows a point made by Rul1an in public review |
| Report rendering and reliance boundary | Role-specific reports from one record; the standard evidences execution and does not certify | This repository doctrine |
| Domain artefact references | ISO 20022 (finance); QIF, ISA-95 / B2MML, MTConnect, EN 10204 (manufacturing) | The named public industry standards |
| Redaction | Hash-substitution redaction with enumerated redacted fields | Established redaction-by-digest practice; field enumeration from this repository |

## Standards referenced

RFC 8785 (JSON Canonicalization Scheme); FIPS 180-4 (SHA-256); RFC 7515 (JWS); RFC 9052 and RFC 9053 (COSE); RFC 3161 (Time-Stamp Protocol); RFC 6962 (Certificate Transparency); RFC 6920 (Naming Things with Hashes); ISO 20022; QIF; ISA-95 / B2MML; MTConnect; EN 10204. IETF transparency work (SCITT) is tracked in the standards watch (`docs/12`); confirm the current document reference before citing it normatively.

## Contributor credits

AXES is better for contributions from, among others: neldan00077 (TrustLayers) for the custody axis; giskard09 / Pablo Etcheverry (argentum-core, Mycelium Trails) for action-ref, real on-chain anchoring, and the custody-ref reference implementation; Tersign (Kevin Zhang) for the independence and completeness disqualifications; jsuich (Holological) for the action-receipt convergence on the canonicalisation baseline; Rul1an for the conformance-oracle discipline. Contributions are credited per component in `registers/decision-register.md` at the point of adoption.

## Scope of derivation

AXES canonicalisation is JCS as defined in RFC 8785, cited as the source. AXES signatures profile over JWS and COSE; the standard does not incorporate post-quantum or zero-knowledge signature constructions. AXES content-addresses over the field sets defined in this repository. New primitives are assessed through the process in `CONTRIBUTING.md` and recorded, with their source, in the decision register.
