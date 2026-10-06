#!/usr/bin/env python3
"""Generate two-sided vectors for axes:x402_correlation@1 (WO20 section 9.3, A1.8). Deterministic.

Each case is a PaymentRequired and PaymentPayload pair (x402 wire spelling, under x402-wire/) and the
expected outcome: a correlation_hash, or a verification condition. Cases are derived from the B2B VAT
example messages by one named change each.
"""
from __future__ import annotations

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import x402_correlation as xc  # noqa: E402

SRC = os.path.join(ROOT, "examples", "x402-b2b-vat", "x402-wire")
OUT = os.path.join(HERE, "vectors")
PROV = {"author_name": "AXES maintainers (Magentix AI)", "authored_on": "2026-10-04"}


def load(name):
    return json.load(open(os.path.join(SRC, name), encoding="utf-8"))


def both(fn):
    def apply(pr, pp):
        fn(pr, pp)
        return pr, pp
    return apply


def set_accepted(key, value):
    def f(pr, pp):
        pp["accepted"][key] = value
        pr["accepts"][0][key] = value
    return f


CASES = [
    ("baseline", None, "B2B VAT example as published"),
    ("address_checksum_case", lambda pr, pp: (pp["payload"]["authorization"].__setitem__("from", pp["payload"]["authorization"]["from"].upper().replace("0X", "0x"))), "same hash: addresses are normalized to lowercase"),
    ("payment_identifier_null", lambda pr, pp: pp["extensions"].__setitem__("payment-identifier", {"info": {"id": None}}), "same hash: an optional member that is null is omitted, never encoded as null"),
    ("amount_changed", lambda pr, pp: (set_accepted("amount", "20000")(pr, pp), pp["payload"]["authorization"].__setitem__("value", "20000")), "different hash"),
    ("nonce_changed", lambda pr, pp: pp["payload"]["authorization"].__setitem__("nonce", "0x" + "ab" * 32), "different hash"),
    ("lane_choice_changed", lambda pr, pp: pp["extensions"]["identity"]["info"].__setitem__("chosen", "axes:x402_disclosure_anonymous@1"), "different hash"),
    ("lane_information_changed", lambda pr, pp: pp["extensions"]["tax"]["info"]["presentation"].__setitem__("buyerDeclarationRef", "sha256:" + "0" * 64), "different hash"),
    ("lookalike_asset_contract", lambda pr, pp: set_accepted("asset", "0x036cbd53842c5426634e7929541ec2318f3dcf7f")(pr, pp), "different hash: the asset is the canonical contract, not a name"),
    ("server_information_deleted", lambda pr, pp: pp["extensions"]["identity"]["info"].pop("supplier"), "refused: a client must not delete echoed server information"),
    ("choice_not_offered", lambda pr, pp: pp["extensions"]["tax"]["info"].__setitem__("chosen", "x402-tax:other@1"), "refused: a choice must be one of the offered profiles"),
    ("required_lane_declined", lambda pr, pp: (pr["extensions"]["identity"]["info"].__setitem__("required", True), pp["extensions"]["identity"]["info"].__setitem__("required", True), pp["extensions"]["identity"]["info"].__setitem__("chosen", "declined")), "refused: a required lane cannot be declined"),
    ("lane_not_echoed", lambda pr, pp: pp["extensions"].pop("tax"), "refused: an advertised lane must be echoed"),
    ("server_salt_absent", lambda pr, pp: (pr["extensions"]["evidence"]["info"].pop("correlationSalt"), pp["extensions"]["evidence"]["info"].pop("correlationSalt")), "indeterminate, never refused: a missing salt is a publication fact"),
    ("splits_present", lambda pr, pp: (pr["accepts"][0]["extra"].__setitem__("splits", [{"payTo": "0x" + "4" * 40, "amount": "1000"}]), pp["accepted"]["extra"].__setitem__("splits", [{"payTo": "0x" + "4" * 40, "amount": "1000"}])), "refused under the EIP-3009 exact recipe: a leg it cannot verify is never skipped"),
    ("payer_not_hex", lambda pr, pp: pp["payload"]["authorization"].__setitem__("from", "0x" + "zz" * 20), "refused: an address must be 20 bytes of ASCII hex"),
    ("amount_non_ascii_digit", lambda pr, pp: (set_accepted("amount", "1٣")(pr, pp), pp["payload"]["authorization"].__setitem__("value", "1٣")), "refused: amounts are ASCII decimal digits only"),
    ("nonce_not_hex", lambda pr, pp: pp["payload"]["authorization"].__setitem__("nonce", "0x" + "zz" * 32), "refused: the nonce must be 32 bytes of ASCII hex"),
    ("non_evm_network", lambda pr, pp: (set_accepted("network", "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp")(pr, pp)), "refused: recipe @1 covers the exact scheme on EVM networks only"),
]
EXPECT = {
    "address_checksum_case": "same", "payment_identifier_null": "same", "amount_changed": "different",
    "nonce_changed": "different", "lane_choice_changed": "different", "lane_information_changed": "different",
    "lookalike_asset_contract": "different",
}


def main():
    base_pr, base_pp = load("payment_required.json"), load("payment_payload.json")
    base_hash = xc.correlation_hash(xc.build_core(base_pr, base_pp))
    vectors = {}
    for name, change, note in CASES:
        pr, pp = copy.deepcopy(base_pr), copy.deepcopy(base_pp)
        if change:
            change(pr, pp)
        d = os.path.join(OUT, "x402-wire", name)
        os.makedirs(d, exist_ok=True)
        for fn, obj in (("payment_required.json", pr), ("payment_payload.json", pp)):
            with open(os.path.join(d, fn), "w", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(obj, indent=2) + "\n")
        try:
            h = xc.correlation_hash(xc.build_core(pr, pp))
            exp = {"correlation_hash": h}
            rel = EXPECT.get(name)
            if rel == "same":
                assert h == base_hash, name
            elif rel == "different":
                assert h != base_hash, name
            exp["baseline_relation_type"] = rel or "baseline"
        except xc.CorrelationError as exc:
            exp = {"verification_condition_code": exc.condition}
        vectors[name] = {"wire_dir_ref": "x402-wire/" + name, "expected_outcome": exp, "provenance": dict(PROV, origin_note=note)}
    # nonce derivation (A1.3, A1.4): x402#3220 section 7 pinned value
    b = xc.mandate_binding("sha256:445fed871d7c43d2b775e68124103c77646fc0f096fb42c9ea3d9f00c960ca05", "pay-001")
    assert b == "0x5aa71c23c84e6763bdb31a473f1981fd37ccf93945205b77eb84e0c271c1e74b", b
    derivations = {
        "mandate_bound": {"authorization_nonce_id": b, "mandate_hash": "445fed871d7c43d2b775e68124103c77646fc0f096fb42c9ea3d9f00c960ca05",
                          "payment_identifier_id": "pay-001", "expected_nonce_derivation_type": "x402_mandate_binding"},
        "random_nonce": {"authorization_nonce_id": base_pp["payload"]["authorization"]["nonce"],
                         "mandate_hash": "445fed871d7c43d2b775e68124103c77646fc0f096fb42c9ea3d9f00c960ca05",
                         "payment_identifier_id": "pay-001", "expected_nonce_derivation_type": "unbindable"},
    }
    doc = {"vector_format_ref": "axes:x402_correlation_vectors@1", "correlation_recipe_ref": xc.RECIPE_REF,
           "summary_note": "Two-sided vectors for the correlation core. Each case changes one thing in the B2B VAT example "
                           "messages. Inputs are x402 wire messages; expected outcomes use AXES key names.",
           "baseline_correlation_hash": base_hash, "vectors": vectors, "nonce_derivation_vectors": derivations}
    with open(os.path.join(OUT, "expected.json"), "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(doc, indent=2) + "\n")
    print("wrote %d correlation vectors; baseline %s" % (len(vectors), base_hash))


if __name__ == "__main__":
    main()
