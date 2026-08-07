# External Assurance / Regulator Evidence Pack - APRUN-2026-06-09-A

## 1. Scope of evidence
Autonomous accounts-payable payment execution by Caldera Robotics Ltd, run APRUN-2026-06-09-A, 2026-06-09 09:00–09:11 UTC, settlement reconciliation T+0 EOD. Evidence bundle `bundle:APRUN-2026-06-09-A` [env:0076 | export.evidence_bundle_id] - 76 envelopes, 29 referenced artifacts.

## 2. Systems involved (execution topology)
agent:caldera/ap-pilot 2.4.1 → orchestrator:caldera/flowdeck 1.9 → model:anthropic/claude-sonnet-4-6 → gateway:caldera/toolproxy-3 → connector:openbank-gw 2.2.0 → provider:first-meridian-bank (SEPA Inst) · context source erp:ledgerworks/prod · runtime aws/eu-west-1 [env:0007 | actor]. One authority chain spans all nodes (AD-7844).

## 3. Authority model
Delegation AD-7844: CFO → AP agent; per-payment €25,000; batch €150,000; approved-beneficiary constraint (supplier-master v2026-05); validity 2026-04-02→2026-12-31; policy `caldera/ap-payments` v3.2 in force [env:0007 | authority.policy_ref]. The granting principal (`delegator_id`) is recorded pseudonymously; resolution is available to authorised reviewers via the access model.

## 4. Evidence completeness and capture boundary
Coverage 14/14 against an independently reconciled population (ERP queue + bank statement) [env:0073 | reconciliation.envelope_commit_count]. **Declared capture boundary:** the interbank leg (pacs.008 between First Meridian and beneficiary banks) is *outside* the emitter's capture boundary and is evidenced indirectly via pacs.002 ACSC and camt.053; this is disclosed, not inferred. Emission posture fail-closed for commit-boundary actions [env:0007 | emission.emission_fail_posture].

## 5. Exceptions and material events
None. 14/14 committed; 0 exceptions; 0 human interventions; 0 control failures [env:0075 | summary].

## 6. Cryptographic sealing status
SHA-256 hash chain over RFC 8785 JCS canonical JSON (`canonicalisation_version = RFC8785-JCS`), contiguous sequence 0001-0076; chain re-verified at generation. External anchoring every 300s to `anchorstore:trustline-demo/eu` (**simulated for golden trace**). Envelope signatures are **stubs** pending the SE signing profile - disclosed per scoped-assurance rules. Personal data carried by reference with hash-substitution redaction (`redact:beneficiary-pii/v1`); redacted fields enumerated per envelope [env:0005 | privacy.redacted_fields].

## 7. Appendix A - artifact register (ISO 20022)
| Artifact | SHA-256 |
|---|---|
| camt053_20260609.xml | `9f5f1a2529ee0d61…` |
| pacs002_P01.xml | `d356feef09879924…` |
| pacs002_P02.xml | `48e0262e359f6a08…` |
| pacs002_P03.xml | `f8eeaf8f88e24172…` |
| pacs002_P04.xml | `c2608b9f878ad19f…` |
| pacs002_P05.xml | `11f1eb536f79f8d0…` |
| pacs002_P06.xml | `069faded18ef6f25…` |
| pacs002_P07.xml | `ec4db0b3fb3f5b01…` |
| pacs002_P08.xml | `f0fcc439be389e5c…` |
| pacs002_P09.xml | `7a48463cb15dc6d9…` |
| pacs002_P10.xml | `e845050d96b5425c…` |
| pacs002_P11.xml | `0bb554bcb8d22ba5…` |
| pacs002_P12.xml | `bafc606a6aa33057…` |
| pacs002_P13.xml | `7fd5a242a1af8800…` |
| pacs002_P14.xml | `daace35cf75851db…` |
| pain001_P01.xml | `c659ef7ca0f22df3…` |
| pain001_P02.xml | `d456264de2aade16…` |
| pain001_P03.xml | `946ea07aad568ecf…` |
| pain001_P04.xml | `dfc787e69b59a874…` |
| pain001_P05.xml | `4ed1ffecc2d18f7c…` |
| pain001_P06.xml | `2dd8b1222bc94ae8…` |
| pain001_P07.xml | `a0621cc93197c383…` |
| pain001_P08.xml | `b3dc070e6bdc6848…` |
| pain001_P09.xml | `37fe631b03d922c7…` |
| pain001_P10.xml | `6af05914138099ef…` |
| pain001_P11.xml | `c0458fef849b5b84…` |
| pain001_P12.xml | `7deab2e1d759ad57…` |
| pain001_P13.xml | `f01e44097deef17c…` |
| pain001_P14.xml | `2c53b3a315788a0f…` |

## 8. Appendix B - anchor receipts
| Receipt | Anchored at | Chain head |
|---|---|---|
| anch:001 | 2026-06-09T09:05:00.000Z | `bb8c3c3402fb5a55…` |
| anch:002 | 2026-06-09T09:10:00.000Z | `b3fedff1591049a0…` |
| anch:003 | 2026-06-09T09:10:52.000Z | `49f364637b9f60c7…` |

## 9. Reliance boundary
Evidence supports: internal audit reliance; external review with re-verification; insurer notification support. It does not constitute: a compliance certification; a fairness or legality determination; coverage of systems outside §4's declared boundary.
