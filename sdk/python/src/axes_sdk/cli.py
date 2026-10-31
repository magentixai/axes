"""Command line: axes-sdk verify-stream | verify-bundle | evaluate | hash.

Exit codes: 0 every requested check verified; 1 a contradiction; 2 a check indeterminate or not evaluated;
3 the command could not run (bad arguments, unreadable or non-strict input, limits, unsupported option).
JSON output carries every finding; the exit code is only a summary.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from . import __version__
from .bundle import verify_bundle
from .canonical import HashPolicy, envelope_preimage, hash_envelope
from .errors import AxesError
from .evaluation import EvaluationContext, evaluate
from .integrity import verify_stream
from .jsonio import load_subject, parse_json, read_bytes
from .profiles import bundled_profiles, load_profile_set
from .results import State

EXIT = {State.VERIFIED: 0, State.CONTRADICTED: 1, State.INDETERMINATE: 2, State.NOT_EVALUATED: 2}


def _report_exit(report) -> int:
    if any(f.state is State.CONTRADICTED for f in report.findings):
        return 1
    return 0 if report.all_requested_checks_verified else 2


def _print_report(report, as_json: bool) -> None:
    if as_json:
        print(report.to_json())
        return
    print("%s: %s (%d envelopes%s)" % (report.kind, report.overall_state.value, report.envelope_count,
                                       ", %d files" % report.file_count if report.file_count else ""))
    if report.chain_head:
        print("chain head %s" % report.chain_head)
    for f in report.findings:
        print("  %-13s %-14s %-28s %s %s" % (f.state.value, f.check, f.condition or "", f.ref or "", f.note))
    for line in report.limitations:
        print("note: " + line)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="axes-sdk", description="Offline AXES evidence verification and evaluation")
    ap.add_argument("--version", action="version", version="axes-sdk " + __version__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("verify-stream", help="recompute hashes, links and sequence of an envelope stream")
    s.add_argument("path")
    s.add_argument("--release", default="gt-v2.1")
    s.add_argument("--expected-chain-head")
    s.add_argument("--window", action="store_true", help="the subject is part of a stream, not all of it")
    s.add_argument("--json", action="store_true")
    b = sub.add_parser("verify-bundle", help="verify an unpacked bundle directory (manifest, files, stream)")
    b.add_argument("path")
    b.add_argument("--release", default="gt-v2.1")
    b.add_argument("--expected-manifest-hash")
    b.add_argument("--expected-chain-head")
    b.add_argument("--json", action="store_true")
    e = sub.add_parser("evaluate", help="apply a requirement profile to an envelope stream")
    e.add_argument("path")
    e.add_argument("--profile", required=True, help="id@version, for example axes:gt_fin_internal_audit@1")
    e.add_argument("--profiles-dir", help="directory of profiles (default: the profiles bundled with the SDK)")
    e.add_argument("--aliases", help="key-aliases file for --profiles-dir")
    e.add_argument("--release", help="release the subject was produced under, for example gt-v2.1")
    e.add_argument("--evaluated-at", default="1970-01-01T00:00:00.000Z")
    e.add_argument("--pins", help="JSON file mapping every profile in the closure to its SHA-256")
    e.add_argument("--out", help="write the evaluation record here instead of standard output")
    h = sub.add_parser("hash", help="print one envelope's hash (and optionally its preimage)")
    h.add_argument("path", help="a file holding one envelope as JSON")
    h.add_argument("--release", default="gt-v2.1")
    h.add_argument("--preimage", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as exc:
        return 3 if exc.code else 0
    try:
        policy = HashPolicy(release=a.release) if a.cmd != "evaluate" else None
        if a.cmd == "verify-stream":
            report = verify_stream(load_subject(a.path), policy=policy, expected_chain_head=a.expected_chain_head,
                                   window=a.window)
            _print_report(report, a.json)
            return _report_exit(report)
        if a.cmd == "verify-bundle":
            report = verify_bundle(a.path, policy=policy, expected_manifest_hash=a.expected_manifest_hash,
                                   expected_chain_head=a.expected_chain_head)
            _print_report(report, a.json)
            return _report_exit(report)
        if a.cmd == "evaluate":
            profiles = load_profile_set(a.profiles_dir, a.aliases) if a.profiles_dir else bundled_profiles()
            pins = parse_json(read_bytes(a.pins)) if a.pins else None
            result = evaluate(load_subject(a.path), a.profile, profiles,
                              EvaluationContext(release=a.release, evaluated_at=a.evaluated_at, pins=pins))
            text = result.to_json() + "\n"
            if a.out:
                with open(a.out, "w", encoding="utf-8", newline="\n") as f:
                    f.write(text)
            else:
                sys.stdout.write(text)
            return EXIT[result.overall_verification_state]
        if a.cmd == "hash":
            env = parse_json(read_bytes(a.path))
            print(hash_envelope(env, policy))
            if a.preimage:
                sys.stdout.write(envelope_preimage(env, policy).decode("utf-8") + "\n")
            return 0
    except (AxesError, OSError, ValueError) as exc:
        print("axes-sdk: %s: %s" % (exc.__class__.__name__, exc), file=sys.stderr)
        return 3
    return 3


if __name__ == "__main__":
    sys.exit(main())
