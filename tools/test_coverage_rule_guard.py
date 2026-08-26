#!/usr/bin/env python3
"""
Prove TLC-008 coverage enforcement can fail (WO17 Deliverable A3).

Builds a temporary predicates manifest missing a fail fixture / required
observation and asserts tools/axes_verify.py exits 2 (suite broken), not 1.
Does not mutate the committed vectors/predicates.json.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VERIFY = os.path.join(ROOT, "tools", "axes_verify.py")


def main() -> int:
    broken = {
        "schema": "axes.predicate-coverage/1",
        "predicates": [
            {
                "id": "deliberately_broken_predicate",
                "description": "Self-test: missing required observation must yield exit 2",
                "pass_fixtures": ["axes_gt_0001_genesis.json"],
                "fail_fixtures": [],
                "required_observations": [
                    {
                        "check": "canonical_bytes",
                        "outcome": "this_outcome_never_occurs",
                    }
                ],
            }
        ],
    }
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "predicates.json")
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(broken, f, indent=2)
            f.write("\n")
        proc = subprocess.run(
            [sys.executable, VERIFY, "--predicates", path],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 2:
            print("FAIL: expected exit 2 for broken coverage manifest")
            print(f"  got exit {proc.returncode}")
            print(proc.stdout[-2000:] if proc.stdout else "")
            print(proc.stderr[-1000:] if proc.stderr else "")
            return 1
        if "SUITE BROKEN" not in proc.stdout and "SUITE BROKEN" not in proc.stderr:
            print("FAIL: exit 2 without SUITE BROKEN marker")
            print(proc.stdout[-2000:])
            return 1
        print("OK: broken coverage manifest yields exit 2 (suite broken)")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
