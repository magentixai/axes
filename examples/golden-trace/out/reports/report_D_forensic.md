# Forensic Execution Pack — APRUN-2026-06-09-A

## 1. Verification procedure (vendor-neutral)
1. Read `envelopes.jsonl` in sequence order. 2. For each envelope, remove `integrity.envelope_hash` and `integrity.signature`; serialise with sorted keys and compact separators; SHA-256; compare to stored hash. 3. Confirm `previous_envelope_hash` equals the prior envelope's hash (genesis = 64×'0'). 4. Confirm sequence numbers are contiguous. 5. Compare chain heads at each `attestation_recorded` event with the anchor receipts in Appendix B of the Regulator Pack. 6. Re-hash each file in `artifacts/` and compare with `manifest.json`. Steps 1–4 and 6 are fully reproducible from the bundle alone; step 5 is simulated in this golden trace.

## 2. Envelope sequence (first 24 of 76; full stream in envelopes.jsonl)
| Seq | event_kind | Pay# | occurred_at | envelope_hash |
|---|---|---|---|---|
| 0001 | execution_started | — | 2026-06-09T09:00:00.000Z | `06b5e40ae177…` |
| 0002 | context_retrieved | — | 2026-06-09T09:00:04.000Z | `c45bf398955a…` |
| 0003 | plan_created | — | 2026-06-09T09:00:09.000Z | `d5ba004f462b…` |
| 0004 | policy_check_performed | 1 | 2026-06-09T09:00:12.000Z | `b1206830ecdb…` |
| 0005 | commit_attempted | 1 | 2026-06-09T09:00:18.000Z | `37f43ef468fa…` |
| 0006 | tool_invoked | 1 | 2026-06-09T09:00:19.000Z | `1f1a382ff7ac…` |
| 0007 | commit_succeeded | 1 | 2026-06-09T09:00:21.000Z | `3676cba2056e…` |
| 0008 | policy_check_performed | 2 | 2026-06-09T09:00:57.000Z | `ee890545177c…` |
| 0009 | heartbeat_event | — | 2026-06-09T09:01:00.000Z | `fbcd1eb02740…` |
| 0010 | commit_attempted | 2 | 2026-06-09T09:01:03.000Z | `d36e6962fba0…` |
| 0011 | tool_invoked | 2 | 2026-06-09T09:01:04.000Z | `a8516a896b1b…` |
| 0012 | commit_succeeded | 2 | 2026-06-09T09:01:06.000Z | `30083260e8b8…` |
| 0013 | policy_check_performed | 3 | 2026-06-09T09:01:42.000Z | `8c0fbc5b10ab…` |
| 0014 | commit_attempted | 3 | 2026-06-09T09:01:48.000Z | `ed4639eaf65b…` |
| 0015 | tool_invoked | 3 | 2026-06-09T09:01:49.000Z | `975a3cb05778…` |
| 0016 | commit_succeeded | 3 | 2026-06-09T09:01:51.000Z | `f06df8908d41…` |
| 0017 | heartbeat_event | — | 2026-06-09T09:02:00.000Z | `896ec4f05690…` |
| 0018 | policy_check_performed | 4 | 2026-06-09T09:02:27.000Z | `7eabe561b7ca…` |
| 0019 | commit_attempted | 4 | 2026-06-09T09:02:33.000Z | `a7f0b15d494f…` |
| 0020 | tool_invoked | 4 | 2026-06-09T09:02:34.000Z | `856e190bd2ec…` |
| 0021 | commit_succeeded | 4 | 2026-06-09T09:02:36.000Z | `152fa0b5e912…` |
| 0022 | heartbeat_event | — | 2026-06-09T09:03:00.000Z | `b19a70816247…` |
| 0023 | policy_check_performed | 5 | 2026-06-09T09:03:12.000Z | `b08c316b464f…` |
| 0024 | commit_attempted | 5 | 2026-06-09T09:03:18.000Z | `22f88bedb6c9…` |

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
Edges: agent→orchestrator→model (inference); agent→gateway→connector→provider (commit path); agent→erp (context, read-only). No undeclared touchpoints observed (third-party touchpoint set exhaustive for this run; basis: connector egress telemetry) [env:0074 | boundary_assessment.basis].

## 5. Chronology and silence semantics
Run window 09:00:00–09:10:52Z; heartbeats every 60s (10 beats, 0 silent windows); anchors at 300s cadence (3 receipts); EOD reconciliation 18:10Z. Emission fail-closed ⇒ within the declared boundary, absence of an envelope implies absence of a commit-boundary action.

## 6. Known stubs and limitations (golden trace)
Signatures are placeholders; anchor store is simulated; pacs.002 webhook authenticity (mTLS) is asserted not demonstrated; the interbank pacs.008 leg is outside the capture boundary by design. Hashes, chain, ordering, coverage arithmetic, and artifact linkage are real and re-verifiable.
