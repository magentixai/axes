#!/usr/bin/env python3
"""
Emit AXES conformance vectors (canoncheck layout) from Golden Trace v2 envelopes.

Every canonical_utf8 and sha256 in expected.json is emitted by the canonicaliser.
Run from repository root after regenerating the golden trace:

  python tools/generate_conformance_vectors.py
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.axes_canonical import (
    CANONICALISATION_VERSION,
    USDC_ASSET,
    amount_from_decimal,
    hash_preimage,
    sha256_hex,
)

VECTORS_DIR = os.path.join(ROOT, "vectors")
GT_OUT = os.path.join(ROOT, "examples", "golden-trace", "out")

EXECUTOR_ID = "agent:caldera/ap-pilot"
DEPLOYER_ID = "org:caldera-robotics"
EXTERNAL_CAPTURER = "org:trustline-custody/eu-west"
EXTERNAL_SIGNER = "key:trustline/notary-2026q2"


def hash_input(envelope: dict) -> dict:
    env = json.loads(json.dumps(envelope))
    integ = env.setdefault("integrity", {})
    integ.pop("envelope_hash", None)
    integ.pop("signature", None)
    return env


def write_vector(name: str, envelope: dict) -> tuple[str, str]:
    os.makedirs(VECTORS_DIR, exist_ok=True)
    path = os.path.join(VECTORS_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(envelope, f, indent=2, ensure_ascii=False)
        f.write("\n")
    cb = hash_preimage(envelope)
    return cb.decode("utf-8"), sha256_hex(cb)


def custody_base(*, capturer_id: str, signer_id: str) -> dict:
    """Minimal commit_attempted envelope exercising the custody axis."""
    amt = amount_from_decimal("1000.00")
    return {
        "se_version": "0.1-draft",
        "profile_id": "se-profile:payments-emitter/0.1-draft",
        "event_kind": "commit_attempted",
        "occurred_at": "2026-06-09T09:02:00.000Z",
        "emitted_at": "2026-06-09T09:02:00.400Z",
        "recorded_at": "2026-06-09T09:02:00.900Z",
        "timestamp_source": "ntp:cluster-sync",
        "clock_sync_confidence": "high",
        "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
        "span_id": "span-custody-vector",
        "org_id": DEPLOYER_ID,
        "tenant_id": "tenant:caldera-prod",
        "environment_id": "env:prod-eu",
        "environment_type": "production",
        "execution_phase": "commit",
        "execution_mode": "autonomous",
        "actor": {"agent_id": EXECUTOR_ID, "agent_version": "2.4.1"},
        "authority": {
            "authority_context_id": "AD-7844",
            "delegation_receipt_id": "delrec:AD-7844/2026-04-02",
            "policy_ref": "policy:caldera/ap-payments",
            "policy_version": "3.2",
        },
        "emission": {
            "capture_layer": "runtime_sdk",
            "capture_status": "captured",
            "emission_fail_posture": "fail_closed",
        },
        "evidence_quality": {
            "evidence_origin": "runtime",
            "assertion_basis": "observed",
            "corroboration_state": "third_party_confirmed",
        },
        "custody": {
            "capture_relationship": "independent_third_party",
            "executor_id": EXECUTOR_ID,
            "deployer_id": DEPLOYER_ID,
            "capturer_id": capturer_id,
            "signing_trust_ref": {
                "ref": "custody-ref:external/notary-001",
                "signer_id": signer_id,
            },
        },
        "operation": {
            "operation": "submit_sepa_inst_credit_transfer",
            "commit_boundary_status": "commit_attempted",
            "commit_mechanism": "payment_initiation",
            "commit_impact_class": "money_movement",
            "monetary": {"amount": amt},
        },
        "integrity": {
            "hash_algorithm": "SHA-256",
            "canonicalisation_version": CANONICALISATION_VERSION,
            "previous_envelope_hash": "0" * 64,
            "signing_key_id": "key:caldera/se-emitter-2026q2",
            "signing_key_provenance_ref": "kms:caldera/provenance/se-emitter-2026q2",
        },
    }


def golden_trace_vectors(envelopes: list[dict]) -> dict:
    """Representative hash-input fixtures from the regenerated corpus."""
    picks = {
        "axes_gt_0001_genesis.json": 0,
        "axes_gt_0004_policy_check_amount.json": 3,
        "axes_gt_0013_policy_check_peak_util.json": 12,
        "axes_gt_0037_attestation_recorded.json": 36,
        "axes_gt_0073_reconciliation.json": 72,
    }
    out = {}
    for name, idx in picks.items():
        out[name] = hash_input(envelopes[idx])
    return out


def adversarial_vectors() -> dict:
    """Edge classes absent from the golden trace data."""
    base = custody_base(capturer_id=EXTERNAL_CAPTURER, signer_id=EXTERNAL_SIGNER)
    base["operation"]["beneficiary"] = "Bolt & Brass Supplies GmbH"
    unicode_vec = hash_input(base)

    large_amt = custody_base(capturer_id=EXTERNAL_CAPTURER, signer_id=EXTERNAL_SIGNER)
    large_amt["operation"]["monetary"]["amount"] = amount_from_decimal("1000000000000000000")
    large_vec = hash_input(large_amt)

    # USDC on Base: exercises decimals=6 / crypto namespaced asset path
    usdc = custody_base(capturer_id=EXTERNAL_CAPTURER, signer_id=EXTERNAL_SIGNER)
    usdc["operation"]["operation"] = "submit_usdc_transfer"
    usdc["operation"]["commit_mechanism"] = "token_transfer"
    usdc["operation"]["monetary"]["amount"] = amount_from_decimal(
        "4475.0", decimals=6, asset=USDC_ASSET
    )
    usdc_vec = hash_input(usdc)

    return {
        "axes_adv_unicode_beneficiary.json": unicode_vec,
        "axes_adv_large_amount_string.json": large_vec,
        "axes_adv_usdc_amount.json": usdc_vec,
    }


def duplicate_key_vector() -> dict:
    """Malformed input: duplicate object key (canonicalisation-layer reject)."""
    raw = (
        '{"amount":{"asset":"iso4217:EUR","decimals":2,"value":"100000"},'
        '"amount":{"asset":"iso4217:EUR","decimals":2,"value":"200000"}}'
    )
    path = os.path.join(VECTORS_DIR, "axes_reject_duplicate_key.json")
    with open(path, "w", encoding="utf-8") as f:
        f.write(raw + "\n")
    return {"axes_reject_duplicate_key.json": {"reject": True}}


def main() -> None:
    env_path = os.path.join(GT_OUT, "envelopes.jsonl")
    envelopes = [json.loads(line) for line in open(env_path, encoding="utf-8")]

    expected: dict = {}

    for name, env in golden_trace_vectors(envelopes).items():
        canon, digest = write_vector(name, env)
        expected[name] = {"canonical_utf8": canon, "sha256": digest}

    for name, env in adversarial_vectors().items():
        canon, digest = write_vector(name, env)
        expected[name] = {"canonical_utf8": canon, "sha256": digest}

    expected.update(duplicate_key_vector())

    reject_env = hash_input(
        custody_base(capturer_id=DEPLOYER_ID, signer_id=EXTERNAL_SIGNER)
    )
    canon, digest = write_vector("custody_deployer_captured_reject.json", reject_env)
    expected["custody_deployer_captured_reject.json"] = {
        "expect": "reject",
        "reject_code": "custody_independence_reject",
        "canonical_utf8": canon,
        "sha256": digest,
    }

    accept_env = hash_input(
        custody_base(capturer_id=EXTERNAL_CAPTURER, signer_id=EXTERNAL_SIGNER)
    )
    canon, digest = write_vector("custody_accept_independent_external.json", accept_env)
    expected["custody_accept_independent_external.json"] = {
        "canonical_utf8": canon,
        "sha256": digest,
    }

    with open(os.path.join(VECTORS_DIR, "expected.json"), "w", encoding="utf-8") as f:
        json.dump(expected, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote {len(expected)} vector expectations to {VECTORS_DIR}")


if __name__ == "__main__":
    main()
