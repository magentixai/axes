#!/usr/bin/env python3
"""AXES envelope signature profile axes:envelope_signature_ed25519@1 (docs/23, D-060).

Signing input (domain-separated, D-050): the RFC 8785 bytes of
  {"domain_tag": "axes:envelope_signature@1", "envelope_hash": <recomputed envelope hash>,
   "hash_algorithm": <integrity.hash_algorithm>, "se_version": <se_version>}
Signature: Ed25519 (RFC 8032) over those bytes, base64url without padding, in
integrity.envelope_signature. The envelope declares the profile in
integrity.envelope_signature_profile_ref and its key in integrity.signing_key_id, both inside the
hash scope. Public keys come from a signing key set (signing_keys[]).

  python tools/axes_signature.py verify <envelopes.jsonl> <signing-keys.json>
"""
from __future__ import annotations

import base64
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools import axes_ed25519 as ed  # noqa: E402
from tools.axes_canonical import DomainError, UnsupportedAlgorithm, canonical_bytes, envelope_digest, strict_loads  # noqa: E402

PROFILE_REF = "axes:envelope_signature_ed25519@1"
DOMAIN_TAG = "axes:envelope_signature@1"


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def b64u_decode(text: str) -> bytes:
    if not isinstance(text, str) or "=" in text:
        raise ValueError("not unpadded base64url")
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def signing_input(env: dict) -> bytes:
    integ = env.get("integrity") or {}
    return canonical_bytes({"domain_tag": DOMAIN_TAG, "envelope_hash": envelope_digest(env),
                            "hash_algorithm": integ.get("hash_algorithm"), "se_version": env.get("se_version")})


def sign_envelope(env: dict, secret: bytes) -> dict:
    """Sets envelope_hash and envelope_signature on an envelope whose other members, including
    integrity.signing_key_id and envelope_signature_profile_ref, are final."""
    integ = env["integrity"]
    integ.pop("envelope_hash", None)
    integ.pop("envelope_signature", None)
    integ["envelope_hash"] = envelope_digest(env)
    integ["envelope_signature"] = b64u(ed.sign(secret, signing_input(env)))
    return env


def _result(state, reason=None, condition=None, subject="artifact", note=""):
    r = {"verification_state": state, "verification_subject_type": subject, "observed_note": note}
    if reason:
        r["verification_reason_code"] = reason
    if condition:
        r["verification_condition_code"] = condition
    return r


def _key(keyset: dict, key_id: str):
    for k in keyset.get("signing_keys") or []:
        if k.get("signing_key_id") == key_id:
            return k
    return None


def verify_envelope(env: dict, keyset: dict) -> dict:
    """Four-state result for one envelope's signature (docs/23 section 4)."""
    integ = env.get("integrity") or {}
    if integ.get("envelope_signature_basis_status") != "demonstrated":
        return _result("indeterminate", "absence", "basis_not_demonstrated", "operator",
                       "envelope_signature_basis_status %s" % integ.get("envelope_signature_basis_status", "absent"))
    profile = integ.get("envelope_signature_profile_ref")
    if profile != PROFILE_REF:
        return _result("not_evaluated", "instrument_failure", "signature_profile_unsupported", "verifier",
                       "profile %s" % profile)
    key = _key(keyset, integ.get("signing_key_id"))
    if key is None or key.get("public_key_algorithm") != "Ed25519":
        return _result("indeterminate", "absence", "signing_key_unresolved", "operator",
                       "no Ed25519 key %s in the signing key set" % integ.get("signing_key_id"))
    try:
        message = signing_input(env)
        public = b64u_decode(key.get("public_key_value", ""))
        signature = b64u_decode(integ.get("envelope_signature", ""))
    except UnsupportedAlgorithm as exc:
        return _result("not_evaluated", "instrument_failure", "hash_algorithm_unsupported", "verifier", str(exc))
    except DomainError as exc:
        return _result("contradicted", "divergence", "value_outside_domain", "artifact", str(exc))
    except ValueError as exc:
        return _result("contradicted", "divergence", "envelope_signature_invalid", "artifact", "encoding: %s" % exc)
    if not ed.verify(public, message, signature):
        return _result("contradicted", "divergence", "envelope_signature_invalid", "artifact",
                       "signature does not verify under %s" % integ.get("signing_key_id"))
    return _result("verified", note="signature verifies under %s" % integ.get("signing_key_id"))


def main(argv):
    if len(argv) != 3 or argv[0] != "verify":
        print(__doc__)
        return 2
    keyset = strict_loads(open(argv[2], encoding="utf-8").read())
    worst = "verified"
    order = {"verified": 0, "not_evaluated": 1, "indeterminate": 2, "contradicted": 3}
    with open(argv[1], encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            env = strict_loads(line)
            r = verify_envelope(env, keyset)
            if order[r["verification_state"]] > order[worst]:
                worst = r["verification_state"]
            print("%-14s %-30s %s" % (r["verification_state"], r.get("verification_condition_code", ""), env.get("envelope_id")))
    print("overall:", worst)
    return {"verified": 0, "contradicted": 1}.get(worst, 3)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
