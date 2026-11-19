#!/usr/bin/env python3
"""Generate the envelope signature vectors (vectors/signatures/), deterministic.

The signing key is RFC 8032 section 7.1 TEST 1. Its secret is published in the RFC, so these
vectors prove the construction, never anyone's identity. Two-sided: every condition the signature
check returns has a case that returns it and a case that does not.

  python tools/generate_signature_vectors.py           # write
  python tools/generate_signature_vectors.py --check   # exit 1 if a vector would change or a case fails
"""
from __future__ import annotations

import copy
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)
from tools import axes_ed25519 as ed  # noqa: E402
from tools import axes_signature as sig  # noqa: E402
from tools.axes_canonical import envelope_digest  # noqa: E402

OUT = os.path.join(ROOT, "vectors", "signatures")
SECRET = bytes.fromhex(ed.RFC8032_TESTS[0][0])
KEY_ID = "key:example/rfc8032-test-1"

BASE = {
    "se_version": "0.1-draft", "implementation_profile_ref": "example:test_emitter@1",
    "event_kind": "commit_succeeded", "envelope_id": "env:sigtest/0001",
    "occurred_at": "2026-11-20T10:00:00.000Z", "emitted_at": "2026-11-20T10:00:00.100Z",
    "recorded_at": "2026-11-20T10:00:00.200Z", "organization_id": "org:example", "tenant_id": "tenant:example",
    "sequence_number": 1,
    "integrity": {"hash_algorithm": "SHA-256", "canonicalization_version": "RFC8785-JCS",
                  "previous_envelope_hash": "0" * 64, "signing_key_id": KEY_ID,
                  "envelope_signature_profile_ref": sig.PROFILE_REF,
                  "envelope_signature_basis_status": "demonstrated"},
}


def signed(**integrity_changes):
    e = copy.deepcopy(BASE)
    e["integrity"].update(integrity_changes)
    return sig.sign_envelope(e, SECRET)


def cases():
    out = []
    out.append(("signed_valid", signed(), ("verified", None, None, "artifact"), "signature verifies"))

    e = signed()
    e["event_kind"] = "commit_failed"  # content changed after signing; the hash is recomputed, the signature is not
    e["integrity"]["envelope_hash"] = envelope_digest({k: v for k, v in e.items()})
    out.append(("content_changed_after_signing", e, ("contradicted", "divergence", "envelope_signature_invalid", "artifact"),
                "a forger can recompute the hash but not the signature"))

    e = signed()
    s = bytearray(sig.b64u_decode(e["integrity"]["envelope_signature"]))
    s[0] ^= 1
    e["integrity"]["envelope_signature"] = sig.b64u(bytes(s))
    out.append(("signature_bytes_changed", e, ("contradicted", "divergence", "envelope_signature_invalid", "artifact"),
                "one bit of the signature changed"))

    e = signed()
    e["integrity"]["envelope_signature"] = "SIG-STUB(not base64url)"
    out.append(("signature_not_base64url", e, ("contradicted", "divergence", "envelope_signature_invalid", "artifact"),
                "demonstrated basis with a value that is not a signature"))

    out.append(("signing_key_unresolved", signed(signing_key_id="key:example/not-in-key-set"),
                ("indeterminate", "absence", "signing_key_unresolved", "operator"), "key not in the signing key set"))

    out.append(("profile_unsupported", signed(envelope_signature_profile_ref="example:rsa_pss@1"),
                ("not_evaluated", "instrument_failure", "signature_profile_unsupported", "verifier"),
                "a profile this verifier does not implement"))

    e = copy.deepcopy(BASE)
    e["integrity"]["envelope_signature_basis_status"] = "stubbed"
    e["integrity"]["envelope_hash"] = envelope_digest(e)
    e["integrity"]["envelope_signature"] = "SIG-STUB(%s)" % e["integrity"]["envelope_hash"][:16]
    out.append(("stubbed_as_in_gt_v2_1", e, ("indeterminate", "absence", "basis_not_demonstrated", "operator"),
                "the gt-v2.1 corpus marks its stub signatures stubbed"))
    return out


def render(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def main(argv):
    keyset = {"signing_key_set_id": "keyset:example/rfc8032-test",
              "signing_keys": [{"signing_key_id": KEY_ID, "public_key_algorithm": "Ed25519",
                                "public_key_value": sig.b64u(ed.public_key(SECRET)),
                                "key_source_note": "RFC 8032 section 7.1 TEST 1; the secret is public. Test only."}]}
    files = {"signing-keys.json": render(keyset)}
    expected = {}
    for name, env, want, note in cases():
        got = sig.verify_envelope(env, keyset)
        state, reason, cond, subject = want
        if (got["verification_state"], got.get("verification_reason_code"), got.get("verification_condition_code"),
                got["verification_subject_type"]) != want:
            print("FAIL %s: got %s" % (name, got))
            return 1
        files["envelopes/%s.json" % name] = render(env)
        exp = {"verification_state": state, "verification_subject_type": subject, "origin_note": note}
        if reason:
            exp["verification_reason_code"] = reason
        if cond:
            exp["verification_condition_code"] = cond
        expected[name + ".json"] = exp
    files["expected.json"] = render({"signature_profile_ref": sig.PROFILE_REF, "signing_key_set_ref": "signing-keys.json",
                                     "vectors": expected})
    if "--check" in argv:
        for rel, text in files.items():
            path = os.path.join(OUT, rel)
            if not os.path.exists(path) or open(path, encoding="utf-8").read() != text:
                print("FAIL vectors/signatures/%s is stale: run tools/generate_signature_vectors.py" % rel)
                return 1
        print("OK %d signature vectors current and two-sided" % len(expected))
        return 0
    os.makedirs(os.path.join(OUT, "envelopes"), exist_ok=True)
    for rel, text in files.items():
        with open(os.path.join(OUT, rel), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print("wrote %d signature vectors" % len(expected))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
