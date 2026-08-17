# Module 01 - Envelope Core

> **Status: DRAFT - first catalogue module, published for challenge.** Keys in this module are *proposed-canonical*: they become immutable only when the module freezes at `core`/`conditional` maturity. Until then, every entry is open to a [Definition challenge](../../CONTRIBUTING.md). Hash and signature fields are **not** defined here - they live in Module 14 and depend on the canonicalisation decision (P1-1); this module only notes what must sit inside the hash scope.

**Module purpose.** Envelope Core answers the questions every other module presupposes: *which* record is this, *what kind* of event does it evidence, *when* did it happen versus when was it captured, *where* does it sit in the execution's ordering, and *whose* evidence stream does it belong to. If Envelope Core is wrong, nothing downstream can be trusted; it therefore carries the strictest requirements in the standard.

**Descriptor legend.** Required: `M` mandatory · `C` conditional (mandatory when its trigger fact is present) · `R` recommended · `O` optional. Maturity: `core` / `conditional` / `recommended` / `experimental`. Conformance: lowest SE-C level at which the field is exercised.

## Summary table

| # | Canonical key | Type | Req | Maturity | Conf |
|---|---|---|---|---|---|
| 1.1 | `se_version` | string (semver-tagged) | M | core | C0 |
| 1.2 | `envelope_id` | string (UUIDv7 recommended) | M | core | C0 |
| 1.3 | `event_kind` | string (controlled vocab) | M | core | C0 |
| 1.4 | `occurred_at` | RFC 3339 timestamp | M | core | C0 |
| 1.5 | `emitted_at` | RFC 3339 timestamp | M | core | C0 |
| 1.6 | `recorded_at` | RFC 3339 timestamp | R | recommended | C5 |
| 1.7 | `timestamp_source` | string (controlled vocab) | R | recommended | C1 |
| 1.8 | `clock_skew_ms` / `clock_sync_confidence` | integer / enum | O | recommended | C5 |
| 1.9 | `org_id` | string (stable identifier) | M | core | C0 |
| 1.10 | `tenant_id` | string (stable identifier) | M | core | C0 |
| 1.11 | `environment_id` | string (stable identifier) | M | core | C0 |
| 1.12 | `trace_id` | string | M | core | C1 |
| 1.13 | `span_id` | string | M | core | C1 |
| 1.14 | `parent_span_id` | string \| null | C | core | C1 |
| 1.15 | `lineage_id` | string | C | core | C3 |
| 1.16 | `event_sequence_number` | integer (monotonic) | M | core | C1 |
| 1.17 | `sequence_stream_id` | string | M | core | C1 |
| 1.18 | `idempotency_key` | string | M | core | C0 |
| 1.19 | `correlation_keys[]` | array of typed objects | C | core | C4 |
| 1.20 | `execution_phase` | string (controlled vocab) | M | core | C1 |
| 1.21 | `execution_mode` | string (controlled vocab) | C | core | C1 |
| 1.22 | `supersedes_envelope_id` / `amendment_reason` | string / string | C | core | C1 |
| 1.23 | `extensions` | namespaced object | O | core | C0 |

---

## 1.1 `se_version`

**Definition.** The exact version of the SE envelope specification this envelope conforms to (e.g. `se-0.1.0`).
**Purpose.** Lets any verifier or consumer select the correct schema, vocabularies and canonicalisation rules - including years later, from an evidence archive.
**Rules.** MUST identify a published spec version; MUST sit inside the hash scope. Consumers encountering an unknown version follow `unknown_field_policy` (docs/08), never guess.
**Canonicalisation registry.** Companion field `integrity.canonicalisation_version` is the closed registry identifier **`RFC8785-JCS`**. What it dereferences to (RFC 8785 revision, UTF-8 output, UTF-16 code-unit member sort, no Unicode normalisation, digest algorithm and encoding declared separately) is stated in [docs/09](../09-canonicalisation-and-hashing.md). The earlier form `RFC8785` is retired. A change in any of those properties is a new identifier.
**Report / audit usage.** Report manifests state the version(s) of every envelope relied on; mixed-version evidence sets are disclosed.
**Misinterpretations.** This is the *spec* version, not the emitter's software version (Module 02) and not the schema-file URI.
**Sources.** REQ-STD-001/007/015; REQ-EXEC-021.

## 1.2 `envelope_id`

**Definition.** Globally unique identifier for this envelope, minted by the emitter at creation time.
**Purpose.** The atomic unit of reference: chains, claims, amendments, exports and access logs all cite envelopes by this ID.
**Rules.** MUST be unique within the org scope and SHOULD be globally unique; UUIDv7 recommended (time-ordered, index-friendly). MUST be assigned **before** hashing and MUST sit inside the hash scope - the Golden Trace build demonstrated that post-hash assignment silently weakens the chain (GT-004). Never reused, never reassigned, never edited (amendments reference it via 1.22).
**Privacy.** None - opaque identifier by design; MUST NOT encode business meaning.
**Misinterpretations.** Not a deduplication key (that is `idempotency_key`); duplicate *delivery* of one envelope shares one `envelope_id`.
**Sources.** REQ-EXEC-021; REQ-IA-002; GT-004.

## 1.3 `event_kind`

**Definition.** The lifecycle event this envelope evidences, from the canonical controlled vocabulary.
**Purpose.** The single most-read field in the standard: topology reconstruction, report sectioning, conformance checks and aggregate analysis all pivot on it.
**Allowed values.** The canonical merge (docs/06 §2.1, §2.10) uses the technical lifecycle backbone (`execution_started`, `model_invoked`, `tool_invoked`, `policy_check_performed`, `approval_requested`, `commit_attempted`, `commit_succeeded`, `commit_failed`, `boundary_exit`, `boundary_entry`, `rollback_attempted`, `escalation_triggered`, `execution_completed`, `evidence_gap_detected`, …) plus assurance events (`human_intervention`, `attestation_recorded`, `evidence_exported`), authority lifecycle (`authority_granted`, `authority_revoked`, `authority_suspended`, `autonomy_state_changed`, `containment_action`), evidence lifecycle (`redaction_applied`, `trace_continuation_declared`), and the practice-sourced `heartbeat_event` and `source_system_reconciliation` (GT-001/002). Final enumeration freezes with this module; values are additive-only thereafter.
**Rules.** One envelope, one event. Compound happenings emit multiple envelopes sharing `trace_id`.
**Witnessed, never authored (correlation and triage).** Two additional `event_kind` values record asynchronous cross-event work no single decision produced:

- `correlation_finding` - a finding that spans events (worked example: three individually permitted tool calls - list a directory, read a credentials file to a temporary path, POST to a collector - produce one critical credential-exfiltration finding no per-call gate can see). Raised in public discussion by Ioannis Loutsis (Agentmetry).
- `triage_disposition` - a later human disposition of that finding, on the same append-only chain.

The custody axis records who produced the finding, when, and how far confirmed. **The custodian attests that a finding was emitted, by whom and when. It never asserts the correlation itself.** Enforcement belongs to the policy engine; correlation belongs to SOC and threat-detection, not the custodian; custody-of-the-fact belongs to the witness (discipline stated by Dani Danwin / TrustLayers). Collapsing the correlator's job into the witness is how a custodian becomes something it has no authority to be.
**Report / audit usage.** Drives every timeline, the prevention-vs-detection distinction (`policy_check_performed` before `commit_attempted`), and silence semantics (`heartbeat_event`).
**Misinterpretations.** `event_kind` is *what happened in the lifecycle*, never *how well it went* (`result_status`, Module 05/06) and never *what it means* (interpretation layer).
**Sources.** REQ-STD-009; REQ-EXEC-018; harmonisation §2.1/§2.10; GT-001/002.

## 1.4 `occurred_at` · 1.5 `emitted_at` · 1.6 `recorded_at`

**Definitions.** `occurred_at`: when the evidenced event happened in the world. `emitted_at`: when the emitter created this envelope. `recorded_at`: when the receiving store durably persisted it (stamped by the recipient, outside emitter control).
**Purpose.** The three-point time model makes capture latency and pipeline delay *measurable* instead of invisible: `emitted_at − occurred_at` = capture lag; `recorded_at − emitted_at` = pipeline lag. Forensic ordering uses `occurred_at`; evidence-pipeline health uses the other two. Named derivations live in the catalogue, not as stored envelope fields, unless the derivation crosses a boundary the consumer cannot reproduce or the executing system computed the value and **acted on it** (then store it with `assertion_basis: derived` and `evidence_origin: runtime`; divergence from independent recomputation is how a miscalculating agent is detected).
**Anchoring lag (pending gt-v2.1 / WO16 Task 12).** Catalogue replacement: **remove** the stored derived field (`anchoring_latency_ms` on corpus tag `corpus/2026-08-08-gt-v2`; `anchoring_latency` on the retired default-branch lineage) and **add** `anchor_requested_at` (ISO 8601 UTC). Named derivation: **`anchored_at − anchor_requested_at` = anchoring lag**. Docs and corpus disagree until the announced regeneration; do not treat the stored latency on today's envelopes as a catalogue-conformant measurement. Unit stays out of the key (D-017). `declared_heartbeat_interval_s` is specified for the same release: carry the unit in the value, following `monetary: {amount, currency}`. **`size_bytes` is exempt:** bytes is the canonical unit for size with no realistic alternative; applying the rule there would be pedantry.
**Rules.** RFC 3339 UTC with millisecond precision or better. `occurred_at ≤ emitted_at` (violations are evidence-quality signals, not silent corrections). `recorded_at` lives outside the emitter hash scope (it is the recipient's assertion - its integrity is the store's chain-of-custody problem, Module 14 / [docs/09a](../09a-hash-scope-and-exclusions.md)).
**Misinterpretations.** None of the three is "the trusted time" by itself - trusted time requires `timestamp_source` plus external anchoring (Module 14). Backfilled evidence shows honest old `occurred_at` with new `emitted_at`, never rewritten timestamps.
**Sources.** REQ-TECH-002; REQ-IA-002; GAP-EXEC-003; BPO-011.

## 1.7 `timestamp_source` · 1.8 `clock_skew_ms`, `clock_sync_confidence`

**Definition.** Provenance of the emitter's clock (`ntp_synced`, `ptp_synced`, `os_clock_unsynced`, `external_authority`, `unknown`), with measured skew and a confidence grade where available.
**Purpose.** A timeline is only as strong as its clocks; auditors and forensic investigators weight ordering claims by clock provenance.
**Rules.** Recommended for all emitters; expected at SE-C5. Cheap to emit, disproportionately valuable in disputes.
**Misinterpretations.** Not a substitute for trusted timestamps (RFC 3161 anchoring, Module 14) - this discloses the emitter's clock quality; anchoring proves a ceiling on when the envelope existed.
**Sources.** Harmonisation §1 (clock provenance); REQ-IA-002; GAP-IA-001.

## 1.9 `org_id` · 1.10 `tenant_id` · 1.11 `environment_id`

**Definition.** The organisational scope of the evidence: owning organisation, tenant within it, and environment (`production`, `staging`, …) - stable opaque identifiers.
**Purpose.** Tenant isolation is a first-class assurance claim ("no cross-tenant exposure") and every access, export and report is scoped by these three. They are also the boundary coordinates for cross-scope navigation (Module 08).
**Rules.** All three mandatory on every envelope, inside the hash scope. Identifiers are opaque; display names live in the presentation layer. `environment_id` identifies *which* environment; whether execution was real is `execution_phase` (1.20) - the two must not be conflated.
**Identifier companions (any identifier field).** Two optional attributes compose with any identifier:
- `<identifier>_scope` - a value from `identifier_scope` (docs/06 §2.11). **Where absent, a consumer MUST NOT assume `global`.**
- `<identifier>_resolution_authority` - a reference to the party able to resolve the identifier. A reference, never the resolution. AXES is not an identity service; linkage lives with the issuer and is reached through legal process.
**AXES prefixed identifier syntax.** Where this corpus uses prefixed forms, the prefix is the namespace and what follows is opaque to consumers who do not implement that namespace. A consumer MAY NOT infer legal identity, correlation across relying parties, or control of the named party from the string alone.

| Prefix | Meaning | What follows |
|---|---|---|
| `agent:` | runtime agent instance | issuer-local path (e.g. `caldera/ap-pilot`) |
| `org:` | organisation | issuer-local org id |
| `person:pseu/` | pseudonymous person key | opaque token; not a civil identity |
| `tool:` | tool or API | issuer-local tool id |
| `runtime:` | execution runtime | issuer-local runtime id |
| `key:` | signing or verification key | issuer-local key id |
| `connector:` | connector | issuer-local connector id |
| `provider:` | service provider | issuer-local provider id |
| `orchestrator:` | orchestrator | issuer-local orchestrator id |

**Portability rule.** A conformance predicate MUST NOT be bound to one identity syntax. A predicate that cannot parse an identifier returns `verification_unavailable` (or the appropriate `derivation_outcome`), never a rejection: rejecting an unparseable identifier manufactures a false negative. Finding and credit: wowlegend (Tersign) in [axes#6](https://github.com/magentixai/axes/issues/6) (11 Aug 2026) - AXES `agent:`/`org:` forms were unparseable to a verifier bound to `0x` addresses, so both custody twins rejected including the one AXES accepts. `identifier_type` on identifier-set members (below) is the parse-rule declaration that finding empirically requires.
**Privacy.** Low, but tenant identifiers can be commercially sensitive: exports to third parties may pseudonymise them under a declared redaction profile (Module 13) without breaking chain verification (post-P1-1).
**Sources.** REQ-EXT-011; REQ-EXEC-016; alignment with the original ingest doctrine (tenant isolation).

## 1.12 `trace_id` · 1.13 `span_id` · 1.14 `parent_span_id`

**Definition.** The execution-graph coordinates within one tenant/environment scope: a trace groups the envelopes of one execution journey; spans nest its steps.
**Purpose.** Deterministic reconstruction of the execution graph - the audit trail's skeleton and the topology view's input.
**Rules.** `trace_id`/`span_id` mandatory; `parent_span_id` null only at the root. SHOULD be W3C Trace Context compatible (GAP-TECH-014) so evidence correlates with existing observability without merging concerns: OTel answers *is it fast and healthy*; AXES answers *who authorised it and did it become real*. The two link by shared trace identity - they do not replace each other.
**Misinterpretations.** `trace_id` is tenant/environment-scoped and does NOT cross liability boundaries - that is `lineage_id`.
**Sources.** REQ-TECH-007; REQ-EXEC-016; GAP-TECH-014.

## 1.15 `lineage_id`

**Definition.** Identifier following the *whole* multi-boundary journey: many trace_ids (across providers, tenants, organisations) may share one lineage_id.
**Purpose.** Cross-provider accountability - "this customer refund started in vendor A's agent and settled through bank C" - without merging evidence stores. Boundary envelopes (Module 08) carry both IDs and opaque continuation references: **navigation, not merge** (doctrine §3.7).
**Rules.** Conditional: mandatory on `boundary_exit`/`boundary_entry` events and any envelope whose journey is known to cross scope. Rules for minting and propagating lineage across parties freeze with Module 08.
**Misinterpretations.** Sharing a lineage_id shares *correlation*, never *access*: dereference across boundaries is governed by the Access & Restriction Model.
**Sources.** REQ-EXEC-016; REQ-TECH-007; doctrine §3.7.

## 1.16 `event_sequence_number` · 1.17 `sequence_stream_id`

**Definition.** A strictly monotonic counter within a declared stream (`sequence_stream_id` names the stream - typically one per emitter instance).
**Purpose.** Gap detection with arithmetic instead of inference: missing sequence numbers are *provable* absences. With heartbeats and `emission_fail_posture` (Module 10) this completes silence semantics - the difference between "nothing happened" and "nothing was recorded".
**Rules.** Both mandatory. Monotonic within stream; resets only with a new `sequence_stream_id` (restart = new stream, disclosed, never a silent renumber). Duplicate numbers within a stream are integrity signals.
**Report / audit usage.** Population completeness: contiguous sequences + source-system reconciliation are the two proofs behind any "coverage 14/14" claim (TRK-012; the Golden Trace's `population_basis: independently_reconciled`).
**Sources.** REQ-IA-002; REQ-TECH-007; GAP-EXEC-006; TRK-012.

## 1.18 `idempotency_key`

**Definition.** Deduplication key for at-least-once delivery: redelivery of the same envelope carries the same key.
**Purpose.** Lossless pipelines (SE-C5) require duplicate-safe ingestion; duplicate-payment detection also leans on it (BPO-011).
**Rules.** Mandatory. Stable across retries of the same emission; distinct for distinct envelopes. On boundary-crossing events, key custody/pass-through is evidenced (GAP-TECH-009, Module 08).
**Misinterpretations.** Deduplicates *delivery*, not *business actions* - a legitimately repeated action is two envelopes with two keys; the *target operation's* idempotency is Module 05 territory.
**Sources.** Ingest doctrine; REQ-TECH-019; GAP-TECH-009; BPO-011.

## 1.19 `correlation_keys[]`

**Definition.** Typed, optional join keys: `{key_type, key_value, key_scheme}` with `key_type` ∈ `counterparty`, `data_subject`, `incident`, `recovery_session`, `equivalent_input`, `attack_trace` (extensible by vocabulary process).
**Purpose.** The aggregate-analysis join mechanism: treatment-consistency across similarly-situated customers (`equivalent_input`), all envelopes touching one counterparty, one incident's full evidence set. Without these, the aggregate-pattern principle (per-action conformance ≠ assurance, TRK-011) has nothing to compute over.
**Rules.** Conditional - present when the referent exists. **`data_subject` keys MUST be pseudonymous, with the key-to-person mapping held separately** (privacy-by-design conformance rule; generalised to all human references per doctrine §3.11). Values are stable within scope so joins work.
**Privacy.** This is the module's most privacy-sensitive field; it exists precisely so envelopes can correlate *without* embedding personal data.
**Sources.** GAP-IA-004; TRK-010; GAP-BPO-007; BLD-006.

## 1.20 `execution_phase` · 1.21 `execution_mode`

**Definition.** `execution_phase`: the reality status of the execution - `live`, `shadow`, `simulation`, `dry_run`, `test`. `execution_mode`: the operating manner - e.g. `autonomous`, `supervised`, `replay`, `batch`.
**Purpose.** The two-field split (External Assurance semantics, TRK-002) prevents the most dangerous conflation in the corpus: evidence from a simulation being read as evidence of live execution - or a live commit being dismissed as a test. Every report banner states phase; regulator packs disclose phase mix.
**Rules.** `execution_phase` mandatory (no default - silence is not "live"). `execution_mode` conditional-recommended. A `live` phase envelope crossing a commit boundary triggers the full Module 06 requirements.
**Misinterpretations.** `environment_id: production` does not imply `execution_phase: live` - shadow mode in production is exactly the case that forced the split (GAP-EXEC-001).
**Sources.** GAP-EXEC-001; GAP-TECH-002; TRK-002; harmonisation §2.9.

## 1.22 `supersedes_envelope_id` · `amendment_reason`

**Definition.** The append-only amendment mechanism: a correcting envelope names the envelope it supersedes and why.
**Purpose.** Corrections without mutation - the admissibility requirement (courts and auditors must see both the error and the correction, in order, in one chain).
**Rules.** Conditional: present exactly when this envelope amends another. The superseded envelope remains in the chain, unmodified. Verifiers present the *effective* view (latest non-superseded) while preserving the full history. Never used to "unsay" evidence - an amendment that removes information requires a `redaction_applied` event under the Access & Restriction Model, not a supersede.
**Sources.** GAP-EA-004; TRK-006; P1-2.

## 1.23 `extensions`

**Definition.** The namespaced extension container (`{"extensions": {"com.example": {...}}}`) with declaration, `must_understand` and `unknown_field_policy` semantics per docs/08.
**Rules.** Extensions never override canonical fields; unknown extensions are preserved and forwarded; hashing treatment of unknown content is fixed by the canonicalisation spec so extensions cannot break verification.
**Sources.** REQ-STD-006/021; harmonisation §2.10.

## 1.24 Identifier sets (content-keyed objects)

**Set versus sequence.** JCS sorts object members by UTF-16 code unit. It does **not** sort array elements. Converting a scalar identifier to an array would mean two emitters recording the same set in different orders produce different digests.

- A **set** (members unique, order carries no meaning) becomes an **object keyed by a content-derived key** - the identifier value itself. JCS then sorts members. Each member is a field, so it composes with per-field selective disclosure.
- A **sequence** (order is part of the fact, for example the acknowledgment ladder) stays an **array where every element carries an explicit sequence or rung field**, so order is stated data rather than implied by position.

Illustrative shape (not a live corpus envelope; `example.test` / `0xEXAMPLE` are obviously illustrative):

```json
"payee_identifiers": {
  "dns:example.test": {
    "identifier_type": "dns",
    "entry_basis": "observed_live_402",
    "verification_status": "verified",
    "verifier_ref": "org:example-verifier",
    "verification_method": "live_402_payTo",
    "verified_at": "2026-06-09T09:02:00.000Z",
    "identifier_role": "primary",
    "identifier_scope": "global"
  },
  "eip155:8453:0xEXAMPLE": {
    "identifier_type": "caip10",
    "entry_basis": "counterparty_asserted",
    "verification_status": "unverified",
    "identifier_role": "alternative",
    "identifier_scope": "global"
  }
}
```

`identifier_type` is not decoration: it tells an external verifier which parse rule to apply (WO16 Task 17; axes#6).

**Containment, not prevention.** Recording `verification_status` contains contaminated attribution, join poisoning, and laundering through a signed envelope. It does not prevent namespace squatting (registry governance, outside AXES). An unverified alternative recorded as established is worse than omitting it: the envelope would amplify the false claim.

**Consumer rule.** A consumer MUST attribute only on identifiers whose `verification_status` meets its stated threshold. Unverified identifiers are recorded but are not attributable. A derivation asked to attribute value to a party whose only matching identifier is `unverified` MUST return `underivable_unverified_identifier` rather than a value.

**Sources.** IDS-001..003; x402 Identity WG (Alfred Tom / OMA3 #3, #4; Nicole Dunn / Baselayer #10).

## 1.25 `assertion_basis` at field or block scope

**Definition.** Epistemic status (`observed` / `measured` / `asserted` / `inferred` / `derived` / `interpreted`) MAY be declared at field or block scope as well as envelope scope (`evidence_quality.assertion_basis`). The more specific declaration governs. An envelope-scope declaration MUST NOT be read as covering a field carrying its own.
**Why this exists.** Envelope-scope `observed` with a stored derived latency, or with an unverified identifier, is a false epistemic declaration with no structural way to tell which field is which. Field-scope applicability resolves both defects. Four-part notes: [field-origin-notes.md](field-origin-notes.md).
**Sources.** IDS-004; REQ-EXT-001; REQ-EXT-009.

## 1.26 `anchor_requested_at` (pending gt-v2.1)

**Definition.** ISO 8601 UTC instant when the emitter requested the external anchor. Catalogue-defined now; corpus values land in the announced Task 12 / Phase 1 regeneration. Until then the published envelopes still carry a stored derived latency field.
**Named derivation.** `anchored_at − anchor_requested_at` = anchoring lag (not stored).
**Sources.** Module 01 three-point time model; D-017; WO16 Task 4.

## 1.27 `signer_presence` and `basis_status`

**`signer_presence`.** Closed vocabulary (docs/06 §2.11). `stripped` MUST fail regardless of any strictness flag. Finding: Ryan Cason (orionsys); endorsement: Chou Deyu (Guardian). Deleting `signature` while leaving `signedBy` made a naive verifier return valid, even under a require-signatures flag, because the signature cannot sit inside its own hash input.
**`basis_status`.** Closed companion (`demonstrated` | `stubbed` | `simulated`) alongside free-text authenticity and `anchoring_method` strings. Stub status MUST NOT live only in a parenthetical (`counterparty_signed (webhook mTLS, STUB)`, `write_once_store (SIMULATED)`). Finding: wowlegend in axes#6 - a disclosure only a human can read is not a control. Field definition lands now; corpus values land in Task 12. D-015 reading rule for SIMULATED anchors remains: a simulated method MUST NOT be read as a closed existence bound; `basis_status: simulated` makes that reachable by a verifier.

---

## Open questions routed to challenge (please pile in)

1. **UUIDv7 vs free-form IDs** for 1.2/1.12/1.13 - is mandating a format worth the interop gain, or should format be profile-level?
2. **`recorded_at` placement** - Envelope Core (here) or Module 10 (evidence pipeline)? It is recipient-stamped, which argues for 10; its role in the three-point time model argues for 1.
3. **`sequence_stream_id` naming** - the working corpus used `monotonic_sequence_stream_id`; this draft shortens it. Definition Challenge welcome before freeze.
4. **`correlation_keys[].key_scheme`** - controlled vocabulary or free-form with registry? Leaning registry.
5. **Should `execution_mode` be mandatory** whenever `execution_phase = live`? The supervised/autonomous distinction is load-bearing for several audiences.
