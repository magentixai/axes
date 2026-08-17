#!/usr/bin/env python3
"""
WO16 Task 6: pin RFC 8785 properties that ASCII-only vectors cannot catch.

Adds four new vector files and four new expected.json keys.
Does not rewrite existing pinned canonical_utf8 / sha256 values.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.axes_canonical import hash_preimage, sha256_hex, write_json_utf8_lf

VECTORS_DIR = os.path.join(ROOT, "vectors")
EXPECTED_PATH = os.path.join(VECTORS_DIR, "expected.json")

# U+1D11E MUSICAL SYMBOL G CLEF (supplementary; UTF-16 D834 DD1E)
# U+FF21 FULLWIDTH LATIN CAPITAL LETTER A (BMP; UTF-16 FF21)
# UTF-16 code-unit order: G-clef (D834…) before fullwidth-A (FF21).
# Unicode code-point order is the reverse. Pinning this catches a code-point sorter.
SURROGATE_KEY = "\U0001d11e"
FULLWIDTH_A = "\uff21"

# NFC e-acute (U+00E9) vs NFD e + combining acute. RFC 8785 §3.1: no normalisation.
NFC_EACUTE = "\u00e9"
NFD_EACUTE = "e\u0301"

DIGEST_HEX = "d68e2599796b1d327c753640b501014fe4af491f62c7285c4eec0a4c41aad580"


def property_vectors() -> dict[str, dict]:
    return {
        "axes_jcs_surrogate_pair_key.json": {
            "se_version": "0.1-draft",
            "event_kind": "jcs_property_check",
            "note": "UTF-16 code-unit member sort (RFC 8785 §3.2.3), not code-point order",
            FULLWIDTH_A: "fullwidth_a",
            SURROGATE_KEY: "g_clef_supplementary",
            "z": "ascii_z",
        },
        "axes_jcs_nfc_nfd_pair.json": {
            "se_version": "0.1-draft",
            "event_kind": "jcs_property_check",
            "note": "NFC and NFD of the same visual key are distinct members (RFC 8785 §3.1)",
            NFC_EACUTE: "composed",
            NFD_EACUTE: "decomposed",
        },
        "axes_jcs_collation_ae.json": {
            "se_version": "0.1-draft",
            "event_kind": "jcs_property_check",
            "note": "ä sorts after z under UTF-16 code units; a locale comparator typically does not",
            "z": "ascii_z",
            "ä": "a_umlaut",
        },
        "axes_jcs_digest_encoding.json": {
            "se_version": "0.1-draft",
            "event_kind": "jcs_property_check",
            "note": "bare lowercase hex and an algorithm-prefixed form are different strings",
            "digest_bare": DIGEST_HEX,
            "digest_prefixed": "sha256:" + DIGEST_HEX,
        },
        "axes_identity_unparseable_hex.json": {
            "se_version": "0.1-draft",
            "event_kind": "jcs_property_check",
            "note": "unparseable identity syntax is verification_unavailable, never a false-negative reject",
            "custody": {
                "capture_relationship": "independent_third_party",
                "executor_id": "agent:caldera/ap-pilot",
                "deployer_id": "org:caldera-robotics",
                "capturer_id": "0xEXAMPLECAFE",
                "signing_trust_ref": {
                    "ref": "custody-ref:external/notary-001",
                    "signer_id": "key:trustline/notary-2026q2",
                },
            },
        },
    }


def main() -> None:
    with open(EXPECTED_PATH, encoding="utf-8") as f:
        expected = json.load(f)
    original_keys = list(expected.keys())
    original_snapshot = {k: expected[k] for k in original_keys}

    for name, obj in property_vectors().items():
        path = os.path.join(VECTORS_DIR, name)
        write_json_utf8_lf(path, obj)
        cb = hash_preimage(obj)
        expected[name] = {
            "canonical_utf8": cb.decode("utf-8"),
            "sha256": sha256_hex(cb),
        }

    for k in original_keys:
        if expected[k] != original_snapshot[k]:
            raise SystemExit(f"refusing to write: existing pin changed for {k}")

    write_json_utf8_lf(EXPECTED_PATH, expected)
    print(f"Added {len(property_vectors())} JCS property vectors. Existing pins unchanged.")


if __name__ == "__main__":
    main()
