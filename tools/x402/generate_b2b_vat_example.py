#!/usr/bin/env python3
"""Generate the WO20 B2B VAT worked example (examples/x402-b2b-vat/). Development tool.

Needs `eth-account` (pip) for the EIP-3009 and envelope signatures. Every key is a deterministic
TEST key derived from a public seed: never fund these addresses. Real cryptography, labelled test
material. Settlement is not executed from this environment; the settled artifact is marked
`simulated` with the reason, and the x402.magentix.ai test bed replaces it with a real Base Sepolia
settlement.

  python tools/x402/generate_b2b_vat_example.py phase1     # messages, correlation, party records 1..n-1
  python tools/x402/generate_b2b_vat_example.py phase2     # append each party's attestation envelope
                                                           # from anchors/x402-b2b-vat-*/anchoring.json
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys

from eth_account import Account
from eth_account.messages import encode_defunct, encode_typed_data

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import x402_correlation as xc  # noqa: E402

OUT = os.path.join(ROOT, "examples", "x402-b2b-vat")
NETWORK = "eip155:84532"   # Base Sepolia
CHAIN_ID = 84532
USDC_BASE_SEPOLIA = "0x036CbD53842c5426634e7929541eC2318f3dCF7e"   # confirm against the facilitator's /supported
RESOURCE = "https://x402.magentix.ai/api/agent/reports"
T0 = 1791158400            # 2026-10-05T00:00:00Z


def key(label):
    return Account.from_key(hashlib.sha256(("axes-x402-b2b-vat/%s/test-key-never-fund" % label).encode()).digest())


def hexseed(label):
    return hashlib.sha256(("axes-x402-b2b-vat/%s" % label).encode()).hexdigest()


BUYER = key("buyer-payer")
SELLER = key("seller-payto")
BUYER_EMITTER = key("buyer-emitter")
SELLER_EMITTER = key("seller-emitter")
FACILITATOR = "0x" + hexseed("facilitator-placeholder")[:40]


def iso(t):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def dump(rel, obj):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")


def requirements():
    return {"scheme": "exact", "network": NETWORK, "amount": "10000", "asset": USDC_BASE_SEPOLIA,
            "payTo": SELLER.address, "maxTimeoutSeconds": 120, "extra": {"name": "USDC", "version": "2"}}


def payment_required():
    return {
        "x402Version": 2,
        "resource": {"url": RESOURCE, "description": "ARBITR evidence report (test bed)", "mimeType": "application/json"},
        "accepts": [requirements()],
        "extensions": {
            "identity": {"info": {"offered": ["axes:x402_disclosure_business_buyer@1", "axes:x402_disclosure_anonymous@1"],
                                  "required": False, "floor": None,
                                  "supplier": {"legalName": "Exemple SAS", "vatId": "FR00000000000",
                                               "identityRef": "did:web:exemple.example"}},
                         "schema": {"$ref": "https://github.com/magentixai/axes/schema/x402-wire/identity-1.json"}},
            "tax": {"info": {"offered": ["x402-tax:eu-vat@rev6"], "required": False,
                             "quote": {"determinationStatus": "DETERMINED", "taxResultRef": "sha256:" + hexseed("tax-result")}},
                    "schema": {"$ref": "https://github.com/magentixai/axes/schema/x402-wire/tax-1.json"}},
            "evidence": {"info": {"offered": ["axes:x402_correlation@1"], "required": False,
                                  "anchorServices": ["https://freetsa.org/tsr", "bip122:000000000019d6689c085ae165831e93"],
                                  "correlationSalt": hexseed("server-salt")},
                         "schema": {"$ref": "https://github.com/magentixai/axes/schema/x402-wire/evidence-1.json"}},
        },
    }


def sign_authorization(nonce):
    auth = {"from": BUYER.address, "to": SELLER.address, "value": "10000", "validAfter": str(T0 - 60),
            "validBefore": str(T0 + 600), "nonce": nonce}
    typed = {
        "types": {"EIP712Domain": [{"name": "name", "type": "string"}, {"name": "version", "type": "string"},
                                   {"name": "chainId", "type": "uint256"}, {"name": "verifyingContract", "type": "address"}],
                  "TransferWithAuthorization": [{"name": "from", "type": "address"}, {"name": "to", "type": "address"},
                                                {"name": "value", "type": "uint256"}, {"name": "validAfter", "type": "uint256"},
                                                {"name": "validBefore", "type": "uint256"}, {"name": "nonce", "type": "bytes32"}]},
        "primaryType": "TransferWithAuthorization",
        "domain": {"name": "USDC", "version": "2", "chainId": CHAIN_ID, "verifyingContract": USDC_BASE_SEPOLIA},
        "message": {"from": auth["from"], "to": auth["to"], "value": int(auth["value"]),
                    "validAfter": int(auth["validAfter"]), "validBefore": int(auth["validBefore"]),
                    "nonce": bytes.fromhex(nonce[2:])},
    }
    sig = Account.sign_message(encode_typed_data(full_message=typed), BUYER.key).signature.hex()
    return auth, "0x" + sig.removeprefix("0x")


def payment_payload(pr, nonce, chosen_identity="axes:x402_disclosure_business_buyer@1"):
    auth, sig = sign_authorization(nonce)
    ext = copy.deepcopy(pr["extensions"])
    ext["identity"]["info"].update({"chosen": chosen_identity,
                                    "presentation": {"legalName": "Buyer GmbH", "vatId": "DE000000000",
                                                     "principalAttributionRef": "sha256:" + hexseed("principal")}})
    ext["tax"]["info"].update({"chosen": "x402-tax:eu-vat@rev6",
                               "presentation": {"buyerDeclarationRef": "sha256:" + hexseed("buyer-declaration")}})
    ext["evidence"]["info"].update({"chosen": "axes:x402_correlation@1", "clientSalt": hexseed("client-salt")})
    return {"x402Version": 2, "resource": pr["resource"], "accepted": requirements(),
            "payload": {"signature": sig, "authorization": auth}, "extensions": ext}


# ---------- AXES party records (gt-v2.1 key names, docs/20) ----------

def chain_and_sign(envs, emitter, label):
    sys.path.insert(0, ROOT)
    import jcs
    prev = "0" * 64
    for i, e in enumerate(envs, 1):
        e["sequence_number"] = i
        e["envelope_id"] = "env:x402-b2b-vat/%s/%04d" % (label, i)
        integ = e["integrity"]
        integ["previous_envelope_hash"] = prev
        integ.pop("envelope_hash", None)
        integ.pop("envelope_signature", None)
        h = hashlib.sha256(jcs.canonicalize(e)).hexdigest()
        integ["envelope_hash"] = h
        integ["envelope_signature"] = "0x" + Account.sign_message(encode_defunct(hexstr=h), emitter.key).signature.hex().removeprefix("0x")
        prev = h
    return envs


def envelope(label, emitter, kind, t, body):
    e = {"se_version": "0.1-draft", "implementation_profile_ref": "example:x402_party_emitter@1", "event_kind": kind,
         "occurred_at": iso(t), "emitted_at": iso(t), "recorded_at": iso(t), "timestamp_source": "ntp:example",
         "organization_id": "org:%s" % label, "tenant_id": "tenant:%s-test" % label,
         "environment_type": "test", "execution_mode": "autonomous",
         "evidence_quality": {"evidence_origin": "runtime", "assertion_basis": "observed",
                              "corroboration_state": "internally_corroborated"},
         "integrity": {"hash_algorithm": "SHA-256", "canonicalization_version": "RFC8785-JCS",
                       "signing_key_id": "key:x402-b2b-vat/%s-emitter-test" % label,
                       "signing_address_id": "eip155:%d:%s" % (CHAIN_ID, emitter.address.lower()),
                       "envelope_signature_basis_status": "demonstrated"}}
    e.update(copy.deepcopy(body))
    return e


def party_records(core_hash, core, pr, pp):
    committed = {"asset_id": core["asset_id"], "total_amount_value": core["total_amount_value"], "payment_legs": core["payment_legs"]}
    settled = copy.deepcopy(committed)
    x402 = {"correlation_recipe_ref": xc.RECIPE_REF, "correlation_hash": core_hash, "correlation_hash_algorithm": "SHA-256",
            "chosen_profile_refs": sorted(l["chosen_profile_ref"] for l in core["lanes"])}
    supplier = {"supplier_identity_ref": "did:web:exemple.example", "supplier_legal_name": "Exemple SAS", "supplier_vat_id": "FR00000000000"}
    tax = {"tax_profile_ref": "x402-tax:eu-vat@rev6", "tax_result_ref": "sha256:" + hexseed("tax-result"),
           "determination_status": "determined", "tax_treatment_type": "reverse_charge",
           "principal_attribution_status": "verified"}
    settlement = {"settlement_transaction_ref": "tx:0x" + hexseed("settlement-tx-simulated"),
                  "settlement_submitter_id": "%s:%s" % (NETWORK, FACILITATOR.lower()),
                  "settlement_role": None, "settlement_purpose_type": "conformance",
                  "nonce_derivation_type": "unbindable",
                  "committed_terms": committed, "settled_artifact": settled,
                  "settled_artifact_basis_status": "simulated",
                  "settled_artifact_note": "No testnet access from the generating environment; the x402.magentix.ai test bed replaces this with a decoded Base Sepolia settlement."}
    out = {}
    for label, emitter, role, t0 in (("buyer", BUYER_EMITTER, "origin", T0), ("seller", SELLER_EMITTER, "origin", T0 + 1)):
        s = dict(settlement, settlement_role=role)
        rows = [
            envelope(label, emitter, "context_retrieved", t0, {"x402": dict(x402, x402_stage_type="offer"), "supplier": supplier}),
            envelope(label, emitter, "policy_check_performed", t0 + 2, {"x402": dict(x402, x402_stage_type="tax"), "tax": tax}),
            envelope(label, emitter, "commit_attempted", t0 + 4, {"x402": dict(x402, x402_stage_type="authorization"),
                                                                  "authority": {"delegator_id": "person:%s/finance-lead" % label,
                                                                                "policy_ref": "policy:%s/procurement" % label}}),
            envelope(label, emitter, "commit_succeeded", t0 + 9, {"x402": dict(x402, x402_stage_type="settlement"), "settlement": s,
                                                                  "supplier": supplier, "tax": tax}),
            envelope(label, emitter, "result_observed", t0 + 10, {"x402": dict(x402, x402_stage_type="receipt"),
                                                                  "receipt": {"receipt_version": "2", "receipt_ref": "x402-wire/receipt_v2.json"}}),
        ]
        if label == "seller":
            for r in rows:
                if "x402" in r:
                    r["buyer"] = {"buyer_legal_name": "Buyer GmbH", "buyer_vat_id": "DE000000000",
                                  "buyer_identity_disclosure_ref": "axes:x402_disclosure_business_buyer@1"}
        out[label] = (rows, emitter)
    return out


def phase1():
    pr = payment_required()
    nonce = "0x" + hexseed("random-nonce")
    pp = payment_payload(pr, nonce)
    core = xc.build_core(pr, pp)
    ch = xc.correlation_hash(core)
    dump("x402-wire/payment_required.json", pr)
    dump("x402-wire/payment_payload.json", pp)
    dump("x402-wire/receipt_v1.json", {"version": 1, "network": NETWORK, "resourceUrl": RESOURCE, "payer": BUYER.address,
                                      "issuedAt": T0 + 10, "transaction": "0x" + hexseed("settlement-tx-simulated"),
                                      "signature": "STUBBED: offer-and-receipt signing format to be aligned at x402@751590a"})
    dump("x402-wire/receipt_v2.json", {"version": 2, "network": NETWORK, "resourceUrl": RESOURCE, "payer": BUYER.address,
                                      "issuedAt": T0 + 10, "transaction": "0x" + hexseed("settlement-tx-simulated"),
                                      "correlationDigest": ch,
                                      "signature": "STUBBED: proposed version 2 member; signing format per offer-and-receipt"})
    dump("correlation/correlation.json", {"correlation_recipe_ref": xc.RECIPE_REF, "correlation_hash": ch,
                                          "correlation_hash_algorithm": "SHA-256", "correlation_core": core})
    # the same payment under an x402#3220 mandate: the nonce is the binding B
    mandate_digest = "sha256:445fed871d7c43d2b775e68124103c77646fc0f096fb42c9ea3d9f00c960ca05"
    b = xc.mandate_binding(mandate_digest, "pay-001")
    ppm = payment_payload(pr, b)
    corem = xc.build_core(pr, ppm)
    dump("x402-wire/payment_payload_mandate_bound.json", ppm)
    dump("correlation/correlation_mandate_bound.json", {
        "correlation_recipe_ref": xc.RECIPE_REF, "correlation_hash": xc.correlation_hash(corem), "correlation_hash_algorithm": "SHA-256",
        "mandate_hash": mandate_digest.split(":", 1)[1], "mandate_hash_algorithm": "SHA-256", "payment_identifier_id": "pay-001",
        "nonce_derivation_type": xc.nonce_derivation_type(b, mandate_digest, "pay-001"), "correlation_core": corem})
    for label, (rows, emitter) in party_records(ch, core, pr, pp).items():
        rows = chain_and_sign(rows, emitter, label)
        path = os.path.join(OUT, label, "envelopes.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        manifest = {"bundle_manifest_note": "%s record of the WO20 B2B VAT example, envelopes 1..%d" % (label, len(rows)),
                    "hash_algorithm": "SHA-256", "envelope_count": len(rows),
                    "chain_head_hash": rows[-1]["integrity"]["envelope_hash"], "correlation_hash": ch}
        adir = os.path.join(ROOT, "anchors", "x402-b2b-vat-%s" % label)
        os.makedirs(adir, exist_ok=True)
        with open(os.path.join(adir, "bundle_manifest.json"), "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(manifest, indent=2) + "\n")
    print("phase1: correlation_hash", ch)


def phase2():
    for label, emitter in (("buyer", BUYER_EMITTER), ("seller", SELLER_EMITTER)):
        path = os.path.join(OUT, label, "envelopes.jsonl")
        rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
        rows = [r for r in rows if r["event_kind"] != "attestation_recorded"]
        anchoring = json.load(open(os.path.join(ROOT, "anchors", "x402-b2b-vat-%s" % label, "anchoring.json"), encoding="utf-8"))
        last = rows[-1]
        att = envelope(label, emitter, "attestation_recorded", T0 + 60,
                       {"x402": dict(last["x402"], x402_stage_type="anchoring"), "anchoring": anchoring,
                        "anchoring_subject_ref": "anchors/x402-b2b-vat-%s/bundle_manifest.json" % label})
        rows = chain_and_sign(rows + [att], emitter, label)
        # envelopes 1..n-1 are unchanged, so the anchored bundle manifest still matches them
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("phase2: attestation envelopes appended")


if __name__ == "__main__":
    {"phase1": phase1, "phase2": phase2}[sys.argv[1]]()
