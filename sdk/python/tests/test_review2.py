"""Regressions for the second independent review of PR #21 (31 Oct 2026), findings S1 to S6. Each case
is a behaviour the SDK must have on its own terms, not agreement with the reference code it packages."""
import copy
import json
import os
import shutil

import pytest

from axes_sdk import (EvaluationContext, Limits, ProfileSet, ResourceLimitError, State, evaluate, hash_envelope,
                      load_subject, verify_bundle, verify_stream)
from axes_sdk import bundle as bundle_mod
from axes_sdk.errors import ParseError, UnsupportedCapabilityError
from axes_sdk.jsonio import parse_json

from conftest import needs_repo, repo


def _profile(pid, reqs, parents=()):
    return {"requirement_profile_id": pid, "requirement_profile_version": "1", "subject_types": ["bundle"],
            "requirements": reqs, "extended_profile_refs": list(parents)}


def _kind(obligation, **extra):
    r = {"requirement_id": "kind", "check_type": "field_presence", "field_path": "/kind",
         "obligation_type": obligation}
    r.update(extra)
    return r


# S1: strictest-wins between two extended profiles does not depend on their order.

@pytest.mark.parametrize("other,expected", [("optional", {"indeterminate"}), ("prohibited", {"indeterminate"})])
def test_sibling_parents_compose_strictest_in_either_order(other, expected):
    subject = load_subject(b'{"sequence_number":1}')
    states = set()
    for parents in (["t:a@1", "t:b@1"], ["t:b@1", "t:a@1"]):
        profiles = ProfileSet.from_documents([_profile("t:a@1", [_kind("required")]),
                                              _profile("t:b@1", [_kind(other)]),
                                              _profile("t:c@1", [], parents)])
        states.add(evaluate(subject, "t:c@1", profiles).overall_verification_state.value)
    assert states == expected


def test_sibling_required_versus_prohibited_is_a_profile_conflict():
    profiles = ProfileSet.from_documents([_profile("t:a@1", [_kind("required")]),
                                          _profile("t:b@1", [_kind("prohibited")]),
                                          _profile("t:c@1", [], ["t:b@1", "t:a@1"])])
    record = evaluate(load_subject(b'{"kind":"x"}'), "t:c@1", profiles).record
    assert "profile_conflict" in {r.get("verification_condition_code") for r in record["results"]}


# S2: the evaluated envelopes are always the bytes whose digest is recorded.

def test_mutating_the_subject_view_cannot_change_the_result():
    profile = {"requirement_id": "kind", "check_type": "value_match", "field_path": "/kind",
               "obligation_type": "required", "accepted_values": ["good"]}
    profiles = ProfileSet.from_documents([_profile("t:p@1", [profile])])
    subject = load_subject(b'{"kind":"bad"}')
    before = evaluate(subject, "t:p@1", profiles)
    subject.envelopes[0]["kind"] = "good"
    after = evaluate(subject, "t:p@1", profiles)
    assert after.result_core_hash == before.result_core_hash
    assert after.record["subject_hashes"] == before.record["subject_hashes"]


def test_a_subject_whose_bytes_do_not_match_its_digest_is_refused():
    subject = load_subject(b'{"kind":"bad"}')
    forged = type(subject)(subject.envelopes, b'{"kind":"good"}', subject.sha256)
    with pytest.raises(ParseError):
        verify_stream(forged)


# S3: the release decides the hash scope, and the digest algorithm must be declared.

@needs_repo
def test_an_added_legacy_signature_member_is_hashed_under_gt_v2_1(fin_path):
    envs = [copy.deepcopy(e) for e in load_subject(fin_path).envelopes[:2]]
    envs[0]["integrity"]["signature"] = "SYNTHETIC_ADDED_VALUE"
    conds = {(f.state.value, f.condition) for f in verify_stream(envs).findings}
    assert ("contradicted", "envelope_hash_mismatch") in conds


@needs_repo
def test_a_missing_hash_algorithm_is_not_defaulted(fin_path):
    env = copy.deepcopy(load_subject(fin_path).envelopes[0])
    del env["integrity"]["hash_algorithm"]
    with pytest.raises(UnsupportedCapabilityError):
        hash_envelope(env)


# S4: a bundle's stream is checked from the bytes that were hashed against the manifest.

@needs_repo
def test_bundle_stream_is_read_once(tmp_path, monkeypatch, release):
    root = tmp_path / "bundle"
    shutil.copytree(repo("examples", "golden-trace", "out"), root)
    stream = root / "envelopes.jsonl"
    real = bundle_mod.read_bytes
    reads = []

    def read_then_swap(path, limits):
        data = real(path, limits)
        if os.path.basename(path) == "envelopes.jsonl":
            reads.append(path)
            stream.write_bytes(data.replace(b"AD-7844", b"AD-7845"))  # the file changes after it is hashed
        return data

    monkeypatch.setattr(bundle_mod, "read_bytes", read_then_swap)
    report = verify_bundle(root, expected_manifest_hash=release["golden-trace"]["bundle_manifest_hash"])
    assert len(reads) == 1
    assert report.overall_state is State.VERIFIED  # it describes the committed bytes, which were the ones read


# S5: every input form respects the limits, and no number may overflow to infinity.

def test_jsonl_bytes_respect_the_total_byte_limit():
    with pytest.raises(ResourceLimitError):
        load_subject(b"{}\n" * 8, jsonl=True, limits=Limits(max_bytes=4))


def test_json_arrays_respect_the_record_limit():
    with pytest.raises(ResourceLimitError):
        load_subject(b"[{},{},{}]", limits=Limits(max_records=1))


def test_string_limits_count_utf8_bytes():
    with pytest.raises(ResourceLimitError):
        parse_json('"' + "é" * 5 + '"', Limits(max_bytes=8))


def test_exponent_overflow_is_refused():
    with pytest.raises(ParseError):
        parse_json(b'{"n":1e999}')


def test_evaluated_at_must_be_a_real_instant():
    with pytest.raises(ValueError):
        EvaluationContext(evaluated_at="2026-99-99T99:99:99.000Z")
    EvaluationContext(evaluated_at="2026-10-31T23:59:59.999Z")


# S6: the manifest itself is held to the bundle's containment rule.

@needs_repo
def test_a_manifest_link_outside_the_bundle_is_not_read(tmp_path):
    root = tmp_path / "bundle"
    shutil.copytree(repo("examples", "golden-trace", "out"), root)
    outside = tmp_path / "outside.json"
    outside.write_text(json.dumps({"files": {"x": "0" * 64}}), encoding="utf-8")
    (root / "manifest.json").unlink()
    try:
        os.symlink(outside, root / "manifest.json")
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not available")
    report = verify_bundle(root)
    assert [(f.state.value, f.condition) for f in report.findings] == [("contradicted", "bundle_path_unsafe")]
