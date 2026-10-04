#!/usr/bin/env python3
"""Generate the WO19 evaluation vectors (vectors/profiles/). Deterministic; rerun after any change.

Each case is a small synthetic subject (gt-v2.1 key names), a test profile, and the expected result
of one requirement. Two-sided per check kind: every condition the evaluator can return has a case
that returns it and a case that does not.
"""
from __future__ import annotations

import copy
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from tools.axes_canonical import envelope_digest  # noqa: E402

OUT = os.path.join(ROOT, "vectors", "profiles")
PROV = {"author_name": "AXES maintainers (Magentix AI)", "authored_on": "2026-10-04"}

BASE = {
    "se_version": "0.1-draft", "implementation_profile_ref": "example:test_emitter@1",
    "event_kind": "commit_succeeded", "occurred_at": "2026-10-04T10:00:00.000Z",
    "emitted_at": "2026-10-04T10:00:00.100Z", "recorded_at": "2026-10-04T10:00:00.200Z",
    "organization_id": "org:example", "tenant_id": "tenant:example",
    "authority": {"delegator_id": "person:example/cfo", "policy_ref": "policy:example/payments"},
    "evidence_quality": {"evidence_origin": "runtime", "assertion_basis": "observed",
                         "corroboration_state": "third_party_confirmed"},
    "sequence_number": 1, "envelope_id": "env:test/0001",
    "integrity": {"hash_algorithm": "SHA-256", "canonicalization_version": "RFC8785-JCS",
                  "previous_envelope_hash": "0" * 64, "signing_key_id": "key:example/emitter"},
}


def chain(envs):
    prev = "0" * 64
    for i, e in enumerate(envs, 1):
        e["sequence_number"] = i
        e["envelope_id"] = "env:test/%04d" % i
        e["integrity"]["previous_envelope_hash"] = prev
        e["integrity"].pop("envelope_hash", None)
        e["integrity"]["envelope_hash"] = envelope_digest(e)
        prev = e["integrity"]["envelope_hash"]
    return envs


def env(**changes):
    e = copy.deepcopy(BASE)
    for path, value in changes.items():
        cur = e
        parts = path.split("__")
        for p in parts[:-1]:
            cur = cur.setdefault(p, {})
        if value is None:
            cur.pop(parts[-1], None)
        else:
            cur[parts[-1]] = value
    return e


def profile(pid, reqs, extends=None):
    p = {"requirement_profile_id": "example:%s@1" % pid, "requirement_profile_version": "1",
         "profile_purpose_type": "sufficiency", "publisher_id": "https://github.com/magentixai/axes",
         "relying_party_roles": ["auditor"], "subject_types": ["bundle"],
         "effective_from": "2026-10-04T00:00:00.000Z", "unsettled_question_notes": [], "requirements": reqs}
    if extends:
        p["extended_profile_refs"] = extends
    return p


def req(rid, **kw):
    r = {"requirement_id": rid, "check_type": "field_presence", "subject_type": "bundle", "obligation_type": "required",
         "floor_indicator": False, "rationale_note": "test", "source_refs": ["WO19"]}
    r.update(kw)
    return r


ANCHOR_OK = {"anchored_subject_type": "envelope", "anchored_subject_hash": "a" * 64, "anchored_subject_hash_algorithm": "SHA-256",
             "anchors": [{"anchor_id": "anch:1", "anchoring_method": "timestamp_authority", "basis_status": "demonstrated",
                          "anchor_commitment_hash": "a" * 64, "anchor_commitment_hash_algorithm": "SHA-256",
                          "anchor_requested_at": "2026-10-04T10:00:00.000Z", "anchored_at": "2026-10-04T10:00:01.000Z",
                          "anchor_service_id": "https://tsa.example/tsr", "anchor_record_ref": "serial:0x01",
                          "anchor_proof_ref": "proofs/x/proof_manifest.json", "anchor_proof_hash": "b" * 64}]}
SETTLE = {"settlement_transaction_ref": "tx:0x" + "c" * 64, "settlement_submitter_id": "eip155:84532:0x" + "1" * 40,
          "committed_terms": {"asset_id": "0x" + "2" * 40, "total_amount_value": "10000",
                              "payment_legs": [{"pay_to_id": "0x" + "3" * 40, "leg_amount_value": "10000"}]}}
SETTLE["settled_artifact"] = copy.deepcopy(SETTLE["committed_terms"])
UNDER = copy.deepcopy(SETTLE)
UNDER["settled_artifact"]["total_amount_value"] = "1000000"
UNDER["settled_artifact"]["payment_legs"][0]["leg_amount_value"] = "1000000"


def anchored(**kw):
    a = copy.deepcopy(ANCHOR_OK)
    for k, v in kw.items():
        a["anchors"][0][k] = v
    return a


COMMIT = 'equals(/event_kind, "commit_succeeded")'
CASES = [
    # name, subject envs, profile requirements, (state, reason, condition, subject), origin
    ("presence_required_present", [env()], [req("r", field_path="/authority/delegator_id")], ("verified", None, None, "artifact"), "D6 required field present"),
    ("presence_required_absent", [env(authority__delegator_id=None)], [req("r", field_path="/authority/delegator_id")], ("indeterminate", "absence", "field_absent_undeclared", "artifact"), "D6 undeclared absence"),
    ("absence_declared_not_captured", [env(authority__delegator_id=None, field_absences=[{"field_path": "/authority/delegator_id", "absence_reason_code": "not_captured"}])], [req("r", field_path="/authority/delegator_id")], ("indeterminate", "absence", "field_absent_declared", "operator"), "WO19 section 5"),
    ("absence_declared_withheld", [env(authority__delegator_id=None, field_absences=[{"field_path": "/authority/delegator_id", "absence_reason_code": "withheld"}])], [req("r", field_path="/authority/delegator_id")], ("not_evaluated", None, "field_withheld", "operator"), "WO19 section 5: withheld is never absent"),
    ("absence_declared_redacted", [env(authority__delegator_id=None, field_absences=[{"field_path": "/authority/delegator_id", "absence_reason_code": "redacted"}])], [req("r", field_path="/authority/delegator_id")], ("not_evaluated", None, "field_redacted", "access"), "WO19 section 5: redacted is a fact about the reader"),
    ("absence_declared_not_applicable", [env(authority__delegator_id=None, field_absences=[{"field_path": "/authority/delegator_id", "absence_reason_code": "not_applicable"}])], [req("r", field_path="/authority/delegator_id")], ("contradicted", "divergence", "field_declared_not_applicable", "artifact"), "WO19 section 5"),
    ("prohibited_absent", [env()], [req("r", field_path="/privacy/beneficiary_name", obligation_type="prohibited")], ("verified", None, None, "artifact"), "D11 disclosure limit respected"),
    ("prohibited_present", [env(privacy__beneficiary_name="A. Person")], [req("r", field_path="/privacy/beneficiary_name", obligation_type="prohibited")], ("contradicted", "divergence", "prohibited_field_present", "artifact"), "D11 disclosure limit breached"),
    ("conditional_false", [env(event_kind="policy_check_performed", authority__delegator_id=None)], [req("r", field_path="/authority/delegator_id", obligation_type="conditional", condition_expression=COMMIT)], ("verified", None, None, "artifact"), "condition false"),
    ("conditional_true_absent", [env(authority__delegator_id=None)], [req("r", field_path="/authority/delegator_id", obligation_type="conditional", condition_expression=COMMIT)], ("indeterminate", "absence", "field_absent_undeclared", "artifact"), "condition true"),
    ("predicate_unparseable", [env()], [req("r", field_path="/authority/delegator_id", obligation_type="conditional", condition_expression="equals(/event_kind commit)")], ("not_evaluated", "instrument_failure", "predicate_unparseable", "verifier"), "D12 closed predicate language"),
    ("accepted_value", [env()], [req("r", field_path="/evidence_quality/assertion_basis", accepted_values=["observed", "measured"])], ("verified", None, None, "artifact"), "accepted set"),
    ("value_not_accepted", [env(evidence_quality__assertion_basis="asserted")], [req("r", field_path="/evidence_quality/assertion_basis", accepted_values=["observed", "measured"])], ("contradicted", "divergence", "value_not_accepted", "artifact"), "accepted set"),
    ("minimum_met", [env()], [req("r", field_path="/evidence_quality/corroboration_state", minimum_value="third_party_confirmed", value_ladder_ref="axes:corroboration_state_ladder@1")], ("verified", None, None, "artifact"), "ladder minimum"),
    ("minimum_not_met", [env(evidence_quality__corroboration_state="internally_corroborated")], [req("r", field_path="/evidence_quality/corroboration_state", minimum_value="third_party_confirmed", value_ladder_ref="axes:corroboration_state_ladder@1")], ("indeterminate", "absence", "value_below_minimum", "artifact"), "ladder minimum"),
    ("conflicting_never_satisfies", [env(evidence_quality__corroboration_state="conflicting_evidence")], [req("r", field_path="/evidence_quality/corroboration_state", minimum_value="uncorroborated", value_ladder_ref="axes:corroboration_state_ladder@1")], ("indeterminate", "divergence", "conflicting_evidence", "artifact"), "conflicting_evidence never satisfies a minimum"),
    ("basis_demonstrated", [env(integrity__envelope_signature="sig", integrity__envelope_signature_basis_status="demonstrated")], [req("r", field_path="/integrity/envelope_signature", required_basis_status="demonstrated")], ("verified", None, None, "artifact"), "catalogue 1.27"),
    ("basis_not_demonstrated", [env(integrity__envelope_signature="SIG-STUB")], [req("r", field_path="/integrity/envelope_signature", required_basis_status="demonstrated")], ("indeterminate", "absence", "basis_not_demonstrated", "operator"), "catalogue 1.27; gt-v2.0 SIG-STUB"),
    ("chain_intact", "chain2", [req("r", check_type="chain_integrity")], ("verified", None, None, "artifact"), "docs/09"),
    ("chain_broken", "chain_broken", [req("r", check_type="chain_integrity")], ("contradicted", "divergence", "chain_break", "artifact"), "docs/09"),
    ("sequence_contiguous", "chain2", [req("r", check_type="sequence_continuity")], ("verified", None, None, "artifact"), "Module 01"),
    ("sequence_gap", "gap", [req("r", check_type="sequence_continuity")], ("indeterminate", "absence", "sequence_gap", "artifact"), "Module 01"),
    ("anchor_sufficient", [env(anchoring=anchored())], [req("r", check_type="anchoring", field_path="/anchoring", required_basis_status="demonstrated", anchoring={"minimum_independent_anchor_count": 1, "maximum_anchoring_lag": "PT24H"})], ("verified", None, None, "artifact"), "WO18 A2"),
    ("anchor_simulated", [env(anchoring=anchored(basis_status="simulated"))], [req("r", check_type="anchoring", field_path="/anchoring", required_basis_status="demonstrated", anchoring={"minimum_independent_anchor_count": 1})], ("indeterminate", "absence", "anchor_insufficient", "artifact"), "D-020"),
    ("anchor_lag_exceeded", [env(anchoring=anchored(anchored_at="2026-10-06T10:00:00.000Z"))], [req("r", check_type="anchoring", field_path="/anchoring", required_basis_status="demonstrated", anchoring={"minimum_independent_anchor_count": 1, "maximum_anchoring_lag": "PT24H"})], ("indeterminate", "absence", "anchor_lag_exceeded", "artifact"), "WO19 section 3"),
    ("settlement_matches", [env(settlement=SETTLE)], [req("r", check_type="settlement_commitment", field_path="/settlement", subject_type="envelope")], ("verified", None, None, "artifact"), "x402#3220 section 13"),
    ("settlement_under_report", [env(settlement=UNDER)], [req("r", check_type="settlement_commitment", field_path="/settlement", subject_type="envelope")], ("contradicted", "divergence", "settlement_commitment_mismatch", "artifact"), "x402#3220 section 13 rule (a): the only under-report detector"),
    ("settlement_not_observed", [env(settlement={"settlement_submitter_id": "x"})], [req("r", check_type="settlement_commitment", field_path="/settlement", subject_type="envelope")], ("indeterminate", "absence", "settlement_not_observed", "artifact"), "x402#3226: a verify is not a settlement"),
]


def special(kind):
    envs = chain([env(), env(event_kind="policy_check_performed")])
    if kind == "chain_broken":
        envs[1]["integrity"]["previous_envelope_hash"] = "f" * 64
    if kind == "gap":
        envs[1]["sequence_number"] = 3
    return envs


def main():
    os.makedirs(os.path.join(OUT, "subjects"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "test_profiles"), exist_ok=True)
    expected = {}
    for name, subject, reqs, want, origin in CASES:
        envs = special(subject) if isinstance(subject, str) else chain(subject)
        with open(os.path.join(OUT, "subjects", name + ".jsonl"), "w", encoding="utf-8", newline="\n") as f:
            for e in envs:
                f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
        p = profile(name, reqs)
        with open(os.path.join(OUT, "test_profiles", name + ".json"), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(p, indent=2) + "\n")
        exp = {"verification_state": want[0], "verification_subject_type": want[3]}
        if want[1]:
            exp["verification_reason_code"] = want[1]
        if want[2]:
            exp["verification_condition_code"] = want[2]
        expected[name + ".jsonl"] = {"requirement_profile_ref": p["requirement_profile_id"], "expected_verification": exp,
                          "provenance": dict(PROV, origin_note=origin)}
    # composition: a child relaxing a parent floor is a conflict, never a silent winner (D10)
    parent = profile("composition_parent", [req("r", field_path="/authority/delegator_id", floor_indicator=True)])
    child = profile("composition_child", [req("r", field_path="/authority/delegator_id", obligation_type="optional")],
                    extends=["example:composition_parent@1"])
    for p in (parent, child):
        with open(os.path.join(OUT, "test_profiles", p["requirement_profile_id"].split(":")[1].split("@")[0] + ".json"),
                  "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(p, indent=2) + "\n")
    with open(os.path.join(OUT, "subjects", "composition.jsonl"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(chain([env()])[0], sort_keys=True) + "\n")
    expected["composition_floor_relaxed.case"] = {
        "requirement_profile_ref": "example:composition_child@1", "subject_file_ref": "composition.jsonl",
        "expected_verification": {"verification_state": "indeterminate", "verification_reason_code": "divergence",
                                  "verification_condition_code": "profile_conflict", "verification_subject_type": "verifier"},
        "provenance": dict(PROV, origin_note="D10: a floor cannot be relaxed by an extending profile")}
    expected["profile_unsupported.case"] = {
        "requirement_profile_ref": "example:not_published@1", "subject_file_ref": "presence_required_present.jsonl",
        "expected_verification": {"verification_state": "not_evaluated", "verification_reason_code": "instrument_failure",
                                  "verification_condition_code": "profile_unsupported", "verification_subject_type": "verifier"},
        "provenance": dict(PROV, origin_note="D9: an unsupported profile is never a pass")}
    doc = {"vector_format_ref": "axes:profile_vectors@1",
           "summary_note": "WO19 evaluation vectors. Each case evaluates one requirement of a test profile against a synthetic subject; "
                           "the expected result is the decisive result for that requirement. Subjects use gt-v2.1 key names.",
           "vectors": expected}
    with open(os.path.join(OUT, "expected.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, indent=2) + "\n")
    print("wrote %d profile vectors" % len(expected))


if __name__ == "__main__":
    main()
