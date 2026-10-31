import copy
import json
import os
import shutil

import pytest

from axes_sdk import State, UnsafePathError, load_subject, verify_bundle, verify_stream
from axes_sdk.bundle import safe_join

from conftest import needs_repo, repo

pytestmark = needs_repo


def conditions(report):
    return {(f.state.value, f.condition) for f in report.findings if f.state is not State.VERIFIED}


def rehash(envs, start):
    """Recompute stored hashes and links from `start` on, as a forger without an anchor would."""
    from axes_sdk import hash_envelope
    for i in range(start, len(envs)):
        if i:
            envs[i]["integrity"]["previous_envelope_hash"] = envs[i - 1]["integrity"]["envelope_hash"]
        envs[i]["integrity"]["envelope_hash"] = hash_envelope(envs[i])


@pytest.mark.parametrize("name,path", [("golden-trace", "fin"), ("golden-trace-ind", "ind")])
def test_published_corpora_verify_with_pinned_heads(name, path, release, fin_path, ind_path):
    subject = load_subject(fin_path if path == "fin" else ind_path)
    report = verify_stream(subject, expected_chain_head=release[name]["chain_head"])
    assert report.overall_state is State.VERIFIED and report.all_requested_checks_verified
    assert report.envelope_count == 76 and report.sequence_range == (1, 76)
    assert report.chain_head == release[name]["chain_head"]
    assert any("signatures are not verified" in line for line in report.limitations)


def test_changed_value_is_a_mismatch_then_a_break(fin_path):
    envs = [copy.deepcopy(e) for e in load_subject(fin_path).envelopes]
    envs[8]["authority"]["authority_context_ref"] = "AD-7845"
    assert ("contradicted", "envelope_hash_mismatch") in conditions(verify_stream(envs))
    from axes_sdk import hash_envelope
    envs[8]["integrity"]["envelope_hash"] = hash_envelope(envs[8])
    assert conditions(verify_stream(envs)) == {("contradicted", "chain_break")}


def test_full_rehash_passes_integrity_but_not_the_pinned_head(fin_path, release):
    envs = [copy.deepcopy(e) for e in load_subject(fin_path).envelopes]
    envs[8]["authority"]["authority_context_ref"] = "AD-7845"
    rehash(envs, 8)
    assert verify_stream(envs).overall_state is State.VERIFIED  # integrity alone cannot see a full rewrite
    pinned = verify_stream(envs, expected_chain_head=release["golden-trace"]["chain_head"])
    assert ("contradicted", "chain_break") in conditions(pinned)


def test_omission_reordering_and_duplication(fin_path):
    base = list(load_subject(fin_path).envelopes)
    omitted = base[:10] + base[11:]
    assert {("contradicted", "chain_break"), ("indeterminate", "sequence_gap")} <= conditions(verify_stream(omitted))
    swapped = base[:10] + [base[11], base[10]] + base[12:]
    assert ("indeterminate", "sequence_gap") in conditions(verify_stream(swapped))
    duplicated = base[:11] + [base[10]] + base[11:]
    assert ("contradicted", "chain_break") in conditions(verify_stream(duplicated))


def test_empty_subject_is_not_verified():
    report = verify_stream([])
    assert report.overall_state is State.INDETERMINATE and not report.all_requested_checks_verified


def test_unsupported_algorithm_and_out_of_domain_values(fin_path):
    envs = [copy.deepcopy(e) for e in load_subject(fin_path).envelopes[:3]]
    envs[1]["integrity"]["hash_algorithm"] = "UNSUPPORTED"
    report = verify_stream(envs)
    assert ("not_evaluated", "hash_algorithm_unsupported") in conditions(report)
    assert report.overall_state is State.INDETERMINATE
    envs = [copy.deepcopy(e) for e in load_subject(fin_path).envelopes[:3]]
    envs[0]["sequence_number"] = 1.0
    assert ("contradicted", "value_outside_domain") in conditions(verify_stream(envs))


def test_window(fin_path):
    envs = list(load_subject(fin_path).envelopes[10:20])
    assert verify_stream(envs).overall_state is not State.VERIFIED
    window = verify_stream(envs, window=True)
    assert window.overall_state is State.VERIFIED and any("Window" in l for l in window.limitations)


@pytest.fixture
def bundle_copy(tmp_path):
    dst = tmp_path / "bundle"
    shutil.copytree(repo("examples", "golden-trace", "out"), dst)
    return dst


def test_bundle_verifies(bundle_copy, release):
    report = verify_bundle(bundle_copy, expected_manifest_hash=release["golden-trace"]["bundle_manifest_hash"])
    assert report.overall_state is State.VERIFIED, report.to_json()
    assert report.file_count == 38 and report.bundle_manifest_hash == release["golden-trace"]["bundle_manifest_hash"]


def test_bundle_file_changed_or_missing(bundle_copy):
    victim = bundle_copy / "artifacts" / "camt053_20260609.xml"
    victim.write_bytes(victim.read_bytes() + b" ")
    assert ("contradicted", "bundle_file_hash_mismatch") in conditions(verify_bundle(bundle_copy))
    victim.unlink()
    assert ("indeterminate", "bundle_file_absent") in conditions(verify_bundle(bundle_copy))


def test_bundle_paths_never_leave_the_root(bundle_copy, tmp_path):
    secret = tmp_path / "secret.txt"
    secret.write_text("outside")
    manifest = json.loads((bundle_copy / "manifest.json").read_text(encoding="utf-8"))
    manifest["files"]["../secret.txt"] = "0" * 64
    manifest["files"]["/etc/passwd"] = "0" * 64
    manifest["files"]["C:/Windows/win.ini"] = "0" * 64
    manifest["files"]["artifacts\\x.xml"] = "0" * 64
    (bundle_copy / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    report = verify_bundle(bundle_copy)
    unsafe = [f for f in report.findings if f.condition == "bundle_path_unsafe"]
    assert len(unsafe) == 4
    assert ("contradicted", "bundle_manifest_hash_mismatch") in conditions(report)


def test_symlink_escape_refused(bundle_copy, tmp_path):
    outside = tmp_path / "outside.txt"
    outside.write_text("x")
    link = bundle_copy / "link.txt"
    try:
        os.symlink(outside, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks not available")
    with pytest.raises(UnsafePathError):
        safe_join(str(bundle_copy), "link.txt")
