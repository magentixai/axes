#!/usr/bin/env python3
"""Two-sided self-test for axes:x402_correlation@1: every published vector reproduces, plus receipt and party checks."""
from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import x402_correlation as xc  # noqa: E402

FAILS = []


def check(cond, msg):
    print(("ok   " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def main():
    doc = json.load(open(os.path.join(HERE, "vectors", "expected.json"), encoding="utf-8"))
    for name, v in doc["vectors"].items():
        d = os.path.join(HERE, "vectors", *v["wire_dir_ref"].split("/"))
        pr = json.load(open(os.path.join(d, "payment_required.json"), encoding="utf-8"))
        pp = json.load(open(os.path.join(d, "payment_payload.json"), encoding="utf-8"))
        exp = v["expected_outcome"]
        try:
            got = {"correlation_hash": xc.correlation_hash(xc.build_core(pr, pp))}
            ok = got["correlation_hash"] == exp.get("correlation_hash")
        except xc.CorrelationError as exc:
            got = {"verification_condition_code": exc.condition}
            ok = exp.get("verification_condition_code") == exc.condition
        check(ok, "%-28s %s" % (name, got))
    for name, v in doc["nonce_derivation_vectors"].items():
        got = xc.nonce_derivation_type(v["authorization_nonce_id"], "sha256:" + v["mandate_hash"], v["payment_identifier_id"])
        check(got == v["expected_nonce_derivation_type"], "nonce %-22s %s" % (name, got))
    base = doc["baseline_correlation_hash"]
    ex = os.path.join(ROOT, "examples", "x402-b2b-vat", "x402-wire")
    r2 = json.load(open(os.path.join(ex, "receipt_v2.json"), encoding="utf-8"))
    check(xc.check_receipt(r2, base)["verification_state"] == "verified", "receipt v2 binds the published core")
    bad = copy.deepcopy(r2)
    bad["correlationDigest"] = "0" * 64
    check(xc.check_receipt(bad, base).get("verification_condition_code") == "correlation_hash_mismatch", "tampered receipt detected")
    r1 = json.load(open(os.path.join(ex, "receipt_v1.json"), encoding="utf-8"))
    check(xc.check_receipt(r1, base)["verification_state"] == "not_evaluated", "version 1 receipt: no binding, never a pass")
    check(xc.compare_parties(base, "f" * 64).get("verification_condition_code") == "correlation_divergence", "divergent party cores reported, no side picked")
    print("FAILED: %d" % len(FAILS) if FAILS else "OK x402 correlation self-test")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
