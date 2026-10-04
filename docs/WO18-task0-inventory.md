# WO18 Task 0: live anchoring inventory (2026-10-04)

Read from `origin/main` at `1e296f0` and `origin/golden-trace-v2` at `a31cb35` before any WO18 change.

## The `anchoring` block as published

| Branch / corpus | `anchoring` keys (in order) | `anchoring_method` | Canonicalisation | `corroboration_state` |
|---|---|---|---|---|
| `golden-trace-v2` fin and ind (corpus of record, tag `corpus/2026-08-08-gt-v2`) | `anchor_receipt_id`, `anchoring_method`, `anchored_at`, `chain_head_hash`, `anchor_store_ref`, `anchoring_latency_ms` | `write_once_store (SIMULATED)` | `RFC8785-JCS` | `externally_anchored` |
| `main` fin and ind (retired pre-merge lineage) | same, with `anchoring_latency` instead of `anchoring_latency_ms` (D-017) | `write_once_store (SIMULATED)` | `GT-JCS-0` | `externally_anchored` |

Envelope-level `profile_id`: `se-profile:payments-emitter/0.1-draft` (fin), `se-profile:manufacturing-emitter/0.1-draft` (ind).

## How the generator emits it (`golden-trace-v2`)

- `ANCHOR_INTERVAL_S = 300`; an `attestation_recorded` envelope is placed at each interval with `anchoring = "__FILL_AT_CHAIN_TIME__"` and `evidence_quality.corroboration_state = "externally_anchored"`.
- `Chain.anchor(sec)` fills the receipt over the current chain head at chain time. The export envelope carries `export.final_anchor` built the same way.
- Fin corpus: 3 anchor envelopes plus 1 `final_anchor`. Every anchor is the hard-coded simulated store; every one claims `externally_anchored`.

## Vocabulary and definitions in force

- `corroboration_state`: defined in `docs/06` §2 (three-axis provenance) and `docs/05-field-catalogue/field-origin-notes.md`; graded scale ending at `externally_anchored`, plus `conflicting_evidence`.
- `basis_status` (`demonstrated` | `stubbed` | `simulated`): `docs/06` §2.11 and catalogue 1.27; defined, not yet in corpus values.
- `anchor_requested_at`: catalogue 1.26; defined, not yet in corpus values.
- Anchoring method vocabulary: named in `PROVENANCE.md` and `registers/adjacent-standards-watch.md` (`distributed_ledger`, `transparency_log`, `timestamp_authority`); EB-002, EB-003, EB-004 in `registers/requirements-register.md` and `docs/interop/x402-and-anchoring.md`. No closed registry yet.
- `custodian_independence`: not defined in `docs/06`; appears only in work orders and `PROVENANCE.md` (confirms WO18 A1.7).
- Reading rule D-015: a SIMULATED anchor with `externally_anchored` MUST NOT be read as a closed existence bound. Stated in prose; not enforced by the verifier.

## Gap against WO18 A2

| A2 element | Live state |
|---|---|
| `anchored_subject_type` / `_hash` / `_hash_algorithm` | absent; `chain_head_hash` only |
| `anchors[]` array | absent; single object |
| `anchor_id`, `anchor_service_ref`, `anchor_record_ref` | absent; `anchor_receipt_id`, `anchor_store_ref` instead |
| `anchor_profile_id`, `anchor_commitment_hash` (+ algorithm) | absent |
| `basis_status` on anchors | absent; status inside the method string |
| `anchor_operator_ref`, `anchor_proof_ref`, `anchor_proof_hash`, `anchor_verification_procedure_ref` | absent |
| stored latency | present (`anchoring_latency_ms`); to be removed |
| verifier guard | absent; `tools/axes_verify.py` does not read `anchoring` |

All corpus-value changes are gated to gt-v2.1 (D-018). WO18 lands the model, tooling, vectors, examples and the detached gt-v2.0 release anchors without touching published bytes.
