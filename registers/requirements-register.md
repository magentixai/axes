# SE v0.1 - Master Requirements Register v0.1

**Generated:** 19 July 2026
**Status:** First assembled register. Merges the six persona-wave requirement registers (REQ-*), the six gap analyses (GAP-*), the Standards close-out tracker (TRK-*), and the Programme Blind Spots actions (BLD-*). Every row is traceable to its source document. The REQ-EXEC series is BACKFILLED per BLD-023 (the Executive compression shipped without a formal register); each backfilled row cites its source section.
**Epistemic tag (applies to all persona-sourced rows):** LLM-persona-derived, pending human confirmation (Blind Spots §1).
**Naming (decided 20 July 2026):** the standard is **AXES - Autonomous eXecution Evidence Standard**; the envelope artifact remains the **Standards Envelope (SE)**. All SE references in this register are unchanged and correct.
**Next consumer:** the Master Data Element Decision Register - each row receives a decision (accept-core / accept-conditional / accept-recommended / experimental / derived-only / arbitr-proprietary / presentation-only / defer / reject-with-reason).

**Layer key:** open_se = open SE envelope | derived = derived report layer | implementation_layer = interpretation-layer (implementation territory) layer | presentation = presentation/terminology layer | conformance_rule = normative rule, not a field | standards_package = spec/tooling/governance artifact | programme_action = backlog action, not schema content.

---

## Part A - Primary requirements (persona-wave registers)

### A.1 Business Process Owners (REQ-BPO)
Source: `SE_v0_1_Business_Process_Owners_Data_Element_Compression.md` §13

| ID | Requirement | Priority | Layer | Schema implication |
|---|---|---|---|---|
| REQ-BPO-001 | Identify the business process, process instance, and process step affected by agentic execution | High | open_se | SEProcessContext: business_process_ref/_name, process_owner_ref, process_instance_id, process_step_id, workflow_ref, case_ref, transaction_ref, process_version |
| REQ-BPO-002 | Distinguish expected process path from actual process path | High | open_se + derived | expected/actual_process_path_ref, process_path_alignment_status, step skipped/reordered/unexpected indicators |
| REQ-BPO-003 | Record business rule evaluation evidence and outcome | High | open_se | SEBusinessRuleEvaluation: business_rule_ref/_version/_evaluation_id/_result/_input_ref, policy_violation_indicator, threshold fields |
| REQ-BPO-004 | Link approvals and delegation to process scope and action type | High | open_se | SEAuthorityContext: approval_required_indicator, approval_ref/status/scope/timestamp, approver_ref, approval_bypass_indicator, delegation_receipt_id, capability_id, delegation_scope/limits |
| REQ-BPO-005 | Identify the commit boundary and the business state changed | High | open_se | SECommitBoundary: commit_boundary_indicator/type, commit_event_id, commit_timestamp, system_of_record_ref, pre/post_state_hash, reversibility_status, rollback/compensation fields |
| REQ-BPO-006 | Separate technical success from business outcome status | High | open_se + derived | technical_result_status vs process_outcome_status vs business_outcome_status + outcome vocabulary |
| REQ-BPO-007 | Capture exception, escalation, handoff, retry, fallback, rollback, and compensation lifecycle | High | open_se | SEExceptionLifecycle: exception indicator/type/severity/owner/queue, escalation, handoff, retry_count, fallback_event_id, remediation owner/due/status, closure_status |
| REQ-BPO-008 | Identify customer, employee, financial, legal, service-level, and downstream impact | High | open_se + derived | SEImpactContext: impact_category, per-domain impact indicators, materiality_class, records_affected_count |
| REQ-BPO-009 | Surface evidence gaps at process-step and source-system confirmation level | High | open_se + derived | SEEvidenceQuality: evidence_completeness_status, evidence_gap indicator/type/location/reason/impact, reliance_boundary, source_system_confirmation_status, external_confirmation_ref, reconstruction_confidence |
| REQ-BPO-010 | Provide recommended next business action with owner and due date | Medium | derived + implementation_layer | recommended_business_action, open_action_summary, decision_owner; ARBITR owns prioritisation/playbooks/routing |
| REQ-BPO-011 | Support process-specific terminology mapping through Terminology Profile Registry | High | presentation | terminology_profile_id, client vocabulary mappings, audience/section-visibility profiles |
| REQ-BPO-012 | Support domain profiles for payment, customer, HR, finance, and legal operations | High | open_se (optional profiles) | SEDomainProfile family: payment, legal (privilege/legal_hold), HR (sensitive_workforce_data_indicator), finance (ledger/posting) - profiles must stay optional (§14.5) |
| REQ-BPO-013 | Avoid implying process correctness, legal sufficiency, fairness, compliance, or finality beyond evidence | High | derived (report rule) | Report language rule; ties to reliance_boundary, known_limitations |
| REQ-BPO-014 | Allow exportable evidence packs for operations, risk, compliance, audit, legal, security, technology, finance, customer teams | High | open_se + derived | SEEvidenceArtifactRef + report/export profile |

### A.2 External Assurance (REQ-EXT)
Source: `SE_v0_1_External_Assurance_Data_Element_Compression.md` §12

| ID | Requirement | Priority | Layer | Schema implication |
|---|---|---|---|---|
| REQ-EXT-001 | Distinguish observed evidence, management assertion, derived interpretation, and proprietary analysis | Critical | open_se + derived | evidence_origin_type, assertion_basis, corroboration_state, management_assertion_ref |
| REQ-EXT-002 | Provide population completeness and source reconciliation support | Critical | manifest + open_se | sequence_number, previous_event_hash, population_scope_ref, reporting_period_id; manifest population_definition/completeness/source_reconciliation_status |
| REQ-EXT-003 | Support independent verification through hashes, signatures, key provenance, and canonicalisation | Critical | open_se (core) | event_hash, hash_algorithm, signature, signature_algorithm, signature_key_ref, signing_key_provenance_ref, canonicalisation_version |
| REQ-EXT-004 | Preserve chain of custody, retention, legal hold, and evidence access history | Critical | open_se + arbitr controls | chain_of_custody_ref, custody_event_ref, retention_profile/until, legal_hold_flag/_ref, access_log_ref |
| REQ-EXT-005 | Capture legal entity, jurisdiction, provider, counterparty, and contractual context | High | open_se (conditional) | legal_entity_id, regulated_entity_id, jurisdiction, data_residency_region, provider_id, counterparty_ref |
| REQ-EXT-006 | Represent external confirmations and third-party corroboration | Critical | open_se (conditional) | external_confirmation_ref, receipt_ref, corroboration_state/refs, independent_anchor_ref, cdc_ref |
| REQ-EXT-007 | Represent regulatory, contractual, policy, consent, licence references without becoming a compliance engine | High | profile + derived | licence_or_permission_ref, consent_ref, policy_snapshot_ref, notification_obligation_ref; derived obligation mappings |
| REQ-EXT-008 | Support insurer underwriting and claims analysis (loss, cause, mitigation, coverage references) | Medium-high | derived + profile + proprietary | claim_trigger_indicator; derived loss_event_summary, loss_estimate_band, coverage_trigger_assessment, causation_chain_summary |
| REQ-EXT-009 | Support litigation/dispute exports separating fact, inference, and expert interpretation | High | derived + open_se | evidence_origin_type, assertion_basis, fact/observation/inference markers, exhibit ID, evidence bundle ID, export hash |
| REQ-EXT-010 | Support incident-response use (affected assets, credentials, containment, revocation, remediation refs) | High | open_se security profile + derived | incident_id/severity, containment_status, prompt_injection_signal, credential_risk_signal, boundary crossings, remediation_ref |
| REQ-EXT-011 | Support customer/counterparty assurance without exposing unauthorised tenant data | High | presentation/access + open_se boundary | tenant_id, tenant/provider_boundary_crossed, boundary_type; audience/redaction views |
| REQ-EXT-012 | Support investor due diligence (maturity, trend, exception, dependency, unresolved-issue indicators) | Medium | derived + implementation | investor_due_diligence_summary, control_maturity_summary, evidence_quality_trend, provider_dependency_concentration |
| REQ-EXT-013 | Static PDF insufficient alone; evidence packs must be machine-readable and exportable | Critical | derived (export profile) | Machine-readable pack + manifest as authoritative artifact |
| REQ-EXT-014 | Avoid claims of compliance, safety, legality, or correctness unless directly supported and scoped | Critical | derived (language rule) | limitation_statement_ref, reliance_boundary_status vocabulary |
| REQ-EXT-015 | Record report-generation provenance so the report itself is auditable | Critical | open_se (report manifest) | report_generation_manifest: report_id, profile id/version, generated_at/by, evidence_set_ref, included/excluded_envelope_refs, filter_criteria, interpretation_engine_version, terminology_profile_id, export_hash/signature, redaction_manifest_ref |

### A.3 Internal Assurance (REQ-IA)
Source: `SE_v0_1_Internal_Assurance_Data_Element_Compression.md` requirements register

| ID | Requirement | Priority | Layer | Schema implication |
|---|---|---|---|---|
| REQ-IA-001 | Distinguish the agent being evidenced from the emitter collecting the evidence | High | open_se | emitter_id/type, emitter_independence_level, capture_point, evidence_collection_method |
| REQ-IA-002 | Support monotonic event sequencing and gap detection | High | open_se + derived | event_sequence_number, emitter_stream_id, sequence_gap indicator/count/locations, late_arrival_indicator, duplicate_event_count |
| REQ-IA-003 | State evidence completeness, gaps, and reliance boundary before assurance conclusions | High | derived | overall_evidence_completeness_rating, known_limitations, reliance_boundary |
| REQ-IA-004 | Report claims must trace back to evidence references | High | derived + open_se | claim_id, claim_type, claim_evidence_refs, claim_confidence, claim_limitations (SEReportClaim) |
| REQ-IA-005 | Control evidence distinguishing design, operation, failure, bypass, not-observed, not-applicable | High | open_se (conditional) | Control Evidence structure; control_result vocab incl. operated_with_compensating_control; compensating_control_ref |
| REQ-IA-006 | Risk reporting incl. appetite, tolerance, residual risk, velocity, concentration | High | derived + open_se primitives | risk_domain, risk_taxonomy_tags, risk_appetite_ref; derived inherent/residual_risk_score, risk_velocity_metric, concentration_ratio |
| REQ-IA-007 | Map evidence to specific compliance obligations without unsupported guarantees | High | open_se (conditional) + derived | compliance_obligation_ref, obligation_status vocab, notification_obligation_indicator, breach_assessment_required |
| REQ-IA-008 | Map execution to critical services, dependencies, tolerances, failover, recovery | Medium-High | open_se (conditional) + derived | business_service_id, impact_tolerance_breach_indicator, failover fields, recovery_time/point_actual, rto/rpo refs |
| REQ-IA-009 | Evidence personal-data handling: lawful basis, purpose, transfer, retention, breach assessment | High | open_se (conditional) | personal/sensitive/special_category data indicators, data_subject_category/count, lawful_basis_ref, dpia_ref, cross_border_transfer_indicator |
| REQ-IA-010 | SOC reporting: trust boundary crossings, injection signals, credential risks, containment | High | open_se (conditional) + proprietary | trust_boundary_crossed, prompt_injection_signal, sandbox_escape/data_exfiltration/privilege_expansion signals, containment_action_ref |
| REQ-IA-011 | Fraud/financial-crime: typology tagging, sanctions/AML evidence, suspicious-pattern flags, case refs | Medium-High | open_se (conditional) + derived | sanctions_screening_ref/result, pep_screening_result, aml/fraud rule refs, typology_tag vocab, mule/scam indicators, case_management_ref |
| REQ-IA-012 | Third-party: vendor, contract, SLA, subprocessor, outsourcing, concentration evidence | Medium-High | open_se (conditional) + derived | vendor_id, contract_ref/clause_ref, sla_breach_indicator, subprocessor_ref, exit_plan_ref, vendor_concentration_indicator |
| REQ-IA-013 | Model risk: version, approved use case, validation, monitoring, drift, autonomy evidence | High | open_se (conditional) + derived | model_id/version, model_card_ref, model_validation_ref, model_approved_use_case_ref, drift_signal_indicator, autonomy_level vocab; hidden CoT excluded |
| REQ-IA-014 | Preserve distinction between raw evidence, derived interpretation, human attestation, proprietary scoring | High | architecture principle | value_origin_type vocab, source_assertion/derived/inference indicators, management_assertion_ref, line_of_defence_ref |
| REQ-IA-015 | Support audit sampling, control testing, and reperformance from machine-readable evidence | High | derived + export profile | sampling_frame_id/definition, sample_item_ref, reperformance_status/result, aggregate_to_envelope_count_match |

### A.4 Standards Group (REQ-STD)
Source: `SE_v0_1_Standards_Group_Data_Element_Compression.md`

| ID | Requirement | Priority | Layer | Schema implication |
|---|---|---|---|---|
| REQ-STD-001 | Vendor-neutral SE envelope usable without ARBITR | Critical | open_se | Whole envelope; minimum evidence profile; se_version, schema_uri |
| REQ-STD-002 | Separate open evidence from derived, proprietary interpretation, and presentation | Critical | mixed | Four-layer architecture; layer tag per field |
| REQ-STD-003 | Normative field definitions: type, cardinality, producer responsibility, validation rules | Critical | open_se | Field catalogue / SEFieldRegistry with per-field conformance tests |
| REQ-STD-004 | Canonicalisation rules for hashing and signing | Critical | open_se | canonicalisation_version, hash_algorithm, byte-level test vectors, unknown-field/redaction treatment |
| REQ-STD-005 | Conformance profiles, not all-or-nothing implementation | Critical | open_se | profile_id/version, conformance_level, ~10 named profiles |
| REQ-STD-006 | Extension namespaces, must_understand, collision handling, preservation rules | Critical | open_se | extension_declarations[], extension_namespace/version/schema_uri, must_understand, unknown_field_policy |
| REQ-STD-007 | Machine-readable JSON Schema and validation tooling | Critical | open_se | schema_uri, schema_validation_status, public reference validator |
| REQ-STD-008 | Test vectors and positive/negative examples | Critical | open_se | Test vector corpus incl. negative examples |
| REQ-STD-009 | Core event taxonomy (agent/model/tool/approval/commit/exception/rollback/compensation/gap/boundary) | Critical | open_se | event_kind controlled vocabulary, event_type_version |
| REQ-STD-010 | Precise authority, delegation, capability, commit, result, evidence-quality semantics | Critical | open_se | authority_context_id, delegation_receipt_id, capability_id, commit fields, result_status, evidence_capture_status |
| REQ-STD-011 | Support partial, missing, redacted, inferred, reconstructed evidence without pretending certainty | Critical | open_se | evidence_capture_status, evidence_gap_flag/reason, evidence_origin_type |
| REQ-STD-012 | Privacy-preserving evidence: references, hashes, redaction markers, tombstones | Critical | open_se | *_ref/*_hash pattern, redaction_applied/reason/profile_id, redaction_tombstone_ref, retention_policy_ref |
| REQ-STD-013 | Emission modes: realtime, buffered, batch, backfill | High | open_se | emission_mode, capture_mode/point, backfill_flag, received_at, clock_sync_confidence |
| REQ-STD-014 | Tool-protocol evidence incl. MCP server, tool schema, request/response, side effects, retries, idempotency | High | open_se | mcp_server_*, tool_schema/request/response ref+hash, side_effect_declared/observed |
| REQ-STD-015 | Field registry with stable canonical keys and lifecycle status | High | open_se | SEFieldRegistry, field_registry_uri, field_status/maturity_status vocabularies |
| REQ-STD-016 | Governance process, contribution model, IPR/licensing clarity, change control | High | governance | Changelog, issue process, IPR/licensing statement |
| REQ-STD-017 | No compliance-guarantee, safety-guarantee, or legal-conclusion language | Critical | presentation | Scoped statements only |
| REQ-STD-018 | Interoperability demonstrations across ≥2 independent emitters/consumers | High | tooling/governance | cross_implementation_parse_status |
| REQ-STD-019 | ARBITR proprietary interpretation allowed; conformance independent of ARBITR acceptance | High | architecture/governance | Conformance defined by spec/validator, not ARBITR ingestion |
| REQ-STD-020 | Implementation guidance for small, medium, high-assurance adopters | High | documentation | Progressive adoption path |
| REQ-STD-021 | Unknown-field handling and extension preservation semantics | High | open_se | unknown_field_policy, preserve_unknown_fields, must_understand |
| REQ-STD-022 | Reference/map existing standards rather than reinvent | High | standards alignment | W3C Trace Context, OTel, JSON Schema, JCS, JWS/COSE, VC, SPDX, SCIM, ISO 42001, NIST AI RMF |
| REQ-STD-023 | Minimum evidence profile supporting third-party report generation at basic quality | Critical | open_se | minimum_evidence profile field sets |
| REQ-STD-024 | Security and privacy considerations in the standard package | High | documentation | Privacy/redaction guide, security considerations |
| REQ-STD-025 | Public issue process and extension proposal route | High | governance | Extension registry, promotion path extension→core |

### A.5 Technical Group (REQ-TECH)
Source: `SE_v0_1_Technical_Group_Data_Element_Compression.md`

| ID | Requirement | Priority | Layer | Schema implication |
|---|---|---|---|---|
| REQ-TECH-001 | Record emitter, capture point, capture layer, capture method per envelope | Core | open_se | emitter_id/type/version, capture_point/layer/method/status |
| REQ-TECH-002 | Distinguish realtime, buffered, replayed, backfilled, reconstructed, imported evidence | Core | open_se | emission_mode vocab, replay/backfill indicators, backfill_reason |
| REQ-TECH-003 | Preserve runtime, model, tool, connector, deployment version provenance | Core | open_se | runtime_*/model_*/tool_* fields, image_digest, deployment_ref, build_pipeline_ref, prompt_template_ref, policy/guardrail version refs |
| REQ-TECH-004 | Correlate committed actions to system-of-record or external confirmation | Core | open_se | system_of_record_correlation_id, commit_confirmation_ref, external_confirmation_ref, before/after_state_ref+hash |
| REQ-TECH-005 | Workload identity, service account, credential scope, token lifetime context | Conditional core | open_se | workload_identity_id/issuer/audience, credential_id/type/scope_ref/expires_at/rotation_status |
| REQ-TECH-006 | Declared vs observed topology references for drift detection | Recommended | open_se + derived | declared/observed_topology_ref; derived drift assessment |
| REQ-TECH-007 | Event ordering: trace, span, causation, correlation, sequence | Core | open_se | trace_id, span_id, parent_span_id, lineage_id, causation_id, correlation_id, event_sequence_number, monotonic_sequence_stream_id |
| REQ-TECH-008 | Retries, timeouts, fallback, DLQ, replay, backfill status | Core/conditional | open_se | retry_count, timeout_indicator, fallback_event_id, dlq_indicator/ref, backpressure_indicator |
| REQ-TECH-009 | Security signals as observations with refs and confidence, never attack verdicts | Core | open_se + derived | prompt_injection/credential_risk/privilege_expansion/sandbox_escape/data_exfiltration signals + confidence |
| REQ-TECH-010 | Untrusted content exposure, taint source, taint propagation | Recommended | open_se | untrusted_content_exposure, taint_indicator/source_ref/propagation_ref, input/output_trust_classification |
| REQ-TECH-011 | Prompt/context/RAG/output/guardrail/evaluation refs - no mandatory hidden chain-of-thought | Core | open_se | prompt_ref/hash, context_artifact_refs, rag_source_refs, visible_model_output_ref, guardrail_*, reasoning_artifact_ref only where safely emitted |
| REQ-TECH-012 | Data lineage, contract, schema version, quality checks, downstream dependencies | Conditional | open_se | data_contract_ref, data_quality_check_ref/result, source/target_dataset_id, transformation_ref, lineage_ref |
| REQ-TECH-013 | Source event type, normalisation profile, mapping confidence, unmapped fields | Core (connector profile) | open_se | source_event_type/id/ref, normalisation_profile_id/version, mapping_confidence, unmapped_field_refs |
| REQ-TECH-014 | Machine-readable export with hashes, signatures, verification instructions, raw envelope linkage | Core | mixed | NDJSON/JSON bundle export, verification_instructions_ref, evidence_pack_index |
| REQ-TECH-015 | Support-session grants, scope, actions, ticket refs for ARBITR staff access | Recommended | implementation_layer | support_session_id, support_grant_ref, support_access_scope - not in raw envelopes |
| REQ-TECH-016 | Redaction at source: profile, reason, effect on evidence quality | Core | mixed | redaction_applied(_at_source), redaction_profile_id, redaction_reason |
| REQ-TECH-017 | Product/feature context connecting evidence to customer-facing surfaces | Recommended | mixed | product_area_ref, feature_ref, release_ref, feature_flag_ref, experiment_ref |
| REQ-TECH-018 | Show whether findings rest on observed evidence, corroboration, self-attestation, reconstruction, or interpretation | Core | mixed | evidence_source, evidence_capture_method, capture_layer vocab, capture confidence |
| REQ-TECH-019 | Connector delivery health inspectable: retries, queue, DLQ, ack status, replay | Core (connector profile) | open_se | connector_delivery/health_status, ingestion_ack_status/at, dedupe_status |
| REQ-TECH-020 | Technical report sections: what changed, did it commit, who authorised, is evidence reliable enough to act | Core | presentation | Report profile technical sections |

### A.6 Executive & Board Assurance (REQ-EXEC) - BACKFILLED register
Source: `SE_v0_1_Executive_Board_Assurance_Data_Element_Compression.md`; register backfilled 19 July 2026 per BLD-023. Each row cites its source section.

| ID | Requirement | Priority | Layer | Schema implication | Source §§ |
|---|---|---|---|---|---|
| REQ-EXEC-001 | First-class authority evidence: context, delegation ref + validity window, capability, approval, scope limits, human approval required/present | P1 | open_se | authority_context_id, authority_source_type, delegation_receipt_id/scope/valid_from/until, capability_id, approval_ref, human_approval_required/present | 3.1, 5.5, 8.4 |
| REQ-EXEC-002 | Distinguish advisory activity from real execution: commit status/type/timestamp/evidence, irreversibility class, rollback/compensation, downstream effects | P1 | open_se | commit_boundary_status/type, commit_event_id/timestamp/evidence_ref, irreversibility_class, rollback/compensation refs, downstream_effects_ref | 3.2, 5.6, 6.2–6.3 |
| REQ-EXEC-003 | Evidence quality visible, never assumed: completeness, missing segments, gap reason, integrity, custody, signature, explicit reliance boundary | P1 | mixed | evidence_completeness_status, missing_segment_count, evidence_gap_reason, integrity/custody/signature status, reliance_boundary, known_limitations | 3.3, 4.3, 5.12 |
| REQ-EXEC-004 | Raw evidence and interpretation separable across four layers; every field classed by evidence basis | P1 | mixed | Four-layer descriptor model; raw envelope export; evidence-to-claim refs; report generation audit trail | 1, 3.4, 7, 13.3 |
| REQ-EXEC-005 | Materiality and impact filtering: materiality class + per-domain impact indicators + board-action flags | P1 | mixed | materiality_class, impact_category, *_impact_indicator set, board_action_required, escalation_status | 3.5, 5.8, 6.12 |
| REQ-EXEC-006 | Risk appetite, KRI, control effectiveness: taxonomy, appetite status, gross/residual risk, KRI breaches, control expected-vs-observed, line of defence | P1 | derived | risk_appetite_statement_id/threshold/status, gross/residual_risk_rating, kri_id/value/threshold, control_evaluation_result, line_of_defence | 3.6, 4.2, 4.7, 5.11, 6.9 |
| REQ-EXEC-007 | Audit-grade integrity and reconciliation: ledger/payment/journal refs, state hashes, SoD, deficiency ratings, retention, audit review refs | P1 cond | mixed | reconciliation_status, ledger_entry_ref, payment_confirmation_ref, sod_initiator/approver/executor_ref, sod_break_flag, retention_policy_ref | 3.7, 4.3, 4.5, 5.9 |
| REQ-EXEC-008 | Security expectation breaks as evidence: untrusted content, injection signals, credential exposure, zone transitions, egress, control outcomes, detection timeline | P1 | open_se | untrusted_content flags, prompt_injection_signal, credential exposure indicators, security zones, egress fields, time_to_detect/alert | 3.8, 4.9, 5.13 |
| REQ-EXEC-009 | Regulatory obligation mapping: jurisdiction, regime, obligation status, automated-decision flags, human oversight, lawful basis, notifiable events | P1 cond | mixed | regulatory_regime_list, obligation_met_flag, automated_decision_flag, lawful_basis_ref, notifiable_event_flag, reporting_deadline | 3.9, 4.10, 5.14 |
| REQ-EXEC-010 | Legal exposure track distinct from compliance: entity, accountable person, authority grant document, contract formation, legal hold, privilege, admissibility risk | P1 cond | mixed | legal_entity_id, accountable_natural_person_id, contract_formation_flag, legal_hold_applied_flag, privilege_asserted_flag, spoliation_risk_flag | 3.9, 4.11, 5.15, 13.4 |
| REQ-EXEC-011 | AI behaviour governance without hidden chain-of-thought: model/prompt/context/RAG refs+hashes, guardrails, evaluations, expected-vs-observed, drift | P1 | mixed | model_id/version/provider, prompt_hash, rag_source_refs, guardrail_ref/status, behaviour_alignment_status, drift_indicator | 3.10, 4.12, 5.16, 13.2 |
| REQ-EXEC-012 | Attestation container attachable to reports/bundles/event sets: attestor identity/role/line of defence, assurance level, basis, limitations, signed statement | P1 | open_se | attestation_id/scope/statement, attestor_id/role/line_of_defence, assurance_level/basis/limitations, attested_at, signature_ref | 10, 6.10–6.11 |
| REQ-EXEC-013 | Report metadata: ID, version, profile, generation time, evidence period, scope, audience profile, generation audit trail | P1 | presentation | report_id/version/profile, report_period_start/end, audience_profile, terminology_profile_id, report_generation_audit_ref | 5.1 |
| REQ-EXEC-014 | Conditional financial fields where agents touch money: value, currency, counterparty, account/ledger/payment/invoice refs, thresholds | P1 cond | mixed | monetary_value, currency, counterparty/beneficiary/account refs, financial_materiality_threshold_ref | 4.5, 5.9 |
| REQ-EXEC-015 | Operational process conformance: process/workflow identity+version, expected-vs-actual steps, SLA, latency, escalation, intervention, resilience | P1 cond | mixed | process_id, workflow_id/version, expected_step_list_hash, process/sla_conformance_status, escalation/intervention event ids | 4.6, 5.10 |
| REQ-EXEC-016 | Topology and cross-scope continuation: run/node refs, boundary type/crossings, continuation and handoff refs, source/target provider+tenant | P1 | open_se | topology_run_id, execution_node_id, boundary_type, boundary_exit/entry_event_id, continuation_ref, handoff_token_ref | 4.8, 5.17, 8.8 |
| REQ-EXEC-017 | Prohibit guaranteed compliance/safety/correctness language; scoped assurance only | - | presentation | Report language rule; confidence + evidence-basis fields | 13.1 |
| REQ-EXEC-018 | Draft controlled vocabularies early (13 domains) to prevent interpretation drift | - | open_se | event_kind, commit status/type, completeness/integrity, divergence, control outcome, appetite, assurance level, line of defence, materiality, reliance boundary | 6.1–6.13 |
| REQ-EXEC-019 | Serve all twelve executive roles from one evidence object with role-specific report entry points | - | presentation | Role-to-section mapping; 18-section MVAR profile | 11, 14.3 |
| REQ-EXEC-020 | Broad schema from v0.1 via maturity labels rather than omission | - | open_se | core/conditional/recommended/experimental/reserved/extension/deprecated per field | 12, 16 |
| REQ-EXEC-021 | Minimum open SE field spine sufficient for a third party to generate a ~50%-credible report | P1 | open_se | ~70-field minimum set: identity/sequencing, org scope, actor, authority, action/target, commit, evidence, boundary, security | 8, 15.1, 16 |
| REQ-EXEC-022 | Minimum derived report set - computable, explainable, traceable to SE evidence | P1 | derived | execution_summary, authority_assessment, materiality_rating, reconstruction_confidence, board_action_required | 9, 7.2, 15.2 |
| REQ-EXEC-023 | Scoring, narratives, packs, terminology mapping, benchmarking, workflow stay implementation-layer | - | implementation_layer | Assurance/risk scores, pack generation, Terminology Profile Registry, benchmarking | 7.3, 15.3 |
| REQ-EXEC-024 | Maintain a report-to-field requirements matrix mapping each report statement to required fields | - | mixed | Report-to-Field Requirements Matrix | 14.2 |

---

## Part B - Gap-derived requirements (GAP-*)
Source: the six second-eyes gap analyses. Tier-1 sourced gaps with schema/standard implications. "Dup" = clearly the same underlying item.

### B.1 Executive gap analysis (GAP-EXEC)

| ID | Gap/requirement | Severity | Layer | Implication | Dup |
|---|---|---|---|---|---|
| GAP-EXEC-001 | Live vs simulated execution not expressible | HIGH | open_se | execution_mode: live/shadow/simulation/dry_run/test/replay | - |
| GAP-EXEC-002 | Two-sided non-repudiation: our record vs counterparty acknowledgment | HIGH | open_se + derived | Acknowledgment ladder rungs 0–5: acknowledgment_refs[], ack_authenticity_basis, counterparty_evidence_strength; companion discovery/confirmation specs; scheme mapping registry | - |
| GAP-EXEC-003 | Timestamp anchoring and multi-party custody | HIGH | open_se | time_anchor_ref + anchoring_method, witness_signature_refs, runtime_attestation_ref (experimental) | - |
| GAP-EXEC-004 | Orchestrator missing as first-class actor | HIGH | open_se | orchestrator_id/version; divergence vocab additions (unexpected model/runtime/provider/orchestration change) | - |
| GAP-EXEC-005 | Point-in-time policy/permission versioning; period-vs-point assurance marker | HIGH | open_se | policy_ref + policy_version_in_effect, effective_permissions_ref, assurance_period_type | - |
| GAP-EXEC-006 | Quantified evidence coverage against a defined population | HIGH | open_se + derived | evidence_population_ref, evidence_coverage_ratio, tamper_evident_coverage_ratio | - |
| GAP-EXEC-007 | Containment and autonomy state-change events absent from event_kind | MED-HIGH | open_se + derived | containment_action, authority_revoked/suspended, autonomy_state_changed event kinds; time_to_contain_seconds | - |
| GAP-EXEC-008 | When controls were evaluated (prevention vs detection) | MED-HIGH | open_se | control_evaluation_phase (pre_commit/at_commit/post_hoc), precheck_results_ref | - |
| GAP-EXEC-009 | Insurer audience omitted from reliance vocab, packs, report profile | MED-HIGH | derived + package | insurance_notification_support, insurance_relevance_indicator, insurer pack/report flavour | - |
| GAP-EXEC-010 | Override, review attribution, recurrence, exception lifecycle fields | MEDIUM | derived | control_override_indicator, management_response_ref, reviewer_ref, prior_occurrence_count, exception_age/closure_status | - |
| GAP-EXEC-011 | Reproducibility/inference configuration underweighted | MEDIUM | open_se + derived | model_parameters_ref → P2; random_seed_ref, environment_spec_ref, replay_recipe_ref | - |
| GAP-EXEC-012 | Boundary proximity quantification (near-miss leading indicators) | MEDIUM | derived | authority_utilisation_ratio, guardrail_near_miss_count, threshold_proximity_band | - |
| GAP-EXEC-013 | Redaction lacks privileged review path | MEDIUM | open_se | redaction_escrow_ref, redaction_clearance_level | - |
| GAP-EXEC-014 | Absence of reasoning artifacts disclosable, not silent | MEDIUM | open_se | reasoning_artifact_availability (available/provider_withheld/not_captured/redacted) | - |
| GAP-EXEC-015 | Infra-change scope field (CTO personas, 3 files) | LOW-MED | open_se | change_blast_radius | - |
| GAP-EXEC-016 | SOX/ICFR relevance flags undefined | LOW-MED | derived | financial_statement_relevance_flag / icfr_relevance_indicator | - |
| GAP-EXEC-017 | Graded input trust vs single boolean | LOW-MED | open_se + derived | input_sources[] with trust_classification; boolean becomes derived rollup | - |
| GAP-EXEC-018 | Execution cost / token utilisation | LOW-MED | open_se | execution_cost_ref (P3 cond) | - |
| GAP-EXEC-019 | Gap-reason vocab can't express cost-driven truncation or sampling | LOW-MED | open_se | Add cost_optimisation_truncation, sampling to gap-reason vocab | - |
| GAP-EXEC-020 | Evidence bundle lacks identity/integrity fields | LOW-MED | open_se | evidence_bundle_id + bundle_manifest_hash | - |
| GAP-EXEC-021 | Versioned policy/control refs are not sufficient for independent re-evaluation: need content-addressed **control-context snapshot** (policy + permissions + reference-data digests), evaluated-input digest, effective dating, and declared evaluation profile - without turning AXES into a policy engine | HIGH | open_se + conformance_rule | policy_snapshot_ref + digest / control_context_hash; effective_from/until on versioned control refs; evaluated_input_digest; evaluation_profile_id; reproducible vs observed_only check rule; control-re-evaluable conformance surface | GAP-EXEC-005, REQ-EXT-007, TRK-024, CRE-* |

### B.2 Technical gap analysis (GAP-TECH)

| ID | Gap/requirement | Severity | Layer | Implication | Dup |
|---|---|---|---|---|---|
| GAP-TECH-001 | External evidence anchoring: chain must terminate outside the system under investigation | HIGH | open_se + derived | external_anchor_ref, anchoring_method, anchored_at, anchoring_latency_ms; anchoring_verification_summary, unanchored_envelope_register | GAP-EXEC-003 |
| GAP-TECH-002 | execution_mode - second-wave confirmation, core status | HIGH | open_se | execution_mode (core) | GAP-EXEC-001 |
| GAP-TECH-003 | Emission fail-posture unrecorded; defines evidentiary meaning of silence | HIGH | open_se + derived | emission_fail_posture (fail_closed/fail_open/mixed/unknown); fail_posture_window_summary | - |
| GAP-TECH-004 | Sampling/determinism parameters need defined structure | MED-HIGH | open_se | sampling_parameters block, random_seed_ref; "reproducible in distribution, not in instance" language | GAP-EXEC-011 |
| GAP-TECH-005 | Corroboration family needs a named module | MED-HIGH | open_se | Corroboration module: corroboration_ref + source_type, cdc_correlation_ref, fail-posture, anchoring, ack_authenticity_basis | - |
| GAP-TECH-006 | Dereference access control unowned | MED-HIGH | package + derived | Reference Resolution section; ref_resolution_status | - |
| GAP-TECH-007 | Erasure vs immutability must be stated normatively | MED-HIGH | conformance_rule | Refs+hashes immutable; referenced content crypto-shreddable; content_erased resolution | - |
| GAP-TECH-008 | Versioned conformance levels, open reference emitter, open test suite, conformance declaration; connector trust registry (open suite + implementation-side registry) | MED-HIGH | package + implementation | Open reference emitter + test suite; conformance_declaration_ref; implementation-side registry/badges | - |
| GAP-TECH-009 | Idempotency key custody across boundaries | MEDIUM | open_se | idempotency_key_forwarded / per-hop custody | - |
| GAP-TECH-010 | Consent linkage and shown-vs-actual divergence | MEDIUM | open_se + derived | consent_event_ref, user_disclosure_ref, shown_vs_actual_divergence | - |
| GAP-TECH-011 | Structured Finding/Action and Timeline object models | MEDIUM | derived | Finding/Action object (id/severity/owner/confidence/action_status); Timeline entry object | GAP-EXEC-010 (partial) |
| GAP-TECH-012 | Gateway identity missing from provenance | LOW-MED | open_se | tool_gateway_id, model_gateway_id | - |
| GAP-TECH-013 | Policy bypass missing from security-signal vocab | LOW-MED | open_se | policy_bypass_signal | - |
| GAP-TECH-014 | W3C Trace Context / OTel interop never stated | LOW-MED | package | SE trace identity SHOULD be W3C Trace Context compatible | - |
| GAP-TECH-015 | Publish emission overhead characteristics per profile | LOW-MED | package | Overhead guidance artifact | - |
| GAP-TECH-016 | Anti-sampling conformance rule for commit-boundary streams | LOW-MED | conformance_rule | No sampling/pre-aggregation of commit-boundary streams | - |
| GAP-TECH-017 | Fault-domain attribution with confidence banding | LOW-MED | derived | fault_domain_indication | - |
| GAP-TECH-018 | Replay side-effect safety assessment | LOW-MED | derived | replay_safety_assessment | - |
| GAP-TECH-019 | Not-a-certification disclaimer | LOW-MED | derived | not_a_certification_notice | - |

### B.3 Internal Assurance gap analysis (GAP-IA)

| ID | Gap/requirement | Severity | Layer | Implication | Dup |
|---|---|---|---|---|---|
| GAP-IA-001 | External anchoring + immutable-storage/retention proof (SEC 17a-4, MiFID II WORM) | HIGH | open_se | timestamp_authority_reference (RFC 3161), hash_anchor, envelope_signature_chain[], retention_immutable_flag, retention_immutability_ref | GAP-EXEC-003 |
| GAP-IA-002 | Unified Access & Restriction Model incl. finding-level restriction (tipping-off) | HIGH | package + open_se | finding_access_class (…/tipping_off_restricted), restriction_basis_ref; restriction metadata must not leak | supersedes GAP-EXEC-013 + GAP-TECH-006 |
| GAP-IA-003 | Per-action conformance ≠ assurance (compliant-fraud-instrument pattern) | HIGH | conformance_rule | Aggregate-pattern report section; absence-of-analysis disclosed as limitation | - |
| GAP-IA-004 | Typed correlation-key family (six members) | MED-HIGH | open_se | correlation_keys[]: counterparty, data_subject (pseudonymous), incident, recovery_session, equivalent_input, attack_trace | - |
| GAP-IA-005 | Privacy-by-design constraint: personal data by reference + pseudonymous subject key, never embedded | MED-HIGH | conformance_rule | Immutable envelopes + erasable content + separately-held subject keys | - |
| GAP-IA-006 | Third-party touchpoint exhaustiveness; shadow-invocation detection | MEDIUM | conformance_rule + derived | third_party_touchpoint_set; shadow-dependency detection vs vendor register | - |
| GAP-IA-007 | Interpretation outputs carry maintained-library versions | MEDIUM | derived + implementation | typology_library_version, obligation_taxonomy_version, etc. | - |
| GAP-IA-008 | Granting principal of a delegation never captured | LOW-MED | open_se | delegator_user_id → canonical delegator_id | - |
| GAP-IA-009 | Override indicator on control evidence | LOW-MED | derived | override_indicator | GAP-EXEC-010 (partial) |
| GAP-IA-010 | policy_violation_signal naming reconciliation | LOW-MED | open_se | Vocabulary harmonisation | - |
| GAP-IA-011 | IPE reliability terminology in audit-facing profile | LOW-MED | package | Terminology profile entry | - |
| GAP-IA-012 | SAR/case fields report-side under tipping-off restriction | LOW-MED | derived | sar_status (tipping_off_restricted); legal-hold cross-ref | - |
| GAP-IA-013 | Delegation-scope serialisation format open question | LOW-MED | package | delegation_scope structure (scope_json) | - |

### B.4 BPO gap analysis (GAP-BPO)

| ID | Gap/requirement | Severity | Layer | Implication | Dup |
|---|---|---|---|---|---|
| GAP-BPO-001 | Commitment/promise evidence: agent utterances as commit boundaries | HIGH | open_se + derived | commitment_made_indicator, commitment_detail_ref; promise_breach_indicator, commitment_policy_alignment_status | - |
| GAP-BPO-002 | Identity verification and consent-authority matching | MED-HIGH | open_se + derived | identity_verification_ref/status; consent_authority_match | - |
| GAP-BPO-003 | Cross-customer exposure within a tenant | MED-HIGH | derived | cross_customer_exposure_indicator; customer-scoped data-boundary semantics | - |
| GAP-BPO-004 | Maker-checker / dual-control fields absent in all waves | MED-HIGH | open_se | dual_control_required_indicator, maker_ref/checker_ref, second_approver_ref; merge with sod_* cluster | - |
| GAP-BPO-005 | Deadline/cut-off/value-date cluster | MEDIUM | open_se | deadline_ref + deadline_type + deadline_impact_indicator; payment profile value_date, settlement_date, scheme_rules_ref | - |
| GAP-BPO-006 | Complaint linkage (regulated process) | MEDIUM | open_se + derived | complaint_ref; complaint_risk_indicator | - |
| GAP-BPO-007 | Treatment-consistency indicator over equivalent_input_key | MEDIUM | derived | treatment_consistency_indicator (never asserts fairness as legal fact) | - |
| GAP-BPO-008 | Per-action expected-vs-actual refs (harmonise with TG) | LOW-MED | open_se | expected_action_ref / actual_action_ref | - |
| GAP-BPO-009 | Recommended timeframe on Action object | LOW-MED | derived | recommended_timeframe | GAP-TECH-011 (partial) |
| GAP-BPO-010 | Employee representation/consultation evidence (HR profile) | LOW-MED | open_se | employee_consultation_ref | - |
| GAP-BPO-011 | Minimum-set dependency statement for duplicate-payment detection | LOW-MED | package | State dependency on provider_id, idempotency_key, sequence_number, correlation_id, recorded_at | - |

### B.5 External Assurance gap analysis (GAP-EA)

| ID | Gap/requirement | Severity | Layer | Implication | Dup |
|---|---|---|---|---|---|
| GAP-EA-001 | Field-level redaction-tolerant integrity structure - pre-JSON-Schema core decision | HIGH | package | How event_hash is computed (salted per-field hashes / Merkle envelopes); decides canonicalisation | - |
| GAP-EA-002 | Agent disclosure marker | HIGH | open_se | agent_disclosure_status (+_ref), conditional on counterparty-facing actions | - |
| GAP-EA-003 | Transaction-time outbound receipt at commit | HIGH | open_se | outbound_receipt_ref/hash on commit events | GAP-EXEC-002 (partial) |
| GAP-EA-004 | Courtroom authentication: records-custodian support, FRE 902 self-authentication path, append-only amendment model | HIGH | open_se + package + implementation | amendment_event_ref, supersedes_envelope_id, amendment_reason; custodian obligations; published verification procedure | - |
| GAP-EA-005 | Underwriting representation conformance | MED-HIGH | open_se + derived | underwriting_representation_ref; representation_conformance_status | - |
| GAP-EA-006 | Graded prompt-injection likelihood | LOW-MED | derived | prompt_injection_likelihood_indicator | - |
| GAP-EA-007 | Jurisdiction terminology variants | LOW-MED | package | jurisdiction_terminology_variant in Terminology Profile Registry | - |
| GAP-EA-008 | Triage ordering for evidence gaps | LOW-MED | derived | evidence_gap_priority | - |
| GAP-EA-009 | Claim-cited narratives (per-sentence claim→evidence citation) | LOW-MED | implementation_layer | Narrative generator citation discipline; SEReportClaim | - |

### B.6 Standards gap analysis (GAP-STD)

| ID | Gap/requirement | Severity | Layer | Implication | Dup |
|---|---|---|---|---|---|
| GAP-STD-001 | IPR and patent posture is the adoption gate - decide before candidate draft | HIGH | package | Royalty-free patent pledge (SE core), CC-BY-4.0 spec, Apache-2.0 code, DCO/no-assignment; written boundary: ARBITR interpretation stays protectable | - |
| GAP-STD-002 | Reference implementation wrongly placed proprietary; open layer must include emitter, validator, test vectors, Annex D basic derived fields | HIGH | package | Move to open layer | GAP-TECH-008 (partial) |
| GAP-STD-003 | Boundary receipts supply side; corroboration coverage decomposition | HIGH | open_se + derived | Receipt slot with scoped semantics; corroboration_coverage_decomposition (anchored/receipted/co_emitted/provider_only) | GAP-EXEC-002 (partial) |
| GAP-STD-004 | Tool manifest identity and conformance missing from MCP profile | MEDIUM | open_se + derived | tool_manifest_ref/hash; manifest_conformance_status | - |
| GAP-STD-005 | Redaction-tolerant hashing recorded as team design decision | note | package | Canonicalisation spec tombstone/hash-substitution rules | GAP-EA-001 |
| GAP-STD-006 | ISO 20022 scheme mapping registry (synthesis recommendation) | note | package | Registry referencing ISO 20022/SWIFT/EDI/AS2 | GAP-EXEC-002 (partial) |
| GAP-STD-007 | FRE 902 self-authentication as standards-recognition strategy | note | package | Standards-body recognition pathway | GAP-EA-004 (partial) |
| GAP-STD-008 | Add SCITT and RFC 3161 to existing-standards profiling list | note | package | Profiling list additions | GAP-IA-001 (partial) |

---

## Part C - Consolidated programme close-out tracker (TRK-*)
Source: `SE_v0_1_Standards_Compression_Gap_Analysis.md` §4

| ID | Item | Layer | Cross-refs |
|---|---|---|---|
| TRK-001 | External anchoring + witness chains + WORM proof (5-wave sourced) - elevate maturity; GT v1 SIMULATED store disclosed (D-015 / EB-*); profile EvidenceAnchor-class backends without AXES implementing runtime ABCs | open_se | GAP-EXEC-003 / GAP-TECH-001 / GAP-IA-001; docs/interop/x402-and-anchoring.md |
| TRK-002 | execution_phase + execution_mode - EA two-field semantics adopted | open_se | GAP-EXEC-001 / GAP-TECH-002 |
| TRK-003 | Acknowledgment ladder + outbound receipts + receipt slot (demand/legal/supply validated) | open_se + derived | GAP-EXEC-002 / GAP-EA-003 / GAP-STD-003 |
| TRK-004 | Access & Restriction Model - one normative section | package | GAP-IA-002 |
| TRK-005 | Field-level redaction-tolerant hashing - decide before JSON Schema | package | GAP-EA-001 |
| TRK-006 | Append-only amendment model - required for admissibility | open_se | GAP-EA-004 |
| TRK-007 | Findings/Action object - restrictable, ageable, owned (5-wave confirmed) | derived | GAP-TECH-011 / GAP-EXEC-010 |
| TRK-008 | Commitment/promise evidence + contractual_commitment commit type (3-wave) | open_se + derived | GAP-BPO-001 |
| TRK-009 | Agent disclosure marker - cheap to standardise now | open_se | GAP-EA-002 |
| TRK-010 | Correlation-key family | open_se | GAP-IA-004 |
| TRK-011 | Aggregate-pattern principle - per-action conformance ≠ assurance (assurance-critical: envelope validity alone must never be presented as assurance) | conformance_rule | GAP-IA-003 |
| TRK-012 | Population completeness: sequence continuity + source reconciliation, two proofs | open_se + derived | GAP-EXEC-006 |
| TRK-013 | Emission fail-posture - adopt | open_se | GAP-TECH-003 |
| TRK-014 | Inference/sampling parameters block + replay scoping (3-wave) | open_se | GAP-EXEC-011 / GAP-TECH-004 |
| TRK-015 | Insurer audience + underwriting representation conformance | open_se + derived | GAP-EXEC-009 / GAP-EA-005 |
| TRK-016 | Erasure vs immutability (crypto-shred + subject-key separation) - state once, normatively | conformance_rule | GAP-TECH-007 / GAP-IA-005 |
| TRK-017 | IPR/patent posture - decide before publication | package | GAP-STD-001 |
| TRK-018 | Open reference implementation + Annex D derived fields - move out of proprietary | package | GAP-STD-002 |
| TRK-019 | Conformance ladder + test vectors + connector trust registry (open suite + implementation-side registry) | package + implementation | GAP-TECH-008 |
| TRK-020 | Vocabulary harmonisation (4 event_kind variants, 4 commit_boundary variants, 3 provenance axes) | package | Harmonisation sheet |
| TRK-021 | Tool manifest conformance | open_se + derived | GAP-STD-004 |
| TRK-022 | Records-custodian operation + self-authentication strategy | implementation + package | GAP-EA-004 |
| TRK-023 | SEQUENCING RULE: settle the five pre-schema design decisions (canonicalisation incl. redaction-tolerant hashing, amendment model, access & restriction model, receipt slot, IPR) before Field Catalogue → matrix → JSON Schema | programme_action | BLD-024 |
| TRK-024 | Three-layer evidence coverage (decision / control-in-force / outcome) + path to independent control re-evaluation - surface honestly now; close L2 via content-addressed control-context (D-014) | open_se + package + conformance_rule | GAP-EXEC-005/021, REQ-EXT-007, P1-1/3/4; tracker: [`three-layer-evidence-and-control-reevaluation.md`](three-layer-evidence-and-control-reevaluation.md) |

---

## Part D - Programme blind spots & pre-catalogue actions (BLD-*)
Source: `SE_v0_1_Programme_Blind_Spots_and_Pre_Catalogue_Actions.md`

| ID | Action/item | Layer | Cross-refs |
|---|---|---|---|
| BLD-001 | Recruit 3–5 human design partners (external auditor, E&O underwriter/claims, payment-ops lead) before candidate draft; test the golden sample report, not the schema | programme_action | - |
| BLD-002 | Divergence log: persona requirement vs human-partner reaction, feeding priority scores | programme_action | - |
| BLD-003 | Extend validation beyond report content: price tolerance, integration ceiling, buying centre, displacement | programme_action | - |
| BLD-004 | Seventh mini-wave: Attacker, Opposing Counsel, Respondent Organisation, Affected Individual | programme_action | - |
| BLD-005 | Threat model document in the standards package | standards_package | - |
| BLD-006 | Human identifiers follow pseudonymous-key + payload-by-reference + access-restriction discipline (generalised subject-key separation) | conformance_rule | GAP-IA-005 |
| BLD-007 | Employee-monitoring/works-council note in EU implementation guidance; employee_consultation_ref as hook | standards_package | GAP-BPO-010 |
| BLD-008 | Positioning language re monitoring people, before a works council asks | programme_action | - |
| BLD-009 | Heartbeat/liveness: detect silence when nothing arrives | open_se + derived | - |
| BLD-010 | Document heartbeats + sequence continuity + fail-posture as one "silence semantics" cluster | standards_package | GAP-TECH-003 |
| BLD-011 | approval_requested_at / approval_granted_at → approval_response_latency_ms | open_se | - |
| BLD-012 | Rubber-stamp pattern detection (implementation layer, scoped language only) | implementation_layer | BLD-011 |
| BLD-013 | Report rule: approval-reliant assurance statements disclose approval-volume and latency context | conformance_rule | - |
| BLD-014 | Evidence cost model per implementation profile | standards_package | GAP-TECH-015 |
| BLD-015 | Dogfood: ARBITR emits SE evidence about its own pipeline, externally anchored; publishes own assurance pack | implementation_layer | - |
| BLD-016 | ARBITR certifications roadmap (SOC 2 etc.) before enterprise sales need it | programme_action | - |
| BLD-017 | agent_identity_assertion_ref (experimental) - slot for verifiable cross-org agent identity | open_se | - |
| BLD-018 | Standards-venue strategy decided as part of the IPR package (coupled decisions) | programme_action | GAP-STD-001/007 |
| BLD-019 | Adjacent-standards watch (OTel GenAI, SCITT, C2PA, VC, NIST/OWASP agentic) with profile-or-differentiate decisions | programme_action | - |
| BLD-020 | Golden trace as architecture test, test-vector seed, and third-party report test - **DONE** (APRUN-2026-06-09-A built; 6 schema findings fed back) | programme_action | - |
| BLD-021 | Rejection/deferral register with rationale; nothing deleted, only staged | programme_action | - |
| BLD-022 | Prioritisation function: waves-sourcing × report-statement dependency (A–D weighted) × implementability per profile | programme_action | - |
| BLD-023 | Backfill REQ-EXEC and REQ-BPO registers before master merge - **REQ-EXEC done in this register (A.6); REQ-BPO existed** | programme_action | - |
| BLD-024 | Single master tracker: merge TRK + BLD into one backlog; five pre-schema decisions at its head | programme_action | TRK-023 |
| BLD-025 | Heartbeat cluster fields (heartbeat_event, declared_heartbeat_interval, liveness_status, silent-window register) | open_se + derived | BLD-009 |
| BLD-026 | approval_response_latency_ms + rubber-stamp detection | open_se + implementation_layer | BLD-011/012 |
| BLD-027 | agent_identity_assertion_ref | open_se | BLD-017 |
| BLD-028 | Human-reference pseudonymisation rule | conformance_rule | BLD-006 |
| BLD-029 | Threat model, evidence cost model, ARBITR self-evidence pack | standards_package + implementation | BLD-005/014/015 |
| BLD-030 | Run the Executive-wave 10-point requirements-governance re-pass (layer placement, claim traceability, reliance wording, conformance-before-reliance, dangerous-to-encode-as-fact, missing vocabulary): the addendum instruction was introduced mid-programme, so the Executive wave ran without it; waves 2–6 absorbed it. Backfilled REQ-EXEC rows partially compensate; the dedicated re-pass is outstanding and should complete before Executive-sourced catalogue modules freeze | programme_action | REQ-EXEC (backfill), GAP-EXEC-* |
| BLD-031 | **ARBITR backlog: Agent 365 / Purview import pack** - ingest Agent 365 OTel (`CloudAppEvents` / observability exporter) and Purview unified audit (CopilotInteraction and related AI record types) into SE envelopes per [`docs/interop/agent365-purview-se-mapping.md`](../docs/interop/agent365-purview-se-mapping.md); join to non-M365 emitters; surface independence caveat in packs (Microsoft log ≠ independent evidence); deliver connector + fixture corpus + report delta vs Golden Trace. Magentix AI commercial battlecard is proprietary (not in this repo) | implementation_layer | REQ-STD-019; adjacent-standards watch |

---

## Golden Trace feedback items (GT-*)
Source: `Example_Golden_Report_Output/README.md` §"Schema findings" - practice-sourced, highest evidentiary weight (only non-LLM-derived rows in this register).

| ID | Finding | Layer | Implication |
|---|---|---|---|
| GT-001 | source_system_reconciliation needed as event_kind (absent from all four wave vocabularies) | open_se | Add to canonical event_kind merge |
| GT-002 | heartbeat_event confirmed necessary in practice | open_se | Confirms BLD-009/025 |
| GT-003 | Acknowledgment-ladder rungs accrete across envelopes over time; catalogue must state this | standards_package | Ladder spec note (commit envelope + later reconciliation envelope) |
| GT-004 | Hash-scope discipline: excluding signing_key_id from hash input and post-hash envelope_id assignment silently weaken the chain | standards_package | Concrete argument for byte-level test vectors; this trace seeds them |
| GT-005 | authority_utilisation_ratio converts pass/fail into a leading indicator (95.6% case) | derived | Confirms GAP-EXEC-012; adopt early |
| GT-006 | outside_capture_boundary works as honest disclosure (interbank pacs.008 leg); capture-boundary declaration belongs in every regulator pack | open_se + conformance_rule | Confirms EA capture_status semantics |


---

## EU AI Act review additions (EU-*)
Source: `EU-AI-ACT_Analysis_transcript.md` (steward regulatory review, 2026-07-22) cross-checked against the register. Regulation-sourced rows: the EU AI Act is demand-side evidence, and the only non-persona, non-practice source in this register. Article numbers cite Regulation (EU) 2024/1689 as amended by the 2026 Digital Omnibus; timeline verified against legal press 2026-07-22.

| ID | Requirement | Source | Layer | Schema implication | Notes |
|---|---|---|---|---|---|
| EU-001 | Evidence the oversight actor's competence and authorisation basis, not just their presence | Art 14/26 | open_se (conditional) | oversight_actor_ref, oversight_authority_basis, competence_ref in Module 03/12 | Extends approval cluster; pairs with approval-latency (BLD-011) |
| EU-002 | Record whether human intervention occurred before or after the commit boundary | Art 14 | open_se (conditional) | intervention_phase (pre_commit / at_commit / post_commit) | Pairs with control_evaluation_phase (GAP-EXEC-008); prevention-vs-reaction is the load-bearing distinction |
| EU-003 | Evidence AI-interaction disclosure: required, displayed, method | Art 50 (applies 2026-08-02) | open_se (conditional) | disclosure_required, disclosure_displayed, disclosure_method; extends agent_disclosure_status (TRK-009) | Regulatory deadline attached to an existing adopted field |
| EU-004 | Evidence machine-readable content marking: required, applied, synthetic-content classification | Art 50 | open_se (conditional) | marking_required, marking_applied, synthetic_content_classification, human_editorial_review_ref | New cluster; C2PA profiling candidate (standards watch) |
| EU-005 | Evidence substantial modification and reassessment triggers | Lifecycle articles | open_se (conditional) + derived | substantial_modification_assessment_ref, reassessment_required | Pairs with versions-in-force cluster and drift signals |
| EU-006 | Regulatory identity references: ai_system_id, intended_purpose_ref, risk_classification (+ basis), conformity/registration refs | Provider/deployer obligations | conditional PROFILE (never canonical core) | Regulatory profile; keeps the core regulation-neutral per doctrine | Placement rule: field slots open, article mapping implementation-layer (see EU-009) |
| EU-007 | Deployer log custody and minimum six-month retention | Art 12/26 | conformance guidance | Existing retention_profile/retention_until fields; implementation-guidance note + evidence cost model input | Also the deployer-custody argument: third-party or chain records are not the deployer's evidence store |
| EU-008 | Incident timing machinery: discovery, escalation, notification deadline, provider/authority notification refs | Serious-incident reporting | open_se (conditional) | incident_discovered_at, escalated_at, notification_deadline, provider/authority_notification_ref | Enriches REQ-EXEC-009 / REQ-IA-007 |
| EU-009 | Open-slots vs proprietary-mapping rule: evidence field slots are open AXES; regulation article mapping, readiness scoring and regulator-pack generation are implementation layer | Architecture rule | conformance_rule | Prevents a third party claiming the open EU-mapping ground over the standard | Decision D-013 |

---

## Three-layer evidence coverage & control re-evaluation (TLC-* / CRE-*)
Source: programme decision D-014. Full task list, doctrine constraints, and acceptance test: [`three-layer-evidence-and-control-reevaluation.md`](three-layer-evidence-and-control-reevaluation.md). Stimulus: external agent-governance convergence on three bound artifacts (decision, control-in-force, outcome); AXES responds in the evidence lane only.

| ID | Item | Layer | Cross-refs |
|---|---|---|---|
| TLC-001 | README working envelope shape (exemplar) - never "the schema" | standards_package | D-006, D-014 |
| TLC-002 | Three-moment illustration (policy-check / control refs / commit+ack) | standards_package | Golden Trace samples |
| TLC-003 | Informative `docs/interop/three-layer-evidence-coverage.md` with L2 gap disclosed | standards_package | TRK-024 |
| TLC-004 | Root CONFORMANCE.md: corpus verify ≠ SE-Cx claim; docs/07 stays normative | conformance_rule | D-008, TRK-019 |
| TLC-005 | Quarantine/label legacy example dialects | standards_package | D-007 |
| TLC-006 | Wire README/CHANGELOG/standards watch | programme_action | BLD-019 |
| TLC-007 | Claim-language review against doctrine §3.10 / §5 | conformance_rule | docs/01 |
| CRE-001 | Control-context snapshot composition (what must be hashed) | open_se | GAP-EXEC-021 |
| CRE-002 | Catalogue: snapshot ref+digest, effective dating on control refs | open_se | GAP-EXEC-005, Modules 03/04/12 |
| CRE-003 | Evaluated-input digest (normalized inputs, hash-scoped) | open_se | P1-1, Module 14 |
| CRE-004 | Decision binding triple (input digest, control-context digest, outcome) | open_se | Module 14, correlation spine |
| CRE-005 | Evaluation-profile neutrality (external engine; AXES does not interpret policy) | open_se + package | docs/01 §5 |
| CRE-006 | Reproducible vs observed_only control results | open_se + conformance_rule | Module 12 |
| CRE-007 | Snapshot access/redaction under P1-3 | package | TRK-004, docs/10 |
| CRE-008 | L3/receipt alignment to same action key (P1-4, Module 06, GT-003) | open_se | TRK-003 |
| CRE-009 | Golden Trace v2 with hashed control-context pack + re-run procedure | programme_action | D-008 |
| CRE-010 | Negative vectors (version-without-digest, etc.) | package | TRK-019 |
| CRE-011 | Control-re-evaluable conformance surface (≠ SE-C2 alone) | conformance_rule | docs/07 |
| CRE-012 | Third-party re-evaluation test protocol and published result | programme_action | design rule in docs/01 |
| CRE-D01 | Faithful-capture / independent witness - orthogonal, not claimed solved by CRE-* | standards_package | docs/11, Module 14/15, EU-007 |
| EB-001 | Reading rule: SIMULATED anchor + externally_anchored ≠ closed existence bound | standards_package | D-015; docs/interop/x402-and-anchoring.md |
| EB-002 | Mechanism-agnostic anchoring_method vocabulary + verify-path requirements (SCITT pluggable, not mandatory) | open_se | TRK-001, Module 14 |
| EB-003 | Profile EvidenceAnchor / Rekor / SCITT / RFC 3161 / OTS receipts into SE anchoring.* | package | D-015 |
| EB-004 | Golden Trace v2 real external anchor (+ replace SIG-STUB per signing profile) | programme_action | D-008, P1-1 |
| EB-005 | Conformance rejects silent overclaim of external anchoring | conformance_rule | EB-001, EB-004 |
| EB-006 | Ack-ladder vs existence-bound discipline (SCITT/TSA ≠ business ack; optional dual registration) | open_se + package | P1-4, GT-003 |

---

**Register totals:** 113 primary REQ rows · 81 GAP rows · 24 TRK rows · 31 BLD rows · 6 GT rows · 9 EU rows · TLC/CRE/EB programme rows as indexed above. TLC/CRE/EB/BLD-031 are programme or implementation tasks, not primary REQs.
**Next step:** CRE-001/002 and EB-002/003/006 catalogue drafts; BLD-031 ARBITR import pack in Magentix AI delivery backlog; do not freeze hashed structure before P1-1.
