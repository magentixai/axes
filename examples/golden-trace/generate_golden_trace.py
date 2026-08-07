#!/usr/bin/env python3
"""
SE v0.1 Golden Trace Generator - "Caldera Robotics / AD-7844" (Pristine variant)
=================================================================================
Generates a fully synthetic, deterministic, end-to-end Agentic Execution
Evidence trace for the canonical scenario:

  "An authorised autonomous process executed 14 payment instructions under
   delegated authority AD-7844. All payments remained within approved policy
   boundaries. No exceptions requiring human intervention occurred. Evidence
   integrity validated. No cross-tenant data exposure detected."

Outputs (under ./out):
  envelopes.jsonl                 - full SE envelope stream (hash-chained)
  samples/*.json                  - pretty-printed exemplar envelopes
  artifacts/*.xml                 - ISO 20022 artifact stand-ins (pain.001, pacs.002, camt.053)
  manifest.json                   - evidence bundle manifest (file hashes, bundle hash)
  reports/report_A_board.md       - Board assurance summary (claim-cited)
  reports/report_B_audit.md       - Audit & control view
  reports/report_C_regulator.md   - Regulator / external assurance pack
  reports/report_D_forensic.md    - Forensic execution pack

Design notes:
  * Field names follow the Cross-Wave Vocabulary Harmonisation sheet (draft canonical keys).
  * Hash chain: SHA-256 over RFC 8785 JCS canonical JSON,
    excluding `integrity.envelope_hash` and `integrity.signature` at hash time.
    `canonicalisation_version` = "RFC8785-JCS". Monetary fields use Amount (integer
    atomic EUR minor units); derived ratios render in the report layer only.
  * Signatures and external anchor receipts are STUBS (clearly marked). Hashes are real.
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
    amount_from_decimal,
    assert_manifest_matches_files,
    assert_no_floats_in_hash_scope,
    canonical_bytes,
    envelope_digest,
    ratio_display,
    sha256_hex,
    write_json_utf8_lf,
    write_text_utf8_lf,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

# ----------------------------------------------------------------------------
# 1. Scenario constants
# ----------------------------------------------------------------------------
SE_VERSION = "0.1-draft"
PROFILE_ID = "se-profile:payments-emitter/0.1-draft"
CONFORMANCE_LEVEL = "SE-C4-assurance-report-capable (claimed, golden-trace)"
CANON = CANONICALISATION_VERSION
CORPUS_ASSET_NOTE = (
    "Golden Trace v2: monetary fields use Amount with asset iso4217:EUR "
    "(decimals=2 minor units); canonical form is RFC 8785 JCS; digest is "
    "SHA-256 over canonical bytes (declared, agile). Crypto Amounts "
    "(e.g. caip19:… USDC decimals=6) are exercised in vectors/."
)

ORG = "org:caldera-robotics"
TENANT = "tenant:caldera-prod"
ENV_ID, ENV_TYPE = "env:prod-eu", "production"

ACTOR = {
    "agent_id": "agent:caldera/ap-pilot", "agent_version": "2.4.1",
    "orchestrator_id": "orchestrator:caldera/flowdeck", "orchestrator_version": "1.9.0",
    "model_id": "model:anthropic/claude-sonnet-4-6", "model_version": "2025-09-29",
    "runtime_id": "runtime:aws/eu-west-1/ecs-apx-11",
    "tool_id": "tool:bankapi/sepa-inst-submit",
    "tool_gateway_id": "gateway:caldera/toolproxy-3",
    "connector_id": "connector:openbank-gw/2.2.0",
    "provider_id": "provider:first-meridian-bank",
}
SAMPLING = {"temperature": "0.2", "top_p": "0.9", "max_tokens": 4096,
            "reproducibility_note": "non-zero temperature: reproducible in distribution, not in instance"}

AUTHORITY = {
    "authority_context_id": "AD-7844",
    "delegation_receipt_id": "delrec:AD-7844/2026-04-02",
    "delegator_id": "person:pseu/cfo-9f31",          # pseudonymous key, held separately
    "policy_ref": "policy:caldera/ap-payments", "policy_version": "3.2",
    "policy_effective_from": "2026-05-01T00:00:00Z",
    "capability_id": "cap:sepa-inst-credit-transfer",
    "scope": {"per_payment_limit": amount_from_decimal("25000.00"),
              "batch_aggregate_limit": amount_from_decimal("150000.00"),
              "beneficiary_constraint": "supplier-master:v2026-05 (approved list only)",
              "approval_rule": "no human approval required at/below per-payment limit to approved beneficiaries",
              "valid_from": "2026-04-02T00:00:00Z", "valid_until": "2026-12-31T23:59:59Z"},
}

T0 = datetime(2026, 6, 9, 9, 0, 0, tzinfo=timezone.utc)   # batch window start
def ts(sec): return (T0 + timedelta(seconds=sec)).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

SUPPLIERS = [
    ("SUP-001", "Bolt & Brass Supplies GmbH"),   ("SUP-002", "Helix Tooling BV"),
    ("SUP-003", "Vanta Servo Systems Ltd"),      ("SUP-004", "Crucible Alloys SARL"),
    ("SUP-005", "Northstar PCB Works OY"),       ("SUP-006", "Greywick Logistics BV"),
    ("SUP-007", "Ferrule & Pin Components AG"),  ("SUP-008", "Optikon Sensors GmbH"),
    ("SUP-009", "Tessera Plastics SP. Z O.O."),  ("SUP-010", "Aldermane Calibration Ltd"),
    ("SUP-011", "Quill Fasteners ApS"),          ("SUP-012", "Marrowgate Packaging BV"),
    ("SUP-013", "Ironreed Hydraulics GmbH"),     ("SUP-014", "Lanternworks Coatings SAS"),
]
AMOUNTS = [4475.00, 12880.50, 23900.00, 9240.10, 3318.75, 15602.00, 7777.77,
           1949.99, 11025.40, 6890.00, 2475.25, 8112.60, 5230.95, 4527.87]
INVOICES = [f"INV-2026-{n}" for n in (3318, 3325, 3327, 3340, 3341, 3355, 3360,
                                      3361, 3372, 3375, 3380, 3384, 3390, 3391)]
BATCH_LIMIT = AUTHORITY["scope"]["batch_aggregate_limit"]
PER_LIMIT = AUTHORITY["scope"]["per_payment_limit"]

TRACE_ID = "4bf92f3577b34da6a3ce929d0e0e4736"   # W3C Trace Context compatible
HEARTBEAT_INTERVAL_S = 60
ANCHOR_INTERVAL_S = 300

# ----------------------------------------------------------------------------
# 2. Hashing, chaining, stub signing
# ----------------------------------------------------------------------------
def canonical(obj) -> bytes:
    return canonical_bytes(obj)

class Chain:
    def __init__(self):
        self.prev = "0" * 64; self.seq = 0; self.envelopes = []; self.anchors = []
    def emit(self, env: dict) -> dict:
        self.seq += 1
        env["sequence_number"] = self.seq
        env["envelope_id"] = f"env:APRUN-2026-06-09-A/{self.seq:04d}"
        env.setdefault("integrity", {})
        env["integrity"].update({
            "hash_algorithm": "SHA-256", "canonicalisation_version": CANON,
            "previous_envelope_hash": self.prev,
            "signing_key_id": "key:caldera/se-emitter-2026q2",
            "signing_key_provenance_ref": "kms:caldera/provenance/se-emitter-2026q2",
        })
        assert_no_floats_in_hash_scope(env)
        h = envelope_digest(env)
        env["integrity"]["envelope_hash"] = h
        env["integrity"]["signature"] = "SIG-STUB(" + h[:16] + ")"     # stub, see README
        self.prev = h
        self.envelopes.append(env)
        return env
    def anchor(self, sec):
        rcpt = {"anchor_receipt_id": f"anch:{len(self.anchors)+1:03d}",
                "anchoring_method": "write_once_store (SIMULATED)",
                "anchored_at": ts(sec), "chain_head_hash": self.prev,
                "anchor_store_ref": "anchorstore:trustline-demo/eu",
                "anchoring_latency_ms": 740}
        self.anchors.append(rcpt)
        return rcpt

def base_env(kind, sec, phase, span, parent=None, payment=None):
    e = OrderedDict()
    e["se_version"], e["profile_id"] = SE_VERSION, PROFILE_ID
    # envelope_id assigned by Chain.emit (inside the hash)
    e["event_kind"] = kind
    e["occurred_at"], e["emitted_at"], e["recorded_at"] = ts(sec), ts(sec + 0.4), ts(sec + 0.9)
    e["timestamp_source"] = "ntp:cluster-sync"; e["clock_sync_confidence"] = "high"
    e["trace_id"], e["span_id"] = TRACE_ID, span
    if parent: e["parent_span_id"] = parent
    e["org_id"], e["tenant_id"] = ORG, TENANT
    e["environment_id"], e["environment_type"] = ENV_ID, ENV_TYPE
    e["execution_phase"] = phase                     # advisory|approval|execution|commit
    e["execution_mode"] = "autonomous"
    e["actor"] = dict(ACTOR)
    e["authority"] = {k: AUTHORITY[k] for k in
                      ("authority_context_id", "delegation_receipt_id", "delegator_id",
                       "policy_ref", "policy_version", "capability_id")}
    e["emission"] = {"capture_layer": "runtime_sdk", "capture_status": "captured",
                     "emission_fail_posture": "fail_closed",
                     "declared_heartbeat_interval_s": HEARTBEAT_INTERVAL_S}
    e["evidence_quality"] = {"evidence_origin": "runtime", "assertion_basis": "observed",
                             "corroboration_state": "internally_corroborated"}
    e["privacy"] = {"personal_data_flag": False, "redaction_applied": False}
    if payment is not None: e["payment_index"] = payment
    return e

# ----------------------------------------------------------------------------
# 3. ISO 20022 artifact stand-ins (synthetic, minimal, own values)
# ----------------------------------------------------------------------------
def pain001_xml(i, e2e, amount, supplier):
    sid, name = supplier
    return f"""<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.11">
  <CstmrCdtTrfInitn>
    <GrpHdr><MsgId>CALD-PAIN-{i:02d}</MsgId><CreDtTm>{ts(0)}</CreDtTm></GrpHdr>
    <PmtInf>
      <Dbtr><Nm>Caldera Robotics Ltd</Nm><Acct><Id>[REDACTED:iban-debtor]</Id></Acct></Dbtr>
      <CdtTrfTxInf>
        <PmtId><EndToEndId>{e2e}</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="EUR">{amount:.2f}</InstdAmt></Amt>
        <Cdtr><Nm>{name}</Nm><Acct><Id>[REDACTED:iban-{sid}]</Id></Acct></Cdtr>
        <RmtInf><Ustrd>{INVOICES[i-1]}</Ustrd></RmtInf>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>"""

def pacs002_xml(i, e2e):
    return f"""<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pacs.002.001.10">
  <FIToFIPmtStsRpt>
    <GrpHdr><MsgId>FMB-STS-{i:02d}</MsgId><CreDtTm>{ts(0)}</CreDtTm></GrpHdr>
    <TxInfAndSts><OrgnlEndToEndId>{e2e}</OrgnlEndToEndId><TxSts>ACSC</TxSts></TxInfAndSts>
  </FIToFIPmtStsRpt>
</Document>"""

def camt053_xml(e2es_amounts):
    lines = "\n".join(
        f"    <Ntry><Amt Ccy=\"EUR\">{a:.2f}</Amt><Sts>BOOK</Sts><NtryDtls><TxDtls>"
        f"<Refs><EndToEndId>{e}</EndToEndId></Refs></TxDtls></NtryDtls></Ntry>"
        for e, a in e2es_amounts)
    return (f"""<Document xmlns="urn:iso:std:iso:20022:tech:xsd:camt.053.001.08">
  <BkToCstmrStmt><Stmt><Id>FMB-STMT-2026-06-09</Id>
{lines}
  </Stmt></BkToCstmrStmt>
</Document>""")

# ----------------------------------------------------------------------------
# 4. Build the trace (two-phase: gather time-stamped events, then chain in time order)
# ----------------------------------------------------------------------------
def build():
    os.makedirs(OUT, exist_ok=True)
    for d in ("samples", "artifacts", "reports"): os.makedirs(os.path.join(OUT, d), exist_ok=True)
    ch = Chain()
    artifacts, pending, payment_rows = {}, [], []

    def save_artifact(name, content):
        p = os.path.join(OUT, "artifacts", name)
        write_text_utf8_lf(p, content)
        h = sha256_hex(content.encode("utf-8")); artifacts[name] = h; return h

    def later(sec, env): pending.append((sec, len(pending), env))

    # --- batch start / context / plan -------------------------------------
    e = base_env("execution_started", 0, "execution", "span-batch")
    e["operation"] = {"operation": "ap_payment_batch_run", "batch_id": "APRUN-2026-06-09-A",
                      "target_system_id": "erp:ledgerworks/prod", "target_resource_type": "approved_invoice_queue"}
    later(0, e)

    e = base_env("context_retrieved", 4, "advisory", "span-plan", "span-batch")
    e["operation"] = {"operation": "load_approved_invoices", "target_system_id": "erp:ledgerworks/prod",
                      "target_resource_type": "invoice", "record_count": 14}
    e["context"] = {"context_artifact_refs": [f"erp:ledgerworks/inv/{x}" for x in INVOICES],
                    "input_trust_classification": "trusted_internal_system",
                    "untrusted_content_indicator": False}
    e["model"] = {"sampling_parameters": SAMPLING,
                  "reasoning_artifact_availability": "provider_withheld"}
    later(4, e)

    e = base_env("plan_created", 9, "advisory", "span-plan", "span-batch")
    e["plan"] = {"planned_payment_count": 14,
                 "planned_aggregate": amount_from_decimal(str(round(sum(AMOUNTS), 2))),
                 "plan_ref": "artifact:plan/APRUN-2026-06-09-A"}
    later(9, e)

    # --- per-payment lifecycle ---------------------------------------------
    for i, ((sid, name), amount) in enumerate(zip(SUPPLIERS, AMOUNTS), start=1):
        p0 = 12 + (i - 1) * 45
        e2e = f"E2E-CALD-20260609-{i:04d}"
        span = f"span-pay-{i:02d}"
        idem = f"idem:APRUN-2026-06-09-A/{i:04d}"
        amt = amount_from_decimal(str(amount))
        util = ratio_display(int(amt["value"]), int(PER_LIMIT["value"]))

        e = base_env("policy_check_performed", p0, "approval", span, "span-batch", payment=i)
        e["controls"] = {"control_evaluation_phase": "pre_commit", "control_set_ref": "ctl:ap-pay/v3.2",
            "checks": [
                {"control_id": "CTL-BENEF-01", "name": "beneficiary on approved supplier master",
                 "control_result": "passed", "evidence_ref": f"suppliermaster:v2026-05/{sid}"},
                {"control_id": "CTL-LIMIT-02", "name": "per-payment limit",
                 "control_result": "passed",
                 "observed": {"amount": amt, "limit": PER_LIMIT}},
                {"control_id": "CTL-DUPL-03", "name": "duplicate instruction (idempotency key unseen)",
                 "control_result": "passed", "idempotency_key": idem}]}
        e["authority"]["approval_status"] = "not_required"
        e["authority"]["approval_basis"] = AUTHORITY["scope"]["approval_rule"]
        later(p0, e)

        pain_name = f"pain001_P{i:02d}.xml"
        pain_hash = save_artifact(pain_name, pain001_xml(i, e2e, amount, (sid, name)))
        e = base_env("commit_attempted", p0 + 6, "commit", span, "span-batch", payment=i)
        e["operation"] = {"operation": "submit_sepa_inst_credit_transfer",
            "target_system_id": "bankapi:first-meridian/sepa-inst", "target_resource_type": "payment_instruction",
            "commit_boundary_status": "commit_attempted",
            "commit_mechanism": "payment_initiation", "commit_impact_class": "money_movement",
            "transaction_ref": e2e, "idempotency_key": idem, "idempotency_key_forwarded": True,
            "monetary": {"amount": amt},
            "beneficiary_ref": f"suppliermaster:v2026-05/{sid}",
            "instruction_artifact": {"ref": f"artifacts/{pain_name}", "sha256": pain_hash,
                                     "scheme": "ISO20022-pain.001.001.11"}}
        e["privacy"] = {"personal_data_flag": True, "redaction_applied": True,
                        "redaction_profile_id": "redact:beneficiary-pii/v1",
                        "redaction_method": "hash_substitution",
                        "redacted_fields": ["beneficiary_iban", "debtor_iban"]}
        e["correlation_keys"] = [{"key_type": "counterparty", "key_scheme": "suppliermaster:v2026-05",
                                  "key_value": sid}]
        later(p0 + 6, e)

        e = base_env("tool_invoked", p0 + 7, "commit", span, "span-batch", payment=i)
        e["operation"] = {"operation": "POST /v2/payments", "transaction_ref": e2e,
                          "target_system_id": "bankapi:first-meridian/sepa-inst"}
        e["tool"] = {"tool_manifest_ref": "manifest:bankapi/sepa-inst-submit@2.2",
                     "tool_manifest_hash": sha256_hex(b"manifest:bankapi/sepa-inst-submit@2.2")}
        later(p0 + 7, e)

        pacs_name = f"pacs002_P{i:02d}.xml"
        pacs_hash = save_artifact(pacs_name, pacs002_xml(i, e2e))
        e = base_env("commit_succeeded", p0 + 9, "commit", span, "span-batch", payment=i)
        e["operation"] = {"operation": "submit_sepa_inst_credit_transfer", "transaction_ref": e2e,
                          "commit_boundary_status": "committed",
                          "commit_mechanism": "payment_initiation", "commit_impact_class": "money_movement",
                          "monetary": {"amount": amt}}
        e["result"] = {"result_status": "success", "side_effect_confirmation_status": "confirmed"}
        e["acknowledgments"] = [
            {"ack_layer": "transport", "ack_scheme": "HTTPS", "ack_code": "200",
             "ack_timestamp": ts(p0 + 7.3), "ack_authenticity_basis": "channel_secured"},
            {"ack_layer": "protocol", "ack_scheme": "bankapi:first-meridian/v2", "ack_code": "ACCEPTED",
             "ack_reason_code": f"instr:{e2e}", "ack_timestamp": ts(p0 + 7.6),
             "ack_authenticity_basis": "channel_secured"},
            {"ack_layer": "business", "ack_scheme": "ISO20022-pacs.002.001.10", "ack_code": "ACSC",
             "ack_timestamp": ts(p0 + 8.8), "ack_artifact_ref": f"artifacts/{pacs_name}",
             "ack_artifact_hash": pacs_hash, "ack_authenticity_basis": "counterparty_signed (webhook mTLS, STUB)"}]
        e["evidence_quality"]["corroboration_state"] = "third_party_confirmed"
        later(p0 + 9, e)
        payment_rows.append({"i": i, "supplier_id": sid, "supplier": name, "invoice": INVOICES[i-1],
                             "amount": amount, "e2e": e2e, "utilisation": util,
                             "pain_hash": pain_hash, "pacs_hash": pacs_hash, "t_commit": ts(p0 + 9)})

    end_sec = 12 + 14 * 45 + 10

    # --- heartbeats (liveness stream) --------------------------------------
    for s in range(HEARTBEAT_INTERVAL_S, int(end_sec), HEARTBEAT_INTERVAL_S):
        e = base_env("heartbeat_event", s, "execution", "span-batch")
        e["liveness"] = {"liveness_status": "alive", "declared_heartbeat_interval_s": HEARTBEAT_INTERVAL_S}
        later(s, e)

    # --- anchor placeholders (receipt filled at chain time) ----------------
    anchor_secs = list(range(ANCHOR_INTERVAL_S, int(end_sec) + ANCHOR_INTERVAL_S, ANCHOR_INTERVAL_S))
    for s in anchor_secs:
        e = base_env("attestation_recorded", min(s, end_sec), "execution", "span-anchor", "span-batch")
        e["anchoring"] = "__FILL_AT_CHAIN_TIME__"
        e["evidence_quality"]["corroboration_state"] = "externally_anchored"
        later(min(s, end_sec), e)

    # --- EOD reconciliation, boundary assessment, completion, export -------
    camt_hash = save_artifact("camt053_20260609.xml",
                              camt053_xml([(r["e2e"], r["amount"]) for r in payment_rows]))
    recon_sec = end_sec + 9 * 3600
    e = base_env("source_system_reconciliation", recon_sec, "execution", "span-recon", "span-batch")
    e["reconciliation"] = {
        "evidence_population_ref": "population:erp-approved-invoice-queue@2026-06-09T08:55Z (14 due) "
                                   "+ bank-statement FMB-STMT-2026-06-09",
        "population_basis": "independently_reconciled",
        "expected_count_erp": 14, "statement_count_bank": 14, "envelope_commit_count": 14,
        "settlement_artifact": {"ref": "artifacts/camt053_20260609.xml", "sha256": camt_hash,
                                "scheme": "ISO20022-camt.053.001.08"},
        "acknowledgment_rung": {"ack_layer": "settlement", "ack_scheme": "ISO20022-camt.053.001.08",
                                "ack_authenticity_basis": "counterparty_signed (statement channel, STUB)"}}
    e["evidence_quality"]["corroboration_state"] = "source_system_corroborated"
    later(recon_sec, e)

    e = base_env("result_observed", recon_sec + 60, "execution", "span-close", "span-batch")
    e["boundary_assessment"] = {"tenant_boundary_crossed": False, "cross_tenant_exposure_indicator": False,
                                "cross_customer_exposure_indicator": False,
                                "basis": "single-tenant runtime; egress limited to bank API and ERP; "
                                         "connector telemetry shows no other destinations"}
    later(recon_sec + 60, e)

    batch_total = amount_from_decimal(str(round(sum(AMOUNTS), 2)))
    e = base_env("execution_completed", recon_sec + 90, "execution", "span-batch")
    e["summary"] = {"committed_count": 14, "exception_count": 0, "human_intervention_count": 0,
                    "aggregate": batch_total}
    later(recon_sec + 90, e)

    e = base_env("evidence_exported", recon_sec + 120, "execution", "span-export", "span-batch")
    e["export"] = {"evidence_bundle_id": "bundle:APRUN-2026-06-09-A",
                   "final_anchor": "__FILL_AT_CHAIN_TIME__"}
    later(recon_sec + 120, e)

    # --- phase 2: chain in time order --------------------------------------
    pending.sort(key=lambda t: (t[0], t[1]))
    for sec, _, env in pending:
        if env.get("anchoring") == "__FILL_AT_CHAIN_TIME__":
            env["anchoring"] = ch.anchor(sec)            # receipt over current chain head
        if isinstance(env.get("export"), dict) and env["export"].get("final_anchor") == "__FILL_AT_CHAIN_TIME__":
            env["export"]["final_anchor"] = ch.anchor(sec)
        ch.emit(env)

    return ch, payment_rows, artifacts

# ----------------------------------------------------------------------------
# 5. Reports A-D (every material sentence carries [env:NNNN | field.path] citations)
# ----------------------------------------------------------------------------
def cite(env, path): return f"[env:{env['sequence_number']:04d} | {path}]"

def fmt_eur(amt: dict) -> float:
    return int(amt["value"]) / (10 ** amt["decimals"])

def write_reports(ch, rows, artifacts):
    by_kind = {}
    for e in ch.envelopes: by_kind.setdefault(e["event_kind"], []).append(e)
    commit_ok = [e for e in by_kind["commit_succeeded"]]
    policy = by_kind["policy_check_performed"]
    recon = by_kind["source_system_reconciliation"][0]
    bound = by_kind["result_observed"][0]
    done = by_kind["execution_completed"][0]
    exported = by_kind["evidence_exported"][0]
    anchors = by_kind["attestation_recorded"]
    hbs = by_kind["heartbeat_event"]
    total_amt = done["summary"]["aggregate"]
    total = fmt_eur(total_amt)
    peak = max(r["utilisation"] for r in rows)
    batch_util = ratio_display(int(total_amt["value"]), int(BATCH_LIMIT["value"]))
    n_env = len(ch.envelopes)

    # ---------------- Report A: Board assurance summary --------------------
    A = f"""# Board Assurance Summary - Autonomous AP Payment Run APRUN-2026-06-09-A
**Organisation:** Caldera Robotics Ltd · **Period:** 2026-06-09 09:00–09:11 UTC (settlement reconciled T+0 EOD) · **Assurance basis:** SE v0.1-draft evidence, scoped - see Reliance Boundary.

## The assurance statement
> **An authorised autonomous process executed 14 payment instructions under delegated authority AD-7844.** {cite(commit_ok[0],'authority.authority_context_id')} {cite(done,'summary.committed_count')} - all 14 commit events carry `authority_context_id = AD-7844` with delegation receipt `delrec:AD-7844/2026-04-02` granted by the CFO {cite(commit_ok[0],'authority.delegation_receipt_id')} {cite(commit_ok[0],'authority.delegator_id')} under payment policy v3.2 in force throughout {cite(commit_ok[0],'authority.policy_version')}.
>
> **All payments remained within approved policy boundaries.** Each of the 14 instructions passed three pre-commit policy checks - approved-beneficiary, per-payment limit, and duplicate-key - evaluated *before* execution, 42 control evaluations in total, all passed {cite(policy[0],'controls.control_evaluation_phase')} {cite(policy[0],'controls.checks[*].control_result')}. Peak single-payment authority utilisation was {peak:.1%} of the EUR 25,000 limit (payment 3, derived from Amount operands) {cite(policy[2],'controls.checks[1].observed.amount')} {cite(policy[2],'controls.checks[1].observed.limit')}; batch aggregate EUR {total:,.2f} used {batch_util:.1%} of the EUR 150,000 batch limit (report-layer derived).
>
> **No exceptions requiring human intervention occurred.** Exception count 0, human-intervention count 0 {cite(done,'summary.exception_count')} {cite(done,'summary.human_intervention_count')}; no approval was required under the policy rule for at-limit payments to approved beneficiaries {cite(policy[0],'authority.approval_status')} {cite(policy[0],'authority.approval_basis')}.
>
> **Evidence integrity validated.** All {n_env} envelopes form an unbroken SHA-256 hash chain (re-verified at report generation), externally anchored at 5-minute intervals - {len(anchors)} anchor receipts {cite(anchors[0],'anchoring.anchor_receipt_id')}; emission ran fail-closed for commit-boundary actions throughout {cite(commit_ok[0],'emission.emission_fail_posture')}; liveness heartbeats present for every 60-second interval of the run with zero silent windows {cite(hbs[0],'liveness.liveness_status')}.
>
> **No cross-tenant data exposure detected.** Tenant-boundary and cross-customer exposure indicators are false, on the stated basis that runtime egress was limited to the bank API and ERP {cite(bound,'boundary_assessment.cross_tenant_exposure_indicator')} {cite(bound,'boundary_assessment.basis')}.

## What the board should know
- **External confirmation, not self-assertion:** every payment carries a three-rung acknowledgment ladder - transport (HTTPS 200), protocol (bank API ACCEPTED), business (ISO 20022 pacs.002 status **ACSC** = settlement completed) {cite(commit_ok[0],'acknowledgments[*]')} - and the bank's end-of-day camt.053 statement reconciles **14 of 14** instructions {cite(recon,'reconciliation.statement_count_bank')}.
- **Completeness is measured, not asserted:** the in-scope population is independently defined (ERP approved-invoice queue: 14 due; bank statement: 14 booked) and evidence coverage is **14/14 = 100%**, tamper-evident coverage 100% (report-layer derived) {cite(recon,'reconciliation.evidence_population_ref')} {cite(recon,'reconciliation.envelope_commit_count')}.
- **Leading indicator:** one payment ran at {peak:.1%} of its limit; nothing breached, but limit headroom on supplier SUP-003 invoices is worth a policy review.
- **Recommended position:** continue autonomous operation at current scope; no restriction indicated by this run's evidence.

## Reliance boundary
This report evidences this run only; it supports internal assurance and audit reliance for the stated period and population. It is **not** a compliance certification, and statements are bounded by the capture boundary declared in the Regulator Pack (§4). Signatures and anchor receipts in this golden trace are stubs pending the SE v0.1 signing profile.
"""

    # ---------------- Report B: Audit & control view -----------------------
    ctl_rows = "\n".join(
        f"| {r['i']:02d} | {r['supplier_id']} | €{r['amount']:,.2f} | passed | passed ({r['utilisation']:.1%}) | passed | not_required |"
        for r in rows)
    B = f"""# Audit & Control View - APRUN-2026-06-09-A

## 1. Controls relevant and evidenced
Three preventive controls (control set `ctl:ap-pay/v3.2`) were evaluated **pre-commit** for each instruction {cite(policy[0],'controls.control_evaluation_phase')}:

| # | Beneficiary | Amount | CTL-BENEF-01 approved-list | CTL-LIMIT-02 per-payment limit | CTL-DUPL-03 duplicate key | Human approval |
|---|---|---|---|---|---|---|
{ctl_rows}

**Result: 42/42 control evaluations passed; 0 failed; 0 bypassed; 0 not_observed.** Approval was `not_required` under policy v3.2's rule for at-or-below-limit payments to approved beneficiaries {cite(policy[0],'authority.approval_basis')}; consequently no SoD/dual-control assertion is made or needed for this run - the control relied upon is the delegated-limit + approved-list pair, both evidenced above.

## 2. Population and completeness (IPE basis)
- Population definition: ERP approved-invoice queue at 08:55Z (14 due) reconciled against bank statement FMB-STMT-2026-06-09 (14 booked) - **independently reconciled**, not self-reported {cite(recon,'reconciliation.population_basis')}.
- Coverage: envelopes 14/14 (100%); tamper-evident 100% (report-layer derived from envelope_commit_count).
- Sequence continuity: envelope sequence numbers 0001–{n_env:04d} contiguous, no gaps (stream-internal proof); heartbeats at 60s intervals, zero silent windows (silence semantics) {cite(hbs[0],'liveness.declared_heartbeat_interval_s')}.

## 3. Evidence quality
- Origin/basis: runtime-observed; commit confirmations are **third-party confirmed** (pacs.002 ACSC per payment) and **source-system corroborated** (camt.053) {cite(commit_ok[0],'evidence_quality.corroboration_state')} {cite(recon,'evidence_quality.corroboration_state')}.
- Corroboration coverage decomposition: anchored 100% · receipted 14/14 · provider-only 0.
- Point-in-time validity: policy v3.2 effective from 2026-05-01, in force at every event {cite(commit_ok[0],'authority.policy_version')}; delegation valid 2026-04-02 → 2026-12-31.
- Model context: sampling parameters recorded (temperature 0.2, top_p 0.9); replay claim scoped - *reproducible in distribution, not in instance* {cite(by_kind['context_retrieved'][0],'model.sampling_parameters')}; reasoning artifacts `provider_withheld` - disclosed, not silent {cite(by_kind['context_retrieved'][0],'model.reasoning_artifact_availability')}.

## 4. Findings register
No exceptions, deficiencies, or open actions arise from this run. One observation (OBS-001, advisory): peak per-payment utilisation {peak:.1%} - recommend limit-headroom review for SUP-003. Owner: AP process owner. Due: next policy cycle.
"""

    # ---------------- Report C: Regulator / external pack -------------------
    art_rows = "\n".join(f"| {n} | `{h[:16]}…` |" for n, h in sorted(artifacts.items()))
    anch_rows = "\n".join(f"| {a['anchoring']['anchor_receipt_id']} | {a['anchoring']['anchored_at']} | `{a['anchoring']['chain_head_hash'][:16]}…` |"
                          for a in anchors)
    C = f"""# External Assurance / Regulator Evidence Pack - APRUN-2026-06-09-A

## 1. Scope of evidence
Autonomous accounts-payable payment execution by Caldera Robotics Ltd, run APRUN-2026-06-09-A, 2026-06-09 09:00–09:11 UTC, settlement reconciliation T+0 EOD. Evidence bundle `bundle:APRUN-2026-06-09-A` {cite(exported,'export.evidence_bundle_id')} - {n_env} envelopes, {len(artifacts)} referenced artifacts.

## 2. Systems involved (execution topology)
agent:caldera/ap-pilot 2.4.1 → orchestrator:caldera/flowdeck 1.9 → model:anthropic/claude-sonnet-4-6 → gateway:caldera/toolproxy-3 → connector:openbank-gw 2.2.0 → provider:first-meridian-bank (SEPA Inst) · context source erp:ledgerworks/prod · runtime aws/eu-west-1 {cite(commit_ok[0],'actor')}. One authority chain spans all nodes (AD-7844).

## 3. Authority model
Delegation AD-7844: CFO → AP agent; per-payment €25,000; batch €150,000; approved-beneficiary constraint (supplier-master v2026-05); validity 2026-04-02→2026-12-31; policy `caldera/ap-payments` v3.2 in force {cite(commit_ok[0],'authority.policy_ref')}. The granting principal (`delegator_id`) is recorded pseudonymously; resolution is available to authorised reviewers via the access model.

## 4. Evidence completeness and capture boundary
Coverage 14/14 against an independently reconciled population (ERP queue + bank statement) {cite(recon,'reconciliation.envelope_commit_count')}. **Declared capture boundary:** the interbank leg (pacs.008 between First Meridian and beneficiary banks) is *outside* the emitter's capture boundary and is evidenced indirectly via pacs.002 ACSC and camt.053; this is disclosed, not inferred. Emission posture fail-closed for commit-boundary actions {cite(commit_ok[0],'emission.emission_fail_posture')}.

## 5. Exceptions and material events
None. 14/14 committed; 0 exceptions; 0 human interventions; 0 control failures {cite(done,'summary')}.

## 6. Cryptographic sealing status
SHA-256 hash chain over RFC 8785 JCS canonical JSON (`canonicalisation_version = {CANON}`), contiguous sequence 0001-{n_env:04d}; chain re-verified at generation. External anchoring every 300s to `anchorstore:trustline-demo/eu` (**simulated for golden trace**). Envelope signatures are **stubs** pending the SE signing profile - disclosed per scoped-assurance rules. Personal data carried by reference with hash-substitution redaction (`redact:beneficiary-pii/v1`); redacted fields enumerated per envelope {cite(commit_ok[0] if False else by_kind['commit_attempted'][0],'privacy.redacted_fields')}.

## 7. Appendix A - artifact register (ISO 20022)
| Artifact | SHA-256 |
|---|---|
{art_rows}

## 8. Appendix B - anchor receipts
| Receipt | Anchored at | Chain head |
|---|---|---|
{anch_rows}

## 9. Reliance boundary
Evidence supports: internal audit reliance; external review with re-verification; insurer notification support. It does not constitute: a compliance certification; a fairness or legality determination; coverage of systems outside §4's declared boundary.
"""

    # ---------------- Report D: Forensic execution pack ---------------------
    seq_rows = "\n".join(
        f"| {e['sequence_number']:04d} | {e['event_kind']} | {e.get('payment_index',' - ')} | {e['occurred_at']} | `{e['integrity']['envelope_hash'][:12]}…` |"
        for e in ch.envelopes[:24])
    pay_rows = "\n".join(
        f"| {r['i']:02d} | {r['e2e']} | €{r['amount']:,.2f} | {r['supplier_id']} | {r['invoice']} | `{r['pain_hash'][:10]}…` | `{r['pacs_hash'][:10]}…` | {r['t_commit']} |"
        for r in rows)
    D = f"""# Forensic Execution Pack - APRUN-2026-06-09-A

## 1. Verification procedure (vendor-neutral)
1. Read `envelopes.jsonl` in sequence order. 2. For each envelope, remove `integrity.envelope_hash` and `integrity.signature`; serialise with RFC 8785 JCS; SHA-256; compare to stored hash. 3. Confirm `previous_envelope_hash` equals the prior envelope's hash (genesis = 64×'0'). 4. Confirm sequence numbers are contiguous. 5. Compare chain heads at each `attestation_recorded` event with the anchor receipts in Appendix B of the Regulator Pack. 6. Re-hash each file in `artifacts/` and compare with `manifest.json`. Steps 1-4 and 6 are fully reproducible from the bundle alone; step 5 is simulated in this golden trace.

## 2. Envelope sequence (first 24 of {n_env}; full stream in envelopes.jsonl)
| Seq | event_kind | Pay# | occurred_at | envelope_hash |
|---|---|---|---|---|
{seq_rows}

## 3. Payment ↔ artifact ↔ confirmation linkage
| # | EndToEndId | Amount | Beneficiary | Invoice | pain.001 hash | pacs.002 hash | Committed at |
|---|---|---|---|---|---|---|---|
{pay_rows}

## 4. Topology graph (declared = observed for this run)
Nodes: agent ap-pilot 2.4.1 · orchestrator flowdeck 1.9 · model claude-sonnet-4-6 · gateway toolproxy-3 · connector openbank-gw 2.2.0 · provider first-meridian-bank · erp ledgerworks · runtime aws/eu-west-1.
Edges: agent→orchestrator→model (inference); agent→gateway→connector→provider (commit path); agent→erp (context, read-only). No undeclared touchpoints observed (third-party touchpoint set exhaustive for this run; basis: connector egress telemetry) {cite(bound,'boundary_assessment.basis')}.

## 5. Chronology and silence semantics
Run window 09:00:00–09:10:52Z; heartbeats every 60s ({len(hbs)} beats, 0 silent windows); anchors at 300s cadence ({len(anchors)} receipts); EOD reconciliation 18:10Z. Emission fail-closed ⇒ within the declared boundary, absence of an envelope implies absence of a commit-boundary action.

## 6. Known stubs and limitations (golden trace v2)
Signatures are placeholders; anchor store is simulated (EB-004 real `distributed_ledger` anchor pending giskard09 confirmation on #3); pacs.002 webhook authenticity (mTLS) is asserted not demonstrated; the interbank pacs.008 leg is outside the capture boundary by design. Hashes, chain, ordering, coverage arithmetic, and artifact linkage are real and re-verifiable under RFC 8785 JCS with integer Amount fields (no JSON floats in hash scope).
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
        stored = integ.pop("envelope_hash"); integ.pop("signature")
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
    # samples
    picks = {"envelope_payment03_policy_check.json": lambda e: e["event_kind"]=="policy_check_performed" and e.get("payment_index")==3,
             "envelope_payment03_commit_succeeded.json": lambda e: e["event_kind"]=="commit_succeeded" and e.get("payment_index")==3,
             "envelope_reconciliation.json": lambda e: e["event_kind"]=="source_system_reconciliation",
             "envelope_anchor.json": lambda e: e["event_kind"]=="attestation_recorded"}
    for name, pred in picks.items():
        env = next(e for e in ch.envelopes if pred(e))
        write_json_utf8_lf(os.path.join(OUT, "samples", name), env)
    # manifest (sorted file list, forward-slash keys, for cross-platform byte stability)
    files = {}
    rel_paths = []
    for root, _, fnames in os.walk(OUT):
        for fn in fnames:
            if fn == "manifest.json":
                continue
            rel_paths.append(os.path.relpath(os.path.join(root, fn), OUT).replace("\\", "/"))
    for rel in sorted(rel_paths):
        p = os.path.join(OUT, *rel.split("/"))
        files[rel] = sha256_hex(open(p, "rb").read())
    assert_manifest_matches_files(OUT, files)
    bundle_hash = sha256_hex(canonical(files))
    manifest = {"evidence_bundle_id": "bundle:APRUN-2026-06-09-A",
                "bundle_manifest_hash": bundle_hash, "generated_at": ts(0),
                "envelope_count": len(ch.envelopes), "chain_head": ch.prev,
                "chain_verification": msg, "files": files,
                "corpus_asset_note": CORPUS_ASSET_NOTE,
                "note": "Golden trace v2: hashes real (RFC 8785 JCS); signatures and anchor store simulated."}
    write_json_utf8_lf(os.path.join(OUT, "manifest.json"), manifest)
    assert_manifest_matches_files(OUT, files)
    print(msg); print(f"envelopes={len(ch.envelopes)} payments={len(rows)} artifacts={len(artifacts)} bundle={bundle_hash[:16]}…")

if __name__ == "__main__":
    main()
