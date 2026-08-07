# Forensic Execution Pack - MRUN-2026-06-11-A

## 1. Verification procedure (vendor-neutral)
1. Read `envelopes.jsonl` in sequence order. 2. For each envelope, remove `integrity.envelope_hash` and `integrity.signature`; serialise with RFC 8785 JCS; SHA-256; compare to stored hash. 3. Confirm `previous_envelope_hash` equals the prior envelope's hash (genesis = 64x'0'). 4. Confirm sequence numbers are contiguous. 5. Compare chain heads at each `attestation_recorded` event with the anchor receipts in Appendix B of the Conformity Assessment Pack. 6. Re-hash each file in `artifacts/` and compare with `manifest.json`. Steps 1-4 and 6 are fully reproducible from the bundle alone; step 5 is simulated in this golden trace.

## 2. Envelope sequence (first 24 of 76; full stream in envelopes.jsonl)
| Seq | event_kind | Part# | occurred_at | envelope_hash |
|---|---|---|---|---|
| 0001 | execution_started |  -  | 2026-06-11T07:00:00.000Z | `742bfa994264…` |
| 0002 | context_retrieved |  -  | 2026-06-11T07:00:04.000Z | `fe760bcf8a71…` |
| 0003 | plan_created |  -  | 2026-06-11T07:00:09.000Z | `32d31c5b1557…` |
| 0004 | policy_check_performed | 1 | 2026-06-11T07:00:12.000Z | `d77d8f3e947a…` |
| 0005 | commit_attempted | 1 | 2026-06-11T07:00:18.000Z | `077baebf7b3b…` |
| 0006 | tool_invoked | 1 | 2026-06-11T07:00:19.000Z | `99ba8bacc1ad…` |
| 0007 | commit_succeeded | 1 | 2026-06-11T07:00:21.000Z | `1449ee63a922…` |
| 0008 | policy_check_performed | 2 | 2026-06-11T07:00:57.000Z | `df4a18ae67d9…` |
| 0009 | heartbeat_event |  -  | 2026-06-11T07:01:00.000Z | `e19f5daff311…` |
| 0010 | commit_attempted | 2 | 2026-06-11T07:01:03.000Z | `692db2f63318…` |
| 0011 | tool_invoked | 2 | 2026-06-11T07:01:04.000Z | `dfb79718b36b…` |
| 0012 | commit_succeeded | 2 | 2026-06-11T07:01:06.000Z | `a66b7c0906b3…` |
| 0013 | policy_check_performed | 3 | 2026-06-11T07:01:42.000Z | `c6c8e3d04840…` |
| 0014 | commit_attempted | 3 | 2026-06-11T07:01:48.000Z | `3f0e856e0349…` |
| 0015 | tool_invoked | 3 | 2026-06-11T07:01:49.000Z | `13a01b710b63…` |
| 0016 | commit_succeeded | 3 | 2026-06-11T07:01:51.000Z | `438ef3ce6130…` |
| 0017 | heartbeat_event |  -  | 2026-06-11T07:02:00.000Z | `a6087b460124…` |
| 0018 | policy_check_performed | 4 | 2026-06-11T07:02:27.000Z | `70793532805d…` |
| 0019 | commit_attempted | 4 | 2026-06-11T07:02:33.000Z | `fe0dcd3e4e9c…` |
| 0020 | tool_invoked | 4 | 2026-06-11T07:02:34.000Z | `aaece7f27b9d…` |
| 0021 | commit_succeeded | 4 | 2026-06-11T07:02:36.000Z | `95535fbc2f47…` |
| 0022 | heartbeat_event |  -  | 2026-06-11T07:03:00.000Z | `75a7874bf103…` |
| 0023 | policy_check_performed | 5 | 2026-06-11T07:03:12.000Z | `1533142125b0…` |
| 0024 | commit_attempted | 5 | 2026-06-11T07:03:18.000Z | `75c4120c99a7…` |

## 3. Part <-> artifact <-> confirmation linkage
| # | Serial | Critical char (Ø25 H7 bore) | Material lot | QIF result hash | MES release hash | Released at |
|---|---|---|---|---|---|---|
| 01 | IMP4471-0001 | 25.0038 mm | HT-88213 | `474aaa15d4…` | `6aae6e47f5…` | 2026-06-11T07:00:21.000Z |
| 02 | IMP4471-0002 | 25.0108 mm | HT-88213 | `459157aed0…` | `f88da7ef27…` | 2026-06-11T07:01:06.000Z |
| 03 | IMP4471-0003 | 25.0201 mm | HT-88213 | `e3a1b6d646…` | `1fbeed755c…` | 2026-06-11T07:01:51.000Z |
| 04 | IMP4471-0004 | 25.0078 mm | HT-88213 | `2fb0e9d794…` | `76f59f8d18…` | 2026-06-11T07:02:36.000Z |
| 05 | IMP4471-0005 | 25.0028 mm | HT-88213 | `2e3f195f40…` | `2f2173c0b9…` | 2026-06-11T07:03:21.000Z |
| 06 | IMP4471-0006 | 25.0131 mm | HT-88213 | `2963ae2607…` | `46c8bbcd1f…` | 2026-06-11T07:04:06.000Z |
| 07 | IMP4471-0007 | 25.0065 mm | HT-88213 | `ec0f8b3026…` | `b629bfe6fa…` | 2026-06-11T07:04:51.000Z |
| 08 | IMP4471-0008 | 25.0016 mm | HT-88213 | `f7758184a0…` | `b949347c49…` | 2026-06-11T07:05:36.000Z |
| 09 | IMP4471-0009 | 25.0093 mm | HT-88213 | `918aaecd9e…` | `1a62e2d829…` | 2026-06-11T07:06:21.000Z |
| 10 | IMP4471-0010 | 25.0058 mm | HT-88213 | `9de650fd53…` | `6f6adaa97d…` | 2026-06-11T07:07:06.000Z |
| 11 | IMP4471-0011 | 25.0021 mm | HT-88213 | `0e1b25391e…` | `6410770987…` | 2026-06-11T07:07:51.000Z |
| 12 | IMP4471-0012 | 25.0068 mm | HT-88213 | `6c51e7703d…` | `1b2ddd3147…` | 2026-06-11T07:08:36.000Z |
| 13 | IMP4471-0013 | 25.0044 mm | HT-88213 | `36a4f54556…` | `ad5c5311c3…` | 2026-06-11T07:09:21.000Z |
| 14 | IMP4471-0014 | 25.0038 mm | HT-88213 | `b807115d40…` | `d0e91b5386…` | 2026-06-11T07:10:06.000Z |

Released tolerance for the critical characteristic: 25.000 +0.021 / 0 mm (H7). Part 3 at 25.0201 mm sits at 95.6% of the tolerance band - inside tolerance, and the tightest unit in the batch.

## 4. Topology graph (declared = observed for this run)
Nodes: agent mfg-pilot 3.1.0 · orchestrator shopfloor-orch 2.2 · model claude-sonnet-4-6 · gateway toolproxy-2 · connector opcua-gw 1.8.0 · cell cnc-cell-4 · mes ironmark/prod · runtime edge-mes-01.
Edges: agent->orchestrator->model (inference); agent->gateway->connector->cell (release path); agent->mes (context and batch record, read/write). No undeclared touchpoints observed (third-party touchpoint set exhaustive for this run; basis: connector egress telemetry) [env:0074 | boundary_assessment.basis].

## 5. Chronology and silence semantics
Run window 07:00:00-07:10:52Z; heartbeats every 60s (10 beats, 0 silent windows); anchors at 300s cadence (3 receipts); end-of-shift reconciliation 16:10Z. Emission fail-closed => within the declared boundary, absence of an envelope implies absence of a release-boundary action.

## 6. Known stubs and limitations (golden trace v2)
Signatures are placeholders; anchor store is simulated (EB-004 real distributed_ledger anchor pending); QIF result webhook authenticity (QMS mTLS) is asserted not demonstrated; the subcontracted heat-treatment and plating legs are outside the capture boundary by design. Hashes, chain, ordering, coverage arithmetic, and part-to-artifact linkage are real and re-verifiable under RFC 8785 JCS with no JSON floats in hash scope.
