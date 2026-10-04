# Module 14: External anchoring

> **Status: DRAFT, open for challenge.** Defined by WO18 (A2 field map, A5 producers and verification). Field definitions land now; Golden Trace corpus values land in the announced gt-v2.1 release (D-018). Every replaced key is listed with its reason in [docs/19](../19-key-change-index.md) and machine-readably in [`schema/key-aliases.json`](../../schema/key-aliases.json). JSON Schema: [`schema/anchoring.schema.json`](../../schema/anchoring.schema.json). Profiles and verification procedures: [docs/anchoring-profiles.md](../anchoring-profiles.md).

**Why this module exists.** A local hash chain proves order and tamper-evidence inside the emitter's own records. It does not prove the bytes existed, unmodified, at a time independent of whoever holds them. An anchor is that independent existence bound: the mechanism (a time-stamp authority, a public chain, a transparency log) commits to a digest, and a third party can check the commitment offline. The strong claim `corroboration_state: externally_anchored` is earned only by an anchor that verifies (14.3); a simulated or self-held anchor never earns it.

## 14.1 Shape: one subject, one or more anchors

A subject (a chain head, one envelope, a bundle manifest, a release statement) can be anchored by several independent mechanisms. The gt-v2.0 release statement already carries two (an RFC 3161 time-stamp authority and OpenTimestamps; see `anchors/gt-v2.0/anchoring.json`), with operator lanes to follow. So the block names the subject once and carries an array of anchors.

```json
"anchoring": {
  "anchored_subject_type": "chain_head",
  "anchored_subject_hash": "<bare lowercase hex>",
  "anchored_subject_hash_algorithm": "SHA-256",
  "anchors": [
    {
      "anchor_id": "anch:004",
      "anchoring_method": "distributed_ledger",
      "anchor_profile_id": "<owner-authored, versioned profile id>",
      "basis_status": "demonstrated",
      "anchor_commitment_hash": "<bare lowercase hex>",
      "anchor_commitment_hash_algorithm": "SHA-256",
      "anchor_requested_at": "2026-10-06T09:00:00.000Z",
      "anchored_at": "2026-10-06T09:00:12.000Z",
      "anchor_service_ref": "eip155:8453:0x...",
      "anchor_record_ref": "0x...",
      "anchor_operator_ref": null,
      "anchor_proof_ref": "anchors/gt-v2.0/argentum/receipt.json",
      "anchor_proof_hash": "<bare lowercase hex>",
      "anchor_verification_procedure_ref": "<runnable procedure>"
    }
  ]
}
```

The same block replaces `export.final_anchor`. `evidence_quality.corroboration_state` stays at envelope level. `externally_anchored` is earned when at least one entry in `anchors` verifies (A2.4).

## 14.2 Keys

### Subject (once per block)

| Key | Status | Description |
|---|---|---|
| `anchored_subject_type` | new | What was anchored: `chain_head`, `envelope`, `bundle_manifest` or `release_statement`. Closed set. `envelope` gives an anchor per lifecycle state; Golden Trace in-envelope anchors use `chain_head`. |
| `anchored_subject_hash` | **replaces `chain_head_hash`** | The AXES digest of the subject. Replaced because the subject is no longer always a chain head: a key called `chain_head_hash` holding an envelope or release-statement digest would mislead. When the type is `chain_head` the value is the same one `chain_head_hash` held. |
| `anchored_subject_hash_algorithm` | new | Algorithm of `anchored_subject_hash`, spelt as `integrity.hash_algorithm` is. MUST equal `integrity.hash_algorithm` for `chain_head` and `envelope`. Present so a detached anchor (a release statement outside any envelope) verifies on its own. |

### Each entry in `anchors`

| Key | Status | Description |
|---|---|---|
| `anchor_id` | **replaces `anchor_receipt_id`** | Identifier AXES mints for this anchor entry (`anch:004`), so reports and forensic steps can cite it. Replaced because "receipt" collides with x402 receipts and with mechanism receipts; this value is neither. `_id`: minted in SE scope. |
| `anchoring_method` | kept (value tightened) | Mechanism class, as a registry identifier: `distributed_ledger`, `transparency_log`, `timestamp_authority`, `opentimestamps`, `write_once_store`, or `<namespace>:<id>`. No status in the value: gt-v2.0's `write_once_store (SIMULATED)` becomes `write_once_store` with `basis_status: simulated`. |
| `anchor_profile_id` | new | The exact, versioned procedure that turns the subject hash into the commitment and back, for example `action-ref-v1-jcs-sha256` or a c2sp tlog-proof profile. Owner-authored registry identifier; a changed procedure gets a new id. |
| `basis_status` | reused (catalogue 1.27) | Whether this anchor is real: `demonstrated` (a real anchoring run produced it), `stubbed`, or `simulated` (illustrative, never written to the mechanism). Kept as the shared companion name rather than a local `anchor_status`, so one closed vocabulary means the same thing in every block. |
| `anchor_commitment_hash` | new | The exact value the mechanism stored. "Commitment" is the established term for the value written to a ledger, log or token. Equal to `anchored_subject_hash` under an identity profile; different when the profile derives it (an `action_ref` preimage, a keccak256 registry). A verifier recomputes it via `anchor_profile_id` and never trusts the stored value alone. |
| `anchor_commitment_hash_algorithm` | new | Algorithm of the commitment, from the declared digest registry. Canonical form pinned, digest agile. |
| `anchor_requested_at` | catalogued (1.26) | When the subject hash was submitted to this mechanism. Per entry, because each lane is submitted separately. |
| `anchored_at` | kept | The time the mechanism attests the commitment existed by: block time, checkpoint time, TSA token time, OTS attestation time. Never adjusted to an illustrative timeline. |
| `anchor_service_ref` | **replaces `anchor_store_ref`** | The anchoring service: `<caip2>:<contract>` for a chain, the log origin for a transparency log, the TSA identifier, the WORM store. Replaced because a timestamp authority or notary is not a store. |
| `anchor_record_ref` | new (was `external_anchor_ref` in the registers) | This anchor's record inside the service: transaction hash or registry entry id, log leaf index, OTS attestation reference, TSA token serial. Named "record" to match the x402ev grammar slot it fills. |
| `anchor_operator_ref` | new | Who operates the service, so a verifier can test it against executor and deployer. `null` for a permissionless chain (no operator party to the transaction). A fact, not an independence claim. |
| `anchor_proof_ref` | new | Pointer to the proof material a verifier needs offline: inclusion proof and checkpoint bundle, OTS proof file, RFC 3161 token, transaction receipt. Pointer, not payload (doctrine). |
| `anchor_proof_hash` | new | Digest of the proof material at `anchor_proof_ref`, algorithm per `integrity.hash_algorithm`, so the pointer is tamper-evident. |
| `anchor_verification_procedure_ref` | new | Pointer to the runnable procedure a third party follows to verify this entry offline. Required for a namespaced `anchoring_method`. |

**Removed:** `anchoring_latency_ms` (gt-v2.0) and `anchoring_latency` (retired lineage), per D-017.

## 14.3 Derived by the verifier, never stored

| Outcome | How it is derived |
|---|---|
| Anchoring lag, per entry | `anchored_at` minus `anchor_requested_at` (D-017). |
| Anchor pending | `anchor_requested_at` present; `anchored_at` and `anchor_record_ref` absent. Not a status value. |
| Anchor custody relationship, per entry | The custody-ref-v1 three-leg predicate agreed on axes#3, applied to `anchor_operator_ref` against executor and deployer; a `null` operator on a permissionless chain counts as independent. Value strings to match custody-ref-v1 exactly (confirm with giskard09). |
| `externally_anchored` earned | At least one entry where `basis_status` is `demonstrated`, the commitment recomputes from the subject hash under `anchor_profile_id`, the proof at `anchor_proof_ref` matches `anchor_proof_hash` and verifies against `anchor_service_ref` and `anchor_record_ref`, and the custody relationship is independent. Otherwise reject with `anchor_simulated_claims_external`, `anchor_independence_unproven` or `anchor_method_unverifiable` (WO18 §4 codes, reported as conditions per WO18 A4.1). |

## 14.4 x402ev representation pair (declared, not derived)

| x402ev slot | AXES source |
|---|---|
| `anchor=<caip2>:<contract>:<record>` | `anchor_service_ref` + `:` + `anchor_record_ref` |
| `digest=<alg>:<hex>` | `anchor_commitment_hash_algorithm` (declared pairing, e.g. `SHA-256` to `sha256`) + `:` + `anchor_commitment_hash` |

Per `docs/06` §3, the algorithm spellings are a declared representation pair, never a derived string transform.

## 14.5 Out of scope

Retention immutability (GAP-IA-001 `retention_immutable_flag`, `retention_immutability_ref`) is a separate property from the existence bound. A WORM store can serve as an anchor through `write_once_store`; retention proof stays its own cluster.
