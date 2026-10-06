#!/usr/bin/env python3
"""axes:x402_correlation@1 (WO20 section 4, A1.2): the correlation core and correlation_hash.

Each party computes the core on its own, from bytes both parties hold identically at the moment
the payer authorizes: the served PaymentRequired and the signed PaymentPayload. Settlement, the
receipt and anything one-sided are excluded. Standard library plus `jcs` (RFC 8785).

  python tools/x402/x402_correlation.py PAYMENT_REQUIRED.json PAYMENT_PAYLOAD.json [--core]

Scope: the `exact` scheme with EIP-3009 on EVM networks. Other schemes need their own recipe
version; this one refuses them rather than claiming coverage it has not defined.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone

try:
    import jcs
except ImportError:  # pragma: no cover
    sys.exit("the 'jcs' package is required (pip install jcs)")

RECIPE_REF = "axes:x402_correlation@1"
LANE_TYPES = ("identity", "tax", "evidence")
HEX32 = 64
# ASCII only: str.isdigit() and a bare length check accept non-ASCII digits and non-hex characters.
ADDRESS_PATTERN = re.compile(r"0x[0-9a-fA-F]{40}")
NONCE_PATTERN = re.compile(r"0x[0-9a-fA-F]{64}")
DECIMAL_PATTERN = re.compile(r"0|[1-9][0-9]*")


class CorrelationError(ValueError):
    """Raised with a verification condition code (docs/06 2.13)."""

    def __init__(self, condition, detail):
        super().__init__("%s: %s" % (condition, detail))
        self.condition = condition
        self.detail = detail


def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    return jcs.canonicalize(obj)


def address(value, what):
    if not isinstance(value, str) or not ADDRESS_PATTERN.fullmatch(value):
        raise CorrelationError("value_not_accepted", "%s is not a 20-byte hex address" % what)
    return value.lower()


def atomic(value, what):
    if not isinstance(value, str) or not DECIMAL_PATTERN.fullmatch(value):
        raise CorrelationError("value_not_accepted", "%s must be a decimal string of atomic units" % what)
    return value


def salt(value, what):
    if not isinstance(value, str) or len(value) != HEX32 or any(c not in "0123456789abcdef" for c in value):
        raise CorrelationError("binding_salt_absent", "%s missing or not 32 bytes of lowercase hex" % what)
    return value


def payment_legs(accepted):
    """Multi-recipient first (A1.2): the primary payTo receives the remainder after splits (#3221)."""
    total = int(atomic(accepted.get("amount"), "accepted.amount"))
    splits = (accepted.get("extra") or {}).get("splits") or []
    legs, carved = [], 0
    for i, s in enumerate(splits):
        if not isinstance(s, dict) or "payTo" not in s or "amount" not in s:
            raise CorrelationError("value_not_accepted", "malformed split %d; a leg is never skipped" % i)
        v = int(atomic(s["amount"], "splits[%d].amount" % i))
        carved += v
        legs.append({"pay_to_id": address(s["payTo"], "splits[%d].payTo" % i), "leg_amount_value": str(v)})
    remainder = total - carved
    if remainder <= 0:
        raise CorrelationError("value_not_accepted", "splits leave no positive remainder for payTo")
    legs.append({"pay_to_id": address(accepted.get("payTo"), "accepted.payTo"), "leg_amount_value": str(remainder)})
    ids = [l["pay_to_id"] for l in legs]
    if len(set(ids)) != len(ids):
        raise CorrelationError("value_not_accepted", "duplicate recipient across legs")
    return sorted(legs, key=lambda l: l["pay_to_id"]), str(total)


def expires_at(valid_before):
    if not isinstance(valid_before, str) or not DECIMAL_PATTERN.fullmatch(valid_before):
        raise CorrelationError("value_not_accepted", "authorization.validBefore must be decimal unix seconds")
    return datetime.fromtimestamp(int(valid_before), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def lanes(payment_required, payment_payload):
    offered = payment_required.get("extensions") or {}
    echoed = payment_payload.get("extensions") or {}
    out = []
    for lane in LANE_TYPES:
        if lane not in offered:
            continue
        if lane not in echoed:
            raise CorrelationError("field_absent_undeclared", "advertised lane %s not echoed" % lane)
        server_info = offered[lane].get("info") or {}
        client_info = echoed[lane].get("info") or {}
        for k, v in server_info.items():
            if client_info.get(k) != v:
                raise CorrelationError("value_not_accepted", "echoed %s info changed or deleted key %s" % (lane, k))
        chosen = client_info.get("chosen")
        if chosen is None:
            raise CorrelationError("field_absent_undeclared", "lane %s echoed without chosen" % lane)
        if chosen != "declined" and chosen not in (server_info.get("offered") or []):
            raise CorrelationError("value_not_accepted", "lane %s chose a profile that was not offered" % lane)
        if chosen == "declined" and server_info.get("required"):
            raise CorrelationError("value_not_accepted", "lane %s is required and cannot be declined" % lane)
        echoed_info = {k: v for k, v in client_info.items() if k != "correlationDigest"}
        out.append({"lane_type": lane, "chosen_profile_ref": chosen, "lane_information_hash": sha256_hex(canonical(echoed_info))})
    return out


def build_core(payment_required: dict, payment_payload: dict, offer: dict | None = None) -> dict:
    accepted = payment_payload.get("accepted") or {}
    if accepted.get("scheme") != "exact" or not str(accepted.get("network", "")).startswith("eip155:"):
        raise CorrelationError("check_type_unsupported", "recipe @1 covers the exact scheme on EVM networks only")
    if accepted not in (payment_required.get("accepts") or []):
        raise CorrelationError("value_not_accepted", "accepted requirements were not among those offered")
    auth = (payment_payload.get("payload") or {}).get("authorization") or {}
    raw_nonce = auth.get("nonce")
    if not isinstance(raw_nonce, str) or not NONCE_PATTERN.fullmatch(raw_nonce):
        raise CorrelationError("value_not_accepted", "authorization.nonce must be 32 bytes of hex")
    nonce = raw_nonce.lower()
    if (accepted.get("extra") or {}).get("splits"):
        # One EIP-3009 authorization moves value to one address. Splits (#3221) need a scheme recipe that can
        # verify every leg; a leg this recipe cannot check is refused, never skipped.
        raise CorrelationError("check_type_unsupported", "splits are not verifiable under the EIP-3009 exact recipe @1")
    if address(auth.get("to"), "authorization.to") != address(accepted.get("payTo"), "accepted.payTo"):
        raise CorrelationError("value_not_accepted", "authorization.to differs from payTo")
    legs, total = payment_legs(accepted)
    if atomic(auth.get("value"), "authorization.value") != total:
        raise CorrelationError("value_not_accepted", "authorization.value differs from accepted.amount")
    evidence_info = ((payment_payload.get("extensions") or {}).get("evidence") or {}).get("info") or {}
    core = {
        "x402_version": payment_payload.get("x402Version"),
        "payment_scheme": accepted["scheme"],
        "payment_flow_type": (accepted.get("extra") or {}).get("paymentFlow", "authorization"),
        "network_id": accepted["network"],
        "asset_id": address(accepted.get("asset"), "accepted.asset"),
        "total_amount_value": total,
        "payment_legs": legs,
        "payer_id": address(auth.get("from"), "authorization.from"),
        "resource_ref": (payment_required.get("resource") or {}).get("url"),
        "authorization_nonce_id": nonce,
        "authorization_expires_at": expires_at(auth.get("validBefore")),
        "server_salt_text": salt(evidence_info.get("correlationSalt"), "evidence correlationSalt"),
        "client_salt_text": salt(evidence_info.get("clientSalt"), "evidence clientSalt"),
        "lanes": lanes(payment_required, payment_payload),
        "hash_algorithm": "SHA-256",
    }
    pid = ((payment_payload.get("extensions") or {}).get("payment-identifier") or {}).get("info", {}).get("id")
    if pid:
        core["payment_identifier_id"] = pid
    if offer is not None:
        core["offer_hash"] = sha256_hex(canonical(offer))
    if not core["resource_ref"]:
        raise CorrelationError("field_absent_undeclared", "PaymentRequired.resource.url absent")
    return core


def correlation_hash(core: dict) -> str:
    return sha256_hex(canonical(core))


# ---------- receipt and party comparison (WO20 sections 5 and 6) ----------

def check_receipt(receipt: dict, core_hash: str) -> dict:
    """Option 2: a version 2 receipt carries correlationDigest; it must equal the recomputed hash."""
    if receipt.get("version") != 2 or "correlationDigest" not in receipt:
        return {"verification_state": "not_evaluated", "verification_subject_type": "operator",
                "verification_condition_code": "field_absent_declared", "observed_note": "receipt carries no correlationDigest (option 1 or none)"}
    if receipt["correlationDigest"] != core_hash:
        return {"verification_state": "contradicted", "verification_reason_code": "divergence", "verification_subject_type": "artifact",
                "verification_condition_code": "correlation_hash_mismatch", "observed_note": "receipt correlationDigest differs from the recomputed core"}
    return {"verification_state": "verified", "verification_subject_type": "artifact", "observed_note": "receipt binds this core"}


def compare_parties(own_hash: str, counterparty_hash: str) -> dict:
    """Divergence is evidence, not an error: record it, never pick a side (WO20 section 6)."""
    if own_hash == counterparty_hash:
        return {"verification_state": "verified", "verification_subject_type": "artifact", "observed_note": "both parties computed the same core"}
    return {"verification_state": "indeterminate", "verification_reason_code": "divergence", "verification_subject_type": "artifact",
            "verification_condition_code": "correlation_divergence", "observed_note": "parties computed different cores"}


# ---------- nonce derivation (A1.3, A1.4) ----------

def mandate_binding(mandate_digest: str, payment_id: str) -> str:
    """x402#3220 section 7: B = SHA-256(tag || UTF8(mandateDigest '\\n' paymentId)); mandateDigest keeps 'sha256:'."""
    if not mandate_digest.startswith("sha256:"):
        raise CorrelationError("value_not_accepted", "mandateDigest keeps its sha256: prefix in the preimage")
    return "0x" + sha256_hex(b"x402-mandate-binding/1\n" + (mandate_digest + "\n" + payment_id).encode("utf-8"))


def nonce_derivation_type(nonce: str, mandate_digest: str | None = None, payment_id: str | None = None) -> str:
    """Classify how the nonce was made. Anything not provably derived is `unbindable`, never a failure."""
    if mandate_digest and payment_id and mandate_binding(mandate_digest, payment_id) == nonce.lower():
        return "x402_mandate_binding"
    return "unbindable"


def main(argv=None):
    ap = argparse.ArgumentParser(description="axes:x402_correlation@1")
    ap.add_argument("payment_required")
    ap.add_argument("payment_payload")
    ap.add_argument("--offer")
    ap.add_argument("--core", action="store_true", help="print the core as well as the hash")
    a = ap.parse_args(argv)
    pr = json.load(open(a.payment_required, encoding="utf-8"))
    pp = json.load(open(a.payment_payload, encoding="utf-8"))
    offer = json.load(open(a.offer, encoding="utf-8")) if a.offer else None
    try:
        core = build_core(pr, pp, offer)
    except CorrelationError as exc:
        print(json.dumps({"verification_state": "indeterminate", "verification_condition_code": exc.condition,
                          "observed_note": exc.detail}))
        return 1
    out = {"correlation_recipe_ref": RECIPE_REF, "correlation_hash": correlation_hash(core),
           "correlation_hash_algorithm": "SHA-256"}
    if a.core:
        out["correlation_core"] = core
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
