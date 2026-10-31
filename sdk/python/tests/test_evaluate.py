import json
import os
import sys

import pytest

from axes_sdk import (EvaluationContext, ProfileResolutionError, ProfileSet, State, bundled_profiles, evaluate,
                      load_profile_set, load_subject, profile_digest)

from conftest import needs_repo, repo

pytestmark = needs_repo


def published(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.parametrize("ref,rel", [
    ("axes:gt_fin_internal_audit@1", "evaluations/gt-v2.1/gt_fin_internal_audit__golden-trace.json"),
    ("axes:gt_fin_regulator@1", "evaluations/gt-v2.1/gt_fin_regulator__golden-trace.json"),
])
def test_published_evaluations_reproduce(ref, rel, fin_path):
    want = published(repo(*rel.split("/")))
    got = evaluate(load_subject(fin_path), ref, bundled_profiles(),
                   EvaluationContext(release="gt-v2.1", evaluated_at=want["evaluated_at"]))
    assert got.result_core_hash == want["result_core_hash"]
    assert got.overall_verification_state.value == want["overall_verification_state"]


@pytest.mark.parametrize("name", sorted(os.listdir(repo("examples", "x402-b2b-vat", "evaluations")))
                         if os.path.isdir(repo("examples", "x402-b2b-vat", "evaluations")) else [])
def test_x402_example_evaluations_reproduce(name):
    want = published(repo("examples", "x402-b2b-vat", "evaluations", name))
    base = name[:-5]
    profile, party = "axes:%s@1" % base.split("__")[0], base.split("__")[1]
    subject = load_subject(repo("examples", "x402-b2b-vat", party, "envelopes.jsonl"))
    got = evaluate(subject, profile, bundled_profiles(), EvaluationContext(release=None, evaluated_at=want["evaluated_at"]))
    assert got.result_core_hash == want["result_core_hash"]


def test_profile_vectors():
    spec = published(repo("vectors", "profiles", "expected.json"))["vectors"]
    profiles = load_profile_set(repo("vectors", "profiles", "test_profiles"))
    for name, case in spec.items():
        subject = load_subject(repo("vectors", "profiles", "subjects", case.get("subject_file_ref", name)))
        rec = evaluate(subject, case["requirement_profile_ref"], profiles, EvaluationContext(release=None))
        got = {k: v for k, v in rec.results[-1].items() if k.startswith("verification_")}
        assert got == case["expected_verification"], name


def test_record_equals_the_reference_evaluator(fin_path):
    sys.path.insert(0, repo())
    try:
        from tools import axes_evaluate as ref
    finally:
        sys.path.remove(repo())
    want = ref.evaluate("axes:gt_fin_regulator@1", fin_path, repo("vendor", "main", "profiles"),
                        repo("vendor", "main", "key-aliases.json"), "gt-v2.1", None, "2026-10-31T00:00:00.000Z")
    got = evaluate(load_subject(fin_path), "axes:gt_fin_regulator@1", bundled_profiles(),
                   EvaluationContext(release="gt-v2.1", evaluated_at="2026-10-31T00:00:00.000Z")).record
    assert got == want


def test_bundled_profiles_are_the_published_ones():
    bundled = bundled_profiles()
    published_set = load_profile_set(repo("profiles"))
    for ref in ("axes:gt_fin_internal_audit@1", "axes:gt_fin_regulator@1", "axes:x402_b2b_buyer_audit@1"):
        assert bundled.digest(ref) == published_set.digest(ref)


def test_closure_pins(fin_path):
    profiles = bundled_profiles()
    pins = {r: profiles.digest(r) for r in profiles.closure("axes:gt_fin_regulator@1")[0]}
    ctx = EvaluationContext(pins=pins)
    assert evaluate(load_subject(fin_path), "axes:gt_fin_regulator@1", profiles, ctx).record[
        "requirement_profile_closure"][0]["requirement_profile_hash"] == pins["axes:gt_fin_internal_audit@1"]
    with pytest.raises(ProfileResolutionError, match="no pin"):
        evaluate(load_subject(fin_path), "axes:gt_fin_regulator@1", profiles,
                 EvaluationContext(pins={"axes:gt_fin_regulator@1": pins["axes:gt_fin_regulator@1"]}))
    bad = dict(pins, **{"axes:gt_fin_internal_audit@1": "0" * 64})
    with pytest.raises(ProfileResolutionError, match="does not match"):
        evaluate(load_subject(fin_path), "axes:gt_fin_regulator@1", profiles, EvaluationContext(pins=bad))


def leaf(**kw):
    p = {"requirement_profile_id": "t:leaf@1", "requirement_profile_version": "1", "subject_types": ["bundle"],
         "requirements": []}
    p.update(kw)
    return p


def test_unresolvable_profile_sets_never_verify(fin_path):
    subject = load_subject(fin_path)
    for doc in (leaf(extended_profile_refs=["t:missing@1"]), leaf(extended_profile_refs=["t:leaf@1"]), leaf()):
        rec = evaluate(subject, "t:leaf@1", ProfileSet.from_documents([doc]))
        assert rec.overall_verification_state is not State.VERIFIED and rec.results
    rec = evaluate(subject, "t:absent@1", ProfileSet.from_documents([leaf()]))
    assert rec.results[0]["verification_condition_code"] == "profile_unsupported"
    with pytest.raises(ProfileResolutionError):
        ProfileSet.from_documents([leaf(), leaf(requirements=[{"requirement_id": "x"}])])


def test_unexercised_condition_is_a_condition(fin_path):
    req = {"requirement_id": "r", "check_type": "field_presence", "field_path": "/authority/delegator_id",
           "obligation_type": "conditional", "condition_expression": 'equals(/event_kind, "no_such_kind")'}
    rec = evaluate(load_subject(fin_path), "t:leaf@1", ProfileSet.from_documents([leaf(requirements=[req])]))
    assert rec.results[0]["verification_condition_code"] == "condition_not_exercised"
    assert rec.overall_verification_state is State.VERIFIED and rec.guarantee_type == "conditional"


def test_evaluation_is_deterministic(fin_path):
    a = evaluate(load_subject(fin_path), "axes:gt_fin_internal_audit@1", bundled_profiles())
    b = evaluate(load_subject(fin_path), "axes:gt_fin_internal_audit@1", bundled_profiles(),
                 EvaluationContext(evaluated_at="2030-01-01T00:00:00.000Z"))
    assert a.result_core_hash == b.result_core_hash and a.record["evaluated_at"] != b.record["evaluated_at"]
    with pytest.raises(ValueError):
        EvaluationContext(evaluated_at="yesterday")
