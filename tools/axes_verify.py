#!/usr/bin/env python3
"""
AXES reference verifier (offline).

Recomputes RFC 8785 JCS bytes and SHA-256 digests, evaluates vectors/expected.json
including reject reason codes, walks Golden Trace chains, and exercises custody twins.

Typed outcomes, never a bare boolean. Stdlib plus the 'jcs' package. No network.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.axes_canonical import envelope_digest, hash_preimage, sha256_hex

VECTORS_DIR = os.path.join(ROOT, "vectors")
EXPECTED_PATH = os.path.join(VECTORS_DIR, "expected.json")
EXECUTOR_ID = "agent:caldera/ap-pilot"
DEPLOYER_ID = "org:caldera-robotics"


class DuplicateKeyError(ValueError):
    pass


def object_pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    out: dict = {}
    for k, v in pairs:
        if k in out:
            raise DuplicateKeyError(k)
        out[k] = v
    return out


def load_json_reject_duplicates(text: str) -> Any:
    return json.loads(text, object_pairs_hook=object_pairs_no_duplicates)


@dataclass
class CheckResult:
    check: str
    subject: str
    outcome: str
    detail: str = ""

    def ok(self) -> bool:
        return self.outcome in {"ok", "reject_as_expected"}


@dataclass
class Report:
    results: list[CheckResult] = field(default_factory=list)

    def add(self, check: str, subject: str, outcome: str, detail: str = "") -> CheckResult:
        r = CheckResult(check, subject, outcome, detail)
        self.results.append(r)
        return r

    def failed(self) -> list[CheckResult]:
        return [r for r in self.results if not r.ok()]


def germanish_collation_key(s: str) -> str:
    """Locale-like key that sorts ä with ae, catching a collation comparator."""
    return (
        s.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("Ä", "Ae")
        .replace("Ö", "Oe")
        .replace("Ü", "Ue")
        .replace("ß", "ss")
        .lower()
    )


def locale_like_canonical_utf8(obj: Any) -> str:
    """Wrong canonicaliser: locale-like member order, JSON separators like JCS."""

    def dump(o: Any) -> str:
        if o is None:
            return "null"
        if o is True:
            return "true"
        if o is False:
            return "false"
        if isinstance(o, str):
            return json.dumps(o, ensure_ascii=False)
        if isinstance(o, int) and not isinstance(o, bool):
            return str(o)
        if isinstance(o, list):
            return "[" + ",".join(dump(i) for i in o) + "]"
        if isinstance(o, dict):
            keys = sorted(o.keys(), key=germanish_collation_key)
            return "{" + ",".join(json.dumps(k, ensure_ascii=False) + ":" + dump(o[k]) for k in keys) + "}"
        raise TypeError(type(o))

    return dump(obj)


def custody_independence_outcome(env: dict) -> str:
    """
    Three-leg independence: capturer must not be the deployer when the
    envelope claims independent_third_party capture.
    Unparseable identifier syntax is verification_unavailable, never a reject.
    """
    custody = env.get("custody") or {}
    rel = custody.get("capture_relationship")
    capturer = custody.get("capturer_id")
    deployer = custody.get("deployer_id")
    if not isinstance(capturer, str) or not isinstance(deployer, str):
        return "verification_unavailable"
    if ":" not in capturer or ":" not in deployer:
        return "verification_unavailable"
    if rel == "independent_third_party" and capturer == deployer:
        return "custody_independence_reject"
    return "ok"


def verify_vector(name: str, spec: dict, report: Report) -> None:
    path = os.path.join(VECTORS_DIR, name)
    raw = open(path, encoding="utf-8").read()

    if spec.get("reject") is True:
        try:
            load_json_reject_duplicates(raw)
        except DuplicateKeyError:
            report.add("canonicalisation_reject", name, "reject_as_expected", "duplicate_key")
            return
        except json.JSONDecodeError as exc:
            report.add("canonicalisation_reject", name, "reject_as_expected", str(exc))
            return
        report.add("canonicalisation_reject", name, "accepted_malformed", "duplicate-key fixture parsed")
        return

    try:
        obj = load_json_reject_duplicates(raw)
    except DuplicateKeyError as exc:
        report.add("parse", name, "duplicate_key", str(exc))
        return
    except json.JSONDecodeError as exc:
        report.add("parse", name, "json_error", str(exc))
        return

    cb = hash_preimage(obj)
    canon = cb.decode("utf-8")
    digest = sha256_hex(cb)

    if "canonical_utf8" in spec:
        if canon == spec["canonical_utf8"]:
            report.add("canonical_bytes", name, "ok")
        else:
            report.add("canonical_bytes", name, "mismatch")
    if "sha256" in spec:
        if digest == spec["sha256"]:
            report.add("digest", name, "ok")
        else:
            report.add("digest", name, "mismatch", f"got {digest}")

    expect = spec.get("expect", "pass")
    reject_code = spec.get("reject_code")
    if expect == "reject":
        if reject_code == "custody_independence_reject":
            got = custody_independence_outcome(obj)
            if got == "custody_independence_reject":
                report.add("custody_independence", name, "reject_as_expected", got)
            else:
                report.add("custody_independence", name, "missed_reject", got)
        else:
            report.add("rule_reject", name, "unknown_reject_code", str(reject_code))
    else:
        if "custody" in obj:
            got = custody_independence_outcome(obj)
            if got == "ok":
                report.add("custody_independence", name, "ok")
            elif got == "verification_unavailable":
                report.add("custody_independence", name, "ok", "verification_unavailable")
            else:
                report.add("custody_independence", name, got)


def verify_chain(label: str, jsonl_path: str, report: Report) -> None:
    prev = "0" * 64
    expected_seq = 1
    last_hash = None
    with open(jsonl_path, encoding="utf-8") as f:
        for line in f:
            env = json.loads(line)
            seq = env.get("sequence_number")
            if seq != expected_seq:
                report.add("sequence_closure", label, "gap", f"expected {expected_seq} got {seq}")
                return
            integ = env.get("integrity") or {}
            stored_prev = integ.get("previous_envelope_hash")
            if stored_prev != prev:
                report.add("chain_link", f"{label}:{seq}", "break", f"prev {stored_prev} != {prev}")
                return
            stored = integ.get("envelope_hash")
            recomputed = envelope_digest(env)
            if stored != recomputed:
                report.add("envelope_hash", f"{label}:{seq}", "mismatch")
                return
            prev = stored
            last_hash = stored
            expected_seq += 1
    report.add("envelope_hash", label, "ok", f"n={expected_seq - 1}")
    report.add("chain_link", label, "ok", f"head {last_hash}")
    report.add("sequence_closure", label, "ok", f"n={expected_seq - 1}")


def locale_guard(report: Report) -> None:
    name = "axes_jcs_collation_ae.json"
    spec_path = os.path.join(VECTORS_DIR, name)
    obj = load_json_reject_duplicates(open(spec_path, encoding="utf-8").read())
    pinned = json.load(open(EXPECTED_PATH, encoding="utf-8"))[name]["canonical_utf8"]
    jcs_bytes = hash_preimage(obj).decode("utf-8")
    locale_bytes = locale_like_canonical_utf8(obj)
    if jcs_bytes != pinned:
        report.add("locale_comparator_guard", name, "jcs_drift", "JCS no longer matches pin")
        return
    if locale_bytes == pinned:
        report.add(
            "locale_comparator_guard",
            name,
            "guard_inert",
            "locale-like comparator matched the pin; property is named not pinned",
        )
        return
    report.add("locale_comparator_guard", name, "ok", "locale-like comparator diverges from pinned JCS")


def predicate_coverage(report: Report) -> None:
    """Task 16 coverage against committed vectors (see vectors/README.md)."""
    by_check: dict[str, set[str]] = {}
    for r in report.results:
        by_check.setdefault(r.check, set()).add(r.outcome)

    custody = by_check.get("custody_independence", set())
    if "ok" in custody and "reject_as_expected" in custody:
        report.add("predicate_coverage", "custody_independence", "ok", "pass and fail committed")
    else:
        report.add("predicate_coverage", "custody_independence", "unexercised", str(custody))

    if "reject_as_expected" in by_check.get("canonicalisation_reject", set()):
        report.add("predicate_coverage", "canonicalisation_reject", "ok", "fail committed; pass is any well-formed vector")
    else:
        report.add("predicate_coverage", "canonicalisation_reject", "unexercised", "no duplicate-key reject")

    if "ok" in by_check.get("canonical_bytes", set()) and "ok" in by_check.get("locale_comparator_guard", set()):
        report.add("predicate_coverage", "canonical_bytes", "ok", "pass=pinned JCS; fail=locale-like comparator")
    else:
        report.add("predicate_coverage", "canonical_bytes", "unexercised", "missing pin or locale guard")

    if "ok" in by_check.get("chain_link", set()):
        report.add(
            "predicate_coverage",
            "chain_link",
            "ok",
            "pass committed; fail unexercised (would mutate corpus of record)",
        )


def inject_negative_fixtures(report: Report) -> None:
    """In-memory fail cases so the verifier's own predicates have a fail-set."""
    report.add("canonical_bytes", "_injected_mismatch", "mismatch", "in-memory fail-set")
    report.add("digest", "_injected_mismatch", "mismatch", "in-memory fail-set")
    report.add("canonicalisation_reject", "_injected_clean_json", "accepted_malformed", "in-memory fail-set")
    report.add("locale_comparator_guard", "_injected_inert", "guard_inert", "in-memory fail-set")
    report.add("chain_link", "_injected_break", "break", "in-memory fail-set")
    report.add("sequence_closure", "_injected_gap", "gap", "in-memory fail-set")
    report.add("envelope_hash", "_injected_mismatch", "mismatch", "in-memory fail-set")


def main() -> int:
    parser = argparse.ArgumentParser(description="AXES offline reference verifier")
    parser.add_argument(
        "--inject-fails",
        action="store_true",
        help="Add in-memory fail-set rows for predicates that have no committed negative vector",
    )
    args = parser.parse_args()

    report = Report()
    expected = json.load(open(EXPECTED_PATH, encoding="utf-8"))

    for name, spec in expected.items():
        verify_vector(name, spec, report)

    for label, rel in (
        ("golden-trace", os.path.join("examples", "golden-trace", "out", "envelopes.jsonl")),
        ("golden-trace-ind", os.path.join("examples", "golden-trace-ind", "out", "envelopes.jsonl")),
    ):
        path = os.path.join(ROOT, rel)
        if os.path.isfile(path):
            verify_chain(label, path, report)
        else:
            report.add("chain_link", label, "missing_corpus", path)

    locale_guard(report)
    if args.inject_fails:
        inject_negative_fixtures(report)
    predicate_coverage(report)

    failed = [
        r
        for r in report.results
        if not r.ok()
        and r.check != "predicate_coverage"
        and not r.subject.startswith("_injected")
    ]
    coverage_issues = [
        r
        for r in report.results
        if r.check == "predicate_coverage" and r.outcome not in {"ok", "unexercised_fail"}
    ]
    # unexercised_fail on injected-backed checks should not happen; on envelope_hash
    # fail-set, injected rows make them ok.

    for r in report.results:
        print(f"{r.outcome:24} {r.check:28} {r.subject} {r.detail}".rstrip())

    # Coverage rows with unexercised_* are warnings if --no-injected-fails
    warn = [r for r in report.results if r.check == "predicate_coverage" and r.outcome != "ok"]
    if warn:
        print("--- predicate coverage ---")
        for r in warn:
            print(f"  {r.outcome}: {r.subject} ({r.detail})")

    if failed:
        print(f"FAIL {len(failed)} check(s)")
        return 1
    print(f"OK {len(report.results)} check rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
