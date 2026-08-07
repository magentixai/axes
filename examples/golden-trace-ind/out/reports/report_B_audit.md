# Quality and Control View - MRUN-2026-06-11-A

## 1. Controls relevant and evidenced
Three preventive quality gates (control set `ctl:part-release/v5.1`) were evaluated **pre-release** for each unit [env:0004 | controls.control_evaluation_phase]:

| # | Serial | Critical characteristic | CTL-DIM-01 dimension in tolerance | CTL-SPC-02 process capability (Cpk >= 1.33) | CTL-MAT-03 material lot verified | QE disposition |
|---|---|---|---|---|---|---|
| 01 | IMP4471-0001 | Ø25 H7 bore | passed (17.9%) | passed (Cpk 1.92) | passed (HT-88213) | not_required |
| 02 | IMP4471-0002 | Ø25 H7 bore | passed (51.5%) | passed (Cpk 1.71) | passed (HT-88213) | not_required |
| 03 | IMP4471-0003 | Ø25 H7 bore | passed (95.6%) | passed (Cpk 1.41) | passed (HT-88213) | not_required |
| 04 | IMP4471-0004 | Ø25 H7 bore | passed (37.0%) | passed (Cpk 1.80) | passed (HT-88213) | not_required |
| 05 | IMP4471-0005 | Ø25 H7 bore | passed (13.3%) | passed (Cpk 1.95) | passed (HT-88213) | not_required |
| 06 | IMP4471-0006 | Ø25 H7 bore | passed (62.4%) | passed (Cpk 1.63) | passed (HT-88213) | not_required |
| 07 | IMP4471-0007 | Ø25 H7 bore | passed (31.1%) | passed (Cpk 1.83) | passed (HT-88213) | not_required |
| 08 | IMP4471-0008 | Ø25 H7 bore | passed (7.8%) | passed (Cpk 1.98) | passed (HT-88213) | not_required |
| 09 | IMP4471-0009 | Ø25 H7 bore | passed (44.1%) | passed (Cpk 1.74) | passed (HT-88213) | not_required |
| 10 | IMP4471-0010 | Ø25 H7 bore | passed (27.6%) | passed (Cpk 1.86) | passed (HT-88213) | not_required |
| 11 | IMP4471-0011 | Ø25 H7 bore | passed (9.9%) | passed (Cpk 1.97) | passed (HT-88213) | not_required |
| 12 | IMP4471-0012 | Ø25 H7 bore | passed (32.5%) | passed (Cpk 1.82) | passed (HT-88213) | not_required |
| 13 | IMP4471-0013 | Ø25 H7 bore | passed (20.9%) | passed (Cpk 1.89) | passed (HT-88213) | not_required |
| 14 | IMP4471-0014 | Ø25 H7 bore | passed (18.1%) | passed (Cpk 1.90) | passed (HT-88213) | not_required |

**Result: 42/42 control evaluations passed; 0 failed; 0 bypassed; 0 not_observed.** Quality-engineer disposition was `not_required` under policy v5.1's rule for characteristics inside tolerance on a released drawing revision [env:0004 | authority.approval_basis]; consequently no manual-disposition assertion is made or needed for this run - the control relied upon is the released-tolerance + verified-material-lot pair, both evidenced above.

## 2. Population and completeness (IPE basis)
- Population definition: MES production order PO-IRN-2026-4471-06 at 06:55Z (14 planned) reconciled against finished-goods goods-receipt GRN-2026-06-11-IMP4471 (14 booked, 0 scrap) - **independently reconciled**, not self-reported [env:0073 | reconciliation.population_basis].
- Coverage: envelopes 14/14 (100%); tamper-evident 100% (report-layer derived from envelope_commit_count).
- Sequence continuity: envelope sequence numbers 0001-0076 contiguous, no gaps (stream-internal proof); heartbeats at 60s intervals, zero silent windows (silence semantics) [env:0009 | liveness.declared_heartbeat_interval_s].

## 3. Evidence quality
- Origin/basis: runtime-observed on the shop-floor edge; release confirmations are **quality-system confirmed** (QIF 3.0 CONFORMING per unit) and **source-system corroborated** (ISA-95 batch record) [env:0007 | evidence_quality.corroboration_state] [env:0073 | evidence_quality.corroboration_state].
- Corroboration coverage decomposition: anchored 100% · quality-receipted 14/14 · provider-only 0.
- Point-in-time validity: policy v5.1 effective from 2026-05-01, in force at every event [env:0007 | authority.policy_version]; drawing rev D released 2026-03-20; delegation valid 2026-04-15 to 2026-12-31.
- Model context: sampling parameters recorded (temperature 0.2, top_p 0.9 as exact decimal strings); replay claim scoped - *reproducible in distribution, not in instance* [env:0002 | model.sampling_parameters]; reasoning artifacts `provider_withheld` - disclosed, not silent [env:0002 | model.reasoning_artifact_availability].

## 4. Findings register
No exceptions, deficiencies, or open actions arise from this run. One observation (OBS-001, advisory): peak characteristic utilisation 95.6% with the lowest capability of the batch at Cpk 1.41 - recommend a process-capability review for the Ø25 H7 bore before the next batch. Owner: manufacturing process owner. Due: next production cycle.
