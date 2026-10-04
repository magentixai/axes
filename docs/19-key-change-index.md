# Key change index

Every key, value or structure that changes between corpus releases is listed here: what it was, what it is now, why, which decision, and what an implementer does about it. Superseded is not the same as wrong: a record valid under its release stays valid under that release. Entries are never deleted. The machine-readable twin is [`schema/key-aliases.json`](../schema/key-aliases.json); the two must agree one for one (checked in CI).

Change types: `renamed` · `restructured` · `removed` · `added` · `value_tightened`.

## gt-v2.0 to gt-v2.1 (planned; lands in the announced gt-v2.1 release, D-018)

### Anchoring block (Module 14, WO18 A2)

| Earlier (gt-v2.0) | Now (gt-v2.1) | Change type | Why | Decision | What an implementer does |
|---|---|---|---|---|---|
| `anchoring` (single object) | `anchoring` with `anchored_subject_*` once and `anchors[]` | `restructured` | One subject can carry several independent anchors (two already exist for the gt-v2.0 release statement) | D-021 (rule 8 pre-v1), WO18 A2.2 | Read anchor fields from each `anchors[]` entry; subject fields from the block |
| `anchoring.chain_head_hash` | `anchoring.anchored_subject_hash` with `anchored_subject_type: chain_head` | `renamed` | The anchored subject is not always a chain head | D-021, WO18 A2.3 | Map the value unchanged; read the type |
| (none) | `anchoring.anchored_subject_hash_algorithm` | `added` | A detached anchor must verify on its own | WO18 A2.3 | Expect `SHA-256` for Golden Trace |
| `anchoring.anchor_receipt_id` | `anchors[].anchor_id` | `renamed` | "Receipt" collides with x402 offer and action receipts and with mechanism receipts | D-021, WO18 A2.3 | Map the value unchanged |
| `anchoring.anchoring_method: "write_once_store (SIMULATED)"` | `anchors[].anchoring_method: "write_once_store"` plus `anchors[].basis_status: "simulated"` | `value_tightened` | Status never lives in a parenthetical (catalogue 1.27) | D-015, WO16 Task 18, WO18 A2.3 | Read status from `basis_status`; treat the method as a registry identifier |
| `anchoring.anchored_at` | `anchors[].anchored_at` | `restructured` | Now per anchor; always the time the mechanism attests | WO18 A1.4, A2.3 | Never compare to an illustrative corpus timeline |
| `anchoring.anchor_store_ref` | `anchors[].anchor_service_id` | `renamed` | A time-stamp authority or notary is not a store; a service is a system, so `_id` (docs/20 N10) | D-021, D-024, WO18 A2.3 | Map the value unchanged |
| `anchoring.anchoring_latency_ms` | removed; derive `anchored_at` minus `anchor_requested_at` | `removed` | Derived values are named, not stored; no unit in a key | D-017 | Compute the lag; do not expect the key |
| (none) | `anchors[].anchor_requested_at`, `anchor_profile_ref`, `anchor_commitment_hash`, `anchor_commitment_hash_algorithm`, `anchor_record_ref`, `anchor_operator_id`, `anchor_proof_ref`, `anchor_proof_hash`, `anchor_verification_procedure_ref` | `added` | Needed for an anchor to be checkable by a third party | WO18 A2.3, WO18 A5 | Populate on real anchors; required when `basis_status` is `demonstrated` |
| `evidence_quality.corroboration_state: externally_anchored` on simulated anchor envelopes | a non-external value | `value_tightened` | `externally_anchored` is earned, never asserted | D-015, D-020 | Expect the verifier to reject `externally_anchored` over a simulated anchor |

### Names used only in registers and work orders (never in a published corpus)

| Earlier name | Where | Now |
|---|---|---|
| `external_anchor_ref`, `time_anchor_ref` | decision register; GAP-TECH-001; GAP-EXEC-003 | `anchors[].anchor_record_ref` |
| `hash_anchor` | GAP-IA-001 | `anchors[].anchor_commitment_hash` |
| `timestamp_authority_reference` | GAP-IA-001 | `anchor_record_ref` with `anchoring_method: timestamp_authority` |
| `anchor_reference_id`, `committed_value`, `committed_value_alg`, `anchor_status`, `anchor_profile`, `verification.*` | WO18 §3 draft | see WO18 A2.6 |
| `ots`, `worm_store`, `simulated` (method values) | WO18 §3a draft | `opentimestamps`, `write_once_store`; simulation is `basis_status` |

### Other gt-v2.1 changes already decided

| Earlier | Now | Change type | Decision |
|---|---|---|---|
| (none) | `anchor_requested_at` on anchor-bearing envelopes | `added` | D-017, WO16 Task 4 (catalogue 1.26) |
| (none) | `basis_status` alongside free-text authenticity strings | `added` | WO16 Task 18 (catalogue 1.27) |


## gt-v2.0 to gt-v2.1: naming rules (D-024, docs/20)

Corrections found by `tools/check_key_naming.py` against the corpus of record, plus `_id` and `_ref` corrections under docs/20 N10 that a lint cannot detect. The gt-v2.0 bytes stay as published; these land in the announced gt-v2.1 release (D-018). Known violations are listed in `tools/naming_baseline.json` on `golden-trace-v2` so CI fails only on new ones.

| Earlier (gt-v2.0) | Now (gt-v2.1) | Change type | Why | Decision | What an implementer does |
|---|---|---|---|---|---|
| `integrity.canonicalisation_version` | `integrity.canonicalization_version` | `renamed` | N2 American spelling | D-024 | Map the value unchanged |
| `integrity.signature` | `integrity.envelope_signature` | `renamed` | N3 keys fully qualified | D-024 | Map the value unchanged |
| `profile_id` | `implementation_profile_ref` | `renamed` | N10 a profile is a document; WO19 D4 taxonomy | D-024 | Map the value unchanged |
| `privacy.redaction_profile_id` | `privacy.redaction_profile_ref` | `renamed` | N10 a profile is a document | D-024 | Map the value unchanged |
| `authority.delegation_receipt_id` | `authority.delegation_receipt_ref` | `renamed` | N10 a receipt is a document | D-024 | Map the value unchanged |
| `authority.authority_context_id` | `authority.authority_context_ref` | `renamed` | N10 a delegation context is a document | D-024 | Map the value unchanged |
| `export.evidence_bundle_id` | `export.evidence_bundle_ref` | `renamed` | N10 a bundle is a document | D-024 | Map the value unchanged |
| `org_id` | `organization_id` | `renamed` | N2 no abbreviations | D-024 | Map the value unchanged |
| `clock_sync_confidence` | `clock_sync_confidence_level` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `privacy.personal_data_flag` | `privacy.personal_data_indicator` | `renamed` | N5 booleans end _indicator | D-024 | Map the value unchanged |
| `privacy.redaction_applied` | `privacy.redaction_applied_indicator` | `renamed` | N5 booleans end _indicator | D-024 | Map the value unchanged |
| `boundary_assessment.tenant_boundary_crossed` | `boundary_assessment.tenant_boundary_crossed_indicator` | `renamed` | N5 booleans end _indicator | D-024 | Map the value unchanged |
| `boundary_assessment.cell_boundary_crossed` | `boundary_assessment.cell_boundary_crossed_indicator` | `renamed` | N5 booleans end _indicator | D-024 | Map the value unchanged |
| `operation.idempotency_key_forwarded` | `operation.idempotency_key_forwarded_indicator` | `renamed` | N5 booleans end _indicator | D-024 | Map the value unchanged |
| `boundary_assessment.cross_programme_exposure_indicator` | `boundary_assessment.cross_program_exposure_indicator` | `renamed` | N2 American spelling | D-024 | Map the value unchanged |
| `boundary_assessment.basis` | `boundary_assessment.boundary_assessment_basis` | `renamed` | N3 keys fully qualified | D-024 | Map the value unchanged |
| `operation.operation` | `operation.operation_type` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `operation.commit_mechanism` | `operation.commit_method` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `result` | `outcome` | `renamed` | N7 a block is not named with a scalar class word | D-024 | Read result_status and side_effect_confirmation_status from outcome |
| `emission.declared_heartbeat_interval_s` | `emission.declared_heartbeat_interval` | `value_tightened` | N4 no unit in key; durations are ISO 8601 | D-024 | Convert seconds to an ISO 8601 duration, for example 60 to PT60S |
| `acknowledgments[].ack_layer` | `acknowledgments[].acknowledgment_layer` | `renamed` | N2 no abbreviations | D-024 | Map the value unchanged |
| `acknowledgments[].ack_scheme` | `acknowledgments[].acknowledgment_scheme` | `renamed` | N2 no abbreviations | D-024 | Map the value unchanged |
| `acknowledgments[].ack_code` | `acknowledgments[].acknowledgment_code` | `renamed` | N2 no abbreviations | D-024 | Map the value unchanged |
| `acknowledgments[].ack_timestamp` | `acknowledgments[].acknowledged_at` | `renamed` | N2, N9 instants end _at | D-024 | Map the value unchanged |
| `acknowledgments[].ack_authenticity_basis` | `acknowledgments[].acknowledgment_authenticity_basis` | `renamed` | N2 no abbreviations | D-024 | Map the value unchanged |
| `acknowledgments[].ack_reason_code` | `acknowledgments[].acknowledgment_reason_code` | `renamed` | N2 no abbreviations | D-024 | Map the value unchanged |
| `acknowledgments[].ack_artifact_ref` | `acknowledgments[].acknowledgment_artifact_ref` | `renamed` | N2 no abbreviations | D-024 | Map the value unchanged |
| `acknowledgments[].ack_artifact_hash` | `acknowledgments[].acknowledgment_artifact_hash` | `renamed` | N2 no abbreviations | D-024 | Map the value unchanged |
| `reconciliation.expected_count_erp` | `reconciliation.erp_expected_count` | `renamed` | N3 class word last, qualifiers first | D-024 | Map the value unchanged |
| `reconciliation.expected_count_mes` | `reconciliation.mes_expected_count` | `renamed` | N3 class word last, qualifiers first | D-024 | Map the value unchanged |
| `reconciliation.statement_count_bank` | `reconciliation.bank_statement_count` | `renamed` | N3 class word last, qualifiers first | D-024 | Map the value unchanged |
| `*.sha256` | `*.hash plus *.hash_algorithm` | `restructured` | N8 no algorithm in a key | D-024 | Move the value to hash; set hash_algorithm to SHA-256 |
| `context.input_trust_classification` | `context.input_trust_class` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `model.reasoning_artifact_availability` | `model.reasoning_artifact_availability_status` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `checks[].name` | `checks[].control_name` | `renamed` | N3 keys fully qualified | D-024 | Map the value unchanged |
| `checks[].material_grade` | `checks[].material_grade_name` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `subject.quantity` | `subject.quantity_value` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `subject.unit` | `subject.quantity_unit` | `renamed` | N3 keys fully qualified | D-024 | Map the value unchanged |
| `subject.drawing_revision` | `subject.drawing_version` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `observed.characteristic` | `observed.characteristic_name` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `observed.nominal_mm` | `observed.nominal_value` | `renamed` | N4 no unit in key; unit in measurement_unit | D-024 | Map the value; read the unit from measurement_unit |
| `observed.tolerance_upper_mm` | `observed.tolerance_upper_value` | `renamed` | N4 no unit in key | D-024 | Map the value; read the unit from measurement_unit |
| `observed.tolerance_lower_mm` | `observed.tolerance_lower_value` | `renamed` | N4 no unit in key | D-024 | Map the value; read the unit from measurement_unit |
| `observed.measured_mm` | `observed.measured_value` | `renamed` | N4 no unit in key | D-024 | Map the value; read the unit from measurement_unit |
| (none) | `observed.measurement_unit` | `added` | N4 the unit travels as a value (UCUM) | D-024 | Expect mm for Golden Trace IND |
| `observed.cpk` | `observed.cpk_value` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `observed.cpk_floor` | `observed.cpk_floor_value` | `renamed` | N3 class word | D-024 | Map the value unchanged |
| `summary.minimum_cpk_observed` | `summary.observed_minimum_cpk_value` | `renamed` | N3 class word last | D-024 | Map the value unchanged |
| `custody.capture_relationship` | `custody.capture_relationship_type` | `renamed` | N3 class word; declared representation pair with custody-ref-v1 | D-024 | Map the value unchanged |
| `custody.signing_trust_ref` | `custody.signing_trust` | `renamed` | N7 an object is not named with a scalar class word | D-024 | Read the same members |

### Conformance harness files (land with gt-v2.1; external runners are told in the release notice)

| File | Earlier keys | Now |
|---|---|---|
| `vectors/expected.json` | `canonical_utf8`, `sha256`, `expect`, `reject`, `reject_code` | `canonical_text`, `canonical_hash` plus `canonical_hash_algorithm`, `expected_result`, `reject_indicator`, `reject_code` |
| `vectors/axes_adv_unicode_beneficiary.json` | `beneficiary` | `beneficiary_name` (the vector also carries every envelope-level rename above) |
| `vectors/predicates.json` | `schema`, `note`, `id`, `description`, `pass_fixtures`, `fail_fixtures`, `fail_mechanism`, `unexercised`, `unexercised_reason`, `required_observations[].check` / `outcome` / `subject`, `credit` | `predicate_format_ref`, `summary_note`, `predicate_id`, `predicate_note`, `pass_fixture_refs`, `fail_fixture_refs`, `fail_mechanism_note`, `unexercised_indicator`, `unexercised_reason_note`, `required_observations[].check_id` / `observed_result` / `subject_ref`, `credit_note` |
| `anchors/gt-v2.0/release_statement.json` | `axes_corpus_release`, `canonicalisation`, `commit`, `chain_head`, `digest_alg`, `tag` | Anchored bytes; never changed. The gt-v2.1 release statement uses `corpus_release_id`, `canonicalization_scheme`, `source_commit_ref`, `chain_head_hash`, `hash_algorithm`, `release_tag_ref` |

### Draft names superseded on 2026-10-04 (never in a published corpus)

| Earlier draft name | Where | Now | Rule |
|---|---|---|---|
| `anchor_service_ref`, `anchor_operator_ref`, `anchor_profile_id` | WO18 A2 (same day) | `anchor_service_id`, `anchor_operator_id`, `anchor_profile_ref` | N10 |
| `axes:opentimestamps-sha256-digest@1`, `axes:rfc3161-sha256-imprint@1`, `axes:x402-correlation@1` | anchoring profiles, WO20 | `axes:opentimestamps_sha256_digest@1`, `axes:rfc3161_sha256_imprint@1`, `axes:x402_correlation@1` | N13 |
| `state`, `state_reason`, `condition`, `subject`, `observed` (verifier results) | `tools/anchoring/verify_anchor.py`, WO19 §4 | `verification_state`, `verification_reason_code`, `verification_condition_code`, `verification_subject_type`, `observed_note` | N3; draft-krausz names are a declared representation pair |
| `description`, `files` | proof manifests | `manifest_note`, `file_hash_algorithm`, `file_hashes` | N3, N8 |
| `workflow_run`, `commit`, `event`, `runner_os` | `anchors/*/last_run.json` | `workflow_run_ref`, `source_commit_ref`, `trigger_event_type`, `runner_os_type` | N3, N10 |
| `release_from`, `release_to`, `decision`, `description` | `schema/key-aliases.json` | `from_release_ref`, `to_release_ref`, `decision_ref`, `summary_note` | N3 |
| `correlation_digest` | WO20, examples | `correlation_hash` plus `correlation_hash_algorithm` (x402 wire spelling `correlationDigest` is the declared pair) | N8, N14 |
| `clock_skew_ms`, `approval_response_latency_ms` | Module 01, BLD-011 | `clock_skew`, `approval_response_latency` (ISO 8601 durations) | N4 |
| `authority_utilisation_ratio` | GAP-EXEC-012 | `authority_utilization_ratio` | N2 |
| `prompt_injection_signal_flag`, `untrusted_content_present_flag`, `retention_immutable_flag` | docs/06 §2, GAP-IA-001 | `prompt_injection_signal_indicator`, `untrusted_content_indicator`, `retention_immutable_indicator` | N5 |
| `size_bytes` | Module 01 artifact references | `byte_count` | N4 |

Further gt-v2.1 entries (the heartbeat-interval rename, the `profile_id` taxonomy of WO19) are added here when their final names are fixed, before the release is cut.
