#!/usr/bin/env python3
"""Self-test: a guard that reads every anchor as verified must fail the suite (exit 1).

A False from a verifier you have never seen return True is not evidence (D-019); the
converse holds too. Swaps in a permissive guard and checks axes_verify.py notices.
"""
from __future__ import annotations

import contextlib
import io
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from tools import axes_anchoring_guard as guard  # noqa: E402
from tools import axes_verify  # noqa: E402


def main() -> int:
    real = guard.evaluate
    guard.evaluate = lambda record, release, ev=None: (
        [{"verification_state": "verified", "verification_reason_code": None, "verification_condition_code": None,
          "verification_subject_type": "artifact", "anchor_id": None}]
        if record.get("anchoring") else [])
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            code = axes_verify.main(["--skip-coverage"])
    finally:
        guard.evaluate = real
    if code != 1:
        print(f"FAIL: permissive anchoring guard gave exit {code}, expected 1")
        return 1
    with contextlib.redirect_stdout(io.StringIO()):
        code = axes_verify.main([])
    if code != 0:
        print(f"FAIL: real anchoring guard gave exit {code}, expected 0")
        return 1
    print("OK: permissive anchoring guard fails the suite; real guard passes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
