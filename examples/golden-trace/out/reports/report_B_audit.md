# Audit & Control View — APRUN-2026-06-09-A

## 1. Controls relevant and evidenced
Three preventive controls (control set `ctl:ap-pay/v3.2`) were evaluated **pre-commit** for each instruction [env:0004 | controls.control_evaluation_phase]:

| # | Beneficiary | Amount | CTL-BENEF-01 approved-list | CTL-LIMIT-02 per-payment limit | CTL-DUPL-03 duplicate key | Human approval |
|---|---|---|---|---|---|---|
| 01 | SUP-001 | €4,475.00 | passed | passed (17.9%) | passed | not_required |
| 02 | SUP-002 | €12,880.50 | passed | passed (51.5%) | passed | not_required |
| 03 | SUP-003 | €23,900.00 | passed | passed (95.6%) | passed | not_required |
| 04 | SUP-004 | €9,240.10 | passed | passed (37.0%) | passed | not_required |
| 05 | SUP-005 | €3,318.75 | passed | passed (13.3%) | passed | not_required |
| 06 | SUP-006 | €15,602.00 | passed | passed (62.4%) | passed | not_required |
| 07 | SUP-007 | €7,777.77 | passed | passed (31.1%) | passed | not_required |
| 08 | SUP-008 | €1,949.99 | passed | passed (7.8%) | passed | not_required |
| 09 | SUP-009 | €11,025.40 | passed | passed (44.1%) | passed | not_required |
| 10 | SUP-010 | €6,890.00 | passed | passed (27.6%) | passed | not_required |
| 11 | SUP-011 | €2,475.25 | passed | passed (9.9%) | passed | not_required |
| 12 | SUP-012 | €8,112.60 | passed | passed (32.5%) | passed | not_required |
| 13 | SUP-013 | €5,230.95 | passed | passed (20.9%) | passed | not_required |
| 14 | SUP-014 | €4,527.87 | passed | passed (18.1%) | passed | not_required |

**Result: 42/42 control evaluations passed; 0 failed; 0 bypassed; 0 not_observed.** Approval was `not_required` under policy v3.2's rule for at-or-below-limit payments to approved beneficiaries [env:0004 | authority.approval_basis]; consequently no SoD/dual-control assertion is made or needed for this run — the control relied upon is the delegated-limit + approved-list pair, both evidenced above.

## 2. Population and completeness (IPE basis)
- Population definition: ERP approved-invoice queue at 08:55Z (14 due) reconciled against bank statement FMB-STMT-2026-06-09 (14 booked) — **independently reconciled**, not self-reported [env:0073 | reconciliation.population_basis].
- Coverage: envelopes 14/14 (100%); tamper-evident 100% [env:0073 | reconciliation.evidence_coverage_ratio].
- Sequence continuity: envelope sequence numbers 0001–0076 contiguous, no gaps (stream-internal proof); heartbeats at 60s intervals, zero silent windows (silence semantics) [env:0009 | liveness.declared_heartbeat_interval_s].

## 3. Evidence quality
- Origin/basis: runtime-observed; commit confirmations are **third-party confirmed** (pacs.002 ACSC per payment) and **source-system corroborated** (camt.053) [env:0007 | evidence_quality.corroboration_state] [env:0073 | evidence_quality.corroboration_state].
- Corroboration coverage decomposition: anchored 100% · receipted 14/14 · provider-only 0.
- Point-in-time validity: policy v3.2 effective from 2026-05-01, in force at every event [env:0007 | authority.policy_version]; delegation valid 2026-04-02 → 2026-12-31.
- Model context: sampling parameters recorded (temperature 0.2, top_p 0.9); replay claim scoped — *reproducible in distribution, not in instance* [env:0002 | model.sampling_parameters]; reasoning artifacts `provider_withheld` — disclosed, not silent [env:0002 | model.reasoning_artifact_availability].

## 4. Findings register
No exceptions, deficiencies, or open actions arise from this run. One observation (OBS-001, advisory): peak per-payment utilisation 95.6% — recommend limit-headroom review for SUP-003. Owner: AP process owner. Due: next policy cycle.
