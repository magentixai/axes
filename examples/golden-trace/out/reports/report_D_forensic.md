# Forensic Execution Pack - APRUN-2026-06-09-A

## 1. Verification procedure (vendor-neutral)
1. Read `envelopes.jsonl` in sequence order. 2. For each envelope, remove `integrity.envelope_hash` and `integrity.envelope_signature`; serialise with RFC 8785 JCS; SHA-256; compare to stored hash. 3. Confirm `previous_envelope_hash` equals the prior envelope's hash (genesis = 64×'0'). 4. Confirm sequence numbers are contiguous. 5. Confirm `anchoring.anchored_subject_hash` at each `attestation_recorded` event equals the chain head before it, and that `anchor_requested_at` is not before that record's `emitted_at`. 6. Re-hash each file in `artifacts/` and compare with `manifest.json`. Steps 1-6 are reproducible from the bundle alone. Step 5 shows internal consistency only: the in-trace anchors are `basis_status: simulated`. The external existence bound is on the release, not the trace: the release statement committing to this corpus is anchored with RFC 3161 and OpenTimestamps (repository `RELEASES.md`, `VERIFY.md`).

## 2. Envelope sequence (first 24 of 76; full stream in envelopes.jsonl)
| Seq | event_kind | Pay# | occurred_at | envelope_hash |
|---|---|---|---|---|
| 0001 | execution_started |  -  | 2026-06-09T09:00:00.000Z | `e38296d9b9d8…` |
| 0002 | context_retrieved |  -  | 2026-06-09T09:00:04.000Z | `8994865a0194…` |
| 0003 | plan_created |  -  | 2026-06-09T09:00:09.000Z | `516f6dfaa15c…` |
| 0004 | policy_check_performed | 1 | 2026-06-09T09:00:12.000Z | `bc6b8e2f8757…` |
| 0005 | commit_attempted | 1 | 2026-06-09T09:00:18.000Z | `5f4777135bd1…` |
| 0006 | tool_invoked | 1 | 2026-06-09T09:00:19.000Z | `233631960ce2…` |
| 0007 | commit_succeeded | 1 | 2026-06-09T09:00:21.000Z | `86eee284570f…` |
| 0008 | policy_check_performed | 2 | 2026-06-09T09:00:57.000Z | `52c2bfef03ba…` |
| 0009 | heartbeat_event |  -  | 2026-06-09T09:01:00.000Z | `741e26e97a1e…` |
| 0010 | commit_attempted | 2 | 2026-06-09T09:01:03.000Z | `7940ca1e390a…` |
| 0011 | tool_invoked | 2 | 2026-06-09T09:01:04.000Z | `b370697e8d06…` |
| 0012 | commit_succeeded | 2 | 2026-06-09T09:01:06.000Z | `c4013507b775…` |
| 0013 | policy_check_performed | 3 | 2026-06-09T09:01:42.000Z | `a6b6a30ab223…` |
| 0014 | commit_attempted | 3 | 2026-06-09T09:01:48.000Z | `8ab9fc75b2b9…` |
| 0015 | tool_invoked | 3 | 2026-06-09T09:01:49.000Z | `4bd343bf0c05…` |
| 0016 | commit_succeeded | 3 | 2026-06-09T09:01:51.000Z | `f88ee8003282…` |
| 0017 | heartbeat_event |  -  | 2026-06-09T09:02:00.000Z | `4e8dd50fa21a…` |
| 0018 | policy_check_performed | 4 | 2026-06-09T09:02:27.000Z | `54ee51315be5…` |
| 0019 | commit_attempted | 4 | 2026-06-09T09:02:33.000Z | `328c47be3dde…` |
| 0020 | tool_invoked | 4 | 2026-06-09T09:02:34.000Z | `7b7dfab85a1d…` |
| 0021 | commit_succeeded | 4 | 2026-06-09T09:02:36.000Z | `4e91af83faea…` |
| 0022 | heartbeat_event |  -  | 2026-06-09T09:03:00.000Z | `6e803aeed0ed…` |
| 0023 | policy_check_performed | 5 | 2026-06-09T09:03:12.000Z | `f41632fb5d16…` |
| 0024 | commit_attempted | 5 | 2026-06-09T09:03:18.000Z | `9c7f0af81208…` |

## 3. Payment ↔ artifact ↔ confirmation linkage
| # | EndToEndId | Amount | Beneficiary | Invoice | pain.001 hash | pacs.002 hash | Committed at |
|---|---|---|---|---|---|---|---|
| 01 | E2E-CALD-20260609-0001 | €4,475.00 | SUP-001 | INV-2026-3318 | `c659ef7ca0…` | `d356feef09…` | 2026-06-09T09:00:21.000Z |
| 02 | E2E-CALD-20260609-0002 | €12,880.50 | SUP-002 | INV-2026-3325 | `d456264de2…` | `48e0262e35…` | 2026-06-09T09:01:06.000Z |
| 03 | E2E-CALD-20260609-0003 | €23,900.00 | SUP-003 | INV-2026-3327 | `946ea07aad…` | `f8eeaf8f88…` | 2026-06-09T09:01:51.000Z |
| 04 | E2E-CALD-20260609-0004 | €9,240.10 | SUP-004 | INV-2026-3340 | `dfc787e69b…` | `c2608b9f87…` | 2026-06-09T09:02:36.000Z |
| 05 | E2E-CALD-20260609-0005 | €3,318.75 | SUP-005 | INV-2026-3341 | `4ed1ffecc2…` | `11f1eb536f…` | 2026-06-09T09:03:21.000Z |
| 06 | E2E-CALD-20260609-0006 | €15,602.00 | SUP-006 | INV-2026-3355 | `2dd8b1222b…` | `069faded18…` | 2026-06-09T09:04:06.000Z |
| 07 | E2E-CALD-20260609-0007 | €7,777.77 | SUP-007 | INV-2026-3360 | `a0621cc931…` | `ec4db0b3fb…` | 2026-06-09T09:04:51.000Z |
| 08 | E2E-CALD-20260609-0008 | €1,949.99 | SUP-008 | INV-2026-3361 | `b3dc070e6b…` | `f0fcc439be…` | 2026-06-09T09:05:36.000Z |
| 09 | E2E-CALD-20260609-0009 | €11,025.40 | SUP-009 | INV-2026-3372 | `37fe631b03…` | `7a48463cb1…` | 2026-06-09T09:06:21.000Z |
| 10 | E2E-CALD-20260609-0010 | €6,890.00 | SUP-010 | INV-2026-3375 | `6af0591413…` | `e845050d96…` | 2026-06-09T09:07:06.000Z |
| 11 | E2E-CALD-20260609-0011 | €2,475.25 | SUP-011 | INV-2026-3380 | `c0458fef84…` | `0bb554bcb8…` | 2026-06-09T09:07:51.000Z |
| 12 | E2E-CALD-20260609-0012 | €8,112.60 | SUP-012 | INV-2026-3384 | `7deab2e1d7…` | `bafc606a6a…` | 2026-06-09T09:08:36.000Z |
| 13 | E2E-CALD-20260609-0013 | €5,230.95 | SUP-013 | INV-2026-3390 | `f01e44097d…` | `7fd5a242a1…` | 2026-06-09T09:09:21.000Z |
| 14 | E2E-CALD-20260609-0014 | €4,527.87 | SUP-014 | INV-2026-3391 | `2c53b3a315…` | `daace35cf7…` | 2026-06-09T09:10:06.000Z |

## 4. Topology graph (declared = observed for this run)
Nodes: agent ap-pilot 2.4.1 · orchestrator flowdeck 1.9 · model claude-sonnet-4-6 · gateway toolproxy-3 · connector openbank-gw 2.2.0 · provider first-meridian-bank · erp ledgerworks · runtime aws/eu-west-1.
Edges: agent→orchestrator→model (inference); agent→gateway→connector→provider (commit path); agent→erp (context, read-only). No undeclared touchpoints observed (third-party touchpoint set exhaustive for this run; basis: connector egress telemetry) [env:0074 | boundary_assessment.boundary_assessment_basis].

## 5. Chronology and silence semantics
Run window 09:00:00–09:10:52Z; heartbeats every 60s (10 beats, 0 silent windows); simulated in-trace anchors at 300s cadence (3); EOD reconciliation 18:10Z. Emission fail-closed ⇒ within the declared boundary, absence of an envelope implies absence of a commit-boundary action.

## 6. Known stubs and limitations (golden trace gt-v2.1)
Signatures are placeholders (`envelope_signature_basis_status: stubbed`). In-trace anchors are simulated (`basis_status: simulated`). The pacs.002 webhook (mTLS) and camt.053 statement-channel authenticity rungs are stubs (`basis_status: stubbed`); the HTTPS and bank-API rungs are `simulated` because the trace is synthetic. Each status is in a field a verifier reads (catalogue 1.27). A real on-chain anchor lane (EB-004, axes#3) remains open; the interbank pacs.008 leg is outside the capture boundary by design. Hashes, chain, ordering, coverage arithmetic, and artifact linkage are real and re-verifiable under RFC 8785 JCS with integer Amount fields (no JSON floats in hash scope).
