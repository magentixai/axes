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

## `axes:anchor_registry_bytes32@1`

**What is anchored.** The subject's SHA-256 is passed as the `bytes32` argument of `anchor(bytes32 ref)` on AnchorRegistry, a permissionless contract by giskard09 (argentum-core), deployed with CREATE2 at `0x49fEcA52bC634a9Ab773226D16619deC547794aa`. Its author states that the same address is used on Base, Arbitrum and Ink. This profile has been exercised on Base mainnet (`eip155:8453`). The call emits `Anchored(bytes32 indexed ref, address indexed anchoredBy, uint256 timestamp)`; selector `0xeecdf927`, event topic `0xfe2289542f7a0110ac112c3a4d712afdcaaf2900a1326f4e6f340b563a0e8734` (keccak-256 of the two signatures).

**Fields.**

| Field | Value |
|---|---|
| `anchoring_method` | `distributed_ledger` |
| `anchor_service_id` | `<CAIP-2 chain>:<contract, lowercase>`, for example `eip155:8453:0x49feca52bc634a9ab773226d16619dec547794aa` |
| `anchor_record_ref` | `tx:<transaction hash>` |
| `anchored_at` | the block's timestamp, which the event's `timestamp` also carries |
| `anchor_operator_id` | `null`: the chain is permissionless and the contract has no operator party to the call |

The submitting address (`anchoredBy`, the transaction's `from`) is recorded in the proof bundle. It is the party who chose to anchor, not an operator of the mechanism, and it is a fact for the custody reading (docs/05 Module 14 §14.3), not an independence claim.

**Proof bundle.**

| File | What it is |
|---|---|
| `evm-rpc/header.json` | The block header as a JSON-RPC node returned it (the node's own key spelling) |
| `evm-rpc/receipt.json` | The transaction receipt, likewise |
| `receipt_proof.json` | `receipts_root_hash`, `transaction_index` and `proof_nodes`: the Merkle-Patricia proof of that receipt under the header's `receiptsRoot`, keyed by RLP(transaction index) |

`tools/anchoring/produce.py registry-collect` builds the bundle from any node, after checking that it can recompute the block's `receiptsRoot` from every receipt in the block and the block hash from the header.

**Offline verification.**
1. The header hashes, as keccak-256 of the RLP of its fields in consensus order, to the receipt's `blockHash`.
2. The proof walks from the header's `receiptsRoot` to the receipt's `transactionIndex`, and the value it reaches is exactly the consensus encoding of `evm-rpc/receipt.json` (EIP-2718 typed receipts, including OP Stack deposit receipts).
3. `anchor_service_id` names the AnchorRegistry contract. Otherwise the result is `contradicted` / `anchor_noncanonical_contract`.
4. The receipt succeeded and carries an `Anchored` event emitted by that contract. Otherwise the result is `contradicted` / `anchor_not_a_commitment`; a plain transfer is never an anchor.
5. The event's `ref` equals `anchor_commitment_hash`, which equals `anchored_subject_hash`; `anchored_at` equals the block time; `anchor_record_ref` equals the transaction hash. Any difference is `contradicted` / `anchor_commitment_mismatch`.

**What this does and does not establish.** It proves the subject digest was committed by a successful call to AnchorRegistry, in a block with that hash and that time. That the block is on the named chain's canonical, finalised history is a separate check against any node of that chain, by block hash; the verifier reports the hash so the check takes one lookup. The header does not name its chain, so `anchor_service_id` is what binds the anchor to a chain. Like the other profiles, it says nothing about the subject's content beyond its digest.

**Producing one.** `produce.py registry-calldata --subject FILE` prints the transaction (target, zero value, calldata). The submitter signs and sends it from their own wallet; no key is held by AXES tooling. After it is mined, `produce.py registry-collect --out DIR --tx HASH` records it.

Self-test: `tools/anchoring/test_anchor_registry.py`, two-sided, over a real Base mainnet block (48936665: giskard09's anchor of an action_ref, and a plain transfer from the same block).

## Adding a profile

A new profile is a new section here with a new identifier, plus a producer and a verifier function, plus two-sided vectors (verified, and each failure the procedure can detect), recorded in the change index. Operator lanes (a witnessed transparency log, an on-chain registry) are added when their operators confirm the interface.
