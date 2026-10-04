# Anchoring crosswalk (informative)

> **Status: informative, DRAFT.** WO18 A3.3. Maps each key of the AXES anchoring block (Module 14, [docs/05/module-14](../05-field-catalogue/module-14-external-anchoring.md)) to its counterpart in eight schemes, with the declared representation pair and any gap. Gaps are stated, not hidden. Where a scheme's own field names have not been confirmed with its author, the row says so and maps the concept only. Corrections from scheme authors are welcome on the repository; each lands with credit and, if a key changes, through the [key change index](../19-key-change-index.md).

## Why one shape covers all of them

Every scheme below answers the same five questions about an anchor, under different names:

1. **What was committed?** A digest (`anchor_commitment_hash`, `anchor_commitment_hash_algorithm`), derived from the subject (`anchored_subject_hash`) by a rule the profile states.
2. **Who or what holds the commitment?** A service or network (`anchor_service_ref`), run by an operator (`anchor_operator_ref`, `null` for a permissionless network).
3. **Where is it in that service?** A record locator (`anchor_record_ref`): a token serial, a block, a log index, a transaction.
4. **When does the mechanism say it existed?** `anchored_at`, always the time the mechanism attests, never the emitter's clock.
5. **How does a third party check it offline?** Proof material (`anchor_proof_ref`, `anchor_proof_hash`) and a procedure (`anchor_profile_id`, `anchor_verification_procedure_ref`).

Variations between schemes are absorbed by two values: `anchoring_method` (the family) and `anchor_profile_id` (the owner-authored, versioned, immutable procedure). No scheme needs a schema change. Whether an anchor is independent of the emitter, whether it is still pending, and how long it took are derived by the verifier (Module 14.3), never stored.

## Key-by-key crosswalk

Abbreviations: **TSA** RFC 3161 time-stamp token; **OTS** OpenTimestamps; **tlog** witnessed transparency log with OpenTimestamps (c2sp tlog-proof, MarkovianProtocol); **chain** on-chain `action_ref` registry (argentum-core, giskard09); **SCITT** IETF SCITT receipt (RFC 9943); **EAS** Ethereum Attestation Service attestation (x402#2833); **EA** AGT EvidenceAnchor `AnchorReceipt` (AGT PR #2244); **x402ev** the x402 evidence-record anchor slots (tsc#4).

| AXES key | TSA | OTS | tlog | chain | SCITT | EAS | EA | x402ev |
|---|---|---|---|---|---|---|---|---|
| `anchoring_method` | `timestamp_authority` | `opentimestamps` | `transparency_log` | `distributed_ledger` | `transparency_log` | `distributed_ledger` | per backend | implied by `anchor=` namespace |
| `anchor_commitment_hash` | `TSTInfo.messageImprint.hashedMessage` | file digest of the `.ots` proof | leaf hash committed in the log | committed `action_ref` value | statement digest the receipt covers | attestation data field holding the digest | committed digest (name to confirm) | hex part of `digest=` |
| `anchor_commitment_hash_algorithm` | `messageImprint.hashAlgorithm` (OID) | file hash op (`sha256`) | log hash function | per registry contract | COSE algorithm of the statement hash | per schema | to confirm | algorithm part of `digest=` (declared pair, e.g. `SHA-256` to `sha256`) |
| `anchor_service_ref` | TSA endpoint URL | Bitcoin network as CAIP-2 `bip122:…` | log origin (checkpoint origin line) | CAIP-2 chain plus canonical contract address | transparency service identifier | CAIP-2 chain plus EAS contract | backend identifier | chain-and-contract part of `anchor=` |
| `anchor_record_ref` | `serial:<TSTInfo.serialNumber>` | `block:<height>:<hash>` | `index:<leaf index>` at a checkpoint size | `tx:<hash>` or log position | receipt's inclusion position | `uid:<attestation UID>` | record id (to confirm) | record part of `anchor=` |
| `anchored_at` | `TSTInfo.genTime` | Bitcoin block header time | checkpoint time (which clock: open question Q2) | block timestamp | registration time in the receipt | attestation `time` | to confirm | not carried |
| `anchor_requested_at` | time the query was sent | time submitted to calendars | time submitted to the log | time the transaction was submitted | time the statement was submitted | time submitted | to confirm | not carried |
| `anchor_operator_ref` | TSA operator | `null` (calendars are transport only) | log operator; witnesses recorded in the proof | `null` on a permissionless chain | transparency service operator | `null` | backend operator | not carried |
| `anchor_proof_ref` / `anchor_proof_hash` | manifest over `token.tsr`, TSA certificate and CA | manifest over `.ots` and the archived block header | manifest over checkpoint, inclusion proof, cosignatures, `.ots` | manifest over transaction receipt and block header | manifest over the COSE receipt | manifest over the attestation and transaction receipt | manifest over the receipt | not carried; resolved via `anchor=` |
| `anchor_profile_id` | `axes:rfc3161-sha256-imprint@1` | `axes:opentimestamps-sha256-digest@1` | owner-authored (to confirm) | owner-authored (to confirm) | to be authored | to be authored | to be authored | profile named by the evidence record, if any |
| `anchor_verification_procedure_ref` | [profile section](../anchoring-profiles.md#axes-rfc3161-sha256-imprint-1) | [profile section](../anchoring-profiles.md#axes-opentimestamps-sha256-digest-1) | owner's published procedure | owner's published procedure | RFC 9943 receipt verification | EAS verification plus canonical-contract check | AGT verification | x402ev procedure |
| `basis_status` | written by the producer from the service response | same | same | same | same | same | same | not carried |

The anchoring profile proposal (seritalien, x402#3389) maps one level up: it is a profile of the whole anchor, so it corresponds to `anchor_profile_id` plus `anchor_verification_procedure_ref` together, and its contents map key by key through the table above.

## Gaps, stated

| Scheme | Gap | Consequence for AXES |
|---|---|---|
| TSA | Trust rests on the TSA's certificate chain; the operator is not independent by construction | Custody relationship derived from `anchor_operator_ref`; a TSA run by the emitter or deployer never earns `externally_anchored` |
| OTS | Pending until a Bitcoin block includes the calendar commitment; reorganisation depth before final is not pinned | Pending is derived (no `anchored_at`); reorganisation depth is open question Q1 |
| tlog | Checkpoint time source not standardised across logs | Open question Q2; `anchored_at` from a tlog anchor names its source in the profile |
| chain | A lookalike contract can emit a matching event; a plain token transfer carries no commitment | Commitment counts only at the canonical contract in `anchor_service_ref` (WO18 A4.4); a transfer is never an anchor. Vector pair required |
| SCITT | Receipt verification needs the transparency service's key, distributed out of band | Key material goes in the proof manifest; absent key is `indeterminate` / `anchor_proof_absent` |
| EAS | Attestation schema fields are per schema; no fixed digest slot | The profile must name the field that carries the commitment |
| EA | Field names not yet confirmed against PR #2244 | Concept mapping only until confirmed |
| x402ev | Carries locator and digest only; no time, no operator, no proof | An x402ev record is a pointer to an anchor, not a verifiable anchor on its own; AXES fills the rest from the anchor it resolves to |

`anchor_record_ref` percent-encoding of identifiers that contain `:` is open question Q3. All three open questions are listed in `vectors/README.md` on `golden-trace-v2` under "Questions this corpus does not settle".

## Worked example 1: one subject, two independent lanes

The gt-v2.0 release statement is already anchored twice, for real: [`anchors/gt-v2.0/anchoring.json`](../../anchors/gt-v2.0/anchoring.json) carries an RFC 3161 anchor (verified offline) and an OpenTimestamps anchor (pending its Bitcoin block when first committed). [`examples/anchoring/dual-lane-tlog-and-chain.json`](../../examples/anchoring/dual-lane-tlog-and-chain.json) shows the next step: the same subject anchored by a witnessed transparency log (MarkovianProtocol) and an on-chain registry (argentum-core), side by side. Both entries carry `basis_status: simulated` and `CONFIRM-WITH-AUTHOR` placeholders until each owner produces the real anchor; they show that the two variations need only `anchoring_method` and `anchor_profile_id` to differ.

## Worked example 2: two parties, one shared digest (WO20)

In an x402 payment each party keeps its own AXES record and anchors it independently. Both records carry the same `correlation_digest` (recipe `axes:x402-correlation@1`), computed by each party from bytes both hold when the payer authorises. [`examples/anchoring/two-party-correlation.json`](../../examples/anchoring/two-party-correlation.json) holds the buyer's and the seller's anchoring blocks, each with `anchored_subject_type: envelope`.

What this gives a third party: two independent commitments to records about the same payment. Neither side can quietly drop a payment the other has anchored (completeness by counterparty, wowlegend, wg-identity#25). If the parties' recomputed cores differ, each records `indeterminate` / `divergence`; a verifier never picks a side.

## Sources

| Scheme | Source |
|---|---|
| x402ev | whawk46, x402 tsc#4 |
| Witnessed transparency log with OpenTimestamps | MarkovianProtocol (Colin H Winter), axes#4 and axes#6; C2SP tlog-proof |
| On-chain `action_ref` registry | giskard09, axes#3; draft-etcheverry-action-ref |
| RFC 3161 | IETF RFC 3161 |
| SCITT | IETF RFC 9943 |
| EAS | x402#2833 |
| EvidenceAnchor | AGT PR #2244 |
| Anchoring profile | seritalien, x402#3389 |
