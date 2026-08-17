# Conformity Assessment / Notified-Body Evidence Pack - MRUN-2026-06-11-A

## 1. Scope of evidence
Autonomous production batch release by Ironmark Precision Ltd, run MRUN-2026-06-11-A, 2026-06-11 07:00–07:11 UTC, batch reconciliation T+0 end of shift. Part IMP-4471 hydraulic manifold, drawing rev D, 14 units. Evidence bundle `bundle:MRUN-2026-06-11-A` [env:0076 | export.evidence_bundle_id] - 76 envelopes, 31 referenced artifacts.

## 2. Systems involved (execution topology)
agent:ironmark/mfg-pilot 3.1.0 -> orchestrator:ironmark/shopfloor-orch 2.2 -> model:anthropic/claude-sonnet-4-6 -> gateway:ironmark/toolproxy-2 -> connector:opcua-gw 1.8.0 -> cell:ironmark/cnc-cell-4 (machining + in-line CMM) · context source mes:ironmark/prod (ISA-95) · runtime edge:ironmark/edge-mes-01 (on-premise) [env:0007 | actor]. One authority chain spans all nodes (MD-5120).

## 3. Authority model
Delegation MD-5120: Quality Director -> manufacturing agent; per-part release inside released drawing rev D tolerances for critical characteristics; batch release up to authorised order quantity (14); released-engineering constraint (drawing IMP-4471 rev D + work instruction WI-4471 v5.1 only); validity 2026-04-15 to 2026-12-31; policy `ironmark/part-release` v5.1 in force [env:0007 | authority.policy_ref]. The granting principal (`delegator_id`) is recorded pseudonymously; resolution is available to authorised reviewers via the access model.

## 4. Evidence completeness and capture boundary
Coverage 14/14 against an independently reconciled population (MES production order + finished-goods goods-receipt) [env:0073 | reconciliation.evidence_coverage_ratio]. **Declared capture boundary:** downstream heat-treatment and plating performed by an external subcontractor are *outside* the emitter's capture boundary and are evidenced indirectly via the incoming EN 10204 3.1 material certificate and the subcontractor's certificate of conformance; this is disclosed, not inferred. Emission posture fail-closed for release-boundary actions [env:0007 | emission.emission_fail_posture].

## 5. Exceptions and material events
None. 14/14 released conforming; 0 exceptions; 0 scrap; 0 human interventions; 0 control failures [env:0075 | summary].

## 6. Cryptographic sealing status
SHA-256 hash chain over canonical JSON (`canonicalisation_version = GT-JCS-0`), contiguous sequence 0001-0076; chain re-verified at generation. External anchoring every 300s to `anchorstore:trustline-demo/eu` (**simulated for golden trace**). Envelope signatures are **stubs** pending the SE signing profile - disclosed per scoped-assurance rules. Operator identity and any personal data carried by reference with hash-substitution redaction (`redact:operator-pii/v1`); redacted fields enumerated per envelope [env:0005 | privacy.redacted_fields].

## 7. Appendix A - artifact register (manufacturing interop standards)
| Artifact | SHA-256 |
|---|---|
| b2mml_batchrecord_MRUN-2026-06-11-A.xml | `a9b32ae60e13c22b…` |
| matcert_HT-88213.xml | `b06cef666a271015…` |
| mes_release_SN0001.xml | `6aae6e47f54dae57…` |
| mes_release_SN0002.xml | `f88da7ef27412875…` |
| mes_release_SN0003.xml | `1fbeed755c24a39b…` |
| mes_release_SN0004.xml | `76f59f8d189c3c93…` |
| mes_release_SN0005.xml | `2f2173c0b9a52b61…` |
| mes_release_SN0006.xml | `46c8bbcd1fd4f692…` |
| mes_release_SN0007.xml | `b629bfe6faeb68ce…` |
| mes_release_SN0008.xml | `b949347c49f31e20…` |
| mes_release_SN0009.xml | `1a62e2d829dbcfa9…` |
| mes_release_SN0010.xml | `6f6adaa97dbd4abd…` |
| mes_release_SN0011.xml | `6410770987024e1a…` |
| mes_release_SN0012.xml | `1b2ddd31478a8725…` |
| mes_release_SN0013.xml | `ad5c5311c334e534…` |
| mes_release_SN0014.xml | `d0e91b53861feb70…` |
| mtconnect_MRUN-2026-06-11-A.xml | `c7e84fe697c4c256…` |
| qif_SN0001.xml | `474aaa15d47a58c9…` |
| qif_SN0002.xml | `459157aed099c207…` |
| qif_SN0003.xml | `e3a1b6d646fa1335…` |
| qif_SN0004.xml | `2fb0e9d79419b82b…` |
| qif_SN0005.xml | `2e3f195f40c2d459…` |
| qif_SN0006.xml | `2963ae2607fc5ebe…` |
| qif_SN0007.xml | `ec0f8b3026b0dd21…` |
| qif_SN0008.xml | `f7758184a01fd539…` |
| qif_SN0009.xml | `918aaecd9eaff49b…` |
| qif_SN0010.xml | `9de650fd531158dd…` |
| qif_SN0011.xml | `0e1b25391e550109…` |
| qif_SN0012.xml | `6c51e7703da9fa0a…` |
| qif_SN0013.xml | `36a4f54556718c83…` |
| qif_SN0014.xml | `b807115d40e49bf4…` |

## 8. Appendix B - anchor receipts
| Receipt | Anchored at | Chain head |
|---|---|---|
| anch:001 | 2026-06-11T07:05:00.000Z | `bdf60861910121b1…` |
| anch:002 | 2026-06-11T07:10:00.000Z | `2fd602e5867fadf9…` |
| anch:003 | 2026-06-11T07:10:52.000Z | `0f271189642a1304…` |

## 9. Reliance boundary
Evidence supports: internal quality-management reliance; customer source-surveillance and incoming acceptance with re-verification; notified-body review. It does not constitute: an airworthiness or conformity certification; a fitness-for-purpose determination; coverage of processes outside §4's declared boundary.
