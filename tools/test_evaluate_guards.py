#!/usr/bin/env python3
"""WO19 guards: the evaluator uses no network, emits no trust score, and a permissive evaluator fails the suite."""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tools import axes_evaluate as ev  # noqa: E402
from tools import axes_verify  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def validation_regressions() -> None:
    """Findings V1 to V4 of the independent validation of PR #21 (31 Oct 2026): each failed before its fix."""
    import copy
    import tempfile
    from tools.axes_canonical import DomainError, canonical_bytes, envelope_digest, hash_preimage, strict_loads

    envs = ev.read_subject(os.path.join(ROOT, "examples/golden-trace/out/envelopes.jsonl"))
    chain = {"requirement_id": "r"}
    # V1: an undeclared-capability algorithm is not evaluated, never verified.
    one = copy.deepcopy(envs[:1])
    one[0]["integrity"]["hash_algorithm"] = "UNSUPPORTED"
    r = ev.check_chain(chain, one)
    check((r["verification_state"], r.get("verification_condition_code")) == ("not_evaluated", "hash_algorithm_unsupported"),
          "V1: an unsupported hash algorithm is not_evaluated, not verified")
    one[0]["integrity"]["hash_algorithm"] = "SHA-256"
    one[0]["integrity"]["canonicalization_version"] = "not-jcs"
    r = ev.check_chain(chain, one)
    check(r["verification_state"] == "not_evaluated", "V1: an unsupported canonicalisation identifier is not_evaluated")
    r = ev.check_chain(chain, [])
    check(r["verification_state"] == "indeterminate", "V5: an empty chain subject is indeterminate, not verified")
    # V2 and V3: profile graphs.
    leaf = {"requirement_profile_id": "t:leaf@1", "requirement_profile_version": "1", "subject_types": ["bundle"],
            "requirements": [], "extended_profile_refs": ["t:missing@1"]}
    subject = os.path.join(ROOT, "examples/golden-trace/out/envelopes.jsonl")
    with tempfile.TemporaryDirectory() as d:
        json.dump(leaf, open(os.path.join(d, "leaf.json"), "w"))
        rec = ev.evaluate("t:leaf@1", subject, d, None)
        check(rec["overall_verification_state"] == "not_evaluated" or rec["overall_verification_state"] == "indeterminate",
              "V2: a missing parent profile never yields verified (got %s)" % rec["overall_verification_state"])
        check(rec["results"] and rec["guarantee_type"] == "conditional", "V2: results are never empty")
        leaf["extended_profile_refs"] = ["t:leaf@1"]
        json.dump(leaf, open(os.path.join(d, "leaf.json"), "w"))
        rec = ev.evaluate("t:leaf@1", subject, d, None)
        check(rec["overall_verification_state"] != "verified", "V2: a self-cycle never yields verified")
        dup = dict(leaf, requirements=[{"requirement_id": "x", "check_type": "field_presence",
                                        "field_path": "/x", "obligation_type": "optional"}])
        json.dump(dup, open(os.path.join(d, "leaf2.json"), "w"))
        try:
            ev.load_profiles(d)
            check(False, "V3: two different files for one id@version are refused")
        except ev.ProfileSetError:
            check(True, "V3: two different files for one id@version are refused")
    rec = ev.evaluate("axes:gt_fin_regulator@1", subject, os.path.join(ROOT, "vendor/main/profiles"),
                      os.path.join(ROOT, "vendor/main/key-aliases.json"), "gt-v2.1")
    refs = [c["requirement_profile_ref"] for c in rec.get("requirement_profile_closure", [])]
    check(refs == ["axes:gt_fin_internal_audit@1", "axes:gt_fin_regulator@1"],
          "V3: the record lists the digest of every profile in the resolved closure")
    # V4: strict JSON and the numeric domain.
    for text in ('{"kind":"good","kind":"bad"}', '{"n":NaN}'):
        try:
            strict_loads(text)
            check(False, "V4: strict loader refuses %s" % text)
        except ValueError:
            check(True, "V4: strict loader refuses %s" % text)
    for bad in (2 ** 53, 1.5):
        e = copy.deepcopy(envs[0])
        e["sequence_number"] = bad
        try:
            hash_preimage(e)
            check(False, "V4: %r in the hash scope is refused" % bad)
        except DomainError:
            check(True, "V4: %r in the hash scope is refused" % bad)
    check(envelope_digest(envs[0]) == envs[0]["integrity"]["envelope_hash"] and canonical_bytes({"a": 1}) == b'{"a":1}',
          "in-domain hashing is unchanged")


def review2_regressions() -> None:
    """Findings S1 and S3 of the second independent review of PR #21 (31 Oct 2026): each failed before its fix."""
    import copy
    import tempfile
    from tools.axes_canonical import UnsupportedAlgorithm, envelope_digest

    envs = ev.read_subject(os.path.join(ROOT, "examples/golden-trace/out/envelopes.jsonl"))
    # S3: under gt-v2.1 only envelope_hash and envelope_signature are outside the hash scope.
    e = copy.deepcopy(envs[:2])
    e[0]["integrity"]["signature"] = "SYNTHETIC_ADDED_VALUE"
    check(envelope_digest(e[0]) != envs[0]["integrity"]["envelope_hash"],
          "S3: a member named signature added to a gt-v2.1 envelope changes its digest")
    r = ev.check_chain({"requirement_id": "r"}, e, "gt-v2.1")
    check((r["verification_state"], r.get("verification_condition_code")) == ("contradicted", "envelope_hash_mismatch"),
          "S3: the chain check reports envelope_hash_mismatch for it")
    archived = ev.read_subject(os.path.join(ROOT, "archive/golden-trace-v1-fin/out/envelopes.jsonl")) \
        if os.path.exists(os.path.join(ROOT, "archive/golden-trace-v1-fin/out/envelopes.jsonl")) else []
    if archived:
        from tools.axes_canonical import DomainError
        in_domain = []
        for a in archived:
            try:
                in_domain.append(envelope_digest(a) == a["integrity"]["envelope_hash"])
            except DomainError:  # this archive predates the integer-only rule
                pass
        check(in_domain and all(in_domain) and "signature" in archived[0]["integrity"],
              "S3: gt-v2.0 digests are unchanged, integrity.signature excluded (%d envelopes)" % len(in_domain))
    e = copy.deepcopy(envs[0])
    del e["integrity"]["hash_algorithm"]
    try:
        envelope_digest(e)
        check(False, "a missing hash_algorithm is refused, not defaulted")
    except UnsupportedAlgorithm:
        check(True, "a missing hash_algorithm is refused, not defaulted")
    # S3: the stream loader in axes_verify refuses duplicate members.
    import tools.axes_verify as av
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "s.jsonl")
        lines = open(os.path.join(ROOT, "examples/golden-trace/out/envelopes.jsonl"), encoding="utf-8").read().splitlines()
        lines[0] = lines[0].replace('{"', '{"sequence_number":999,"', 1)
        open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines) + "\n")
        rep = av.Report()
        av.verify_chain("dup", path, rep)
        check([r.outcome for r in rep.results] == ["malformed"], "S3: a duplicate sequence_number fails the stream row")

    # S1: strictest-wins between two extended profiles, whatever their order.
    def prof(pid, reqs, parents=()):
        return {"requirement_profile_id": pid, "requirement_profile_version": "1", "subject_types": ["bundle"],
                "requirements": reqs, "extended_profile_refs": list(parents)}

    def req(obligation):
        return {"requirement_id": "kind", "check_type": "field_presence", "field_path": "/kind",
                "obligation_type": obligation}

    subject = [{"sequence_number": 1}]
    for other, want, label in (("optional", "contradicted", "required beats optional"),
                               ("prohibited", "indeterminate", "required versus prohibited is a conflict")):
        states = set()
        for parents in (["t:a@1", "t:b@1"], ["t:b@1", "t:a@1"]):
            profiles = {"t:a@1": prof("t:a@1", [req("required")]), "t:b@1": prof("t:b@1", [req(other)]),
                        "t:c@1": prof("t:c@1", [], parents)}
            rec = ev.evaluate_envelopes("t:c@1", subject, "0" * 64, profiles, ev.Translator(None, None, entries=[]))
            states.add(rec["overall_verification_state"])
        check(states == {want} or (want == "contradicted" and states <= {"contradicted", "indeterminate"} and "verified" not in states),
              "S1: sibling parents, %s, in either order (got %s)" % (label, sorted(states)))
    # A diamond: the shared ancestor's requirement reaches the child twice, identically, with no conflict.
    profiles = {"t:p@1": prof("t:p@1", [req("required")]), "t:a@1": prof("t:a@1", [], ["t:p@1"]),
                "t:b@1": prof("t:b@1", [], ["t:p@1"]), "t:c@1": prof("t:c@1", [], ["t:a@1", "t:b@1"])}
    reqs, conflicts = ev.resolve("t:c@1", profiles)
    check(len(reqs) == 1 and not conflicts, "S1: a diamond resolves to one requirement with no conflict")


def main() -> int:
    for mod in ("axes_evaluate.py", "axes_anchoring_guard.py"):
        src = open(os.path.join(ROOT, "tools", mod), encoding="utf-8").read()
        check(not re.search(r"^\s*(import|from)\s+(socket|urllib|http|requests|ssl|ftplib)\b", src, re.M),
              "%s imports no network library (D12)" % mod)
    for path in ("evaluations/gt-v2.0/gt_fin_regulator__golden-trace.json",):
        text = open(os.path.join(ROOT, path), encoding="utf-8").read()
        check(not re.search(r'"[a-z_]*(score|trust_level|confidence_value)[a-z_]*"\s*:', text),
              "%s carries no trust score (D7)" % path)
    rec = json.load(open(os.path.join(ROOT, "evaluations/gt-v2.0/gt_fin_regulator__golden-trace.json"), encoding="utf-8"))
    conds = {r.get("verification_condition_code") for r in rec["results"]}
    check(rec["overall_verification_state"] == "indeterminate" and {"basis_not_demonstrated", "anchor_insufficient"} <= conds,
          "gt-v2.0 under the regulator profile is indeterminate with basis_not_demonstrated and anchor_insufficient")
    real = ev.evaluate_requirement
    ev.evaluate_requirement = lambda req, envs, tr, release: ev.result(req["requirement_id"], "verified", note="permissive")
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            code = axes_verify.main(["--skip-coverage"])
    finally:
        ev.evaluate_requirement = real
    check(code == 1, "a permissive evaluator fails the suite (exit %s)" % code)
    validation_regressions()
    review2_regressions()
    print("FAILED: %s" % FAILS if FAILS else "OK evaluator guards")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
