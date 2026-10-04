#!/usr/bin/env python3
"""Two-sided self-test for verify_anchor.py with SYNTHETIC fixtures (no network).

Builds, in a temporary directory: a throwaway local RFC 3161 time-stamp authority and an
OpenTimestamps proof attested in a regtest-difficulty Bitcoin header. These are test
fixtures only; real-run vectors live under anchors/ and vectors/anchoring/.

Exit 0 when every case returns its expected state and condition.
"""
import copy
import hashlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anchor_common as ac  # noqa: E402
import verify_anchor as va  # noqa: E402

SUBJECT = b'{"axes_test_subject":"anchoring self-test"}'
DIGEST = hashlib.sha256(SUBJECT).digest()
DHEX = DIGEST.hex()
FAILS = []


def expect(name, results, state, condition=None):
    r = results[-1]
    ok = r["state"] == state and (condition is None or r["condition"] == condition)
    print("%s %-44s -> %s/%s" % ("ok  " if ok else "FAIL", name, r["state"], r["condition"]))
    if not ok:
        FAILS.append(name)


def sh(*args, cwd=None, data=None):
    subprocess.run(args, cwd=cwd, input=data, check=True, capture_output=True)


def build_tsa(root):
    """Local CA + TSA certificate and one RFC 3161 token over DIGEST."""
    cnf = os.path.join(root, "tsa.cnf")
    with open(cnf, "w") as f:
        f.write("""[ tsa ]
default_tsa = tsa_config
[ tsa_config ]
serial = %(r)s/serial
signer_cert = %(r)s/tsa.crt
certs = %(r)s/tsa.crt
signer_key = %(r)s/tsa.key
signer_digest = sha256
default_policy = 1.2.3.4.1
digests = sha256
accuracy = secs:1
ordering = no
tsa_name = no
ess_cert_id_chain = no
ess_cert_id_alg = sha256
[ tsa_ext ]
basicConstraints = critical,CA:FALSE
extendedKeyUsage = critical,timeStamping
keyUsage = critical,digitalSignature
""" % {"r": root})
    with open(os.path.join(root, "serial"), "w") as f:
        f.write("01\n")
    sh("openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", "ca.key", "-out", "tsa-ca.pem",
       "-days", "2", "-subj", "/CN=AXES test CA", cwd=root)
    sh("openssl", "req", "-newkey", "rsa:2048", "-nodes", "-keyout", "tsa.key", "-out", "tsa.csr", "-subj", "/CN=AXES test TSA", cwd=root)
    sh("openssl", "x509", "-req", "-in", "tsa.csr", "-CA", "tsa-ca.pem", "-CAkey", "ca.key", "-CAcreateserial",
       "-out", "tsa.crt", "-days", "2", "-extfile", cnf, "-extensions", "tsa_ext", cwd=root)
    sh("openssl", "ts", "-query", "-digest", DHEX, "-sha256", "-cert", "-out", "req.tsq", cwd=root)
    sh("openssl", "ts", "-reply", "-config", cnf, "-queryfile", "req.tsq", "-out", "token.tsr", cwd=root)
    out = subprocess.run(["openssl", "ts", "-reply", "-in", "token.tsr", "-text"], cwd=root, capture_output=True, text=True).stdout
    import re
    from produce import openssl_time_to_iso
    gen = openssl_time_to_iso(re.search(r"Time stamp: (.+)", out).group(1).strip())
    serial = re.search(r"Serial number: (\S+)", out).group(1)
    return gen, serial


def build_ots(pdir, with_btc=True):
    from opentimestamps.core.op import OpAppend, OpSHA256
    from opentimestamps.core.serialize import StreamSerializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp
    from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
    ts = Timestamp(DIGEST)
    t1 = ts.ops.add(OpAppend(b"\x01" * 16))
    t2 = t1.ops.add(OpSHA256())
    height = 100
    if with_btc:
        t2.attestations.add(BitcoinBlockHeaderAttestation(height))
    else:
        t2.attestations.add(PendingAttestation("https://calendar.example"))
    buf = io.BytesIO()
    DetachedTimestampFile(OpSHA256(), ts).serialize(StreamSerializationContext(buf))
    with open(os.path.join(pdir, "subject.ots"), "wb") as f:
        f.write(buf.getvalue())
    # regtest-difficulty header whose merkle root is the attested value
    version = (0x20000000).to_bytes(4, "little")
    prev = b"\x00" * 32
    t = 1790000000
    bits = 0x207FFFFF
    for nonce in range(1 << 20):
        raw = version + prev + t2.msg + t.to_bytes(4, "little") + bits.to_bytes(4, "little") + nonce.to_bytes(4, "little")
        h = hashlib.sha256(hashlib.sha256(raw).digest()).digest()
        if int.from_bytes(h, "little") <= va.bits_to_target(bits):
            break
    with open(os.path.join(pdir, "bitcoin-header-%d.hex" % height), "w") as f:
        f.write(raw.hex() + "\n")
    return height, h[::-1].hex(), t


def make_block(root):
    base = os.path.join(root, "anchor")
    block = ac.new_block("release_statement", DHEX)
    # RFC 3161
    tdir = os.path.join(base, "proofs", "timestamp_authority")
    os.makedirs(tdir)
    tsa_root = os.path.join(root, "tsa")
    os.makedirs(tsa_root)
    gen, serial = build_tsa(tsa_root)
    for n in ("token.tsr", "tsa-ca.pem", "tsa.crt"):
        shutil.copy(os.path.join(tsa_root, n), tdir)
    ac.upsert_anchor(block, {
        "anchor_id": "anch:tsa", "anchoring_method": "timestamp_authority", "anchor_profile_id": ac.PROFILE_RFC3161,
        "basis_status": "demonstrated", "anchor_commitment_hash": DHEX, "anchor_commitment_hash_algorithm": "SHA-256",
        "anchor_requested_at": gen, "anchored_at": gen, "anchor_service_ref": "local-test-tsa",
        "anchor_record_ref": "serial:" + serial, "anchor_operator_ref": "local-test-tsa",
        "anchor_proof_ref": "proofs/timestamp_authority/" + ac.PROOF_MANIFEST,
        "anchor_proof_hash": ac.write_proof_manifest(tdir, ["token.tsr", "tsa-ca.pem", "tsa.crt"], "synthetic"),
        "anchor_verification_procedure_ref": "docs/anchoring-profiles.md"})
    # OpenTimestamps
    odir = os.path.join(base, "proofs", "opentimestamps")
    os.makedirs(odir)
    height, bhash, t = build_ots(odir)
    ac.upsert_anchor(block, {
        "anchor_id": "anch:ots", "anchoring_method": "opentimestamps", "anchor_profile_id": ac.PROFILE_OTS,
        "basis_status": "demonstrated", "anchor_commitment_hash": DHEX, "anchor_commitment_hash_algorithm": "SHA-256",
        "anchor_requested_at": ac.iso_from_unix(t - 600), "anchored_at": ac.iso_from_unix(t),
        "anchor_service_ref": ac.BITCOIN_MAINNET, "anchor_record_ref": "block:%d:%s" % (height, bhash),
        "anchor_operator_ref": None, "anchor_proof_ref": "proofs/opentimestamps/" + ac.PROOF_MANIFEST,
        "anchor_proof_hash": ac.write_proof_manifest(odir, ["subject.ots", "bitcoin-header-%d.hex" % height], "synthetic"),
        "anchor_verification_procedure_ref": "docs/anchoring-profiles.md"})
    ac.write_json(os.path.join(base, ac.ANCHORING_FILE), block)
    return base


def only(base, aid):
    return [r for r in va.verify_block(base) if r["anchor_id"] == aid]


def mutate(base, fn):
    path = os.path.join(base, ac.ANCHORING_FILE)
    block = ac.read_json(path)
    orig = copy.deepcopy(block)
    fn(block)
    ac.write_json(path, block)
    return lambda: ac.write_json(path, orig)


def main():
    strict = os.environ.get("AXES_REQUIRE_ANCHOR_DEPS") == "1"
    if not shutil.which("openssl"):
        print("SKIP openssl not available")
        return 1 if strict else 0
    try:
        import opentimestamps  # noqa: F401
    except ImportError:
        print("SKIP opentimestamps not installed")
        return 1 if strict else 0
    with tempfile.TemporaryDirectory() as root:
        base = make_block(root)
        expect("rfc3161 verifies", only(base, "anch:tsa"), "verified")
        expect("ots verifies", only(base, "anch:ots"), "verified")

        undo = mutate(base, lambda b: b["anchors"][1].update(anchored_at="2020-01-01T00:00:00.000Z"))
        expect("rfc3161 anchored_at altered", only(base, "anch:tsa"), "contradicted", "anchor_commitment_mismatch")
        undo()

        tok = os.path.join(base, "proofs", "timestamp_authority", "token.tsr")
        data = open(tok, "rb").read()
        open(tok, "wb").write(data[:-1] + bytes([data[-1] ^ 1]))
        expect("rfc3161 token byte flipped", only(base, "anch:tsa"), "contradicted", "anchor_proof_hash_mismatch")
        open(tok, "wb").write(data)

        # token for a different digest, manifest rebuilt: only the RFC 3161 check can catch it
        tsa_root = os.path.join(root, "tsa")
        sh("openssl", "ts", "-query", "-digest", "11" * 32, "-sha256", "-cert", "-out", "other.tsq", cwd=tsa_root)
        sh("openssl", "ts", "-reply", "-config", os.path.join(tsa_root, "tsa.cnf"), "-queryfile", "other.tsq", "-out", "other.tsr", cwd=tsa_root)
        tdir = os.path.dirname(tok)
        shutil.copy(os.path.join(tsa_root, "other.tsr"), tok)
        undo = mutate(base, lambda b: b["anchors"][1].update(
            anchor_proof_hash=ac.write_proof_manifest(tdir, ["token.tsr", "tsa-ca.pem", "tsa.crt"], "tampered")))
        expect("rfc3161 token for other digest (manifest rebuilt)", only(base, "anch:tsa"), "contradicted", "anchor_commitment_mismatch")
        open(tok, "wb").write(data)
        ac.write_proof_manifest(tdir, ["token.tsr", "tsa-ca.pem", "tsa.crt"], "synthetic")
        undo()

        hdr = os.path.join(base, "proofs", "opentimestamps", "bitcoin-header-100.hex")
        hd = open(hdr).read()
        odir0 = os.path.dirname(hdr)
        raw = bytearray(bytes.fromhex(hd.strip()))
        raw[40] ^= 1  # inside the merkle root
        open(hdr, "w").write(raw.hex() + "\n")
        undo = mutate(base, lambda b: b["anchors"][0].update(
            anchor_proof_hash=ac.write_proof_manifest(odir0, ["subject.ots", "bitcoin-header-100.hex"], "tampered")))
        expect("ots header merkle root altered (manifest rebuilt)", only(base, "anch:ots"), "contradicted", "anchor_commitment_mismatch")
        open(hdr, "w").write(hd)
        ac.write_proof_manifest(odir0, ["subject.ots", "bitcoin-header-100.hex"], "synthetic")
        undo()

        os.remove(hdr)
        expect("ots header missing", only(base, "anch:ots"), "not_evaluated", "anchor_proof_unresolvable")
        open(hdr, "w").write(hd)

        undo = mutate(base, lambda b: b["anchors"][0].update(anchor_commitment_hash="00" * 32))
        expect("ots commitment differs from subject", only(base, "anch:ots"), "contradicted", "anchor_commitment_mismatch")
        undo()

        undo = mutate(base, lambda b: b["anchors"][0].update(basis_status="simulated"))
        expect("simulated never verifies", only(base, "anch:ots"), "indeterminate", "basis_not_demonstrated")
        undo()

        undo = mutate(base, lambda b: b["anchors"][0].pop("anchor_proof_ref"))
        expect("proof ref absent", only(base, "anch:ots"), "indeterminate", "anchor_proof_absent")
        undo()

        odir = os.path.join(base, "proofs", "opentimestamps")
        build_ots(odir, with_btc=False)
        undo = mutate(base, lambda b: (b["anchors"][0].pop("anchored_at"), b["anchors"][0].update(
            anchor_proof_hash=ac.write_proof_manifest(odir, ["subject.ots"], "synthetic pending"))))
        expect("ots pending", only(base, "anch:ots"), "indeterminate", "anchor_pending")
        undo()

        old = os.environ.get("PATH", "")
        os.environ["PATH"] = ""
        try:
            expect("openssl absent -> instrument_failure", only(base, "anch:tsa"), "not_evaluated", "anchor_method_unverifiable")
        finally:
            os.environ["PATH"] = old
    print("FAILED: %s" % FAILS if FAILS else "OK anchoring self-test")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
