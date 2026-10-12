# Board Assurance Summary - Autonomous AP Payment Run APRUN-2026-06-09-A
**Organisation:** Caldera Robotics Ltd · **Period:** 2026-06-09 09:00–09:11 UTC (settlement reconciled T+0 EOD) · **Assurance basis:** SE v0.1-draft evidence, scoped - see Reliance Boundary.

## The assurance statement
> **An authorised autonomous process executed 14 payment instructions under delegated authority AD-7844.** [env:0007 | authority.authority_context_ref] [env:0075 | summary.committed_count] - all 14 commit events carry `authority_context_ref = AD-7844` with delegation receipt `delrec:AD-7844/2026-04-02` granted by the CFO [env:0007 | authority.delegation_receipt_ref] [env:0007 | authority.delegator_id] under payment policy v3.2 in force throughout [env:0007 | authority.policy_version].
>
> **All payments remained within approved policy boundaries.** Each of the 14 instructions passed three pre-commit policy checks - approved-beneficiary, per-payment limit, and duplicate-key - evaluated *before* execution, 42 control evaluations in total, all passed [env:0004 | controls.control_evaluation_phase] [env:0004 | controls.checks[*].control_result]. Peak single-payment authority utilisation was 95.6% of the EUR 25,000 limit (payment 3, derived from Amount operands) [env:0013 | controls.checks[1].observed.amount] [env:0013 | controls.checks[1].observed.limit]; batch aggregate EUR 117,406.18 used 78.3% of the EUR 150,000 batch limit (report-layer derived).
>
> **No exceptions requiring human intervention occurred.** Exception count 0, human-intervention count 0 [env:0075 | summary.exception_count] [env:0075 | summary.human_intervention_count]; no approval was required under the policy rule for at-limit payments to approved beneficiaries [env:0004 | authority.approval_status] [env:0004 | authority.approval_basis].
>
> **Evidence integrity validated.** All 76 envelopes form an unbroken SHA-256 hash chain (re-verified at report generation), with the chain head recorded every 5 minutes in 3 in-trace anchors that are simulated and say so (`basis_status: simulated`, never `externally_anchored`) [env:0036 | anchoring.anchors[0].basis_status]; emission ran fail-closed for commit-boundary actions throughout [env:0007 | emission.emission_fail_posture]; liveness heartbeats present for every 60-second interval of the run with zero silent windows [env:0009 | liveness.liveness_status].
>
> **No cross-tenant data exposure detected.** Tenant-boundary and cross-customer exposure indicators are false, on the stated basis that runtime egress was limited to the bank API and ERP [env:0074 | boundary_assessment.cross_tenant_exposure_indicator] [env:0074 | boundary_assessment.boundary_assessment_basis].

## What the board should know
- **External confirmation, not self-assertion:** every payment carries a three-rung acknowledgment ladder - transport (HTTPS 200), protocol (bank API ACCEPTED), business (ISO 20022 pacs.002 status **ACSC** = settlement completed) [env:0007 | acknowledgments[*]] - and the bank's end-of-day camt.053 statement reconciles **14 of 14** instructions [env:0073 | reconciliation.bank_statement_count].
- **Completeness is measured, not asserted:** the in-scope population is independently defined (ERP approved-invoice queue: 14 due; bank statement: 14 booked) and evidence coverage is **14/14 = 100%**, tamper-evident coverage 100% (report-layer derived) [env:0073 | reconciliation.evidence_population_ref] [env:0073 | reconciliation.envelope_commit_count].
- **Leading indicator:** one payment ran at 95.6% of its limit; nothing breached, but limit headroom on supplier SUP-003 invoices is worth a policy review.
- **Recommended position:** continue autonomous operation at current scope; no restriction indicated by this run's evidence.

## Reliance boundary
This report evidences this run only; it supports internal assurance and audit reliance for the stated period and population. It is **not** a compliance certification, and statements are bounded by the capture boundary declared in the Regulator Pack (§4). In this golden trace envelope signatures are stubs (`envelope_signature_basis_status: stubbed`) and in-trace anchors are simulated (`basis_status: simulated`); neither is an independently verifiable claim.
