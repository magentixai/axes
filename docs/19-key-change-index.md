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
| `anchoring.anchor_store_ref` | `anchors[].anchor_service_ref` | `renamed` | A time-stamp authority or notary is not a store | D-021, WO18 A2.3 | Map the value unchanged |
| `anchoring.anchoring_latency_ms` | removed; derive `anchored_at` minus `anchor_requested_at` | `removed` | Derived values are named, not stored; no unit in a key | D-017 | Compute the lag; do not expect the key |
| (none) | `anchors[].anchor_requested_at`, `anchor_profile_id`, `anchor_commitment_hash`, `anchor_commitment_hash_algorithm`, `anchor_record_ref`, `anchor_operator_ref`, `anchor_proof_ref`, `anchor_proof_hash`, `anchor_verification_procedure_ref` | `added` | Needed for an anchor to be checkable by a third party | WO18 A2.3, WO18 A5 | Populate on real anchors; required when `basis_status` is `demonstrated` |
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

Further gt-v2.1 entries (the heartbeat-interval rename, the `profile_id` taxonomy of WO19) are added here when their final names are fixed, before the release is cut.
