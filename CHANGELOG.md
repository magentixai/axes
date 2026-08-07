# Changelog

All notable changes to the AXES specification and repository.

## [Unreleased - SE v0.1 Public Working Draft]

### 2026-08-07 - Golden Trace v2 manifest portability fix
- Generators write all corpus files as UTF-8 with explicit LF (`newline="\n"`); never platform text mode (fixes CRLF and CP1252 Ø in Ind QIF).
- `.gitattributes` marks `examples/**/out/**`, `vectors/**`, and archived v1 corpora as `-text` so git cannot re-normalise pinned bytes.
- Generator self-check: `assert_manifest_matches_files` before exit. Bundle hashes change once to portable values; chain heads unchanged.
- Verification report: [`docs/13b-AXES_Golden_Trace_v2_Linux_Verification.md`](docs/13b-AXES_Golden_Trace_v2_Linux_Verification.md).

### 2026-08-07 - Golden Trace v2 (P1-1 canonicalisation ruling)
- **RFC 8785 JCS** replaces GT-JCS-0; `tools/axes_canonical.py` + `requirements-dev.txt` (`jcs` package).
- **Numeric kinds:** `Amount` for money/limits with namespaced `asset` (`iso4217:EUR` in Fin; `caip19:…` USDC decimals=6 in vectors); derived ratios removed from hash scope; `temperature`/`top_p` and industrial measurements/Cpk as exact decimal strings; zero JSON floats in hash scope (generator assertion).
- Golden Trace **Fin and Ind** corpora regenerated; v1 archived at [`archive/golden-trace-v1-fin/`](archive/golden-trace-v1-fin/) and [`archive/golden-trace-v1-ind/`](archive/golden-trace-v1-ind/).
- **Conformance vectors:** [`vectors/`](vectors/) (canoncheck layout) including custody deployer-capturer twins and USDC Amount example; `tools/generate_conformance_vectors.py`.
- **Schema:** [`schema/amount.schema.json`](schema/amount.schema.json), [`schema/ratio.schema.json`](schema/ratio.schema.json).
- **Docs:** [`docs/09-canonicalisation-and-hashing.md`](docs/09-canonicalisation-and-hashing.md) expanded; decision register P1-1 partial decision recorded (MarkovianProtocol, Tersign credits).
- EB-004 real `distributed_ledger` anchor deferred pending giskard09 confirmation on axes#3 (SIMULATED stub retained, honestly disclosed).
- Rule-layer custody verdicts are declared via `reject_code` on vectors; proven by two-sided interop (custody-ref-v1), not an in-repo verifier (Planned, P4).

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
