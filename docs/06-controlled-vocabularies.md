> **Status: adopted working sheet.** This is the cross-wave vocabulary harmonisation record feeding the field catalogue's canonical keys and enums. It is published as-is (working form) per the govern-maturity-visibly posture; catalogue entries formalise it.

# SE v0.1 Cross-Wave Vocabulary & Field-Name Harmonisation Sheet

**Status:** Working sheet, seeded after passes over Executive (EX), Technical (TG), and Internal Assurance (IA) compressions. To be updated during Business Process Owners (BPO), External Assurance (EA), and Standards (SG) passes, then used as direct input to the Field Catalogue's canonical-key decisions.
**Rule:** Each concept gets one canonical key and one canonical enum in the catalogue; wave-specific names are recorded as aliases so requirement traceability survives the rename.

---

## 1. Field-name reconciliation table

| Concept | EX name | TG name | IA name | Recommended canonical | Notes |
|---|---|---|---|---|---|
| Commit boundary marker | `commit_boundary_indicator` + `commit_boundary_status` | `commit_boundary_crossed` | `commit_boundary` (sources) | `commit_boundary_status` (enum) + drop boolean | Status enum subsumes the boolean; "crossed" only captures one state |
| Hash chain predecessor | `previous_event_hash` | `previous_envelope_hash` | `previous_envelope_hash` | `previous_envelope_hash` | Envelope is the hashed unit; 2:1 usage |
| Untrusted content | `untrusted_content_present_flag` | `untrusted_content_exposure` | `untrusted_content_indicator` | `untrusted_content_indicator` | Pair with `input_trust_classification` (graded) as primary; boolean as derived rollup |
| Injection signal | `prompt_injection_signal_flag` | `prompt_injection_signal` | `prompt_injection_signal` | `prompt_injection_signal` | Drop `_flag` suffix convention for signals |
| Clock provenance | `clock_source` | `timestamp_source` | `timestamp_source` | `timestamp_source` | Add `clock_skew_ms`, `clock_sync_confidence` from TG/IA |
| Approval (human) | `human_approval_required` / `human_approval_present` | `approval_required` / `approval_status` + `human_review_required` / `human_review_obtained` | (reuses TG) | `approval_required` + `approval_status` + `approver_type` | One approval cluster; human-vs-system as `approver_type`, review vs approval as `approval_kind` |
| Personal data | `personal_data_flag` | `personal_data_flag` | `personal_data_involved` | `personal_data_flag` | Keep IA's `special_category_data_indicator` and `sensitive_data_involved` as separate fields (distinct legal concepts) |
| Evidence completeness | `evidence_completeness_status` | `evidence_quality` | `evidence_completeness_indicator` | Split two axes: `evidence_completeness_status` + `evidence_provenance_class` | TG's enum mixes completeness with provenance (reconstructed/backfilled/redacted); separate the axes |
| Delegator identity | - (approver_id only) | - | `delegator_user_id` (sources) | `delegator_id` | New field, all waves lacked it; the principal who granted the delegation |
| Coverage measure | - (gap 2.6) | `coverage_ratio` | expected/received sequence counts + reconciliation | `evidence_coverage_ratio` + `evidence_population_ref` | Two proof mechanisms: sequence continuity (stream) + source-system reconciliation (estate) |
| Counterparty ack | `counterparty_confirmation_ref` (addendum) | `external_confirmation_ref` + `side_effect_confirmation_status` | `source_system_reconciliation_ref` | Acknowledgment ladder structure (`acknowledgment_refs[]`) | EX Section 7.2 ladder is the superset; TG/IA fields become rungs/uses of it |
| Policy in force | `policy_version_in_effect` (gap 2.5) | `policy_version_ref` | `policy_version` + `effective_from/until` | `policy_ref` + `policy_version` + `effective_from/until` | IA's effective-dating pattern generalises to all versioned refs |
| Containment | containment events (gap 2.7) | `containment_action_ref` | `containment_action_ref` + `containment_event_indicator` | `containment_action_ref` + event kinds | Event kinds still missing from all event_kind enums |
| Guardrail outcome | `guardrail_status` (no bypassed) | `guardrail_result` | `guardrail_check_ref` + control_result | `guardrail_result` using the canonical control_result enum | Guardrails are technical controls; one result enum |

---

## 2. Controlled-vocabulary reconciliation

### 2.1 event_kind - DIVERGENT (EX 6.1 vs TG 9.1)
- EX: `intent_received, plan_created, model_call, tool_call_requested, tool_call_executed, authority_checked, approval_requested, approval_granted, approval_denied, commit_boundary_reached, commit_executed, commit_failed, rollback_executed, compensation_executed, boundary_exit, boundary_entry, exception_detected, escalation_triggered, human_intervention, evidence_exported, attestation_recorded`
- TG: `execution_started, prompt_received, context_loaded, model_invoked, model_output_received, plan_created, tool_selected, tool_invoked, tool_response_received, policy_check_performed, guardrail_check_performed, approval_requested, approval_received, commit_attempted, commit_succeeded, commit_failed, boundary_entry, boundary_exit, fallback_started, retry_attempted, escalation_triggered, rollback_attempted, rollback_succeeded, compensation_action_started, execution_completed, execution_failed, evidence_gap_detected`
- **Recommendation:** TG is the better lifecycle backbone (finer-grained, attempt/succeed split). Merge in EX-only values (`authority_checked`→`policy_check_performed`? keep both pending W6; `human_intervention`, `evidence_exported`, `attestation_recorded`, `approval_denied`). Add missing across both: `containment_action`, `authority_revoked`, `authority_suspended`, `autonomy_state_changed`, `override_executed`.

### 2.2 commit_boundary_type - TWO AXES, NOT ONE ENUM
- EX 6.3 is impact-class oriented (`money_movement, financial_record, customer_record, regulated_record, contract_or_representation, external_communication, production_database_write, infrastructure_change, credential_or_permission_change, data_disclosure, legal_or_compliance_status_change, operational_workflow_trigger`)
- TG 3.3 is mechanism oriented (`database_write, system_of_record_update, payment_initiation, payment_submission, refund_issue, customer_message_send, external_api_side_effect, infrastructure_change, permission_change, record_delete, case_closure, contractual_action, notification_dispatch, workflow_trigger`)
- **Recommendation:** define `commit_mechanism` (TG enum) and `commit_impact_class` (EX enum) as two fields. They answer different reader questions (engineer: *how*; board/audit: *what kind of consequence*).

### 2.3 result_status - SUPERSET MERGE
- EX: `success, failure, partial, rejected, timeout, compensated`
- TG: adds `partial_success, blocked, escalated, timed_out, retried, rolled_back, pending, unknown`
- **Recommendation:** TG set as canonical (`partial_success` over `partial`; `timed_out` over `timeout`); review whether `retried`/`escalated` are statuses or events (likely events - a retried action still ends in some terminal status).

### 2.4 control_result - MERGE WITH AXIS SPLIT
- EX 6.8: `passed, failed, blocked, alerted, escalated, bypassed, not_evaluated, not_applicable, not_observable, unknown`
- IA 9.4: `passed, failed, bypassed, not_observed, not_applicable, operated_with_exception, operated_with_compensating_control, inconclusive`
- **Recommendation:** IA as canonical *result* enum (its compensating-control values are assurance-grade); EX's `blocked, alerted, escalated` move to `control_action_taken` (already an EX field) - result vs action are different axes. Reconcile `not_evaluated`/`not_observed`/`not_observable` into two values: `not_evaluated` (control didn't run) and `not_observable` (no evidence either way).

### 2.5 risk_appetite_status - MERGE
- EX 6.9: `within_appetite, near_threshold, breached, unknown, not_defined, not_applicable`
- IA 9.5: `within_appetite, near_tolerance, exceeds_appetite, critical_breach, not_assessed, evidence_insufficient`
- **Recommendation:** `within_appetite, near_tolerance, exceeds_appetite, critical_breach, not_defined, not_applicable, evidence_insufficient`. IA's `evidence_insufficient` is a distinct and valuable state (≠ unknown); IA's two-tier breach severity is better; EX's `not_defined` (no appetite statement exists) is distinct from `not_assessed`.

### 2.6 security_signal_type - THREE-WAY MERGE
- EX 6.7 (as behaviour_divergence_type), TG 9.8, IA 9.9-adjacent - heavily overlapping.
- **Recommendation:** TG 9.8 as the base (cleanest); add IA's `indirect_instruction_exposure`, `untrusted_content_dependency`, `policy_guardrail_failure`→ rename `policy_or_guardrail_bypass`; add EX-only divergence values (`unexpected_commit_attempt`, `delegation_context_missing`, `human_approval_missing`, `model_drift`, `capability_overreach`) - decide in catalogue whether behaviour-divergence and security-signal are one enum or two related ones (likely two: security signals are a subset re-read adversarially).

### 2.7 Single-wave vocabularies to adopt as seeds (no conflicts yet)
- IA 9.12 `autonomy_level` - first definition; adopt.
- IA 9.2 `emitter_independence_level` + IA 3.2 `value_origin_type` - adopt; merge TG 14.4's evidence-basis list into `value_origin_type`.
- IA 9.1 `evidence_collection_method` vs TG 9.4 `capture_layer` - near-duplicates; merge into `capture_layer` + `capture_method` pair (TG's split is cleaner).
- TG 9.6 `side_effect_confirmation_status` (incl. `contradicted`) - adopt; becomes the status rollup of the acknowledgment ladder.
- TG 9.3 `environment_type`, TG 9.2 `actor_type` - adopt; extend `actor_type` with `orchestrator` (present) - confirm EX catalogue uses it.
- IA 9.6 `obligation_status`, IA 9.8 privacy-boundary status, IA 9.10 typology tags, IA 9.11 model approval status - adopt.
- EX 6.10 assurance_level, 6.11 line_of_defence, 6.12 materiality class, 6.13 reliance_boundary (+ insurer value pending W5) - adopt.
- BPO 10.1 process step status, 10.3 path alignment status, 10.7 reversibility status, 10.10 recommended business action - adopt as seeds.

## 2.8 BPO-wave additions and collisions

- **`approval_status` - BPO 10.5 is best-of-breed** (`not_required, required_pending, required_obtained, required_missing, bypassed, expired, revoked, unknown`): adopt as canonical, superseding the EX/TG approval cluster recommendation in §1; fold `human_approval_required/present` and `human_review_required/obtained` into this enum + `approval_kind`/`approver_type`.
- **`fail_open`/`fail_closed` COLLISION:** TG `emission_fail_posture` (evidence-pipeline posture) vs BPO 10.6 exception-handling-path values `fail_open`/`fail_closed` (business exception behaviour). Two distinct concepts sharing words. Canonical: keep `emission_fail_posture` for the pipeline; rename BPO values to `proceed_without_control` / `halt_on_exception` (or similar) in the exception-path enum to prevent conflation.
- **Outcome triple vs confirmation:** BPO `technical_result_status` / `process_outcome_status` / `business_outcome_status` adopted; remove `externally_effective`/`not_confirmed` from process-outcome enum - external effect belongs to `side_effect_confirmation_status` (acknowledgment-ladder rollup) to avoid double-encoding.
- **`unexpected_tool_use` lives in three modules** (BPO path alignment 10.3, EX behaviour divergence 6.7, TG/IA security signals): catalogue records the observation once; path/divergence/security are read-lenses, not three fields.
- **Maker-checker:** merge BPO `dual_control_*`/`maker_ref`/`checker_ref` with EX `sod_initiator_ref`/`sod_approver_ref`/`sod_executor_ref` into one SoD/dual-control cluster.
- **Result status naming:** BPO `technical_result_status` vs EX/TG `result_status` - canonical `result_status` (the "technical" qualifier is implied once process/business outcomes are separate fields).

---

## 2.9 External Assurance (W5) additions

- **Provenance is THREE axes, not one vocabulary.** Reconcile IA `value_origin_type`, EA `evidence_origin_type`, EA `assertion_basis`, EA `corroboration_state` into: (a) `evidence_origin` (who produced it: runtime / platform / connector / third party / management / ARBITR); (b) `assertion_basis` (epistemic: observed / measured / asserted / inferred / derived / interpreted); (c) `corroboration_state` (uncorroborated → internally corroborated → source-system corroborated → third-party confirmed → externally anchored, + `conflicting_evidence`). Retire `value_origin_type` as a merged alias.
- **`capture_status` (EA 10.3) adopted as the canonical capture axis** - `missing_recoverable`/`missing_irrecoverable` split and `outside_capture_boundary` (the uninstrumented-path disclosure) are superior; TG `evidence_quality` and prior completeness enums map onto it + the completeness axis.
- **`execution_phase` + `execution_mode` (EA 6.7) adopted** - supersedes the single `execution_mode` enum proposed in EX/TG passes; simulation/shadow/dry-run/test map to `execution_phase`; replay/batch/supervision map to `execution_mode`.
- **`commit_boundary_type` (EA 10.7)** - third variant; confirms two-axis decision (mechanism + impact class); distribute EA values across both.
- **`assurance_level`** - merge EX 6.10 + EA 10.5 (adds `agreed_upon_procedures`, `regulator_reviewed`, `court_submitted`).
- **`reliance_boundary_status` (EA 10.6) adopted as canonical**; EX 6.13's audience list becomes companion `reliance_audience` (now including `insurance_notification_support` - resolved by EA's insurer role).
- **`redaction_method` (EA 10.9) adopted** - first defined redaction-method enum; `cryptographic_tombstone` value to be designed jointly with the field-level redaction-tolerant hash scheme (W6 core question).
- **New single-wave seeds:** `legal_hold_status` (10.11), `notification_status` (10.10), `claim_coverage_status` (10.12), report-generation manifest fields (4.7).

## 2.10 Standards Group (W6) - final additions

- **`event_kind` fourth variant (SG 10.1):** contributes `authority_granted`, `authority_revoked` (only wave to source it - closes the Exec containment-events gap), `redaction_applied`, `trace_continuation_declared`, `evidence_gap_recorded`. Final merge: TG lifecycle backbone + EX assurance events + SG authority/evidence-lifecycle events + containment additions (`containment_action`, `authority_suspended`, `autonomy_state_changed`, `override_executed`).
- **`commit_boundary_type` fourth variant (SG 10.10):** adds `contractual_commitment` (commitment-cluster commit type) - distribute across the mechanism/impact two-axis split with EX/TG/EA values.
- **Conformance ladder `SE-C0-schema-valid` → `SE-C5-lossless-pipeline-capable` (SG 10.2): adopt as canonical conformance structure**; Technical-wave implementation profiles map orthogonally (profile = scope implemented; C-level = completeness achieved).
- **`must_understand` + `unknown_field_policy` (SG 11.6): adopt** - they also settle unknown-field treatment during canonical hashing/verification.
- **Naming conventions (§3 below):** no SG-source opinions exist; these are confirmed as editorial decisions for the Field Catalogue - ratify there.

## 2.11 Alignment vocabs (WO16 / AGT #276 / x402 Identity WG) - closed sets

Closed enumerations. Values are `lower_snake`. Additive-only after freeze.

**`identifier_scope` (closed):**
- `global` - comparable across all parties; the same value denotes the same subject everywhere
- `relying_party_pairwise` - stable for one (subject, relying party) pair; uncorrelatable across relying parties by design
- `issuer_internal` - meaningful only within the issuing system
- `ephemeral` - valid for a single session or transaction; no cross-record continuity

Where `<identifier>_scope` is absent, a consumer MUST NOT assume `global`. A defaulting reader is the failure this vocabulary prevents.

**`entry_basis` (closed):** `counterparty_asserted` | `observed_live_402` | `credential_backed` | `third_party_attested`

**`verification_status` (closed):** `unverified` | `verified` | `verification_failed` | `verification_unavailable`

**`identifier_role` (closed):** `primary` | `alternative`

**`signer_presence` (closed):**
- `unsigned` - no signature was attempted; the record makes no authorship claim
- `stripped` - an author is named but no signature is present; the authorship claim is unsupported. **MUST fail regardless of any strictness flag** (the attacker chooses whether the verifier runs strict)
- `unverifiable` - a signature is present but the key or its authorisation cannot be resolved
- `invalid` - a signature is present and resolvable and does not verify

A top-level failure verdict is a fail-closed aggregate, not a claim that every lower property failed. AXES hashes the whole canonical envelope (self-referential signature excluded), which is what makes `stripped` detectable; see [docs/09a](09a-hash-scope-and-exclusions.md).

**`hash_scope_exclusion_reason` (closed):** `self_referential` | `recipient_stamped` | `syntax_mutable`

**`derivation_outcome` (closed):** each value supports a different conclusion for a reader.
- `ok`
- `underivable_missing_input` - a required input was never captured; a genuine evidence gap
- `undisclosed` - committed at emission but not disclosed to this reader. NOT a gap. If redaction reads as missing evidence, an auditor concludes the opposite of the truth.
- `not_independently_reproducible_keyed` - depends on a secret; a verifier without it can check consistency but not recompute. A designed privacy property working correctly.
- `indeterminate_clock_skew` - clock provenance unknown on one side, or the margin falls inside the combined uncertainty
- `underivable_identifier_scope` - the join crosses relying parties on a pairwise identifier; unsound by design, not unavailable by accident
- `underivable_unverified_identifier` - attribution attempted on an identifier below the threshold
- `derived_with_gap` - the span contains a recorded evidence gap
- `superseded` - the source envelope has been superseded by an amendment
- `underivable_conflicting_inputs` - inputs carry `corroboration_state: conflicting_evidence`; a derivation MUST NOT silently pick a side
- `precision_insufficient` - input precision cannot support the requested output precision
- `outside_capture_boundary` - the path was outside the capture boundary

**`basis_status` (closed):** `demonstrated` | `stubbed` | `simulated` - structured companion to free-text authenticity / anchoring method strings. Status MUST NOT be embedded only in parenthetical prose.

**`assertion_basis` field/block scope.** The existing envelope-scope values (`observed` / `measured` / `asserted` / `inferred` / `derived` / `interpreted`) remain. The more specific declaration governs. An envelope-scope declaration MUST NOT be read as covering a field or block that carries its own `assertion_basis`. This one change resolves two defects: a derived quantity sitting inside an envelope labelled observed, and an unverified identifier sitting inside an envelope labelled observed.

**`settlement_role` (closed), direction-neutral:**
- `origin` - the principal: the party whose value it is, whether earned or spent
- `facilitator` - a relay settling on another party's behalf
- `proxy_gateway` - a pass-through intermediary that fronts other services and routes value onward

Correction: an earlier draft defined `origin` as "the party that earns the value", which inverts on the payer side. Checkability runs against the `primary` identifier; a mismatch on an `alternative` is a signal, not a disqualification. See [docs/15](15-AXES_Payee_Settlement_Role_Design_Note.md).

## 3. Naming-convention decisions (route to catalogue)

**Closed - casing.** Field keys are `lower_snake`; enum values are `lower_snake`. Rationale: ISO 20022 API/JSON best-practices whitepaper §7.1 recommends unabbreviated snake_case for JSON representations of ISO 20022 semantics; lowerCamelCase appears in none of ISO 20022's maintained representations (business model spaced title-case; XML vowel-stripped tags; JSON Schema generation draft retains those). AXES is internally consistent at this spelling. Concept-level interoperability uses declared representation pairs, never derived camel-to-snake transforms (ambiguous at digit boundaries and acronyms). Under JCS two spellings sort to different positions and produce different canonical bytes; see [docs/12](12-standards-alignment.md). Designed exception: a relying-party-scoped identifier (identifier_scope) legitimately produces different digests at different relying parties.

Still open:
1. Suffix discipline: `_flag` vs `_indicator` vs `_signal` - propose: `_indicator` for observed booleans, `_signal` for security/behaviour observations carrying confidence, no `_flag`.
2. `_ref` vs `_id`: propose `_id` for identifiers minted within SE scope; `_ref` for pointers to external artifacts/systems.
3. Effective-dating pattern: `*_version` + `effective_from`/`effective_until` standardised for every versioned reference (policy, delegation, control, model, terminology profile).
4. Boolean polarity: always positive-presence (`redaction_applied`, not `unredacted`).
5. `delegation_scope` serialisation structure (`scope_json` question) - W6.