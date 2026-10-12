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
    print("FAILED: %s" % FAILS if FAILS else "OK evaluator guards")
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
