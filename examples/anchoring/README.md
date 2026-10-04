# Anchoring examples (Module 14)

Example `anchoring` blocks in the WO18 A2 shape. Field definitions: [Module 14](../../docs/05-field-catalogue/module-14-external-anchoring.md). Schema: [`schema/anchoring.schema.json`](../../schema/anchoring.schema.json). Crosswalk to other schemes: [docs/interop/anchoring-crosswalk.md](../../docs/interop/anchoring-crosswalk.md).

CI validates every file here on Linux, macOS and Windows (`tools/anchoring/check_schema_and_aliases.py`): each top-level file must validate, each file in `invalid/` must be rejected.

## Real anchors

The real examples are not copied here; they live where they were produced. [`anchors/gt-v2.0/anchoring.json`](../../anchors/gt-v2.0/anchoring.json) anchors the gt-v2.0 release statement with an RFC 3161 time-stamp token (FreeTSA, verified offline) and an OpenTimestamps proof (Bitcoin). Both carry `basis_status: demonstrated` because the tool wrote it from the service response. Verify them yourself with the commands in [`anchors/README.md`](../../anchors/README.md).

## Illustrative examples

Every value below is illustrative and every entry carries `basis_status: simulated`. A simulated anchor never verifies and never earns `externally_anchored`.

| File | Shows | Notes |
|---|---|---|
| `simulated-write-once-store.json` | The gt-v2.0 stub `"write_once_store (SIMULATED)"` expressed correctly: method as a registry value, status in `basis_status` | What gt-v2.1 corpora carry where no real anchor exists |
| `transparency-log.json` | A transparency-log anchor: log origin, leaf index at a checkpoint size, proof manifest | `example:` namespace profile; open question Q2 (checkpoint clock) applies |
| `distributed-ledger.json` | An on-chain registry anchor on a test network, with the canonical contract in `anchor_service_id` | The procedure reference is marked `CONFIRM-WITH-PABLO` until the LFDT lab procedure is agreed. A matching event from any other contract is not evidence (WO18 A4.4) |
| `dual-lane-tlog-and-chain.json` | The real gt-v2.0 release statement digest anchored by two further lanes side by side | Profile, service and procedure values are `CONFIRM-WITH-AUTHOR` placeholders for MarkovianProtocol and argentum-core to replace with real anchors |
| `two-party-correlation.json` | Buyer and seller each anchor their own envelope; both carry the same `correlation_hash` (WO20) | Completeness by counterparty |

## Invalid examples (must be rejected)

| File | Why it is rejected |
|---|---|
| `invalid/parenthetical-method.json` | Status inside the method value (`write_once_store (SIMULATED)`), catalogue 1.27 |
| `invalid/anchored-without-record.json` | `anchored_at` with no `anchor_record_ref`: a time the mechanism attests must say where it attests it |
| `invalid/demonstrated-without-proof.json` | `basis_status: demonstrated` without profile, request time, proof and procedure |
| `invalid/legacy-gt-v2.0-key.json` | A gt-v2.0 key (`anchor_receipt_id`) in a gt-v2.1 block; see the [key change index](../../docs/19-key-change-index.md) |
| `invalid/namespaced-method-without-procedure.json` | A namespaced method with no `anchor_verification_procedure_ref` |
