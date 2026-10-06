#!/usr/bin/env python3
"""Cross-check axes:x402_correlation@1 against the external x402-payment-fingerprint/0 vectors (tsc#4).

Each vector holds one copy of a payment. It is wrapped into a version 2 PaymentRequired and PaymentPayload with a
fixed resource and fixed salts and no lanes, so only the payment members differ. Two passes:
  as held     version 1 copies must be refused (check_type_unsupported), never given a hash;
  normalised  version 1 network aliases mapped to CAIP-2 with the fingerprint's own table; the two recipes must
              partition the vectors identically (same, different, refused).
Exit status 0 when both passes agree.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import x402_correlation as xc  # noqa: E402

SOURCE = os.path.join(HERE, "external", "x402-payment-fingerprint-0", "vectors.json")
# Copied from the fingerprint recipe's NETWORK_ALIASES, only the aliases its vectors use.
NETWORK_ALIASES = {"base": "eip155:8453", "base-sepolia": "eip155:84532"}
SALTS = {"correlationSalt": "11" * 32, "clientSalt": "22" * 32}


def wrap(held, normalise):
    accepted = dict(held.get("accepted") or {k: held[k] for k in ("scheme", "network", "asset") if k in held})
    accepted.setdefault("scheme", "exact")
    authorization = held["payload"]["authorization"]
    if normalise:
        accepted["network"] = NETWORK_ALIASES.get(accepted.get("network"), accepted.get("network"))
    accepted.update({"payTo": authorization.get("to"), "amount": authorization.get("value"), "maxTimeoutSeconds": 60})
    version = 2 if normalise else held.get("x402Version", 1)
    payment_required = {"x402Version": version, "resource": {"url": "https://example.test/resource"}, "accepts": [accepted]}
    payment_payload = {"x402Version": version, "accepted": accepted, "payload": held["payload"],
                       "extensions": {"evidence": {"info": dict(SALTS)}}}
    return payment_required, payment_payload


def ours(held, normalise):
    try:
        return "ok", xc.correlation_hash(xc.build_core(*wrap(held, normalise)))
    except xc.CorrelationError as exc:
        return "refused", exc.condition


def main():
    vectors = json.load(open(SOURCE, encoding="utf-8"))["vectors"]
    failures = []

    for v in vectors:
        if v["held"].get("x402Version", 1) == 1:
            outcome, detail = ours(v["held"], False)
            if (outcome, detail) != ("refused", "check_type_unsupported"):
                failures.append("as held: %s gave %s %s, expected refusal" % (v["name"], outcome, detail))

    theirs_to_ours = {}
    ours_to_theirs = {}
    for v in vectors:
        expected = v["expect"]
        outcome, detail = ours(v["held"], True)
        if expected["outcome"] == "malformed":
            if outcome != "refused":
                failures.append("normalised: %s is malformed upstream but got a hash" % v["name"])
            print("  %-28s malformed %-34s refused %s" % (v["name"], expected["condition"], detail))
            continue
        if outcome != "ok":
            failures.append("normalised: %s has a fingerprint but was refused (%s)" % (v["name"], detail))
            continue
        fingerprint = expected["fingerprint"]
        if theirs_to_ours.setdefault(fingerprint, detail) != detail:
            failures.append("normalised: one fingerprint, two correlation hashes (%s)" % v["name"])
        if ours_to_theirs.setdefault(detail, fingerprint) != fingerprint:
            failures.append("normalised: two fingerprints, one correlation hash (%s)" % v["name"])
        print("  %-28s %s  %s" % (v["name"], fingerprint[7:23], detail[:16]))

    for f in failures:
        print("FAIL " + f)
    if failures:
        return 1
    print("OK both recipes partition the %d vectors identically; version 1 copies are refused as held" % len(vectors))
    return 0


if __name__ == "__main__":
    sys.exit(main())
