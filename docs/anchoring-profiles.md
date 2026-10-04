# Anchor profiles and verification procedures

Each `anchor_profile_ref` below is an immutable registry entry (WO18 A2, decision on registry identifiers): it dereferences to exactly this statement, and any change to the procedure produces a new identifier. Each section is also the target of `anchor_verification_procedure_ref` for anchors made with it.

Reference tooling: `tools/anchoring/produce.py` (makes anchors), `tools/anchoring/verify_anchor.py` (checks them offline). Results use the four verification states of draft-krausz-verification-state-03 (`verified`, `contradicted`, `indeterminate`, `not_evaluated`) with a closed `condition`.

## Common rules (all profiles)

- **Commitment.** Under both profiles here the commitment is the subject digest itself: `anchor_commitment_hash` equals `anchored_subject_hash` (SHA-256, bare lowercase hex). A different value is `contradicted` / `anchor_commitment_mismatch`.
- **Proof bundle.** `anchor_proof_ref` points to a `proof_manifest.json` listing every proof file with its SHA-256; `anchor_proof_hash` is the SHA-256 of that manifest. A missing reference is `indeterminate` / `anchor_proof_absent` (subject `operator`: the producer did not provide it). A reference that does not resolve at audit time is `not_evaluated` / `anchor_proof_unresolvable` (subject `network`). An altered file is `contradicted` / `anchor_proof_hash_mismatch`.
- **Status.** Only `basis_status: demonstrated` can verify. `simulated` or `stubbed` is `indeterminate` / `basis_not_demonstrated`, never `verified`.
- **Tooling absent.** If the verifier lacks a library or binary a method needs, the result is `not_evaluated`, reason `instrument_failure`, condition `anchor_method_unverifiable`, subject `verifier`. It is never a pass and never a finding about the anchor.

## `axes:opentimestamps_sha256_digest@1`

**What is anchored.** The subject's SHA-256 is submitted to public OpenTimestamps calendars. The calendars aggregate it into a Bitcoin transaction; once mined, the proof upgrades to a Bitcoin block header attestation.

**Fields.** `anchoring_method: opentimestamps`; `anchor_service_id: bip122:000000000019d6689c085ae165831e93` (Bitcoin mainnet, CAIP-2); `anchor_operator_id: null` (the completed proof depends only on Bitcoin; calendars are transport); `anchor_record_ref: block:<height>:<block hash>`; `anchored_at`: the block header time. Before the Bitcoin attestation exists the entry has `anchor_requested_at` and no `anchored_at`: the anchor is pending (derived, not stored).

**Proof bundle.** `subject.ots` (OpenTimestamps detached proof) and `bitcoin-header-<height>.hex` (the 80-byte block header, archived when the proof is upgraded).

**Offline verification.**
1. The `.ots` file's digest equals `anchor_commitment_hash`.
2. Replay the proof's operations from the digest to each Bitcoin attestation.
3. The value reached equals the merkle root in the archived header (bytes 36 to 68).
4. The header's double-SHA-256 meets the target encoded in its own `nBits` (proof of work).
5. `anchor_record_ref` and `anchored_at` equal the header's height, hash and time.

**What this does and does not establish.** It proves the subject digest was committed into a Bitcoin block header with valid proof of work. That the block is in Bitcoin's main chain is a separate check against any Bitcoin node or block explorer, by block hash; the verifier reports the hash so the check takes one lookup. It says nothing about the subject's content beyond its digest.

## `axes:rfc3161_sha256_imprint@1`

**What is anchored.** An RFC 3161 time-stamp request carrying the subject's SHA-256 as the message imprint is sent to a public time-stamp authority, which returns a signed token.

**Fields.** `anchoring_method: timestamp_authority`; `anchor_service_id`: the TSA endpoint; `anchor_operator_id`: the TSA operator; `anchor_record_ref: serial:<token serial>`; `anchored_at`: the token's `genTime`.

**Proof bundle.** `token.tsr` (the RFC 3161 response), `tsa-ca.pem` (the TSA's root certificate), `tsa.crt` (the TSA signing certificate), as published by the TSA at the time of the run.

**Offline verification.**
1. `openssl ts -verify -digest <anchor_commitment_hash> -in token.tsr -CAfile tsa-ca.pem -untrusted tsa.crt` reports `Verification: OK`.
2. The token's time and serial equal `anchored_at` and `anchor_record_ref`.

**What this does and does not establish.** It proves the named TSA signed the digest at the stated time, under the certificate chain in the bundle. Trust in that chain is the relying party's decision: the bundle records which chain was used, it does not make it trusted. Custody: the TSA is a single operator, independent of the subject's producer.

## Adding a profile

A new profile is a new section here with a new identifier, plus a producer and a verifier function, plus two-sided vectors (verified, and each failure the procedure can detect), recorded in the change index. Operator lanes (a witnessed transparency log, an on-chain registry) are added when their operators confirm the interface.
