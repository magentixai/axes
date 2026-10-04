#!/usr/bin/env python3
"""Verify AXES anchors offline, method by method (WO18 A5.3).

  python tools/anchoring/verify_anchor.py DIR [--subject FILE] [--json]

DIR holds anchoring.json (WO18 A2 block) and the proof files it points to. No network access.
Results use the draft-krausz-verification-state-03 vocabulary (WO19 D5): state, state_reason,
condition, subject, observed. A missing optional dependency is `not_evaluated` with reason
`instrument_failure`: never a pass and never a fault in the anchor.

Exit status: 0 if no anchor is `contradicted`; 1 otherwise; 2 if the input cannot be read.
"""
import argparse
import io
import json
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anchor_common as ac  # noqa: E402

DEMONSTRATED = "demonstrated"


def result(anchor_id, state, condition=None, reason=None, subject="artifact", observed=""):
    return {"anchor_id": anchor_id, "state": state, "state_reason": reason,
            "condition": condition, "subject": subject, "observed": observed}


def check_manifest(base, entry):
    """Returns (files dict, failure result or None)."""
    aid = entry["anchor_id"]
    ref = entry.get("anchor_proof_ref")
    if not ref:
        return None, result(aid, "indeterminate", "anchor_proof_absent", "absence", "operator", "no anchor_proof_ref")
    path = os.path.join(base, ref)
    if not os.path.isfile(path):
        return None, result(aid, "not_evaluated", "anchor_proof_unresolvable", None, "network", "proof manifest not found at " + ref)
    if ac.sha256_file(path) != entry.get("anchor_proof_hash"):
        return None, result(aid, "contradicted", "anchor_proof_hash_mismatch", None, "artifact", "manifest bytes differ from anchor_proof_hash")
    manifest = ac.read_json(path)
    pdir = os.path.dirname(path)
    for name, digest in manifest.get("files", {}).items():
        fp = os.path.join(pdir, name)
        if not os.path.isfile(fp):
            return None, result(aid, "not_evaluated", "anchor_proof_unresolvable", None, "network", "listed proof file missing: " + name)
        if ac.sha256_file(fp) != digest:
            return None, result(aid, "contradicted", "anchor_proof_hash_mismatch", None, "artifact", "proof file altered: " + name)
    return {n: os.path.join(pdir, n) for n in manifest.get("files", {})}, None


def bits_to_target(bits):
    exp = bits >> 24
    mant = bits & 0xFFFFFF
    return mant * (1 << (8 * (exp - 3)))


def verify_ots(entry, files, commitment):
    aid = entry["anchor_id"]
    try:
        from opentimestamps.core.serialize import StreamDeserializationContext
        from opentimestamps.core.timestamp import DetachedTimestampFile
        from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
    except ImportError:
        return result(aid, "not_evaluated", "anchor_method_unverifiable", "instrument_failure", "verifier",
                      "opentimestamps package not installed (tools/anchoring/requirements.txt)")
    import hashlib
    with open(files["subject.ots"], "rb") as f:
        dtf = DetachedTimestampFile.deserialize(StreamDeserializationContext(io.BytesIO(f.read())))
    if dtf.file_digest.hex() != commitment:
        return result(aid, "contradicted", "anchor_commitment_mismatch", None, "artifact", "proof commits to a different digest")
    btc = [(msg, att) for msg, att in dtf.timestamp.all_attestations() if isinstance(att, BitcoinBlockHeaderAttestation)]
    if not btc or not entry.get("anchored_at"):
        return result(aid, "indeterminate", "anchor_pending", "absence", "operator",
                      "calendar commitment only; no Bitcoin attestation yet (run produce.py upgrade)")
    for msg, att in btc:
        hname = "bitcoin-header-%d.hex" % att.height
        if hname not in files:
            return result(aid, "not_evaluated", "anchor_proof_unresolvable", None, "network", "archived header missing for block %d" % att.height)
        with open(files[hname]) as f:
            raw = bytes.fromhex(f.read().strip())
        if len(raw) != 80:
            return result(aid, "contradicted", "anchor_proof_hash_mismatch", None, "artifact", "header is not 80 bytes")
        if raw[36:68] != msg:
            return result(aid, "contradicted", "anchor_commitment_mismatch", None, "artifact",
                          "attested value is not the merkle root of block %d" % att.height)
        h = hashlib.sha256(hashlib.sha256(raw).digest()).digest()
        bits = int.from_bytes(raw[72:76], "little")
        if int.from_bytes(h, "little") > bits_to_target(bits):
            return result(aid, "contradicted", "anchor_commitment_mismatch", None, "artifact", "header fails proof of work")
        bhash = h[::-1].hex()
        t = int.from_bytes(raw[68:72], "little")
        if entry.get("anchor_record_ref") != "block:%d:%s" % (att.height, bhash):
            return result(aid, "contradicted", "anchor_commitment_mismatch", None, "artifact", "anchor_record_ref does not match the header")
        if entry["anchored_at"] != ac.iso_from_unix(t):
            return result(aid, "contradicted", "anchor_commitment_mismatch", None, "artifact", "anchored_at does not match the block time")
        return result(aid, "verified", None, None, "artifact",
                      "committed in Bitcoin block %d (%s), header proof of work valid; main-chain membership of that "
                      "block is checked separately against any Bitcoin node or explorer" % (att.height, bhash))
    return result(aid, "indeterminate", "anchor_pending", "absence", "operator", "no usable attestation")


def verify_rfc3161(entry, files, commitment):
    aid = entry["anchor_id"]
    if not shutil.which("openssl"):
        return result(aid, "not_evaluated", "anchor_method_unverifiable", "instrument_failure", "verifier", "openssl binary not available")
    for need in ("token.tsr", "tsa-ca.pem", "tsa.crt"):
        if need not in files:
            return result(aid, "indeterminate", "anchor_proof_absent", "absence", "operator", "proof bundle lacks " + need)
    p = subprocess.run(["openssl", "ts", "-verify", "-digest", commitment, "-in", files["token.tsr"],
                        "-CAfile", files["tsa-ca.pem"], "-untrusted", files["tsa.crt"]], capture_output=True, text=True)
    if "Verification: OK" not in (p.stdout + p.stderr):
        return result(aid, "contradicted", "anchor_commitment_mismatch", None, "artifact",
                      "token does not verify for this digest against the supplied chain: " + (p.stdout + p.stderr).strip()[-200:])
    q = subprocess.run(["openssl", "ts", "-reply", "-in", files["token.tsr"], "-text"], capture_output=True, text=True)
    import re
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from produce import openssl_time_to_iso  # noqa: E402
    gen = re.search(r"Time stamp: (.+)", q.stdout)
    serial = re.search(r"Serial number: (\S+)", q.stdout)
    if not gen or openssl_time_to_iso(gen.group(1).strip()) != entry.get("anchored_at"):
        return result(aid, "contradicted", "anchor_commitment_mismatch", None, "artifact", "anchored_at does not match the token time")
    if not serial or entry.get("anchor_record_ref") != "serial:" + serial.group(1):
        return result(aid, "contradicted", "anchor_commitment_mismatch", None, "artifact", "anchor_record_ref does not match the token serial")
    return result(aid, "verified", None, None, "artifact",
                  "RFC 3161 token verifies for the digest against the supplied TSA chain; token time %s" % entry["anchored_at"])


METHODS = {"opentimestamps": verify_ots, "timestamp_authority": verify_rfc3161}
IDENTITY_PROFILES = {ac.PROFILE_OTS, ac.PROFILE_RFC3161}


def verify_block(base, subject=None):
    block = ac.load_block(base)
    if block is None:
        raise FileNotFoundError(os.path.join(base, ac.ANCHORING_FILE))
    out = []
    shash = block["anchored_subject_hash"]
    if subject is not None and ac.sha256_file(subject) != shash:
        out.append(result("subject", "contradicted", "anchor_commitment_mismatch", None, "artifact",
                          "subject file does not hash to anchored_subject_hash"))
        return out
    for entry in block["anchors"]:
        aid = entry["anchor_id"]
        if entry.get("basis_status") != DEMONSTRATED:
            out.append(result(aid, "indeterminate", "basis_not_demonstrated", "absence", "operator",
                              "basis_status is %s" % entry.get("basis_status")))
            continue
        commitment = entry.get("anchor_commitment_hash")
        if entry.get("anchor_profile_id") in IDENTITY_PROFILES and commitment != shash:
            out.append(result(aid, "contradicted", "anchor_commitment_mismatch", None, "artifact",
                              "identity profile requires commitment == subject hash"))
            continue
        files, failure = check_manifest(base, entry)
        if failure:
            out.append(failure)
            continue
        fn = METHODS.get(entry.get("anchoring_method"))
        if fn is None:
            if not entry.get("anchor_verification_procedure_ref"):
                out.append(result(aid, "indeterminate", "anchor_method_unverifiable", "absence", "operator", "no verification procedure"))
            else:
                out.append(result(aid, "not_evaluated", "anchor_method_unverifiable", None, "verifier",
                                  "no verifier for %s in this version" % entry.get("anchoring_method")))
            continue
        out.append(fn(entry, files, commitment))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir")
    ap.add_argument("--subject")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        results = verify_block(args.dir, args.subject)
    except (OSError, ValueError, KeyError) as exc:
        print("ERROR cannot read anchoring block: %s" % exc)
        return 2
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            extra = "/".join(x for x in (r["state_reason"], r["condition"]) if x)
            print("%-14s %-18s %-40s %s" % (r["state"], r["anchor_id"], extra, r["observed"]))
    return 1 if any(r["state"] == "contradicted" for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
