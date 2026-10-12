#!/usr/bin/env python3
"""
SE v0.1 Golden Trace Generator - "Ironmark Precision / MD-5120" (Industrial variant)
====================================================================================
Generates a fully synthetic, deterministic, end-to-end Agentic Execution
Evidence trace for the canonical manufacturing scenario:

  "An authorised autonomous process released 14 machined parts under delegated
   authority MD-5120. Every part remained within released engineering tolerance.
   No exceptions requiring human intervention occurred. Evidence integrity
   validated. No cross-programme contamination detected."

Outputs (under ./out):
  envelopes.jsonl                 - full SE envelope stream (hash-chained)
  samples/*.json                  - pretty-printed exemplar envelopes
  artifacts/*.xml                 - QIF / MES / B2MML / MTConnect / matcert stand-ins
  manifest.json                   - evidence bundle manifest (file hashes, bundle hash)
  reports/report_A_board.md       - Board assurance summary (claim-cited)
  reports/report_B_audit.md       - Quality & control view
  reports/report_C_regulator.md   - Conformity assessment pack
  reports/report_D_forensic.md    - Forensic execution pack

Design notes:
  * Same structural skeleton as examples/golden-trace/ (76 envelopes, RFC 8785 JCS).
  * No JSON floats in hash scope: measurements/Cpk as exact decimal strings; ratios report-layer.
  * gt-v2.1 (docs/19): every authenticity claim carries `basis_status`. Signatures are
    `stubbed`; in-trace anchors are `simulated` (a synthetic trace cannot be anchored at
    fictional past instants) and never assert `externally_anchored`. Hashes are real.
    The release statement over this corpus is anchored for real under anchors/.
  * Deterministic: fixed timestamps, no randomness.
"""

import json, hashlib, os, sys
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from decimal import Decimal

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from tools.axes_canonical import (
    CANONICALISATION_VERSION,
    assert_manifest_matches_files,
    assert_no_floats_in_hash_scope,
    canonical_bytes,
    decimal_str,
    envelope_digest,
    sha256_hex,
    write_json_utf8_lf,
    write_text_utf8_lf,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# ----------------------------------------------------------------------------
# 1. Scenario constants
# ----------------------------------------------------------------------------
SE_VERSION = "0.1-draft"
PROFILE_ID = "se-profile:manufacturing-emitter/0.1-draft"
CONFORMANCE_LEVEL = "SE-C4-assurance-report-capable (claimed, golden-trace-ind)"
CANON = CANONICALISATION_VERSION

ORG = "org:ironmark-precision"
TENANT = "tenant:ironmark-prod"
ENV_ID, ENV_TYPE = "env:prod-eu", "production"

ACTOR = {
    "agent_id": "agent:ironmark/mfg-pilot", "agent_version": "3.1.0",
    "orchestrator_id": "orchestrator:ironmark/shopfloor-orch", "orchestrator_version": "2.2.0",
    "model_id": "model:anthropic/claude-sonnet-4-6", "model_version": "2025-09-29",
    "runtime_id": "runtime:ironmark/edge-mes-01",
    "tool_id": "tool:opcua/part-release",
    "tool_gateway_id": "gateway:ironmark/toolproxy-2",
    "connector_id": "connector:opcua-gw/1.8.0",
    "provider_id": "cell:ironmark/cnc-cell-4",
}
SAMPLING = {"temperature": "0.2", "top_p": "0.9", "max_tokens": 4096,
            "reproducibility_note": "non-zero temperature: reproducible in distribution, not in instance"}

AUTHORITY = {
    "authority_context_ref": "MD-5120",
    "delegation_receipt_ref": "delrec:MD-5120/2026-04-15",
    "delegator_id": "person:pseu/quality-director-7c20",
    "policy_ref": "policy:ironmark/part-release", "policy_version": "5.1",
    "policy_effective_from": "2026-05-01T00:00:00Z",
    "capability_id": "cap:release-conforming-part",
    "engineering_release_ref": "drawing:IMP-4471/revD + wi:WI-4471/v5.1",
    "scope": {"authorised_order_quantity": 14,
              "part_number": "IMP-4471", "drawing_version": "D",
              "critical_characteristic": "\u00d825 H7 bore (25.000 +0.021 / 0 mm)",
              "cpk_floor": "1.33",
              "material_grade_name": "15-5PH stainless",
              "material_heat": "HT-88213",
              "approval_rule": "no quality-engineer disposition required for characteristics inside tolerance on a released drawing revision",
              "valid_from": "2026-04-15T00:00:00Z", "valid_until": "2026-12-31T23:59:59Z"},
}

T0 = datetime(2026, 6, 11, 7, 0, 0, tzinfo=timezone.utc)
def ts(sec): return (T0 + timedelta(seconds=sec)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

# audit table: tolerance utilisation and Cpk per part (part 3 peak util 0.956, Cpk 1.41)
UTILS = [0.179, 0.515, 0.956, 0.370, 0.133, 0.624, 0.311, 0.078,
         0.441, 0.276, 0.099, 0.325, 0.209, 0.181]
CPKS = [1.92, 1.71, 1.41, 1.80, 1.95, 1.63, 1.83, 1.98,
        1.74, 1.86, 1.97, 1.82, 1.89, 1.90]
TOL_UPPER, TOL_LOWER, TOL_RANGE = Decimal("25.021"), Decimal("25.0"), Decimal("0.021")
CHARACTERISTIC = "\u00d825 H7 bore"

def measured_mm(util):
    """Exact measured value as Decimal (stored as decimal string in envelopes)."""
    return (TOL_LOWER + Decimal(str(util)) * TOL_RANGE).quantize(Decimal("0.0001"))

SERIALS = [f"IMP4471-{n:04d}" for n in range(1, 15)]
ORDER_QTY = AUTHORITY["scope"]["authorised_order_quantity"]
CPK_FLOOR = AUTHORITY["scope"]["cpk_floor"]

TRACE_ID = "7c1de4a90b6f42e8b3a5c0d9e1f28a44"
HEARTBEAT_INTERVAL_S = 60
HEARTBEAT_INTERVAL = "PT60S"            # ISO 8601 duration (D-017, D-024 N4)
ANCHOR_INTERVAL_S = 300

# ----------------------------------------------------------------------------
# 2. Hashing, chaining, stub signing
# ----------------------------------------------------------------------------
def canonical(obj) -> bytes:
    return canonical_bytes(obj)

class Chain:
    def __init__(self):
        self.prev = "0" * 64; self.seq = 0; self.envelopes = []; self.anchors = []
        self.prev_emitted_at = None
    def emit(self, env: dict) -> dict:
        self.seq += 1
        env["sequence_number"] = self.seq
        env["envelope_id"] = f"env:MRUN-2026-06-11-A/{self.seq:04d}"
        env.setdefault("integrity", {})
        env["integrity"].update({
            "hash_algorithm": "SHA-256", "canonicalization_version": CANON,
            "previous_envelope_hash": self.prev,
            "signing_key_id": "key:ironmark/se-emitter-2026q2",
            "signing_key_provenance_ref": "kms:ironmark/provenance/se-emitter-2026q2",
            "envelope_signature_basis_status": "stubbed",     # catalogue 1.27; inside the hash
        })
        assert_no_floats_in_hash_scope(env)
        h = envelope_digest(env)
        env["integrity"]["envelope_hash"] = h
        env["integrity"]["envelope_signature"] = "SIG-STUB(" + h[:16] + ")"
        self.prev = h
        self.prev_emitted_at = env["emitted_at"]
        self.envelopes.append(env)
        return env
    def anchor(self, sec):
        """Module 14 block over the current chain head (gt-v2.1, docs/19).

        Simulated: the trace is synthetic, so nothing is written to a mechanism and the
        status is stated in `basis_status`, never in the method value (catalogue 1.27).
        Timing: requested at the anchoring tick, after the anchored record was emitted;
        anchored 250 ms later; the lag is derived, never stored (D-017)."""
        anchor_id = f"anch:{len(self.anchors)+1:03d}"
        requested, anchored = ts(sec), ts(sec + 0.25)
        assert self.prev_emitted_at <= requested, "anchor requested before the anchored record was emitted"
        block = {"anchored_subject_type": "chain_head",
                 "anchored_subject_hash": self.prev,
                 "anchored_subject_hash_algorithm": "SHA-256",
                 "anchors": [{
                     "anchor_id": anchor_id,
                     "anchoring_method": "write_once_store",
                     "basis_status": "simulated",
                     "anchor_commitment_hash": self.prev,
                     "anchor_commitment_hash_algorithm": "SHA-256",
                     "anchor_requested_at": requested,
                     "anchored_at": anchored,
                     "anchor_service_id": "anchorstore:trustline-demo/eu",
                     "anchor_record_ref": "object:trustline-demo/eu/" + anchor_id.split(":")[1],
                     "anchor_operator_id": "org:trustline-demo"}]}
        self.anchors.append(block)
        return block

def base_env(kind, sec, phase, span, parent=None, part=None):
    e = OrderedDict()
    e["se_version"], e["implementation_profile_ref"] = SE_VERSION, PROFILE_ID
    e["event_kind"] = kind
    e["occurred_at"], e["emitted_at"], e["recorded_at"] = ts(sec), ts(sec + 0.4), ts(sec + 0.9)
    e["timestamp_source"] = "ntp:cluster-sync"; e["clock_sync_confidence_level"] = "high"
    e["trace_id"], e["span_id"] = TRACE_ID, span
    if parent: e["parent_span_id"] = parent
    e["organization_id"], e["tenant_id"] = ORG, TENANT
    e["environment_id"], e["environment_type"] = ENV_ID, ENV_TYPE
    e["execution_phase"] = phase
    e["execution_mode"] = "autonomous"
    e["actor"] = dict(ACTOR)
    e["authority"] = {k: AUTHORITY[k] for k in
                      ("authority_context_ref", "delegation_receipt_ref", "delegator_id",
                       "policy_ref", "policy_version", "capability_id", "engineering_release_ref")}
    e["emission"] = {"capture_layer": "runtime_sdk", "capture_status": "captured",
                     "emission_fail_posture": "fail_closed",
                     "declared_heartbeat_interval": HEARTBEAT_INTERVAL}
    e["evidence_quality"] = {"evidence_origin": "runtime", "assertion_basis": "observed",
                             "corroboration_state": "internally_corroborated"}
    e["privacy"] = {"personal_data_indicator": False, "redaction_applied_indicator": False}
    if part is not None: e["part_index"] = part
    return e

def subject(serial):
    return {"part_number": "IMP-4471", "drawing_version": "D", "serial_number": serial}

# ----------------------------------------------------------------------------
# 3. Manufacturing artifact stand-ins (synthetic, minimal)
# ----------------------------------------------------------------------------
def qif_xml(i, serial, measured):
    sn = f"SN{i:04d}"
    meas_s = decimal_str(measured, 4)
    return f"""<QIFDocument xmlns="http://qifstandards.org/xsd/qif3">
  <Product><PartNumber>IMP-4471</PartNumber><SerialNumber>{serial}</SerialNumber></Product>
  <ResultsSummary>
    <Characteristic name="{CHARACTERISTIC}" nominal="25.000" upper="{TOL_UPPER}" lower="{TOL_LOWER}">
      <MeasuredValue unit="mm">{meas_s}</MeasuredValue>
      <Disposition>CONFORMING</Disposition>
    </Characteristic>
    <InspectionRecord id="{sn}"/>
  </ResultsSummary>
</QIFDocument>"""

def mes_release_xml(i, serial):
    sn = f"SN{i:04d}"
    return f"""<MESRelease xmlns="urn:ironmark:mes:v3">
  <ReleaseOrder run="MRUN-2026-06-11-A" line="{i:02d}">
    <PartNumber>IMP-4471</PartNumber><Revision>D</Revision><Serial>{serial}</Serial>
    <ProductionOrder>PO-IRN-2026-4471-06</ProductionOrder>
    <Disposition>RELEASED</Disposition>
    <RecordId>{sn}</RecordId>
  </ReleaseOrder>
</MESRelease>"""

def b2mml_batchrecord_xml(rows):
    lines = "\n".join(
        f'    <MaterialProducedActual serial="{r["serial"]}" qty="1" disposition="conforming"/>'
        for r in rows)
    return f"""<B2MML xmlns="http://www.mesa.org/xml/B2MML-V0600">
  <ProductionPerformance id="MRUN-2026-06-11-A">
    <ProductionOrder>PO-IRN-2026-4471-06</ProductionOrder>
    <PartNumber>IMP-4471</PartNumber><Revision>D</Revision>
    <Quantity produced="{len(rows)}" scrap="0"/>
    <MaterialProducedActualList>
{lines}
    </MaterialProducedActualList>
  </ProductionPerformance>
</B2MML>"""

def mtconnect_xml():
    return f"""<MTConnectStreams xmlns="urn:mtconnect.org:MTConnectStreams:1.4">
  <DeviceStream name="cnc-cell-4" uuid="ironmark-cell-4">
    <ComponentStream component="Controller" name="controller">
      <Events><Availability dataItemId="avail" timestamp="{ts(0)}">AVAILABLE</Availability></Events>
    </ComponentStream>
    <ComponentStream component="Path" name="path">
      <Events><Execution dataItemId="exec" timestamp="{ts(652)}">ACTIVE</Execution></Events>
    </ComponentStream>
  </DeviceStream>
</MTConnectStreams>"""

def matcert_xml():
    return f"""<MaterialCertificate xmlns="urn:en10204:3.1">
  <Certificate type="3.1" heat="HT-88213">
    <MaterialGrade>15-5PH stainless</MaterialGrade>
    <Standard>EN 10204 3.1</Standard>
    <Supplier>Northforge Metals Ltd</Supplier>
    <PartApplication>IMP-4471 rev D</PartApplication>
  </Certificate>
</MaterialCertificate>"""

# ----------------------------------------------------------------------------
# 4. Build the trace
# ----------------------------------------------------------------------------
def build():
    os.makedirs(OUT, exist_ok=True)
    for d in ("samples", "artifacts", "reports"): os.makedirs(os.path.join(OUT, d), exist_ok=True)
    ch = Chain()
    artifacts, pending, part_rows = {}, [], []

    def save_artifact(name, content):
        p = os.path.join(OUT, "artifacts", name)
        write_text_utf8_lf(p, content)
        h = sha256_hex(content.encode("utf-8")); artifacts[name] = h; return h

    def later(sec, env): pending.append((sec, len(pending), env))

    # --- batch start / context / plan -------------------------------------
    e = base_env("execution_started", 0, "execution", "span-batch")
    e["operation"] = {"operation_type": "mfg_batch_release_run", "batch_id": "MRUN-2026-06-11-A",
                      "target_system_id": "mes:ironmark/prod", "target_resource_type": "production_order"}
    later(0, e)

    e = base_env("context_retrieved", 4, "advisory", "span-plan", "span-batch")
    e["operation"] = {"operation_type": "load_production_order", "target_system_id": "mes:ironmark/prod",
                      "target_resource_type": "production_order", "record_count": 14}
    e["context"] = {"context_artifact_refs": ["mes:ironmark/PO-IRN-2026-4471-06",
                    "drawing:IMP-4471/revD", "matcert:EN10204-3.1/HT-88213"],
                    "input_trust_class": "trusted_internal_system",
                    "untrusted_content_indicator": False}
    e["model"] = {"sampling_parameters": SAMPLING,
                  "reasoning_artifact_availability_status": "provider_withheld"}
    later(4, e)

    e = base_env("plan_created", 9, "advisory", "span-plan", "span-batch")
    e["plan"] = {"planned_part_count": 14,
                 "planned_order_ref": "PO-IRN-2026-4471-06",
                 "plan_ref": "artifact:plan/MRUN-2026-06-11-A"}
    later(9, e)

    # --- per-part lifecycle ------------------------------------------------
    for i, (serial, util, cpk) in enumerate(zip(SERIALS, UTILS, CPKS), start=1):
        p0 = 12 + (i - 1) * 45
        span = f"span-part-{i:02d}"
        idem = f"idem:MRUN-2026-06-11-A/{i:04d}"
        meas = measured_mm(util)
        qif_name = f"qif_SN{i:04d}.xml"
        mes_name = f"mes_release_SN{i:04d}.xml"

        meas_s = decimal_str(meas, 4)
        cpk_s = decimal_str(cpk, 2)
        e = base_env("policy_check_performed", p0, "approval", span, "span-batch", part=i)
        e["subject"] = subject(serial)
        e["controls"] = {"control_evaluation_phase": "pre_commit", "control_set_ref": "ctl:part-release/v5.1",
            "checks": [
                {"control_id": "CTL-DIM-01", "control_name": "critical dimension within released tolerance",
                 "control_result": "passed",
                 "observed": {"characteristic_name": CHARACTERISTIC, "nominal_value": "25.000",
                              "tolerance_upper_value": decimal_str(TOL_UPPER, 3),
                              "tolerance_lower_value": decimal_str(TOL_LOWER, 3),
                              "measured_value": meas_s, "measurement_unit": "mm",
                              "measurement_artifact_ref": f"artifacts/{qif_name}",
                              "measurement_scheme": "ISO23952-QIF-3.0"}},
                {"control_id": "CTL-SPC-02", "control_name": "process in statistical control",
                 "control_result": "passed",
                 "observed": {"cpk_value": cpk_s, "cpk_floor_value": CPK_FLOOR,
                              "subgroup_ref": "spc:IMP-4471/revD/2026-06-11"}},
                {"control_id": "CTL-MAT-03", "control_name": "material lot verified to certified heat",
                 "control_result": "passed", "evidence_ref": "matcert:EN10204-3.1/HT-88213",
                 "material_grade_name": "15-5PH stainless"}]}
        e["authority"]["approval_status"] = "not_required"
        e["authority"]["approval_basis"] = AUTHORITY["scope"]["approval_rule"]
        later(p0, e)

        qif_hash = save_artifact(qif_name, qif_xml(i, serial, meas))
        mes_hash = save_artifact(mes_name, mes_release_xml(i, serial))
        e = base_env("commit_attempted", p0 + 6, "commit", span, "span-batch", part=i)
        e["subject"] = subject(serial)
        e["operation"] = {"operation_type": "release_conforming_part",
            "target_system_id": "mes:ironmark/prod", "target_resource_type": "part_release",
            "commit_boundary_status": "commit_attempted",
            "commit_method": "quality_disposition", "commit_impact_class": "material_state_change",
            "transaction_ref": serial, "idempotency_key": idem, "idempotency_key_forwarded_indicator": True,
            "subject": {**subject(serial), "quantity_value": 1, "quantity_unit": "each"},
            "instruction_artifact": {"ref": f"artifacts/{mes_name}", "hash": mes_hash, "hash_algorithm": "SHA-256",
                                     "scheme": "mes:ironmark/release-v3"}}
        e["privacy"] = {"personal_data_indicator": True, "redaction_applied_indicator": True,
                        "redaction_profile_ref": "redact:operator-pii/v1",
                        "redaction_method": "hash_substitution",
                        "redacted_fields": ["operator_badge_id", "shift_supervisor_id"]}
        e["correlation_keys"] = [{"key_type": "serial", "key_scheme": "ironmark:serial",
                                  "key_value": serial}]
        later(p0 + 6, e)

        e = base_env("tool_invoked", p0 + 7, "commit", span, "span-batch", part=i)
        e["operation"] = {"operation_type": "OPC-UA Write ReleaseDisposition", "transaction_ref": serial,
                          "target_system_id": "cell:ironmark/cnc-cell-4"}
        e["tool"] = {"tool_manifest_ref": "manifest:opcua/part-release@1.8",
                     "tool_manifest_hash": sha256_hex(b"manifest:opcua/part-release@1.8")}
        later(p0 + 7, e)

        e = base_env("commit_succeeded", p0 + 9, "commit", span, "span-batch", part=i)
        e["operation"] = {"operation_type": "release_conforming_part", "transaction_ref": serial,
                          "commit_boundary_status": "committed",
                          "commit_method": "quality_disposition",
                          "commit_impact_class": "material_state_change",
                          "subject": {**subject(serial), "quantity_value": 1, "quantity_unit": "each"}}
        e["outcome"] = {"result_status": "success", "side_effect_confirmation_status": "confirmed"}
        e["acknowledgments"] = [
            {"acknowledgment_layer": "transport", "acknowledgment_scheme": "OPC-UA", "acknowledgment_code": "Good",
             "acknowledged_at": ts(p0 + 7.3), "acknowledgment_authenticity_basis": "channel_secured", "basis_status": "simulated"},
            {"acknowledgment_layer": "machine", "acknowledgment_scheme": "mes:ironmark/v3", "acknowledgment_code": "ACCEPTED",
             "acknowledgment_reason_code": f"release:{serial}", "acknowledged_at": ts(p0 + 7.6),
             "acknowledgment_authenticity_basis": "channel_secured", "basis_status": "simulated"},
            {"acknowledgment_layer": "quality", "acknowledgment_scheme": "ISO23952-QIF-3.0", "acknowledgment_code": "CONFORMING",
             "acknowledged_at": ts(p0 + 8.8), "acknowledgment_artifact_ref": f"artifacts/{qif_name}",
             "acknowledgment_artifact_hash": qif_hash, "acknowledgment_authenticity_basis": "qms_signed", "basis_status": "stubbed"}]
        e["evidence_quality"]["corroboration_state"] = "third_party_confirmed"
        later(p0 + 9, e)
        part_rows.append({"i": i, "serial": serial, "measured": meas_s, "util": util, "cpk": cpk_s,
                          "qif_hash": qif_hash, "mes_hash": mes_hash, "t_commit": ts(p0 + 9)})

    end_sec = 12 + 14 * 45 + 10

    # --- heartbeats --------------------------------------------------------
    for s in range(HEARTBEAT_INTERVAL_S, int(end_sec), HEARTBEAT_INTERVAL_S):
        e = base_env("heartbeat_event", s, "execution", "span-batch")
        e["liveness"] = {"liveness_status": "alive", "declared_heartbeat_interval": HEARTBEAT_INTERVAL}
        later(s, e)

    # --- anchors -----------------------------------------------------------
    # The anchor covers the chain head as it stood at the tick, so it sorts before any
    # other event in the same second. corroboration_state stays internally_corroborated:
    # a simulated anchor never earns externally_anchored (D-020).
    anchor_secs = list(range(ANCHOR_INTERVAL_S, int(end_sec) + ANCHOR_INTERVAL_S, ANCHOR_INTERVAL_S))
    for s in anchor_secs:
        tick = min(s, end_sec)
        e = base_env("attestation_recorded", tick, "execution", "span-anchor", "span-batch")
        e["anchoring"] = ("__FILL_AT_CHAIN_TIME__", tick)
        later(tick - 0.5, e)

    # --- batch-level artifacts + reconciliation ----------------------------
    save_artifact("matcert_HT-88213.xml", matcert_xml())
    b2mml_hash = save_artifact("b2mml_batchrecord_MRUN-2026-06-11-A.xml", b2mml_batchrecord_xml(part_rows))
    save_artifact("mtconnect_MRUN-2026-06-11-A.xml", mtconnect_xml())

    recon_sec = end_sec + 9 * 3600
    e = base_env("source_system_reconciliation", recon_sec, "execution", "span-recon", "span-batch")
    e["reconciliation"] = {
        "evidence_population_ref": "population:mes-production-order PO-IRN-2026-4471-06@2026-06-11T06:55Z "
                                   "(14 planned) + goods-receipt GRN-2026-06-11-IMP4471",
        "population_basis": "independently_reconciled",
        "mes_expected_count": 14, "goods_receipt_count": 14, "envelope_commit_count": 14,
        "scrap_count": 0,
        "batch_record_count": 14,
        "settlement_artifact": {"ref": "artifacts/b2mml_batchrecord_MRUN-2026-06-11-A.xml",
                                  "hash": b2mml_hash, "hash_algorithm": "SHA-256", "scheme": "ISA95-B2MML"},
        "acknowledgment_rung": {"acknowledgment_layer": "settlement", "acknowledgment_scheme": "ISA95-B2MML",
                                "acknowledgment_authenticity_basis": "source_system_signed", "basis_status": "stubbed"}}
    e["evidence_quality"]["corroboration_state"] = "source_system_corroborated"
    later(recon_sec, e)

    e = base_env("result_observed", recon_sec + 60, "execution", "span-close", "span-batch")
    e["boundary_assessment"] = {"cell_boundary_crossed_indicator": False, "cross_order_exposure_indicator": False,
                                "cross_program_exposure_indicator": False,
                                "boundary_assessment_basis": "single-cell runtime; MES order lock on PO-IRN-2026-4471-06; "
                                         "connector telemetry shows no other production orders touched"}
    later(recon_sec + 60, e)

    e = base_env("execution_completed", recon_sec + 90, "execution", "span-batch")
    min_cpk = min(r["cpk"] for r in part_rows)
    e["summary"] = {"released_count": 14, "exception_count": 0, "scrap_count": 0,
                    "human_intervention_count": 0,
                    "order_ref": "PO-IRN-2026-4471-06",
                    "observed_minimum_cpk_value": min_cpk}
    later(recon_sec + 90, e)

    e = base_env("evidence_exported", recon_sec + 120, "execution", "span-export", "span-batch")
    e["export"] = {"evidence_bundle_ref": "bundle:MRUN-2026-06-11-A",
                   "final_anchor": ("__FILL_AT_CHAIN_TIME__", recon_sec + 120)}
    later(recon_sec + 120, e)

    pending.sort(key=lambda t: (t[0], t[1]))
    for sec, _, env in pending:
        if isinstance(env.get("anchoring"), tuple):
            env["anchoring"] = ch.anchor(env["anchoring"][1])     # block over current chain head
        if isinstance(env.get("export"), dict) and isinstance(env["export"].get("final_anchor"), tuple):
            env["export"]["final_anchor"] = ch.anchor(env["export"]["final_anchor"][1])
        for blk in (env.get("anchoring"), (env.get("export") or {}).get("final_anchor")):
            if isinstance(blk, dict):   # anchored before the carrying record is emitted
                assert blk["anchors"][0]["anchored_at"] <= env["emitted_at"], env["event_kind"]
        ch.emit(env)

    return ch, part_rows, artifacts

# ----------------------------------------------------------------------------
# 5. Reports A-D
# ----------------------------------------------------------------------------
def cite(env, path): return f"[env:{env['sequence_number']:04d} | {path}]"

def write_reports(ch, rows, artifacts):
    by_kind = {}
    for e in ch.envelopes: by_kind.setdefault(e["event_kind"], []).append(e)
    commit_ok = by_kind["commit_succeeded"]
    policy = by_kind["policy_check_performed"]
    recon = by_kind["source_system_reconciliation"][0]
    bound = by_kind["result_observed"][0]
    done = by_kind["execution_completed"][0]
    exported = by_kind["evidence_exported"][0]
    anchors = by_kind["attestation_recorded"]
    hbs = by_kind["heartbeat_event"]
    peak = max(r["util"] for r in rows)
    min_cpk = done["summary"]["observed_minimum_cpk_value"]
    n_env = len(ch.envelopes)
    part3_policy = policy[2]

    A = f"""# Board Assurance Summary - Autonomous Production Batch Release MRUN-2026-06-11-A
**Organisation:** Ironmark Precision Ltd · **Period:** 2026-06-11 07:00–07:11 UTC (batch reconciled T+0 end of shift) · **Assurance basis:** SE v0.1-draft evidence, scoped - see Reliance Boundary.

## The assurance statement
> **An authorised autonomous process released 14 machined parts under delegated authority MD-5120.** {cite(commit_ok[0],'authority.authority_context_ref')} {cite(done,'summary.released_count')} - all 14 release events carry `authority_context_ref = MD-5120` with delegation receipt `delrec:MD-5120/2026-04-15` granted by the Quality Director {cite(commit_ok[0],'authority.delegation_receipt_ref')} {cite(commit_ok[0],'authority.delegator_id')} under part-release policy v5.1 in force throughout {cite(commit_ok[0],'authority.policy_version')}, against released engineering drawing IMP-4471 rev D and work instruction WI-4471 v5.1.
>
> **Every part remained within released engineering tolerance.** Each of the 14 units passed three pre-release quality gates - critical-dimension conformance, statistical process control, and material-lot verification - evaluated *before* the part was dispositioned conforming, 42 control evaluations in total, all passed {cite(policy[0],'controls.control_evaluation_phase')} {cite(policy[0],'controls.checks[*].control_result')}. The tightest characteristic ran at {peak:.1%} of the released tolerance band (part 3, SN IMP4471-0003, {CHARACTERISTIC}, report-layer derived from measured_mm vs tolerance band) {cite(part3_policy,'controls.checks[0].observed.measured_mm')}; the lowest process capability observed was Cpk {min_cpk} against a 1.33 floor (part 3) {cite(part3_policy,'controls.checks[1].observed.cpk')}.
>
> **No exceptions requiring human intervention occurred.** Exception count 0, scrap count 0, human-intervention count 0 {cite(done,'summary.exception_count')} {cite(done,'summary.scrap_count')} {cite(done,'summary.human_intervention_count')}; no quality-engineer disposition was required under the policy rule for parts inside tolerance on a released drawing {cite(policy[0],'authority.approval_status')} {cite(policy[0],'authority.approval_basis')}.
>
> **Evidence integrity validated.** All {n_env} envelopes form an unbroken SHA-256 hash chain (re-verified at report generation), with the chain head recorded every 5 minutes in {len(anchors)} in-trace anchors that are simulated and say so (`basis_status: simulated`, never `externally_anchored`) {cite(anchors[0],'anchoring.anchors[0].basis_status')}; emission ran fail-closed for release-boundary actions throughout {cite(commit_ok[0],'emission.emission_fail_posture')}; liveness heartbeats present for every 60-second interval of the run with zero silent windows {cite(hbs[0],'liveness.liveness_status')}.
>
> **No cross-programme contamination detected.** Cell-boundary and cross-order exposure indicators are false, on the stated basis that the cell processed only order PO-IRN-2026-4471-06 during the window {cite(bound,'boundary_assessment.cross_order_exposure_indicator')} {cite(bound,'boundary_assessment.boundary_assessment_basis')}.

## What the board should know
- **External confirmation, not self-assertion:** every release carries a three-rung acknowledgment ladder - transport (OPC-UA Good), machine (MES ACCEPTED), quality (QIF 3.0 / ISO 23952 inspection result **CONFORMING**) {cite(commit_ok[0],'acknowledgments[*]')} - and the end-of-shift ISA-95 batch record reconciles **14 of 14** units against the production order {cite(recon,'reconciliation.batch_record_count')}.
- **Completeness is measured, not asserted:** the in-scope population is independently defined (MES production order PO-IRN-2026-4471-06: 14 planned; finished-goods goods-receipt: 14 booked; scrap: 0) and evidence coverage is **14/14 = 100%**, tamper-evident coverage 100% (report-layer derived) {cite(recon,'reconciliation.evidence_population_ref')} {cite(recon,'reconciliation.envelope_commit_count')}.
- **Leading indicator:** one part ran at {peak:.1%} of its tolerance band; nothing out of tolerance, but characteristic headroom on the {CHARACTERISTIC} is worth a process-capability review before the next batch.
- **Recommended position:** continue autonomous release at current scope; no restriction indicated by this run's evidence.

## Reliance boundary
This report evidences this run only; it supports internal assurance, quality-management reliance, and customer source-surveillance for the stated period and population. It is **not** an airworthiness or conformity certification, and statements are bounded by the capture boundary declared in the Conformity Assessment Pack (§4). In this golden trace envelope signatures are stubs (`envelope_signature_basis_status: stubbed`) and in-trace anchors are simulated (`basis_status: simulated`); neither is an independently verifiable claim.
"""

    ctl_rows = "\n".join(
        f"| {r['i']:02d} | {r['serial']} | {CHARACTERISTIC} | passed ({r['util']:.1%}) | passed (Cpk {r['cpk']}) | passed (HT-88213) | not_required |"
        for r in rows)
    B = f"""# Quality and Control View - MRUN-2026-06-11-A

## 1. Controls relevant and evidenced
Three preventive quality gates (control set `ctl:part-release/v5.1`) were evaluated **pre-release** for each unit {cite(policy[0],'controls.control_evaluation_phase')}:

| # | Serial | Critical characteristic | CTL-DIM-01 dimension in tolerance | CTL-SPC-02 process capability (Cpk >= 1.33) | CTL-MAT-03 material lot verified | QE disposition |
|---|---|---|---|---|---|---|
{ctl_rows}

**Result: 42/42 control evaluations passed; 0 failed; 0 bypassed; 0 not_observed.** Quality-engineer disposition was `not_required` under policy v5.1's rule for characteristics inside tolerance on a released drawing revision {cite(policy[0],'authority.approval_basis')}; consequently no manual-disposition assertion is made or needed for this run - the control relied upon is the released-tolerance + verified-material-lot pair, both evidenced above.

## 2. Population and completeness (IPE basis)
- Population definition: MES production order PO-IRN-2026-4471-06 at 06:55Z (14 planned) reconciled against finished-goods goods-receipt GRN-2026-06-11-IMP4471 (14 booked, 0 scrap) - **independently reconciled**, not self-reported {cite(recon,'reconciliation.population_basis')}.
- Coverage: envelopes 14/14 (100%); tamper-evident 100% (report-layer derived from envelope_commit_count).
- Sequence continuity: envelope sequence numbers 0001-{n_env:04d} contiguous, no gaps (stream-internal proof); heartbeats at 60s intervals, zero silent windows (silence semantics) {cite(hbs[0],'liveness.declared_heartbeat_interval')}.

## 3. Evidence quality
- Origin/basis: runtime-observed on the shop-floor edge; release confirmations are **quality-system confirmed** (QIF 3.0 CONFORMING per unit) and **source-system corroborated** (ISA-95 batch record) {cite(commit_ok[0],'evidence_quality.corroboration_state')} {cite(recon,'evidence_quality.corroboration_state')}.
- Corroboration coverage decomposition: externally anchored 0 (in-trace anchors are `basis_status: simulated`) · quality-receipted 14/14 · provider-only 0.
- Point-in-time validity: policy v5.1 effective from 2026-05-01, in force at every event {cite(commit_ok[0],'authority.policy_version')}; drawing rev D released 2026-03-20; delegation valid 2026-04-15 to 2026-12-31.
- Model context: sampling parameters recorded (temperature 0.2, top_p 0.9 as exact decimal strings); replay claim scoped - *reproducible in distribution, not in instance* {cite(by_kind['context_retrieved'][0],'model.sampling_parameters')}; reasoning artifacts `provider_withheld` - disclosed, not silent {cite(by_kind['context_retrieved'][0],'model.reasoning_artifact_availability_status')}.

## 4. Findings register
No exceptions, deficiencies, or open actions arise from this run. One observation (OBS-001, advisory): peak characteristic utilisation {peak:.1%} with the lowest capability of the batch at Cpk {min_cpk} - recommend a process-capability review for the {CHARACTERISTIC} before the next batch. Owner: manufacturing process owner. Due: next production cycle.
"""

    art_rows = "\n".join(f"| {n} | `{h[:16]}…` |" for n, h in sorted(artifacts.items()))
    anch_rows = "\n".join(
        f"| {a['anchoring']['anchors'][0]['anchor_id']} | {a['anchoring']['anchors'][0]['anchor_requested_at']} | {a['anchoring']['anchors'][0]['anchored_at']} | `{a['anchoring']['anchored_subject_hash'][:16]}…` | {a['anchoring']['anchors'][0]['basis_status']} |"
        for a in anchors)
    C = f"""# Conformity Assessment / Notified-Body Evidence Pack - MRUN-2026-06-11-A

## 1. Scope of evidence
Autonomous production batch release by Ironmark Precision Ltd, run MRUN-2026-06-11-A, 2026-06-11 07:00–07:11 UTC, batch reconciliation T+0 end of shift. Part IMP-4471 hydraulic manifold, drawing rev D, 14 units. Evidence bundle `bundle:MRUN-2026-06-11-A` {cite(exported,'export.evidence_bundle_ref')} - {n_env} envelopes, {len(artifacts)} referenced artifacts.

## 2. Systems involved (execution topology)
agent:ironmark/mfg-pilot 3.1.0 -> orchestrator:ironmark/shopfloor-orch 2.2 -> model:anthropic/claude-sonnet-4-6 -> gateway:ironmark/toolproxy-2 -> connector:opcua-gw 1.8.0 -> cell:ironmark/cnc-cell-4 (machining + in-line CMM) · context source mes:ironmark/prod (ISA-95) · runtime edge:ironmark/edge-mes-01 (on-premise) {cite(commit_ok[0],'actor')}. One authority chain spans all nodes (MD-5120).

## 3. Authority model
Delegation MD-5120: Quality Director -> manufacturing agent; per-part release inside released drawing rev D tolerances for critical characteristics; batch release up to authorised order quantity (14); released-engineering constraint (drawing IMP-4471 rev D + work instruction WI-4471 v5.1 only); validity 2026-04-15 to 2026-12-31; policy `ironmark/part-release` v5.1 in force {cite(commit_ok[0],'authority.policy_ref')}. The granting principal (`delegator_id`) is recorded pseudonymously; resolution is available to authorised reviewers via the access model.

## 4. Evidence completeness and capture boundary
Coverage 14/14 against an independently reconciled population (MES production order + finished-goods goods-receipt) {cite(recon,'reconciliation.envelope_commit_count')}. **Declared capture boundary:** downstream heat-treatment and plating performed by an external subcontractor are *outside* the emitter's capture boundary and are evidenced indirectly via the incoming EN 10204 3.1 material certificate and the subcontractor's certificate of conformance; this is disclosed, not inferred. Emission posture fail-closed for release-boundary actions {cite(commit_ok[0],'emission.emission_fail_posture')}.

## 5. Exceptions and material events
None. 14/14 released conforming; 0 exceptions; 0 scrap; 0 human interventions; 0 control failures {cite(done,'summary')}.

## 6. Cryptographic sealing status
SHA-256 hash chain over RFC 8785 JCS canonical JSON (`canonicalization_version = {CANON}`), contiguous sequence 0001-{n_env:04d}; chain re-verified at generation. In-trace anchoring every 300s to `anchorstore:trustline-demo/eu` is **simulated** (`anchoring_method: write_once_store`, `basis_status: simulated`), and no envelope asserts `externally_anchored` (D-020). Envelope signatures are **stubs** (`envelope_signature_basis_status: stubbed`) pending the SE signing profile. Every stub and simulation is stated in a `basis_status` field a verifier reads, not only in this prose (catalogue 1.27). Operator identity and any personal data carried by reference with hash-substitution redaction (`redact:operator-pii/v1`); redacted fields enumerated per envelope {cite(by_kind['commit_attempted'][0],'privacy.redacted_fields')}.

## 7. Appendix A - artifact register (manufacturing interop standards)
| Artifact | SHA-256 |
|---|---|
{art_rows}

## 8. Appendix B - in-trace anchors (simulated)
| Anchor | Requested at | Anchored at | Chain head | basis_status |
|---|---|---|---|---|
{anch_rows}

## 9. Reliance boundary
Evidence supports: internal quality-management reliance; customer source-surveillance and incoming acceptance with re-verification; notified-body review. It does not constitute: an airworthiness or conformity certification; a fitness-for-purpose determination; coverage of processes outside §4's declared boundary.
"""

    seq_rows = "\n".join(
        f"| {e['sequence_number']:04d} | {e['event_kind']} | {e.get('part_index',' - ')} | {e['occurred_at']} | `{e['integrity']['envelope_hash'][:12]}…` |"
        for e in ch.envelopes[:24])
    part_link_rows = "\n".join(
        f"| {r['i']:02d} | {r['serial']} | {r['measured']} mm | HT-88213 | `{r['qif_hash'][:10]}…` | `{r['mes_hash'][:10]}…` | {r['t_commit']} |"
        for r in rows)
    D = f"""# Forensic Execution Pack - MRUN-2026-06-11-A

## 1. Verification procedure (vendor-neutral)
1. Read `envelopes.jsonl` in sequence order. 2. For each envelope, remove `integrity.envelope_hash` and `integrity.envelope_signature`; serialise with RFC 8785 JCS; SHA-256; compare to stored hash. 3. Confirm `previous_envelope_hash` equals the prior envelope's hash (genesis = 64x'0'). 4. Confirm sequence numbers are contiguous. 5. Confirm `anchoring.anchored_subject_hash` at each `attestation_recorded` event equals the chain head before it, and that `anchor_requested_at` is not before that record's `emitted_at`. 6. Re-hash each file in `artifacts/` and compare with `manifest.json`. Steps 1-6 are reproducible from the bundle alone. Step 5 shows internal consistency only: the in-trace anchors are `basis_status: simulated`. The external existence bound is on the release, not the trace: the release statement committing to this corpus is anchored with RFC 3161 and OpenTimestamps (repository `RELEASES.md`, `VERIFY.md`).

## 2. Envelope sequence (first 24 of {n_env}; full stream in envelopes.jsonl)
| Seq | event_kind | Part# | occurred_at | envelope_hash |
|---|---|---|---|---|
{seq_rows}

## 3. Part <-> artifact <-> confirmation linkage
| # | Serial | Critical char ({CHARACTERISTIC}) | Material lot | QIF result hash | MES release hash | Released at |
|---|---|---|---|---|---|---|
{part_link_rows}

Released tolerance for the critical characteristic: 25.000 +0.021 / 0 mm (H7). Part 3 at {rows[2]['measured']} mm sits at {rows[2]['util']:.1%} of the tolerance band - inside tolerance, and the tightest unit in the batch.

## 4. Topology graph (declared = observed for this run)
Nodes: agent mfg-pilot 3.1.0 · orchestrator shopfloor-orch 2.2 · model claude-sonnet-4-6 · gateway toolproxy-2 · connector opcua-gw 1.8.0 · cell cnc-cell-4 · mes ironmark/prod · runtime edge-mes-01.
Edges: agent->orchestrator->model (inference); agent->gateway->connector->cell (release path); agent->mes (context and batch record, read/write). No undeclared touchpoints observed (third-party touchpoint set exhaustive for this run; basis: connector egress telemetry) {cite(bound,'boundary_assessment.boundary_assessment_basis')}.

## 5. Chronology and silence semantics
Run window 07:00:00-07:10:52Z; heartbeats every 60s ({len(hbs)} beats, 0 silent windows); simulated in-trace anchors at 300s cadence ({len(anchors)}); end-of-shift reconciliation 16:10Z. Emission fail-closed => within the declared boundary, absence of an envelope implies absence of a release-boundary action.

## 6. Known stubs and limitations (golden trace gt-v2.1)
Signatures are placeholders (`envelope_signature_basis_status: stubbed`). In-trace anchors are simulated (`basis_status: simulated`). The QIF result (QMS mTLS) and MES batch-record authenticity rungs are stubs (`basis_status: stubbed`); the OPC-UA and MES-acceptance rungs are `simulated` because the trace is synthetic. Each status is in a field a verifier reads (catalogue 1.27). A real on-chain anchor lane (EB-004, axes#3) remains open; the subcontracted heat-treatment and plating legs are outside the capture boundary by design. Hashes, chain, ordering, coverage arithmetic, and part-to-artifact linkage are real and re-verifiable under RFC 8785 JCS with no JSON floats in hash scope.
"""
    for name, content in (("report_A_board.md", A), ("report_B_audit.md", B),
                          ("report_C_regulator.md", C), ("report_D_forensic.md", D)):
        write_text_utf8_lf(os.path.join(OUT, "reports", name), content)

# ----------------------------------------------------------------------------
# 6. Manifest, samples, verify, main
# ----------------------------------------------------------------------------
def verify(envs):
    prev = "0" * 64
    for n, e in enumerate(envs, 1):
        e2 = json.loads(json.dumps(e)); integ = e2["integrity"]
        stored = integ.pop("envelope_hash"); integ.pop("envelope_signature")
        if e["sequence_number"] != n: return False, f"sequence gap at {n}"
        if integ["previous_envelope_hash"] != prev: return False, f"chain break at {n}"
        if sha256_hex(canonical(e2)) != stored: return False, f"hash mismatch at {n}"
        prev = stored
    return True, f"chain verified: {len(envs)} envelopes, head {prev[:16]}…"

def main():
    ch, rows, artifacts = build()
    write_text_utf8_lf(
        os.path.join(OUT, "envelopes.jsonl"),
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in ch.envelopes),
    )
    ok, msg = verify(ch.envelopes); assert ok, msg
    write_reports(ch, rows, artifacts)
    picks = {"envelope_part03_quality_gate.json": lambda e: e["event_kind"]=="policy_check_performed" and e.get("part_index")==3,
             "envelope_part03_commit_succeeded.json": lambda e: e["event_kind"]=="commit_succeeded" and e.get("part_index")==3,
             "envelope_reconciliation.json": lambda e: e["event_kind"]=="source_system_reconciliation",
             "envelope_anchor.json": lambda e: e["event_kind"]=="attestation_recorded"}
    for name, pred in picks.items():
        env = next(e for e in ch.envelopes if pred(e))
        write_json_utf8_lf(os.path.join(OUT, "samples", name), env)
    files = {}
    rel_paths = []
    for root, _, fnames in os.walk(OUT):
        for fn in fnames:
            if fn == "manifest.json":
                continue
            rel_paths.append(os.path.relpath(os.path.join(root, fn), OUT).replace("\\", "/"))
    for rel in sorted(rel_paths):
        files[rel] = sha256_hex(open(os.path.join(OUT, *rel.split("/")), "rb").read())
    assert_manifest_matches_files(OUT, files)
    bundle_hash = sha256_hex(canonical(files))
    manifest = {"evidence_bundle_ref": "bundle:MRUN-2026-06-11-A",
                "bundle_manifest_hash": bundle_hash, "generated_at": ts(0),
                "envelope_count": len(ch.envelopes), "chain_head": ch.prev,
                "chain_verification": msg, "files": files,
                "note": "Golden Trace gt-v2.1 (industrial): hashes real (RFC 8785 JCS); signatures stubbed and in-trace anchors simulated, each stated in basis_status."}
    write_json_utf8_lf(os.path.join(OUT, "manifest.json"), manifest)
    assert_manifest_matches_files(OUT, files)
    print(msg)
    print(f"envelopes={len(ch.envelopes)} parts={len(rows)} artifacts={len(artifacts)} bundle={bundle_hash[:16]}…")

if __name__ == "__main__":
    main()
