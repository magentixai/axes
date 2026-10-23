#!/usr/bin/env python3
"""Two-sided self-test for the AnchorRegistry profile (axes:anchor_registry_bytes32@1). No network.

The fixture is a real Base mainnet block (48936665) as a JSON-RPC node returned it: the
transaction giskard09 used to anchor an action_ref in AnchorRegistry, and a plain transfer from
the same block. Every failing case is a copy of the real bundle with one thing changed.

Exit 0 when every case returns its expected state and condition.
"""
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anchor_common as ac  # noqa: E402
import evm  # noqa: E402
import verify_anchor as va  # noqa: E402

FIXTURE = os.path.join(HERE, "fixtures", "anchor-registry-base-48936665")
COMMITMENT = "d0f0a32e5290e0e71efc9265d86fe517db80f1c209ddff5106b9f69ba3c181db"
TX = "0xf00a5317e47d4f4d581eb16bf08b64dde45944706c615299c334f8082562f184"
ENTRY = {
    "anchor_id": "anch:anchor-registry-8453",
    "anchoring_method": "distributed_ledger",
    "anchor_profile_ref": ac.PROFILE_ANCHOR_REGISTRY,
    "basis_status": "demonstrated",
    "anchor_commitment_hash": COMMITMENT,
    "anchor_commitment_hash_algorithm": "SHA-256",
    "anchored_at": "2026-07-21T19:37:57.000Z",
    "anchor_service_id": "eip155:8453:" + ac.ANCHOR_REGISTRY_CONTRACT,
    "anchor_record_ref": "tx:" + TX,
    "anchor_operator_id": None,
    "anchor_proof_ref": "proofs/distributed_ledger/" + ac.PROOF_MANIFEST,
    "anchor_verification_procedure_ref": "docs/anchoring-profiles.md#axesanchor_registry_bytes321",
}
FAILS = []


def run(name, expect_state, expect_condition=None, which="anchor", entry_edit=None, file_edit=None, drop=None):
    tmp = tempfile.mkdtemp()
    try:
        pdir = os.path.join(tmp, "proofs", "distributed_ledger")
        shutil.copytree(os.path.join(FIXTURE, which), pdir)
        if file_edit:
            name_, fn = file_edit
            path = os.path.join(pdir, name_)
            obj = ac.read_json(path)
            fn(obj)
            ac.write_json(path, obj)
        names = [n for n in ("evm-rpc/header.json", "evm-rpc/receipt.json", "receipt_proof.json") if n != drop]
        if drop:
            os.remove(os.path.join(pdir, drop))
        entry = copy.deepcopy(ENTRY)
        entry["anchor_proof_hash"] = ac.write_proof_manifest(pdir, names, "test bundle")
        if entry_edit:
            entry_edit(entry)
        ac.write_json(os.path.join(tmp, ac.ANCHORING_FILE), {
            "anchored_subject_type": "envelope", "anchored_subject_hash": COMMITMENT,
            "anchored_subject_hash_algorithm": "SHA-256", "anchors": [entry]})
        r = va.verify_block(tmp)[-1]
    finally:
        shutil.rmtree(tmp)
    ok = r["verification_state"] == expect_state and r["verification_condition_code"] == expect_condition
    print("%s %-46s -> %s/%s" % ("ok  " if ok else "FAIL", name, r["verification_state"], r["verification_condition_code"]))
    if not ok:
        FAILS.append(name)
        print("     " + r["observed_note"])


def main():
    run("real anchor verifies", "verified")
    run("header timestamp altered", "contradicted", "anchor_commitment_mismatch",
        file_edit=("evm-rpc/header.json", lambda h: h.update(timestamp=hex(int(h["timestamp"], 16) + 1))))
    run("receipt log topic altered", "contradicted", "anchor_commitment_mismatch",
        file_edit=("evm-rpc/receipt.json", lambda r: r["logs"][0]["topics"].__setitem__(1, "0x" + "00" * 32)))
    run("proof for another transaction index", "contradicted", "anchor_commitment_mismatch",
        file_edit=("evm-rpc/receipt.json", lambda r: r.update(transactionIndex=hex(int(r["transactionIndex"], 16) + 1))))
    run("proof node dropped", "contradicted", "anchor_commitment_mismatch",
        file_edit=("receipt_proof.json", lambda p: p["proof_nodes"].pop()))
    run("commitment is not the anchored ref", "contradicted", "anchor_commitment_mismatch",
        entry_edit=lambda e: e.update(anchor_commitment_hash="11" * 32))
    run("anchored_at differs from block time", "contradicted", "anchor_commitment_mismatch",
        entry_edit=lambda e: e.update(anchored_at="2026-07-21T19:37:58.000Z"))
    run("anchor_record_ref names another tx", "contradicted", "anchor_commitment_mismatch",
        entry_edit=lambda e: e.update(anchor_record_ref="tx:0x" + "ab" * 32))
    run("service id names a lookalike contract", "contradicted", "anchor_noncanonical_contract",
        entry_edit=lambda e: e.update(anchor_service_id="eip155:8453:0x49feca52bc634a9ab773226d16619dec547794ab"))
    run("plain transfer in the same block", "contradicted", "anchor_not_a_commitment", which="plain",
        entry_edit=lambda e: e.update(anchor_record_ref="tx:" + ac.read_json(os.path.join(FIXTURE, "plain", "evm-rpc", "receipt.json"))["transactionHash"]))
    run("bundle without the inclusion proof", "indeterminate", "anchor_proof_absent", drop="receipt_proof.json")
    run("simulated entry never verifies", "indeterminate", "basis_not_demonstrated",
        entry_edit=lambda e: e.update(basis_status="simulated"))
    run("unknown distributed_ledger profile", "not_evaluated", "anchor_method_unverifiable",
        entry_edit=lambda e: e.update(anchor_profile_ref="example:other_registry@1"))

    # The primitives against the whole recorded block are covered by the fixture's own consistency.
    header = ac.read_json(os.path.join(FIXTURE, "anchor", "evm-rpc", "header.json"))
    if evm.header_hash(header) != header["hash"]:
        FAILS.append("fixture header hash")
    if evm.keccak256(b"Anchored(bytes32,address,uint256)").hex() != ac.ANCHOR_REGISTRY_TOPIC[2:] or \
            evm.keccak256(b"anchor(bytes32)")[:4].hex() != ac.ANCHOR_REGISTRY_SELECTOR:
        FAILS.append("event topic or selector constant")
    print("FAILED: %s" % ", ".join(FAILS) if FAILS else "OK AnchorRegistry profile self-test")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
