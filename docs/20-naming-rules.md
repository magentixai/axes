# Naming rules (normative)

> **Status: normative.** Decision D-024. Every key, enum value and AXES-minted identifier follows these rules, in records, schemas, vectors, tool output and manifests. Checked by [`tools/check_key_naming.py`](../tools/check_key_naming.py) in CI on Linux, macOS and Windows. Known violations in frozen bytes (the gt-v2.0 corpus of record, anchored statements, harness files) are listed in `tools/naming_baseline.json` with the [key change index](19-key-change-index.md) entry that corrects them; anything new fails.

**Why.** A developer who knows these rules can predict the name, type and meaning of a field they have not read yet. AXES is a record format that several parties write and many read; names that follow one method are the cheapest interoperability there is. Each rule below fixes one thing a reader would otherwise have to look up.

**Prose is not covered.** Documentation prose uses British English (house style). Keys, enum values and identifiers use American English (N2), because they are code.

---

## N1 Casing

Keys and enum values match `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`: lower case, words joined by a single underscore, no leading digit, no hyphen, no camelCase. Rationale: docs/06 §3 (ISO 20022 JSON practice; JCS sorts two spellings to different bytes).

## N2 Spelling: American, whole words

- American spelling: `canonicalization_version`, `authority_utilization_ratio`, `cross_program_exposure_indicator`.
- No abbreviations: `organization_id`, not `org_id`; `acknowledgment_code`, not `ack_code`.
- Approved acronyms and domain terms, used as words: `id`, `ref`, `se`, `url`, `api`, `caip`, `iban`, `erp`, `mes`, `cpk`, `x402`. New ones are added here by decision.

## N3 Shape: qualifiers first, class word last

A scalar key is `<qualifier>_..._<property>_<class word>`. The **class word** is always the last token and fixes the value type. Keys are **fully qualified**: a key keeps its meaning when copied out of its parent, so a bare class word (`state`, `name`, `basis`) is not a key, except as a member of a registered datatype (N12).

| Class word | Value | Examples |
|---|---|---|
| `_id` | Identifier of a party, system or component, or of this object itself (N10) | `agent_id`, `anchor_service_id`, `envelope_id` |
| `_ref` | Citation of a document, artefact or record a reader fetches and reads (N10) | `policy_ref`, `anchor_proof_ref`, `implementation_profile_ref` |
| `_key` | Cryptographic or idempotency key identifier | `idempotency_key` |
| `_hash` | Bare lowercase hex digest (N8) | `envelope_hash` |
| `_algorithm` | Registry identifier of an algorithm | `anchor_commitment_hash_algorithm` |
| `_signature` | Encoded signature | `envelope_signature` |
| `_at` | RFC 3339 UTC instant, millisecond precision, `Z` (N9) | `occurred_at`, `acknowledged_at` |
| `_on` | Calendar date `YYYY-MM-DD` | `authored_on` |
| `_from`, `_until` | Instants bounding validity; only as `effective_from`, `effective_until` | |
| `_duration`, `_interval`, `_lag`, `_latency`, `_timeout` | ISO 8601 duration (N4) | `declared_heartbeat_interval: "PT60S"` |
| `_count` | Non-negative integer | `erp_expected_count` |
| `_number` | Ordinal or business number, as a string | `sequence_number`, `serial_number` |
| `_index` | Integer position | `payment_index` |
| `_ratio` | Decimal string in [0, 1] | `evidence_coverage_ratio` |
| `_value` | Measured value; its unit is a sibling `_unit` | `measured_value` |
| `_unit` | UCUM unit code | `measurement_unit: "mm"` |
| `_version` | Version string | `se_version` |
| `_path` | JSON Pointer (RFC 6901) | `field_path` |
| `_expression` | Predicate expression in a declared language | `condition_expression` |
| `_name` | Human-readable name | `control_name` |
| `_note` | Free text, never parsed | `observed_note` |
| `_text` | Exact string payload whose bytes matter | `canonical_text` |
| `_indicator` | Boolean (N5) | `redaction_applied_indicator` |
| `_type`, `_kind`, `_class`, `_status`, `_state`, `_code`, `_mode`, `_phase`, `_basis`, `_method`, `_role`, `_scope`, `_source`, `_scheme`, `_level`, `_posture`, `_origin`, `_layer`, `_result` | Value from a closed vocabulary in docs/06 (N11) | `event_kind`, `verification_state`, `commit_method` |

Enumeration class words, by meaning: `_type` what kind of thing an object is; `_kind` event classification; `_class` a category on a declared scale; `_status` the outcome or progress of a step; `_state` a position on a declared ladder or a verdict; `_code` a reason or condition code; `_basis` an epistemic or legal basis; `_method` a mechanism; `_role` a party role; `_scope` the reach of an identifier or grant; `_source` where a value came from; `_scheme` an encoding scheme; `_level` a graded level; `_posture` a configured stance; `_origin` the class of producer; `_layer` a capture layer; `_result` the result of a control or check.

## N4 No unit in a key

The unit is part of the value or a sibling, never the name (D-017). Durations are ISO 8601 (`PT60S`); measurements carry `_value` plus `_unit`; money uses the Amount datatype. `anchoring_latency_ms`, `measured_mm` and `size_bytes` are the defect this rule exists for.

## N5 Booleans

A boolean key ends `_indicator` and names the positive condition: `personal_data_indicator`, `redaction_applied_indicator`. Never `_flag`, `is_`, `has_`, and never a negated name. An absent indicator means not recorded, never `false` (N11).

## N6 Arrays

An array key is the plural of its element: `anchors`, `acknowledgments`, `redacted_fields`. An array of identifiers or citations ends `_ids` or `_refs`. A mass noun takes `_items`: `pinned_evidence_items`.

## N7 Objects

An object key is a singular noun naming the block (`anchoring`, `integrity`, `outcome`, `signing_trust`), never a scalar class word. A registered datatype keeps its datatype name (`amount`).

## N8 Digests

A digest is `<subject>_hash`, bare lowercase hex, with its algorithm in `<subject>_hash_algorithm` or in a block-level `hash_algorithm` that governs every `_hash` in that block. Never an algorithm name in a key (`sha256`), never a prefix in the value (`sha256:...`) unless an external format requires it, in which case it is a representation pair (N14).

## N9 Time

Instants end `_at`; dates end `_on`. Never `_timestamp`, `_time`, `_date`. Each instant states which clock it reads (`timestamp_source`) where more than one clock is involved.

## N10 `_id` versus `_ref`

`_id` names **who or what acts or exists**: a party, system, service, component, or the object carrying the key. `_ref` cites **what a reader fetches and reads**: a document, artefact, profile, receipt, record or proof. Test: if you would retrieve it to read its contents, it is a `_ref`. (D-022, as restated 2026-10-04.)

Companions: `<x>_id_scope` and `<x>_resolution_authority` (WO16 identifier scope) qualify an `_id`; `<x>_ref` may pair with `<x>_hash` to pin what it cites.

## N11 Enumerations and absence

- Enum values are lower_snake, American, from a closed set in docs/06. A new value is added by decision, never by an emitter.
- Absent means not recorded. A reader never defaults an absent value (absent `identifier_scope` is not `global`; absent `assertion_basis` is not `observed`; an unlabeled settlement is never organic demand).
- An optional member is omitted when absent, never `null`, unless `null` is declared meaningful for that key (for example `anchor_operator_id: null` for a permissionless network).

## N12 Registered datatypes, data maps and external blocks

- **Datatypes** have fixed members, listed here and nowhere else: Amount `{value, asset, decimals}`; artifact reference `{ref, hash, hash_algorithm, scheme}`; identifier object `{scheme, value}`.
- **Data maps** use data as keys (file names, corpus names): `file_hashes` in a proof manifest. Their keys are not field names.
- **External blocks** carry another system's names verbatim and are declared here: `sampling_parameters` (model provider parameters). Nothing else.

## N13 Identifiers AXES mints

Profiles, recipes, formats and derivations minted by AXES are `axes:<lower_snake_name>@<version>`: `axes:rfc3161_sha256_imprint@1`, `axes:x402_correlation@1`, `axes:authority_valid_at_action@1`. The identifier is immutable; a change is a new version. Identifiers minted by others are carried verbatim (`x402-mandate/1`, `x402-tax:eu-vat@rev6`).

## N14 Representation pairs

Another standard's spelling never becomes an AXES key. Where AXES carries the same concept, the pair is declared, never derived by string transformation (docs/06 §3).

| External spelling | Where | AXES key |
|---|---|---|
| `correlationDigest` | x402 receipt / evidence lane (WO20) | `correlation_hash` plus `correlation_hash_algorithm` |
| `offered`, `required`, `chosen`, `profileRegistry` | x402 lane common contract (WO20) | `offered_profile_ids`, `required_indicator`, `chosen_profile_id`, `profile_registry_ref` |
| `x402Version`, `payTo`, `validBefore` | x402 v2 | `x402_version`, `pay_to_id`, `authorization_valid_before` |
| `state`, `state_reason`, `subject` | draft-krausz-verification-state-03 | `verification_state`, `verification_reason_code`, `verification_subject_type` |
| `capture_relationship` | custody-ref-v1 | `capture_relationship_type` |
| `mandateDigest`, `paymentId` | x402 `authority` (#3220) | `mandate_hash` (prefix stripped, algorithm in `mandate_hash_algorithm`), `payment_identifier_id` |
| `anchor=`, `digest=` | x402ev | `anchor_service_id` + `anchor_record_ref`; `anchor_commitment_hash_algorithm` + `anchor_commitment_hash` |

## N15 Changing a name

Before v1, a key whose name breaks these rules or no longer fits its definition is replaced (D-021), only in an announced release (D-018), and indexed permanently in [docs/19](19-key-change-index.md) and `schema/key-aliases.json`. From module freeze, keys are immutable.

---

## Checking

```bash
python tools/check_key_naming.py schema examples/anchoring anchors --baseline tools/naming_baseline.json
```

On `golden-trace-v2`: the same tool over both corpora and `vectors/`. The lint checks N1 to N9, N11 (spelling of enum values) and N13. N10 and the meaning of each enumeration class word are checked in catalogue review, because a lint cannot know whether a thing acts or is read.
